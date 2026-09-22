#!/usr/bin/env python3
"""D0-S3 Stage-1 production training runtime (blocks B1 = L1, B3 = L2).

This script IS the "D0 trainer runtime" that pins production training
constants (configs/reexploration/config.yaml: "Production iteration counts
are pinned by the D0 trainer runtime, outside this tree").  The in-repo CPU
smoke trainers (train_fact_surrogate / train_l1_coordinate_heads) are
reference loops on synthetic uniform-shape batches; this runtime trains on
the real ragged lab-asset-v3 episode stream by owning the loop while calling
the frozen primitives verbatim: model forwards, loss composition helpers,
the E-3 engine-bridge mechanism, the RNG-tree substreams, and the L1-5/L2-4
lock-checkpoint writer.

Design pins (recorded in every block manifest):

* Training episodes are generated on the fly from the frozen DGP derivation
  (seed_root, episode_index) at episode indices [episode_start,
  episode_start + n_train), DISJOINT from the 64 eval episodes of the D0-S2
  corpus (indices 0..63) so evaluation fixtures are never trained on.
* Episodes are bucketed by exact round count (the stream is ragged, T in
  ~7..22); each iteration is one pass over all buckets in ascending-T order
  with a single Adam step, and the channel loss is the exact global
  round-weighted mean  sum(((pred-target)/s_ch)^2) / (sum_e T_e * C) — the
  frozen trainers' `.mean()` generalized to ragged T (identical on uniform
  batches).
* Device is CPU-only: the trained surfaces are d_hidden-64 MLP/GRU models
  (GPU advantage negligible), the through-M engine bridge is per-call pure
  Python, and G8/G9 byte-identical re-execution requires deterministic
  kernels (CUDA RNN backward is not).
* Raw arms supervise the coordinate head decode exactly as the frozen
  loops; through-M arms supervise the engine-executed channel cumulation.
  Through-M coordinate composition mode (blind vs differentiated) is a
  PI-ratified constant -- see --through-m-coordinate-mode.

No frozen file is modified; scripts/lab_asset/ is imported read-only.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict
from multiprocessing import Pool
from pathlib import Path
from typing import Any

import yaml

# ------------------------------------------------------------------ constants

CAMPAIGN_ID = "alpha_cube_d0_20260919"
DEFAULT_R2_PREFIX = "alpha_cube_d0_20260921/train_stage1/"

FREEZE_COMMIT = "f4e61bafed21f12a6ec73dbe82b9ed4ea87bdd37"
FREEZE_FILE_PINS: dict[str, str] = {
    "configs/reexploration/dgp/lab_asset.yaml": (
        "06b9691af333be8a6891ee1213032a785e61c03c3c26e8f8a4beb159b202c801"
    ),
    "experiments/reexploration/seed_stream_manifest_20260907/seeds_manifest.json": (
        "361679c4a56e8e7fe7d393499ed22f5c9f61bef81706a1befa8ca7df27ea32f8"
    ),
    "scripts/lab_asset/dgp_request_generator.py": (
        "2cef5a334cc7f0020459062e3f37d76aab55d4440c8a305e50a222bfd4d72152"
    ),
}

# PI decision pi_d0s2_corpus_seed_pins_20260921: corpus = 64 eval episodes.
# Training starts one past the corpus window.
CORPUS_EPISODES_PER_SEED = 64
DEFAULT_EPISODE_START = CORPUS_EPISODES_PER_SEED

TRAINING_AXIS = "id"          # training stream is the ID axis (C4)
TRAINING_KERNEL = "fifo"      # C4(i): through-M training embeds M with FIFO
N_CHANNELS = 2
K_INFERENCE_DRAWS = 16        # C2(b) amendment (11); LockCorpusBinding n_draws

RUNTIME_ID = "train_stage1_d0s3"
RUNTIME_SCHEMA = "ecomd-d0s3-train-runtime-v1"

ARM_IDS = (
    "absolute_raw",
    "increment_raw",
    "absolute_through_m",
    "increment_through_m",
)

LINEAGE_BLOCK = {"l1": "B1", "l2": "B3"}

_SURFACE: dict[str, Any] = {}


# ------------------------------------------------------------------- helpers

def canonical_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_bytes(payload: bytes) -> str:
    import hashlib

    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write_bytes(path: Path, payload: bytes) -> None:
    tmp = path.with_name(f"{path.name}.tmp.{os.getpid()}")
    with open(tmp, "wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def ensure_repo(repo_root: Path) -> None:
    sys.path.insert(0, str(repo_root / "scripts"))
    sys.path.insert(0, str(repo_root))


def enforce_freeze_pins(repo_root: Path) -> None:
    for rel, pinned in FREEZE_FILE_PINS.items():
        actual = sha256_file(repo_root / rel)
        if actual != pinned:
            raise RuntimeError(
                f"freeze file pin violated for {rel}: {actual} != {pinned}"
            )
    head = git_head(repo_root)
    if head is None:
        raise RuntimeError("cannot resolve git HEAD (git missing or not a repo)")
    if not descends_from(repo_root, head, FREEZE_COMMIT):
        raise RuntimeError(
            f"git HEAD {head[:9]} does not descend from freeze commit {FREEZE_COMMIT[:9]}"
        )


def descends_from(repo_root: Path, head: str, ancestor: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "merge-base", "--is-ancestor", ancestor, head],
        capture_output=True,
    )
    return result.returncode == 0


def git_head(repo_root: Path) -> str | None:
    try:
        return subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except Exception:
        return None


def load_surface(repo_root: Path) -> dict[str, Any]:
    """Import repo modules once per process (pool workers re-import)."""

    if _SURFACE:
        return _SURFACE
    ensure_repo(repo_root)
    from lab_asset import dgp_request_generator as dgp
    from lab_asset.conserving_emitter import (
        conservation_violations,
        emit_conserving_channels,
        settlement_violations,
    )
    from lab_asset.matching import ReferenceEngine
    from lab_asset.schema import AllocationRule

    from ecomd.corpus.fexec_projector import project_fexec_corpus
    from ecomd.corpus.l1_corpus_adapter import build_l1_corpus
    from ecomd.mechanisms.through_m import Kernel
    from ecomd.models.fact_surrogate import (
        FactSurrogateBatch,
        FactSurrogateConfig,
        RecurrentFactSurrogate,
    )
    from ecomd.models.l1_coordinate_heads import (
        L1CoordinateHeads,
        L1CoordinateHeadsConfig,
    )
    from ecomd.training.l1_supervised import (
        MinibatchOrderStream,
        build_coordinate_targets,
        coordinate_state_prediction,
        init_substream_seed,
    )
    from ecomd.training.lock_checkpoint import LockCorpusBinding, save_lock_checkpoint
    from ecomd.training.losses import smooth_dev
    from ecomd.training.train_fact_surrogate import (
        Coordinate,
        Enforcement,
        EstimatorKind,
        FactSurrogateTrainConfig,
        MechanismBackend,
        build_mechanism,
        config_payload,
        derive_substream_seeds,
        substream_generator,
    )

    _SURFACE.update(
        dgp=dgp,
        conservation_violations=conservation_violations,
        emit_conserving_channels=emit_conserving_channels,
        settlement_violations=settlement_violations,
        ReferenceEngine=ReferenceEngine,
        AllocationRule=AllocationRule,
        project_fexec_corpus=project_fexec_corpus,
        build_l1_corpus=build_l1_corpus,
        Kernel=Kernel,
        FactSurrogateBatch=FactSurrogateBatch,
        FactSurrogateConfig=FactSurrogateConfig,
        RecurrentFactSurrogate=RecurrentFactSurrogate,
        L1CoordinateHeads=L1CoordinateHeads,
        L1CoordinateHeadsConfig=L1CoordinateHeadsConfig,
        MinibatchOrderStream=MinibatchOrderStream,
        build_coordinate_targets=build_coordinate_targets,
        coordinate_state_prediction=coordinate_state_prediction,
        init_substream_seed=init_substream_seed,
        LockCorpusBinding=LockCorpusBinding,
        save_lock_checkpoint=save_lock_checkpoint,
        smooth_dev=smooth_dev,
        Coordinate=Coordinate,
        Enforcement=Enforcement,
        EstimatorKind=EstimatorKind,
        FactSurrogateTrainConfig=FactSurrogateTrainConfig,
        MechanismBackend=MechanismBackend,
        build_mechanism=build_mechanism,
        config_payload=config_payload,
        derive_substream_seeds=derive_substream_seeds,
        substream_generator=substream_generator,
    )
    return _SURFACE


# ------------------------------------------------------- configs (E-5 frozen)

def load_arm(repo_root: Path, arm_id: str) -> dict[str, Any]:
    path = repo_root / "configs" / "reexploration" / "arm" / f"{arm_id}.yaml"
    arm = yaml.safe_load(path.read_text())
    for field in ("coordinate", "enforcement", "estimator", "training_kernel"):
        if field not in arm:
            raise RuntimeError(f"arm config {path.name} missing field {field}")
    if arm["training_kernel"] != TRAINING_KERNEL:
        raise RuntimeError(
            f"arm {arm_id} training_kernel={arm['training_kernel']} violates "
            f"C4(i) (through-M training embeds M with FIFO; all trained arms fifo)"
        )
    return arm


def load_lineage(repo_root: Path, lineage: str) -> dict[str, Any]:
    path = repo_root / "configs" / "reexploration" / "lineage" / f"{lineage}.yaml"
    return yaml.safe_load(path.read_text())


def check_lineage_against_module_defaults(lineage_cfg: dict[str, Any], surface: dict[str, Any]) -> None:
    """Subset of validate_e5_configs: the fields this runtime consumes must
    equal the frozen module defaults (the tree 'cannot drift from the code')."""

    model = lineage_cfg["model"]
    if model["d_hidden"] != 64 or model["n_channels"] != 2 or model["n_slots"] != 8:
        raise RuntimeError(f"lineage model block drifted from module defaults: {model}")
    train = lineage_cfg["train"]
    expected = {
        "lr": 0.0003,
        "grad_clip": 1.0,
        "w_supervised": 1.0,
        "w_gain_loss": 0.0,
        "w_agg_gauss": 0.0,
        "w_fano": 0.0,
        "w_dfa_hurst": 0.0,
    }
    for key, value in expected.items():
        if train.get(key) != value:
            raise RuntimeError(
                f"lineage train.{key}={train.get(key)} drifted from module default {value}"
            )
    if train.get("n_iters") != 8:
        raise RuntimeError(
            "lineage train.n_iters must stay the frozen module default 8; "
            "production n_iters is a runtime pin (--n-iters), never a tree edit"
        )


def load_dgp_config(repo_root: Path) -> dict[str, Any]:
    """The DGP parameter mapping (the yaml's `config` sub-key, as the corpus
    driver passes it); the wrapper keys dgp_id/dgp_label/series_law are not
    DGPConfig fields."""
    path = repo_root / "configs" / "reexploration" / "dgp" / "lab_asset.yaml"
    return yaml.safe_load(path.read_text())["config"]


# --------------------------------------------------- training-episode stream

def train_data_dir(out_dir: Path, seed_root: int) -> Path:
    return out_dir / "train_data" / f"seed_{seed_root:06d}"


def generate_training_episode(surface: dict[str, Any], job: dict[str, Any],
                              episode_index: int) -> dict[str, Any]:
    """One training episode: frozen DGP derivation -> engine -> corpus tensors.

    Identical derivation chain to the D0-S2 corpus driver (axis id, kernel
    fifo), at episode indices >= 64 (disjoint from the eval fixtures).
    """

    import torch

    dgp = surface["dgp"]
    seed_root = job["seed_root"]
    cfg = dgp.config_for_axis(dgp.config_from_mapping(job["config"]), TRAINING_AXIS)
    stream = dgp.generate_episode(seed_root, episode_index, cfg)
    episode_sha = sha256_bytes(dgp.episode_canonical_json(stream))
    draw_seed = dgp.derive_seed(seed_root, "draw", episode_index)
    prestate = dgp.build_prestate(
        stream, surface["AllocationRule"](TRAINING_KERNEL), draw_seed
    )

    engine = surface["ReferenceEngine"](prestate)
    for request in dgp.order_requests(stream):
        engine.submit(request)
    engine.finish()
    tape = engine.tape

    series = surface["emit_conserving_channels"](prestate, tape)
    violations = surface["conservation_violations"](series)
    settlement = surface["settlement_violations"](prestate, tape, series)
    if violations or settlement:
        raise RuntimeError(
            f"conservation/settlement gate failed seed_root={seed_root} "
            f"episode={episode_index}: {violations + settlement}"
        )

    if job["lineage"] == "l1":
        corpus = surface["build_l1_corpus"](prestate, tape, draw_seed, series=series)
        features = corpus.features
        channels = corpus.channels_abs
        corpus_hash = corpus.corpus_hash
    else:
        corpus = surface["project_fexec_corpus"](
            prestate, tape, draw_seed, n_slots=8, dtype=torch.float32
        )
        # E-1/E-4 round-grid agreement (parity with the corpus driver's hard
        # gate and the L1 branch's internal checks).
        if corpus.channels_delta.tolist() != series.increment_matrix():
            raise RuntimeError(
                f"E-1/E-4 grid agreement failed seed_root={seed_root} "
                f"episode={episode_index}"
            )
        features = corpus.features
        channels = corpus.channels_cumulative
        corpus_hash = corpus.corpus_hash

    payload = {
        "features": features.to(torch.float32),
        "channels": channels.to(torch.float32),
        "slot_prices": corpus.slot_prices.to(torch.int64),
        "n_rounds": int(features.shape[0]),
        "episode_sha256": episode_sha,
        "prestate_hash": tape[0].payload["prestate_hash"],
        "corpus_hash": corpus_hash,
    }
    out = Path(job["dir"]) / f"episode_{episode_index:06d}.pt"
    torch.save(payload, out)
    return {
        "episode_index": episode_index,
        "n_rounds": payload["n_rounds"],
        "episode_sha256": episode_sha,
        "prestate_hash": payload["prestate_hash"],
        "corpus_hash": corpus_hash,
        "file": out.name,
        "file_sha256": sha256_file(out),
    }


def _episode_worker(args: tuple[dict[str, Any], int]) -> dict[str, Any]:
    job, episode_index = args
    return generate_training_episode(_SURFACE or load_surface(Path(job["repo_root"])), job, episode_index)


def stage_seed_episodes(args: Any) -> dict[str, Any]:
    """Pool initializer target: stage every training episode for one seed."""

    job = args["job"]
    surface = load_surface(Path(job["repo_root"]))
    tdir = Path(job["dir"])
    tdir.mkdir(parents=True, exist_ok=True)
    manifest_path = tdir / "train_episodes_manifest.json"

    wanted = list(range(job["episode_start"], job["episode_start"] + job["n_train"]))
    entries: list[dict[str, Any]] = []
    prior = None
    if manifest_path.exists():
        prior = json.loads(manifest_path.read_text())
        if prior.get("n_train") != job["n_train"] or prior.get("episode_start") != job["episode_start"]:
            prior = None

    todo = []
    if prior is not None:
        done_files = {e["file"]: e for e in prior["episodes"]}
        for index in wanted:
            name = f"episode_{index:06d}.pt"
            entry = done_files.get(name)
            if entry is not None and (tdir / name).exists():
                entries.append(entry)
            else:
                todo.append(index)
    else:
        todo = wanted

    if todo:
        import torch

        torch.set_num_threads(1)
        with Pool(job["workers"], initializer=_pool_init,
                  initargs=(Path(job["repo_root"]),)) as pool:
            produced = pool.map(
                _episode_worker, [({**job, "dir": str(tdir)}, i) for i in todo],
                chunksize=16,
            )
        entries.extend(produced)
        entries.sort(key=lambda e: e["episode_index"])

    corpus_hash = sha256_bytes(canonical_bytes(
        [[e["episode_index"], e["episode_sha256"]] for e in entries]
    ))
    prestate_hash = sha256_bytes(canonical_bytes(
        [e["prestate_hash"] for e in entries]
    ))
    manifest = {
        "schema_version": RUNTIME_SCHEMA,
        "campaign_id": CAMPAIGN_ID,
        "seed_root": job["seed_root"],
        "lineage": job["lineage"],
        "axis": TRAINING_AXIS,
        "kernel": TRAINING_KERNEL,
        "episode_start": job["episode_start"],
        "n_train": job["n_train"],
        "corpus_window_reserved": list(range(0, CORPUS_EPISODES_PER_SEED)),
        "episodes": entries,
        "train_corpus_hash": corpus_hash,
        "train_prestate_hash": prestate_hash,
    }
    atomic_write_bytes(manifest_path, canonical_bytes(manifest))
    return manifest


def _pool_init(repo_root: Path) -> None:
    import torch

    torch.set_num_threads(1)
    load_surface(repo_root)


# ------------------------------------------------------------- batch assembly

class SeedBatches:
    """Per-seed training batches bucketed by exact round count.

    Buckets are held in ascending-T order; the training iteration walks them
    in that fixed order so the engine-bridge kernel stream consumption is
    deterministic.
    """

    def __init__(self, tdir: Path) -> None:
        import torch

        manifest = json.loads((tdir / "train_episodes_manifest.json").read_text())
        by_rounds: dict[int, list[dict[str, Any]]] = {}
        for entry in manifest["episodes"]:
            payload = torch.load(tdir / entry["file"], map_location="cpu", weights_only=False)
            by_rounds.setdefault(entry["n_rounds"], []).append(payload)
        self.manifest = manifest
        self.buckets: list[dict[str, Any]] = []
        for rounds in sorted(by_rounds):
            items = by_rounds[rounds]
            self.buckets.append({
                "n_rounds": rounds,
                "n_episodes": len(items),
                "features": torch.stack([it["features"] for it in items]),
                "channels": torch.stack([it["channels"] for it in items]),
                "slot_prices": torch.stack([it["slot_prices"] for it in items]),
            })
        self.total_rounds = sum(b["n_rounds"] * b["n_episodes"] for b in self.buckets)
        self.total_episodes = sum(b["n_episodes"] for b in self.buckets)
        if self.total_episodes != manifest["n_train"]:
            raise RuntimeError(
                f"bucket assembly lost episodes: {self.total_episodes} != {manifest['n_train']}"
            )

    def shuffled(self, bucket: dict[str, Any], order) -> Any:
        from ecomd.models.fact_surrogate import FactSurrogateBatch

        return FactSurrogateBatch(
            features=bucket["features"][order],
            channels=bucket["channels"][order],
            slot_prices=bucket["slot_prices"][order],
            channels_init=None,
        )


# ------------------------------------------------- through-M channel composition

def mechanism_channel_prediction(batch: Any, flow: Any, demand: Any, mechanism: Any,
                                 coordinate_mode: str, increment_arm: bool) -> Any:
    """Engine-executed conserving-channel prediction (contract C5 exact arm).

    Mirrors RecurrentFactSurrogate.forward's mechanism loop verbatim
    (step-major, episode-inner; allocation.sum() and allocation*slot_prices
    cumulated), with the PI-ratified coordinate composition:

    * blind          -- cumulation from the zero/init base for both coordinates
                        (the frozen _predicted_channels semantics).
    * differentiated -- INCREMENT arms predict observed-previous + per-round
                        mechanism increment (teacher-forced base, mirroring the
                        raw increment head's composition); ABSOLUTE arms
                        cumulate from the base.

    Device policy (pi_d0s3_train_constants_20260921 item 4): the engine bridge
    is a CPU Python engine, so on CUDA each per-call slice round-trips through
    CPU (.to("cpu") is autograd-transparent and a no-op on CPU; the composed
    increments move back to the flow device before cumulation).
    """

    import torch

    device = flow.device
    batch_size, n_rounds, _ = flow.shape
    rows = []
    for step in range(n_rounds):
        for episode in range(batch_size):
            allocation = mechanism(
                flow[episode, step].to("cpu"),
                int(demand[episode, step].detach().item()),
            )
            cash_increment = (
                allocation * batch.slot_prices[episode, step].to("cpu")
            ).sum()
            rows.append(torch.stack(
                (allocation.sum().unsqueeze(0), cash_increment.unsqueeze(0))
            ))
    increments = (
        torch.stack(rows).view(n_rounds, batch_size, N_CHANNELS)
        .permute(1, 0, 2).to(device)
    )
    if batch.channels_init is not None:
        base = batch.channels_init.unsqueeze(1).to(device)
    else:
        base = torch.zeros(batch_size, 1, N_CHANNELS, dtype=increments.dtype, device=device)
    if coordinate_mode == "differentiated" and increment_arm:
        previous = torch.cat((base, batch.channels[:, :-1]), dim=1)
        return previous + increments
    return base + torch.cumsum(increments, dim=1)


def raw_channel_prediction(output: Any, batch: Any, surface: dict[str, Any],
                           config: Any) -> Any:
    """The frozen _predicted_channels raw branch (L2 config semantics)."""

    import torch

    target = batch.channels
    if config.coordinate is surface["Coordinate"].ABSOLUTE:
        return output.abs_channels
    base = (
        batch.channels_init.unsqueeze(1)
        if batch.channels_init is not None
        else torch.zeros_like(target[:, :1])
    )
    previous = torch.cat((base, target[:, :-1]), dim=1)
    return previous + output.inc_channels


def save_progress_snapshot(path: Path, model: Any, optimizer: Any,
                           iteration: int, config: dict[str, Any], seed: int) -> None:
    """Save a private progress checkpoint, excluded from final lock inputs."""
    import io
    import torch

    payload = {
        "role": "private_training_progress", "resume_supported": False,
        "iter_idx": iteration, "seed": seed, "config": config,
        "model_state_dict": {k: v.detach().cpu().clone() for k, v in model.state_dict().items()},
        "optimizer_state_dict": optimizer.state_dict(),
    }
    buffer = io.BytesIO()
    torch.save(payload, buffer)
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_bytes(path, buffer.getvalue())


# ------------------------------------------------------------- training jobs

def train_one(job: dict[str, Any]) -> dict[str, Any]:
    import torch

    surface = load_surface(Path(job["repo_root"]))
    arm = job["arm"]
    lineage = job["lineage"]
    seed_root = job["seed_root"]
    n_iters = job["n_iters"]
    coordinate_mode = job["through_m_coordinate_mode"]
    device = torch.device(job.get("device", "cpu"))
    through_m = arm["enforcement"] == "through_m"
    increment_arm = arm["coordinate"] == "increment"

    lineage_cfg = load_lineage(Path(job["repo_root"]), lineage)
    check_lineage_against_module_defaults(lineage_cfg, surface)

    seeds_map = surface["derive_substream_seeds"](seed_root)
    init_generator = surface["substream_generator"](seed_root, "init")
    minibatch_generator = None
    if lineage == "l2":
        minibatch_generator = torch.Generator(device="cpu")
        minibatch_generator.manual_seed(seeds_map["minibatch"])

    if lineage == "l2":
        # Raw arms carry estimator: null (no estimator; through-M arms only);
        # omit it and take the module default, which build_mechanism never
        # consumes on the raw path.  Enum values are lowercase (by-value).
        l2_extra = {}
        if arm["estimator"] is not None:
            l2_extra["estimator"] = surface["EstimatorKind"](arm["estimator"])
        config = surface["FactSurrogateTrainConfig"](
            n_iters=n_iters,
            coordinate=surface["Coordinate"](arm["coordinate"]),
            enforcement=surface["Enforcement"](arm["enforcement"]),
            kernel=surface["Kernel"](TRAINING_KERNEL),
            mechanism_backend=surface["MechanismBackend"].ENGINE_BRIDGE,
            **l2_extra,
        )
        model = surface["RecurrentFactSurrogate"](
            surface["FactSurrogateConfig"](), generator=init_generator
        ).to(device)
        config_json = surface["config_payload"](config)
        order_stream = None
    else:
        # L1 has no enforcement/estimator/kernel config fields (deliberate,
        # E-3/L1-3a/b); the arm yaml carries the cube identity, and the
        # mechanism (through-M arms) is built directly from the E-3 hooks.
        from ecomd.training.l1_supervised import L1SupervisedTrainConfig

        config = L1SupervisedTrainConfig(
            n_iters=n_iters,
            coordinate=surface["Coordinate"](arm["coordinate"]),
        )
        config_json = {
            **asdict(config),
            "coordinate": config.coordinate.value,
            "enforcement": arm["enforcement"],
            "estimator": arm["estimator"],
            "kernel": TRAINING_KERNEL,
            "mechanism_backend": "engine_bridge",
        }
        model = surface["L1CoordinateHeads"](
            surface["L1CoordinateHeadsConfig"](), generator=init_generator
        ).to(device)
        order_stream = surface["MinibatchOrderStream"].from_seed_root(seed_root)

    mechanism = None
    if through_m:
        mech_config = surface["FactSurrogateTrainConfig"](
            coordinate=surface["Coordinate"](arm["coordinate"]),
            enforcement=surface["Enforcement"].THROUGH_M,
            estimator=surface["EstimatorKind"](arm["estimator"]),
            kernel=surface["Kernel"](TRAINING_KERNEL),
            mechanism_backend=surface["MechanismBackend"].ENGINE_BRIDGE,
        )
        mechanism = surface["build_mechanism"](mech_config, seed_root=seed_root)

    scales = torch.tensor((1.0, 1.0), dtype=torch.float32, device=device)  # sealed s_ch = module default (C5)
    lr = float(lineage_cfg["train"]["lr"])
    grad_clip = float(lineage_cfg["train"]["grad_clip"])
    w_supervised = float(lineage_cfg["train"]["w_supervised"])

    batches = SeedBatches(Path(job["train_dir"]))
    if device.type != "cpu":
        for bucket in batches.buckets:
            for key in ("features", "channels", "slot_prices"):
                bucket[key] = bucket[key].to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    denominator = float(batches.total_rounds * N_CHANNELS)

    history: list[dict[str, Any]] = []
    started = time.time()
    last_progress_checkpoint = started
    for iteration in range(n_iters):
        optimizer.zero_grad()
        loss_sum = 0.0
        for bucket in batches.buckets:
            if lineage == "l2":
                order = torch.randperm(bucket["n_episodes"], generator=minibatch_generator)
            else:
                order = order_stream.next_order(bucket["n_episodes"])
            shuffled = batches.shuffled(bucket, order)

            if lineage == "l2":
                if through_m and coordinate_mode == "blind":
                    output = model(shuffled, mechanism=mechanism)
                    prediction = output.mechanism_channels
                else:
                    output = model(shuffled)  # mechanism=None also for L2 differentiated
                    if through_m:
                        prediction = mechanism_channel_prediction(
                            shuffled, output.flow, output.demand, mechanism,
                            coordinate_mode, increment_arm,
                        )
                    else:
                        prediction = raw_channel_prediction(output, shuffled, surface, config)
                deviation = ((prediction - shuffled.channels) / scales) ** 2
            else:
                output = model(shuffled)
                if through_m:
                    prediction = mechanism_channel_prediction(
                        shuffled, output.flow, output.demand, mechanism,
                        coordinate_mode, increment_arm,
                    )
                    deviation = ((prediction - shuffled.channels) / scales) ** 2
                else:
                    targets = surface["build_coordinate_targets"](
                        shuffled.channels, shuffled.channels_init
                    )
                    prediction = surface["coordinate_state_prediction"](
                        output, targets.base, config.coordinate
                    )
                    deviation = surface["smooth_dev"](
                        prediction / scales, targets.abs_targets.to(prediction) / scales,
                        mode=str(lineage_cfg["train"]["distance_mode"]),
                    )

            (w_supervised * deviation.sum() / denominator).backward()
            loss_sum += float(deviation.sum().item()) / denominator

        with torch.no_grad():
            grad_sq = torch.tensor(0.0, device=device)
            for parameter in model.parameters():
                if parameter.grad is not None:
                    grad_sq = grad_sq + parameter.grad.detach().pow(2).sum()
            grad_norm = float(grad_sq.sqrt().item())
        torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
        optimizer.step()

        history.append({
            "iter": iteration,
            "total": loss_sum,
            "channel_loss": loss_sum,
            "c5_endpoint": loss_sum ** 0.5 if loss_sum >= 0 else float("nan"),
            "grad_norm": grad_norm,
            "coordinate": arm["coordinate"],
            "enforcement": arm["enforcement"],
            "lineage": lineage,
        })
        if job.get("progress_dir") and time.time() - last_progress_checkpoint >= 1800:
            save_progress_snapshot(
                Path(job["progress_dir"]) / "latest.pt", model, optimizer,
                iteration + 1, config_json, seed_root,
            )
            last_progress_checkpoint = time.time()
    wall_seconds = time.time() - started

    # ---- lock checkpoint (L1-5 / L2-4 format, adopted verbatim)
    out_dir = Path(job["job_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = out_dir / "checkpoint.lock"
    train_manifest = batches.manifest
    binding = surface["LockCorpusBinding"](
        seed_root=seed_root,
        corpus_hash=train_manifest["train_corpus_hash"],
        prestate_hash=train_manifest["train_prestate_hash"],
        allocation_rule=TRAINING_KERNEL,
        n_draws=K_INFERENCE_DRAWS,
        tape_hash=None,
        manifest_hash=sha256_bytes(canonical_bytes(
            {k: train_manifest[k] for k in
             ("seed_root", "lineage", "axis", "kernel", "episode_start", "n_train",
              "train_corpus_hash", "train_prestate_hash")}
        )),
    )
    execution_metadata = {
        "runtime": RUNTIME_ID,
        "runtime_schema": RUNTIME_SCHEMA,
        "campaign_id": CAMPAIGN_ID,
        "block_id": job["block_id"],
        "arm_id": job["arm_id"],
        "lineage": lineage,
        "git_sha": job["git_sha"],
        "device": job.get("device", "cpu"),
        "n_train": job["n_train"],
        "episode_start": job["episode_start"],
        "n_iters": n_iters,
        "through_m_coordinate_mode": coordinate_mode,
        "mechanism_backend": "engine_bridge" if through_m else "none",
        "torch_version": torch.__version__,
        "wall_seconds": wall_seconds,
        "production_constants_decision": job["production_constants_decision"],
    }
    substream_generators = {"init": init_generator}
    if minibatch_generator is not None:
        # L1 consumes MinibatchOrderStream's private generator, which is not
        # exposable without touching frozen code; freezing the unconsumed
        # twin would misrepresent the C1 stream state (lock-contract finding).
        substream_generators["minibatch"] = minibatch_generator
    sidecar = surface["save_lock_checkpoint"](
        checkpoint_path,
        model=model,
        config=config_json,
        corpus=binding,
        substream_generators=substream_generators,
        execution_metadata=execution_metadata,
        iter_idx=n_iters,
        history=history,
        recurrent_hidden=None,
    )

    stream_hashes = sha256_bytes(canonical_bytes(
        {name: seeds_map[name] for name in ("data", "init", "minibatch", "train_kernel")}
    ))
    config_sha = sha256_bytes(canonical_bytes(config_json))
    cell_id = f"{arm['coordinate']}-{arm['enforcement']}-{arm['enforcement']}"
    record_key = (
        f"{job['block_id']}.training.train.{TRAINING_AXIS}.00."
        f"{cell_id}.{seed_root:05d}.00"
    )
    record = {
        "record_key": record_key,
        "record_class": "training",
        "run_id": f"{job['block_id']}.{job['arm_id']}.{seed_root}",
        "block_id": job["block_id"],
        "lineage": lineage,
        "dgp_variant": "lab-asset-v3",
        "seed": seed_root,
        "cell_id": cell_id,
        "axis": TRAINING_AXIS,
        "horizon": 0,
        "draw_index": 0,
        "condition": "train",
        "config_sha256": config_sha,
        "git_sha": job["git_sha"],
        "fixture_manifest_sha256": FREEZE_FILE_PINS["configs/reexploration/dgp/lab_asset.yaml"],
        "schema_version": "lab-asset-v3",
        "stream_hashes": stream_hashes,
        "checkpoint_lock_sha256": sidecar.checkpoint_sha256,
        "allocation_rule": TRAINING_KERNEL,
        "n_draws": K_INFERENCE_DRAWS,
        "metrics": {
            "first_total": history[0]["total"],
            "final_total": history[-1]["total"],
            "final_c5_endpoint": history[-1]["c5_endpoint"],
            "final_grad_norm": history[-1]["grad_norm"],
            "n_iters": n_iters,
            "n_train": job["n_train"],
            "total_rounds": batches.total_rounds,
            "finite_final": bool(
                history[-1]["total"] == history[-1]["total"]
                and history[-1]["c5_endpoint"] == history[-1]["c5_endpoint"]
            ),
            "wall_seconds": wall_seconds,
        },
        "train_manifest_sha256": sha256_file(Path(job["train_dir"]) / "train_episodes_manifest.json"),
    }
    record_path = out_dir / "training_record.json"
    atomic_write_bytes(record_path, canonical_bytes(record))

    # G4 hook (analyzer contract §4.4 pin): training_log.json with
    # checkpoint_sha256, the file+key train_distributed.py:1265-1273 writes.
    training_log = {
        "schema_version": RUNTIME_SCHEMA,
        "run_id": f"{job['block_id']}.{job['arm_id']}.{seed_root}",
        "record_class": "training",
        "record_key": record_key,
        "checkpoint_sha256": sidecar.checkpoint_sha256,
        "lock_chain_sha256": sidecar.lock_chain_sha256,
        "final_total": history[-1]["total"],
    }
    atomic_write_bytes(out_dir / "training_log.json", canonical_bytes(training_log))

    return {
        "arm_id": job["arm_id"],
        "seed_root": seed_root,
        "block_id": job["block_id"],
        "checkpoint": str(checkpoint_path),
        "checkpoint_sha256": sidecar.checkpoint_sha256,
        "lock_chain_sha256": sidecar.lock_chain_sha256,
        "record": str(record_path),
        "record_key": record_key,
        "final_total": history[-1]["total"],
        "final_c5_endpoint": history[-1]["c5_endpoint"],
        "finite_final": record["metrics"]["finite_final"],
        "wall_seconds": wall_seconds,
    }


# ------------------------------------------------------------------ probe mode

def run_probe(args: argparse.Namespace, repo_root: Path) -> int:
    """Reduced single-job timing probe (no checkpoint, no manifest entry)."""

    import torch

    surface = load_surface(repo_root)
    arm = load_arm(repo_root, "increment_through_m")
    seeds_map = surface["derive_substream_seeds"](args.seeds_start)
    init_generator = surface["substream_generator"](args.seeds_start, "init")
    minibatch_generator = torch.Generator(device="cpu")
    minibatch_generator.manual_seed(seeds_map["minibatch"])

    config = surface["FactSurrogateTrainConfig"](
        n_iters=8,
        coordinate=surface["Coordinate"].INCREMENT,
        enforcement=surface["Enforcement"].THROUGH_M,
        estimator=surface["EstimatorKind"].STRAIGHT_THROUGH,
        kernel=surface["Kernel"](TRAINING_KERNEL),
        mechanism_backend=surface["MechanismBackend"].ENGINE_BRIDGE,
    )
    model = surface["RecurrentFactSurrogate"](
        surface["FactSurrogateConfig"](), generator=init_generator
    )
    mechanism = surface["build_mechanism"](config, seed_root=args.seeds_start)

    dgp_cfg = load_dgp_config(repo_root)
    dgp = surface["dgp"]
    n_probe = args.probe_episodes
    episodes = []
    t0 = time.time()
    for index in range(DEFAULT_EPISODE_START, DEFAULT_EPISODE_START + n_probe):
        cfg = dgp.config_for_axis(dgp.config_from_mapping(dgp_cfg), TRAINING_AXIS)
        stream = dgp.generate_episode(args.seeds_start, index, cfg)
        draw_seed = dgp.derive_seed(args.seeds_start, "draw", index)
        prestate = dgp.build_prestate(
            stream, surface["AllocationRule"](TRAINING_KERNEL), draw_seed
        )
        engine = surface["ReferenceEngine"](prestate)
        for request in dgp.order_requests(stream):
            engine.submit(request)
        engine.finish()
        corpus = surface["project_fexec_corpus"](
            prestate, engine.tape, draw_seed, n_slots=8, dtype=torch.float32
        )
        episodes.append(corpus)
    gen_seconds = time.time() - t0

    # Ragged stream: T in ~7..22, so a flat torch.stack would raise.  Probe on
    # the largest uniform-T bucket (timing representative; production buckets
    # every T separately with the same total-rounds denominator).
    by_rounds: dict[int, list[Any]] = {}
    for corpus in episodes:
        by_rounds.setdefault(int(corpus.features.shape[0]), []).append(corpus)
    t_probe = max(by_rounds, key=lambda t: len(by_rounds[t]))
    uniform = by_rounds[t_probe]

    batch = surface["FactSurrogateBatch"](
        features=torch.stack([c.features for c in uniform]),
        channels=torch.stack([c.channels_cumulative.to(torch.float32) for c in uniform]),
        slot_prices=torch.stack([c.slot_prices.to(torch.int64) for c in uniform]),
        channels_init=None,
    )
    scales = torch.tensor((1.0, 1.0), dtype=torch.float32)
    optimizer = torch.optim.Adam(model.parameters(), lr=3e-4)
    timings = []
    for iteration in range(8):
        t0 = time.time()
        optimizer.zero_grad()
        order = torch.randperm(len(uniform), generator=minibatch_generator)
        shuffled = surface["FactSurrogateBatch"](
            features=batch.features[order],
            channels=batch.channels[order],
            slot_prices=batch.slot_prices[order],
            channels_init=None,
        )
        output = model(shuffled, mechanism=mechanism)
        loss = (((output.mechanism_channels - shuffled.channels) / scales) ** 2).mean()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        timings.append(time.time() - t0)

    Path(args.out_dir).mkdir(parents=True, exist_ok=True)
    per_episode_gen = gen_seconds / n_probe
    per_iter = sum(timings) / len(timings)
    report = {
        "schema_version": RUNTIME_SCHEMA,
        "probe": True,
        "lineage": args.lineage,
        "seed_root": args.seeds_start,
        "n_probe_episodes": n_probe,
        "probe_bucket_n_rounds": t_probe,
        "probe_bucket_episodes": len(uniform),
        "generation_seconds_per_episode": per_episode_gen,
        "through_m_iteration_seconds": per_iter,
        "uniform_probe_note": (
            "probe times the largest uniform-T bucket (ragged stream); "
            "production buckets every T with the same total-rounds denominator"
        ),
        "loss_first": float(loss.item()),
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    atomic_write_bytes(Path(args.out_dir) / "probe_report.json", canonical_bytes(report))
    return 0


# ------------------------------------------------------------------------ main

def parse_seed_range(text: str) -> range:
    start, stop = text.split(":")
    return range(int(start), int(stop))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--lineage", required=True, choices=["l1", "l2"])
    parser.add_argument("--seeds", required=True,
                        help="seed range START:STOP (exclusive), e.g. 11000:11030")
    parser.add_argument("--arms", default=",".join(ARM_IDS))
    parser.add_argument("--n-train", type=int, required=True,
                        help="training episodes per seed (F1 anchor: 2048 L1 / 4096 L2)")
    parser.add_argument("--n-iters", type=int, required=True,
                        help="production full-pass optimizer iterations")
    parser.add_argument("--episode-start", type=int, default=DEFAULT_EPISODE_START)
    parser.add_argument("--through-m-coordinate-mode", choices=["blind", "differentiated"],
                        default="blind")
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu",
                        help="training device (pi_d0s3_train_constants_20260921: cuda; "
                             "blind mode is cpu-only — the frozen forward routes the "
                             "mechanism without device marshalling)")
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--pip-freeze", type=Path, default=None)
    parser.add_argument("--production-constants-decision", default=None,
                        help="PI decision id pinning n_train/n_iters/episode window/mode")
    parser.add_argument("--probe", action="store_true")
    parser.add_argument("--probe-episodes", type=int, default=64)
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    enforce_freeze_pins(repo_root)

    if args.probe:
        args.seeds_start = parse_seed_range(args.seeds)[0]
        return run_probe(args, repo_root)

    if args.n_train < 1 or args.n_iters < 1:
        raise RuntimeError("n_train and n_iters must be >= 1")
    if args.episode_start < CORPUS_EPISODES_PER_SEED:
        raise RuntimeError(
            f"episode_start {args.episode_start} overlaps the D0-S2 corpus eval "
            f"window [0, {CORPUS_EPISODES_PER_SEED}) -- training/eval contamination"
        )
    if args.production_constants_decision is None:
        raise RuntimeError(
            "refusing to run production training without --production-constants-decision "
            "(the PI decision id pinning n_train / n_iters / episode window / "
            "through-M coordinate mode)"
        )
    if args.device != "cpu" and args.through_m_coordinate_mode == "blind":
        raise RuntimeError(
            "blind mode is cpu-only: the frozen forward calls the mechanism on "
            "device-resident slices without marshalling. Use differentiated "
            "(the ratified production mode) or --device cpu."
        )

    block_id = LINEAGE_BLOCK[args.lineage]
    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    for arm_id in arms:
        if arm_id not in ARM_IDS:
            raise RuntimeError(f"unknown arm {arm_id}")
    seeds = list(parse_seed_range(args.seeds))
    git_sha = git_head(repo_root) or "unknown"

    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[{RUNTIME_ID}] block {block_id} lineage {args.lineage} "
          f"seeds {seeds[0]}..{seeds[-1]} arms {arms} n_train {args.n_train} "
          f"n_iters {args.n_iters} mode {args.through_m_coordinate_mode}", flush=True)

    # stage 1: per-seed training episodes (shared across arms)
    for seed_root in seeds:
        job = {
            "job": {
                "repo_root": str(repo_root),
                "seed_root": seed_root,
                "lineage": args.lineage,
                "config": load_dgp_config(repo_root),
                "dir": str(train_data_dir(out_dir, seed_root)),
                "episode_start": args.episode_start,
                "n_train": args.n_train,
                "workers": args.workers,
            }
        }
        manifest = stage_seed_episodes(job)
        print(f"  episodes staged seed {seed_root}: {manifest['n_train']} episodes, "
              f"corpus_hash {manifest['train_corpus_hash'][:12]}", flush=True)

    # stage 2: trainings
    manifest_entries: list[dict[str, Any]] = []
    for arm_id in arms:
        arm = load_arm(repo_root, arm_id)
        for seed_root in seeds:
            job = {
                "repo_root": str(repo_root),
                "arm": arm,
                "arm_id": arm_id,
                "lineage": args.lineage,
                "block_id": block_id,
                "seed_root": seed_root,
                "n_train": args.n_train,
                "n_iters": args.n_iters,
                "episode_start": args.episode_start,
                "through_m_coordinate_mode": args.through_m_coordinate_mode,
                "device": args.device,
                "train_dir": str(train_data_dir(out_dir, seed_root)),
                "job_dir": str(out_dir / block_id / f"arm_{arm_id}" / f"seed_{seed_root:06d}"),
                "git_sha": git_sha,
                "production_constants_decision": args.production_constants_decision,
            }
            entry = train_one(job)
            manifest_entries.append(entry)
            print(f"  trained {arm_id} seed {seed_root}: final_total "
                  f"{entry['final_total']:.6g} c5 {entry['final_c5_endpoint']:.6g} "
                  f"({entry['wall_seconds']:.0f}s) finite={entry['finite_final']}",
                  flush=True)

    block_manifest = {
        "schema_version": RUNTIME_SCHEMA,
        "campaign_id": CAMPAIGN_ID,
        "block_id": block_id,
        "lineage": args.lineage,
        "dgp_variant": "lab-asset-v3",
        "training_axis": TRAINING_AXIS,
        "training_kernel": TRAINING_KERNEL,
        "seed_start": seeds[0],
        "seed_stop_inclusive": seeds[-1],
        "arms": arms,
        "production_constants": {
            "n_train": args.n_train,
            "n_iters": args.n_iters,
            "episode_start": args.episode_start,
            "through_m_coordinate_mode": args.through_m_coordinate_mode,
            "device": args.device,
            "lr": 3e-4,
            "grad_clip": 1.0,
            "channel_scales": [1.0, 1.0],
            "decision": args.production_constants_decision,
        },
        "freeze_commit": FREEZE_COMMIT,
        "freeze_sha256": "fd4a40b0306d415cef9a8a41b8e94e5afb21126e4e3d7ff99097e066f9981f57",
        "git_sha": git_sha,
        "corpus_window_reserved": list(range(0, CORPUS_EPISODES_PER_SEED)),
        "jobs": manifest_entries,
    }
    manifest_path = out_dir / block_id / "block_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_bytes(manifest_path, canonical_bytes(block_manifest))
    print(f"[{RUNTIME_ID}] block manifest: {manifest_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
