#!/usr/bin/env python3
"""D0-S4 evaluation-draw driver for B1 and the ratified recurrent B3 lineage.

Emits the RC1 mandatory-axes records (8 cells x 4 axes x 4 horizons x K=16
draws per seed), the RC2 truncation deployment passes (ID axis, conditions
trunc_lag W=20 / trunc_cap W=40, same 8 cells x 4 horizons x K=16 grid; PR
§3.4 secondary family), and the RC4 horizon-one probes of analyzer-contract
Part 4.9 for B1: 30 seeds x 2,048 + 30 x 1,024 + 30 x 4 = 61,440 + 30,720
+ 120 records.  NOT a frozen D0
file (freeze sha256 fd4a40b0...): this driver must CONFORM to the frozen
pins.  Remote execution only (PI compute rule 2026-09-06) -- never run on the
Mac beyond argument parsing.

The 8-cell grid per seed: four trained arms (coordinate c, training
enforcement t) from train_stage1/B1 checkpoints, each evaluated at inference
enforcement e in {raw, through_m}.  Cross-enforcement cells (t != e) are the
C11 zero-training surgery cells: the parent checkpoint's parameters are
loaded byte-identically (load_lock_checkpoint) and deployed under the other
enforcement map with zero optimizer steps, inheriting the seed-owned kernel
streams (build_inference_mechanism derives kernel:k from the seed root,
replayed identically across cells within the seed -- C2(b)).

Autoregressive rollout (contract C4 "autoregressive clearing rounds"):
within one episode the decode for round t consumes only strictly pre-round
information; the pre-round channel state fed forward is the MODEL'S OWN
rolled state, never the observed channels (raw: head decode; through-M: the
engine-executed increment cumulated).  L1 is stateless per round, so the
frozen forward is called verbatim on length-1 slices with channels_init
carrying the rolled pre-round state -- arithmetic identical to a prefix
call, O(T) instead of O(T^2).

Endpoint Y per record (contract C5 / Part 6.2):
Y = sqrt(mean_ch mean_t ((x_hat_ch,t - x_ch,t)/s_ch)^2) pooled over the
horizon window (see --horizon-mode) across the seed's 64 eval episodes.
s_ch comes from --scales-json (Annex B(e) hash-sealed DGP-only sample);
the (1.0, 1.0) training placeholder is REFUSED here.

G8 mechanics: draw k varies only (draw_index, record_key, run_id); the
evaluation payload (metrics + hashes + BBO + conservation counters) is
byte-identical across draws whenever the deployment kernel is deterministic
(fifo through-M cells, all raw cells).  Raw-inference cells' kswap records
are copies of their ID records with axis=kswap, a distinct run_id (G2
uniqueness), and allocation_rule pinned fifo (C4(iii)/G10); payload
byte-identity is what the analyzer checks.

RC4 probes (G6): replay the DISK prestate/tape of episode 0 of each axis's
fifo corpus stream through lab_asset.replay (the D0-S2 validate recipe):
re-execute the request stream and compare sequence, event types, payloads,
all four hashes record-by-record.  K-independent.

PI-GATED constants (no frozen authority pins these; each is recorded
verbatim in the eval manifest and needs a decision record before first
production execution): --horizon-mode, --scales-json, the record literals
(record_class/condition/axis strings), the pooled-record hash construction
(window_hash), probes' cell_id/draw_index conventions.

B3 requires pi_gamma_l2_units_revision_20260923 and its hash-bound unit
configuration. It retains recurrent history within each episode and resets
at episode boundaries. B3 includes trunc_lag only: 61,440 RC1 records,
15,360 RC2 records and 120 probes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import yaml

# ------------------------------------------------------------------ constants

CAMPAIGN_ID = "alpha_cube_d0_20260919"
RUNTIME_ID = "eval_draws_d0s4"
RUN_ID_DECISION = "pi_d0s4_run_id_horizon_20260923"
RUNTIME_SCHEMA = "ecomd-d0s4-eval-runtime-v1"

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

TRAINING_AXIS = "id"          # training stream axis (C4); kswap shares the id corpus
TRAINING_KERNEL = "fifo"      # C4(i): every trained arm embedded M with FIFO
N_CHANNELS = 2
K_INFERENCE_DRAWS = 16        # C2(b) amendment (11)
HORIZONS: tuple[int, ...] = (1, 4, 16, 31)
CORPUS_EPISODES_PER_SEED = 64
PROBE_EPISODE_INDEX = 0

# RC2 truncation passes (PI decision pi_d0s4_eval_constants_20260922):
# D_trunc^W removes initial resting orders with arrival_clock > W from the
# deployed book before replaying the recorded request stream (lemma writeup
# kt_g4_g5 §4).  cap = the frozen latency window (latency_window_ticks = 40;
# exactly the per-level first orders survive, every level straddles by
# construction); lag = the half-window rung (late firsts dropped too, levels
# can empty; 61/64 seed-11000 episodes discriminate the two conditions).
RC2_AXIS = "id"               # truncation passes run at the ID axis (PR §3.4)
RC2_W: dict[str, int] = {"trunc_lag": 20, "trunc_cap": 40}
DRAW_SEED_TAG = "draw"        # must equal generate_corpus_d0s2.py's tag

# E-5 AXIS_SPECS vocabulary (campaign.py) -- kswap reuses the id corpus with
# the through-M deployment kernel swapped (C4(ii)).
AXES: tuple[dict[str, Any], ...] = (
    {"axis_id": "id", "corpus_axis": "id", "deployment_kernel": "fifo"},
    {"axis_id": "pop_2x", "corpus_axis": "pop_2x", "deployment_kernel": "fifo"},
    {"axis_id": "tick_2x", "corpus_axis": "tick_2x", "deployment_kernel": "fifo"},
    {"axis_id": "kswap", "corpus_axis": "id", "deployment_kernel": "random_unit_within_price"},
)
AXES_BY_ID = {axis["axis_id"]: axis for axis in AXES}

ARM_IDS = (
    "absolute_raw",
    "increment_raw",
    "absolute_through_m",
    "increment_through_m",
)

# 8-cell grid: (trained arm, inference enforcement).  Cross cells are the
# C11 surgery deployments of the same locked checkpoint.
INFERENCE_ENFORCEMENTS = ("raw", "through_m")

_SURFACE: dict[str, Any] = {}


# ------------------------------------------------------------------- helpers

def canonical_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
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


def git_head(repo_root: Path) -> str | None:
    try:
        return subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:
        return None


def enforce_freeze_pins(repo_root: Path) -> None:
    for rel, pinned in FREEZE_FILE_PINS.items():
        actual = sha256_file(repo_root / rel)
        if actual != pinned:
            raise RuntimeError(f"freeze file pin violated for {rel}: {actual} != {pinned}")
    head = git_head(repo_root)
    if head is None:
        raise RuntimeError("cannot resolve git HEAD")
    result = subprocess.run(
        ["git", "-C", str(repo_root), "merge-base", "--is-ancestor", FREEZE_COMMIT, head],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git HEAD {head[:9]} does not descend from freeze commit {FREEZE_COMMIT[:9]}"
        )


def load_surface(repo_root: Path) -> dict[str, Any]:
    if _SURFACE:
        return _SURFACE
    sys.path.insert(0, str(repo_root / "scripts"))
    sys.path.insert(0, str(repo_root))

    from lab_asset import dgp_request_generator as dgp
    from lab_asset.conserving_emitter import (
        conservation_violations,
        emit_conserving_channels,
        settlement_violations,
    )
    from lab_asset.matching import ReferenceEngine
    from lab_asset.replay import replay
    from lab_asset.schema import AllocationRule, prestate_from_json, record_to_json
    from lab_asset.verify_fixtures import load_tape

    from ecomd.corpus.fexec_projector import project_fexec_corpus
    from ecomd.models.fact_surrogate import FactSurrogateBatch
    from ecomd.models.fact_surrogate import FactSurrogateConfig, RecurrentFactSurrogate
    from ecomd.models.unit_fact_surrogate import UnitRecurrentFactSurrogate
    from ecomd.models.l1_coordinate_heads import (
        L1CoordinateHeads,
        L1CoordinateHeadsConfig,
    )
    from ecomd.reexploration.campaign import BLOCKS_BY_ID
    from ecomd.training.lock_checkpoint import load_lock_checkpoint, lock_sidecar_path
    from ecomd.training.train_fact_surrogate import (
        Enforcement,
        build_inference_mechanism,
        derive_substream_seeds,
    )

    _SURFACE.update(
        repo_root=repo_root,
        dgp=dgp,
        replay=replay,
        load_tape=load_tape,
        prestate_from_json=prestate_from_json,
        AllocationRule=AllocationRule,
        conservation_violations=conservation_violations,
        emit_conserving_channels=emit_conserving_channels,
        settlement_violations=settlement_violations,
        ReferenceEngine=ReferenceEngine,
        record_to_json=record_to_json,
        project_fexec_corpus=project_fexec_corpus,
        FactSurrogateBatch=FactSurrogateBatch,
        FactSurrogateConfig=FactSurrogateConfig,
        RecurrentFactSurrogate=RecurrentFactSurrogate,
        UnitRecurrentFactSurrogate=UnitRecurrentFactSurrogate,
        L1CoordinateHeads=L1CoordinateHeads,
        L1CoordinateHeadsConfig=L1CoordinateHeadsConfig,
        BLOCKS_BY_ID=BLOCKS_BY_ID,
        load_lock_checkpoint=load_lock_checkpoint,
        lock_sidecar_path=lock_sidecar_path,
        Enforcement=Enforcement,
        build_inference_mechanism=build_inference_mechanism,
        derive_substream_seeds=derive_substream_seeds,
    )
    return _SURFACE


def stream_hashes_for(surface: dict[str, Any], seed_root: int) -> str:
    """Envelope stream_hashes: the four pinned names, training's recipe.

    §5.2 names data/init/minibatch/train_kernel and train_stage1_d0s3 hashes
    exactly that 4-name sub-dict; eval records use the identical preimage so
    G2's per-seed pairing holds across record classes.
    """

    seeds_map = surface["derive_substream_seeds"](seed_root)
    pinned = {name: seeds_map[name] for name in ("data", "init", "minibatch", "train_kernel")}
    return sha256_bytes(canonical_bytes(pinned))


def load_arm(repo_root: Path, arm_id: str) -> dict[str, Any]:
    path = repo_root / "configs" / "reexploration" / "arm" / f"{arm_id}.yaml"
    arm = yaml.safe_load(path.read_text())
    for field in ("coordinate", "enforcement", "estimator", "training_kernel"):
        if field not in arm:
            raise RuntimeError(f"arm config {path.name} missing field {field}")
    return arm


def load_scales(path: Path) -> tuple[Any, dict[str, Any]]:
    import torch

    payload = json.loads(path.read_text())
    if "s_ch" not in payload or "provenance" not in payload:
        raise RuntimeError("scales file must carry s_ch (list of 2) and provenance")
    scales = torch.tensor(payload["s_ch"], dtype=torch.float32)
    if tuple(scales.shape) != (N_CHANNELS,) or bool((scales <= 0).any()):
        raise RuntimeError(f"invalid s_ch {payload['s_ch']}")
    if scales.tolist() == [1.0, 1.0]:
        raise RuntimeError(
            "s_ch [1.0, 1.0] is the training placeholder (train_stage1 channel_scales), "
            "not the Annex B(e) sealed DGP-only sample"
        )
    return scales, payload


# ------------------------------------------------------------ corpus ingestion

def corpus_stream_dir(corpus_root: Path, axis: str, seed_root: int) -> Path:
    # D0-S2 layout: lab_asset/axis_*/kernel_*/seed_*/; l1 and l2 share the
    # tree (seed namespaces 11000+/12000+ separate them).
    return corpus_root / "lab_asset" / f"axis_{axis}" / f"kernel_{TRAINING_KERNEL}" / f"seed_{seed_root:06d}"


def load_eval_episodes(corpus_root: Path, axis: str, seed_root: int) -> tuple[list[dict[str, Any]], str]:
    """The seed's 64 eval episodes of one corpus axis (fifo truth side, C4).

    Returns (episodes, fixture_manifest_sha256) where the fixture binding is
    the sha256 of the corpus stream manifest (G3).
    """

    import torch

    sdir = corpus_stream_dir(corpus_root, axis, seed_root)
    stream_manifest_path = sdir / "stream_manifest.json"
    manifest = json.loads(stream_manifest_path.read_text())
    episodes: list[dict[str, Any]] = []
    for entry in sorted(manifest["episodes"], key=lambda e: e["episode_index"]):
        edir = sdir / f"episode_{entry['episode_index']:04d}"
        fexec = json.loads((edir / "fexec_corpus.json").read_text())
        features = torch.tensor(fexec["features"], dtype=torch.float32)
        channels = torch.tensor(fexec["channels_cumulative"], dtype=torch.float32)
        slot_prices = torch.tensor(fexec["slot_prices"], dtype=torch.int64)
        if features.ndim != 2 or channels.shape != (features.shape[0], N_CHANNELS):
            raise RuntimeError(
                f"{edir}: fexec shapes features{tuple(features.shape)} "
                f"channels{tuple(channels.shape)} violate C5"
            )
        if slot_prices.shape != (features.shape[0], int(fexec["n_slots"])):
            raise RuntimeError(f"{edir}: slot_prices shape {tuple(slot_prices.shape)}")
        episodes.append({
            "episode_index": entry["episode_index"],
            "n_rounds": entry["n_rounds"],
            "corpus_hash": entry["corpus_hash"],
            "canonical_sha": entry["episode_canonical_json_sha256"],
            "config_fingerprint": entry["config_fingerprint"],
            "dir": edir,
            "features": features,
            "channels_cumulative": channels,
            "slot_prices": slot_prices,
            "boundaries": episode_boundaries(tape_records(edir / "tape.jsonl")),
        })
    if len(episodes) != CORPUS_EPISODES_PER_SEED:
        raise RuntimeError(
            f"seed {seed_root} axis {axis}: {len(episodes)} episodes != {CORPUS_EPISODES_PER_SEED}"
        )
    return episodes, sha256_file(stream_manifest_path)


def tape_records(tape_path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in tape_path.read_text().splitlines()]


def episode_boundaries(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Envelope boundary facts of one session tape (parsed records).

    The four state hashes are top-level on the first/last records
    (session_start/session_end).  Best quotes live inside the payloads of
    quote-carrying events (order_accepted/execution): the session's pre BBO
    is the first event's pre_best_*, the post BBO the last event's post_best_*.
    """

    first, last = records[0], records[-1]
    pre_quote = next(
        r["payload"] for r in records if "pre_best_bid" in r["payload"]
    )
    post_quote = next(
        r["payload"] for r in reversed(records) if "post_best_bid" in r["payload"]
    )
    return {
        "pre_state_hash": first["pre_state_hash"],
        "post_state_hash": last["post_state_hash"],
        "pre_aggregate_state_hash": first["pre_aggregate_state_hash"],
        "post_aggregate_state_hash": last["post_aggregate_state_hash"],
        "pre_best_bid": pre_quote["pre_best_bid"],
        "pre_best_ask": pre_quote["pre_best_ask"],
        "post_best_bid": post_quote["post_best_bid"],
        "post_best_ask": post_quote["post_best_ask"],
    }


# ------------------------------------------------------------- horizon windows

def horizon_window(episodes: list[dict[str, Any]], horizon: int, mode: str) -> list[tuple[int, int]]:
    """(episode_index, rounds_to_take) pairs covering the horizon's rounds.

    chained     -- episodes in index order, each contributing all its execution
                   rounds, until the window fills (the filling episode
                   contributes the remainder).  Every horizon in {1,4,16,31}
                   and the descriptive h=64 are materializable (64 episodes x
                   ragged T in ~[6,24]).
    within_cap  -- every episode contributes min(horizon, T_e) rounds; the
                   pooled record counts fewer rounds when episodes are short.
    """

    if mode not in ("chained", "within_cap"):
        raise RuntimeError(f"unknown horizon mode {mode!r}")
    window: list[tuple[int, int]] = []
    if mode == "within_cap":
        for episode in episodes:
            window.append((episode["episode_index"], min(horizon, episode["n_rounds"])))
        return window
    remaining = horizon
    for episode in episodes:
        if remaining <= 0:
            break
        take = min(remaining, episode["n_rounds"])
        window.append((episode["episode_index"], take))
        remaining -= take
    if remaining > 0:
        raise RuntimeError(
            f"seed corpus exhausted before horizon {horizon}: short by {remaining} rounds"
        )
    return window


def window_hash(episodes: list[dict[str, Any]], window: list[tuple[int, int]]) -> dict[str, str]:
    """The four envelope hashes for a pooled record.

    The record pools episodes, so each hash binds the pooled set: sha256 of
    the canonical JSON list of per-episode dicts carrying the boundary facts
    PLUS (episode_index, rounds taken) -- the coverage pair distinguishes
    horizons that would otherwise hash identically (chained h=1/4/16 over one
    episode).
    """

    by_index = {episode["episode_index"]: episode for episode in episodes}
    payload = [
        {"episode_index": i, "rounds": r, **by_index[i]["boundaries"]}
        for i, r in window
    ]
    digest = sha256_bytes(canonical_bytes(payload))
    return {name: digest for name in (
        "pre_state_hash", "post_state_hash",
        "pre_aggregate_state_hash", "post_aggregate_state_hash",
    )}


# ------------------------------------------------------- RC2 truncation passes

def trunc_session_episodes(
    surface: dict[str, Any],
    repo_root: Path,
    seed_root: int,
    id_episodes: list[dict[str, Any]],
    window: int,
) -> list[dict[str, Any]]:
    """D_trunc^W sessions of one seed at the ID axis (RC2 truth side).

    Per episode: re-derive the stream from the seed with the frozen generator
    and PASS the episode_canonical_json_sha256 guard against the corpus
    manifest (clocks live only in the raw flow -- corpus prestates do not
    serialize them), drop initial resting orders with arrival_clock > W, then
    re-execute the recorded request stream from the truncated prestate (the
    replay contract's native operation, prestate side).  Features AND truth
    come from the truncated session itself, mirroring the pop_2x axis
    treatment.  E-4 conservation/settlement gates re-run on every truncated
    tape.  The request stream and round structure are clock-independent by
    construction (all arrival clocks <= initial_clock_max 80 <
    request_tick_start 100).
    """

    import dataclasses

    dgp = surface["dgp"]
    mapping = yaml.safe_load(
        (repo_root / "configs" / "reexploration" / "dgp" / "lab_asset.yaml").read_text()
    )["config"]
    cfg = dgp.config_for_axis(dgp.config_from_mapping(mapping), RC2_AXIS)
    episodes: list[dict[str, Any]] = []
    for episode in id_episodes:
        index = episode["episode_index"]
        stream = dgp.generate_episode(seed_root, index, cfg)
        if dgp.config_fingerprint(cfg) != episode["config_fingerprint"]:
            raise RuntimeError(
                f"RC2 re-derivation config mismatch seed={seed_root} ep={index}"
            )
        if sha256_bytes(dgp.episode_canonical_json(stream)) != episode["canonical_sha"]:
            raise RuntimeError(
                f"RC2 canonical-json guard failed seed={seed_root} ep={index}: "
                "re-derived episode does not match the corpus manifest"
            )
        kept = tuple(o for o in stream.initial_book if o.arrival_clock <= window)
        trunc = dataclasses.replace(stream, initial_book=kept)
        draw_seed = dgp.derive_seed(seed_root, DRAW_SEED_TAG, index)
        prestate = dgp.build_prestate(
            trunc, surface["AllocationRule"](TRAINING_KERNEL), draw_seed
        )
        engine = surface["ReferenceEngine"](prestate)
        for request in dgp.order_requests(stream):
            engine.submit(request)
        engine.finish()
        tape = engine.tape
        series = surface["emit_conserving_channels"](prestate, tape)
        violations = surface["conservation_violations"](series) + \
            surface["settlement_violations"](prestate, tape, series)
        if violations:
            raise RuntimeError(
                f"RC2 truncated-session gate failed seed={seed_root} ep={index} "
                f"W={window}: {violations}"
            )
        corpus = surface["project_fexec_corpus"](prestate, tape, seed_root)
        records = [json.loads(surface["record_to_json"](r)) for r in tape]
        episodes.append({
            "episode_index": index,
            "n_rounds": int(corpus.features.shape[0]),
            "corpus_hash": episode["corpus_hash"],
            "canonical_sha": episode["canonical_sha"],
            "config_fingerprint": episode["config_fingerprint"],
            "dir": episode["dir"],
            "features": corpus.features.float(),
            "channels_cumulative": corpus.channels_cumulative.float(),
            "slot_prices": corpus.slot_prices,
            "boundaries": episode_boundaries(records),
        })
    return episodes


def load_arm_surface(
    surface: dict[str, Any], block_dir: Path, arm_id: str, seed_root: int
) -> tuple[Any, str]:
    """(model, checkpoint_lock_sha256) of one trained arm checkpoint."""

    checkpoint_path = block_dir / f"arm_{arm_id}" / f"seed_{seed_root:06d}" / "checkpoint.lock"
    if not checkpoint_path.exists():
        raise RuntimeError(f"missing trained checkpoint {checkpoint_path}")
    sidecar_path = surface["lock_sidecar_path"](checkpoint_path)
    sidecar = json.loads(sidecar_path.read_text())
    if block_dir.name == "B3":
        import torch
        from train_b3_units import DECISION, REVISION, require_decision

        locked = surface["load_lock_checkpoint"](checkpoint_path)
        unit_config = locked.payload["sim_config"].get("l2_units")
        metadata = locked.payload["execution_metadata"]
        if (not unit_config or unit_config["revision"] != REVISION
                or unit_config["decision"] != DECISION or unit_config["seed"] != seed_root
                or unit_config["decision_sha256"] != require_decision(surface["repo_root"])
                or unit_config["n_train"] != 4096 or unit_config["episode_start"] != 64
                or metadata["production_constants_decision"] != DECISION
                or metadata["block_id"] != "B3" or metadata["arm_id"] != arm_id
                or metadata["n_iters"] != 100 or metadata["device"] != "cuda"
                or locked.sidecar.binding["seed_root"] != seed_root):
            raise RuntimeError("B3 requires an accepted revised L2 production checkpoint")
        model = surface["UnitRecurrentFactSurrogate"](
            surface["FactSurrogateConfig"](),
            {key: torch.tensor(value, dtype=torch.float32) for key, value in unit_config["values"].items()},
            generator=torch.Generator().manual_seed(0),
        )
    else:
        model = surface["L1CoordinateHeads"](surface["L1CoordinateHeadsConfig"]())
    expected_buffers = {key: value.clone() for key, value in model.named_buffers()}
    surface["load_lock_checkpoint"](checkpoint_path, model=model)
    if block_dir.name == "B3" and any(
            not torch.equal(value, dict(model.named_buffers())[key]) for key, value in expected_buffers.items()):
        raise RuntimeError("B3 unit buffers differ from the locked unit configuration")
    model.eval()
    return model, sidecar["checkpoint_sha256"]


# ------------------------------------------------------------------- rollouts

def rollout_episode(
    surface: dict[str, Any],
    model: Any,
    mechanism: Any | None,
    episode: dict[str, Any],
    rounds: int,
    *,
    inference_enforcement: str,
    coordinate: str,
) -> dict[str, Any]:
    """Autoregressive rollout of the first ``rounds`` rounds of one episode.

    L1 is stateless per round: the frozen forward is called on a length-1
    slice whose channels_init carries the model's rolled pre-round state
    (the decode consumes only (features_t, x_t); arithmetic identical to a
    teacher-forced prefix call at that index).
    """

    import torch

    batch_cls = surface["FactSurrogateBatch"]
    features = episode["features"]          # (T, d)
    truth = episode["channels_cumulative"]  # (T, C)
    slot_prices = episode["slot_prices"]    # (T, S)
    n_rounds = int(features.shape[0])
    if rounds > n_rounds:
        raise RuntimeError(f"rounds {rounds} > episode rounds {n_rounds}")

    prediction = torch.zeros(rounds, N_CHANNELS, dtype=torch.float32)
    state = torch.zeros(1, N_CHANNELS, dtype=torch.float32)   # zero base (E-1/E-4)
    volume_violations = 0
    cash_violations = 0
    with torch.no_grad():
        recurrent = isinstance(model, surface.get("RecurrentFactSurrogate", ()))
        if recurrent:
            recurrent_output = model(batch_cls(
                features=features[:rounds].unsqueeze(0),
                channels=torch.zeros(1, rounds, N_CHANNELS),
                slot_prices=slot_prices[:rounds].unsqueeze(0),
                channels_init=state,
            ))
        for step in range(rounds):
            batch = batch_cls(
                features=features[step: step + 1].unsqueeze(0),
                channels=torch.zeros(1, 1, N_CHANNELS),
                slot_prices=slot_prices[step: step + 1].unsqueeze(0),
                channels_init=state,
            )
            output = recurrent_output if recurrent else model(batch)
            output_step = step if recurrent else 0
            if inference_enforcement == "through_m":
                allocation = mechanism(
                    output.flow[0, output_step].to("cpu"),
                    int(output.demand[0, output_step].detach().item()),
                )
                increment = torch.stack((
                    allocation.sum(),
                    (allocation * slot_prices[step].to(allocation.dtype)).sum(),
                ))
                if float(allocation.sum().item()) != round(float(allocation.sum().item())):
                    volume_violations += 1
                cash = float(increment[1].item())
                if cash != round(cash):
                    cash_violations += 1
                state = state + increment.unsqueeze(0)
            elif coordinate == "absolute":
                state = output.abs_channels[0, output_step].unsqueeze(0)
            else:
                state = state + output.inc_channels[0, output_step].unsqueeze(0)
            prediction[step] = state[0]
    return {
        "prediction": prediction,
        "truth": truth[:rounds],
        "volume_violations": volume_violations,
        "cash_violations": cash_violations,
    }


def evaluate_cell(
    surface: dict[str, Any],
    model: Any,
    mechanism: Any | None,
    episodes: list[dict[str, Any]],
    window: list[tuple[int, int]],
    *,
    inference_enforcement: str,
    coordinate: str,
) -> dict[str, Any]:
    """One (cell, axis, horizon, draw) evaluation pooled over the window."""

    import torch

    by_index = {episode["episode_index"]: episode for episode in episodes}
    errors: list[Any] = []
    volume_violations = 0
    cash_violations = 0
    boundaries: dict[str, Any] = {}
    covered = 0
    for episode_index, rounds in window:
        episode = by_index[episode_index]
        result = rollout_episode(
            surface, model, mechanism, episode, rounds,
            inference_enforcement=inference_enforcement,
            coordinate=coordinate,
        )
        errors.append(result["prediction"] - result["truth"])
        volume_violations += result["volume_violations"]
        cash_violations += result["cash_violations"]
        boundaries = episode["boundaries"]
        covered += rounds
    if covered == 0:
        raise RuntimeError("empty horizon window")
    return {
        "n_window_rounds": covered,
        "error": torch.cat(errors, dim=0),
        "volume_violations": volume_violations,
        "cash_violations": cash_violations,
        "boundaries": boundaries,
    }


def endpoint_y(error: Any, scales: Any) -> float:
    import torch

    scaled = error / scales
    return float(torch.sqrt((scaled ** 2).mean()).item())


# -------------------------------------------------------------------- records

def record_key(block_id: str, record_class: str, condition: str, axis: str,
               horizon: int, cell_id: str, seed_root: int, draw_index: int) -> str:
    return (
        f"{block_id}.{record_class}.{condition}.{axis}.{horizon:02d}."
        f"{cell_id}.{seed_root:05d}.{draw_index:02d}"
    )


def make_record(**fields: Any) -> dict[str, Any]:
    if fields["record_class"] in ("RC1", "RC2"):
        fields["run_id"] += f".h{fields['horizon']:02d}"
    if fields.get("block_id") == "B3":
        fields["protocol_amendment"] = "pi_gamma_l2_units_revision_20260923"
    return dict(fields)


def validate_existing_record_ids(out_records: Path) -> None:
    """Check resume metadata before any production record is written."""
    run_ids: set[str] = set()
    for path in sorted(out_records.glob("*.json")):
        record = json.loads(path.read_text())
        key = record_key(
            record["block_id"], record["record_class"], record["condition"],
            record["axis"], record["horizon"], record["cell_id"],
            record["seed"], record["draw_index"],
        )
        if record["record_key"] != key or path.stem != key:
            raise RuntimeError(f"record-key binding mismatch: {path.name}")
        run_id = record["run_id"]
        if record["record_class"] in ("RC1", "RC2"):
            suffix = f".h{record['horizon']:02d}"
            if record["axis"] == "kswap" and record["cell_id"].endswith("-raw"):
                suffix += ".kswap"
            if not run_id.endswith(suffix):
                raise RuntimeError(f"run-ID horizon binding mismatch: {path.name}")
        if run_id in run_ids:
            raise RuntimeError(f"duplicate run_id: {run_id}")
        run_ids.add(run_id)


def require_run_id_decision(repo_root: Path, decision_id: str, block_id: str = "B1") -> str:
    """Return the hash of the ratified production metadata decision."""
    expected = {"B1": RUN_ID_DECISION, "B3": "pi_gamma_l2_units_revision_20260923"}
    if block_id not in expected or decision_id != expected[block_id]:
        raise RuntimeError(f"production requires {expected.get(block_id, 'a supported block')}")
    path = repo_root / "research" / "discovery" / "decisions" / f"{decision_id}.yaml"
    decision = yaml.safe_load(path.read_text())
    if (decision.get("decision_id") != decision_id
            or decision.get("status") != "ratified"
            or decision.get("authorized_by") != "PI"):
        raise RuntimeError(f"production decision is not PI-ratified: {decision_id}")
    return sha256_file(path)


def write_record(out_records: Path, record: dict[str, Any]) -> str:
    path = out_records / f"{record['record_key']}.json"
    atomic_write_bytes(path, canonical_bytes(record))
    return record["record_key"]


# ------------------------------------------------------------------ RC4 probe

def run_probe(surface: dict[str, Any], episode_dir: Path) -> dict[str, Any]:
    """G6 horizon-one clearing-identity probe on one axis.

    Replays the DISK prestate/tape of the axis's episode 0 through
    lab_asset.replay -- the same recipe as the D0-S2 validate step (v):
    re-execute the request stream record-by-record and compare sequence,
    event types, payloads, all four hashes.  K-independent.
    """

    prestate = surface["prestate_from_json"]((episode_dir / "prestate.json").read_text())
    tape = surface["load_tape"](episode_dir / "tape.jsonl")
    report = surface["replay"](prestate, tape)
    return {
        "replay_ok": bool(report.ok),
        "events_replayed": int(report.events_replayed),
        "mismatch": (
            None if report.first_mismatch_sequence is None
            else int(report.first_mismatch_sequence)
        ),
    }


# ----------------------------------------------------------------------- main

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--train-dir", required=True, type=Path,
                        help="train_stage1 dir containing B1/arm_*/seed_* checkpoints")
    parser.add_argument("--corpus-root", required=True, type=Path,
                        help="D0-S2 corpus root containing lab_asset/axis_*/kernel_*/seed_*")
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--seeds", required=True, help="seed range START:STOP (exclusive)")
    parser.add_argument("--arms", default=",".join(ARM_IDS))
    parser.add_argument("--axes", default="id,pop_2x,tick_2x,kswap")
    parser.add_argument("--horizons", default=",".join(str(h) for h in HORIZONS))
    parser.add_argument("--rc2-conditions", default=None,
                        help="RC2 truncation conditions to emit ('none' disables; "
                             "subset of trunc_lag,trunc_cap)")
    parser.add_argument("--horizon-mode", default="chained", choices=["chained", "within_cap"])
    parser.add_argument("--scales-json", required=True, type=Path,
                        help="s_ch materialization (Annex B(e)) with provenance")
    parser.add_argument("--production-decision", required=True,
                        help="PI decision id authorizing the PI-gated constants")
    parser.add_argument("--max-records", type=int, default=0,
                        help="smoke cap: stop after N written records (0 = unlimited)")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--block-id", default="B1")
    args = parser.parse_args(argv)

    import torch

    torch.set_num_threads(1)
    if torch.device(args.device).type != "cpu":
        raise RuntimeError(
            "eval records are generated on CPU only (deterministic kernels for "
            "G8/G9 byte-identity)"
        )

    repo_root = args.repo_root.resolve()
    production_decision_sha256 = require_run_id_decision(repo_root, args.production_decision, args.block_id)
    enforce_freeze_pins(repo_root)
    surface = load_surface(repo_root)
    scales, scales_payload = load_scales(args.scales_json)

    parts = args.seeds.split(":")
    if len(parts) != 2 or not all(p.strip() for p in parts):
        parser.error("--seeds must be exactly START:STOP (two integers, stop exclusive)")
    seed_start, seed_stop = int(parts[0]), int(parts[1])
    seeds = range(seed_start, seed_stop)
    if not seeds:
        parser.error(f"--seeds {args.seeds!r} is an empty range")
    if args.block_id not in surface["BLOCKS_BY_ID"]:
        raise RuntimeError(f"unknown block id {args.block_id!r} (campaign.BLOCKS_BY_ID)")
    lineage = "l2" if args.block_id == "B3" else "l1"
    if args.rc2_conditions is None:
        args.rc2_conditions = "trunc_lag" if args.block_id == "B3" else ",".join(RC2_W)
    block_seeds = set(surface["BLOCKS_BY_ID"][args.block_id].seeds)
    outside = [s for s in seeds if s not in block_seeds]
    if outside:
        raise RuntimeError(
            f"seeds {outside[:3]} outside block {args.block_id} namespace "
            f"({min(block_seeds)}..{max(block_seeds)})"
        )
    arm_ids = [a.strip() for a in args.arms.split(",") if a.strip()]
    axis_ids = [a.strip() for a in args.axes.split(",") if a.strip()]
    horizons = [int(h) for h in args.horizons.split(",") if h.strip()]
    rc2_conditions = (
        [] if args.rc2_conditions.strip().lower() in ("", "none")
        else [c.strip() for c in args.rc2_conditions.split(",") if c.strip()]
    )
    unknown = [c for c in rc2_conditions if c not in RC2_W]
    if unknown:
        parser.error(f"unknown RC2 conditions {unknown} (choose from {sorted(RC2_W)})")
    if args.block_id == "B3" and any(condition != "trunc_lag" for condition in rc2_conditions):
        parser.error("B3 includes only the frozen trunc_lag condition")
    if rc2_conditions and RC2_AXIS not in axis_ids:
        parser.error(f"RC2 requires the {RC2_AXIS!r} axis in --axes (truncation passes "
                     "re-derive the ID corpus)")
    arms = {arm_id: load_arm(repo_root, arm_id) for arm_id in arm_ids}
    for arm_id, arm in arms.items():
        if arm["training_kernel"] != TRAINING_KERNEL:
            raise RuntimeError(f"arm {arm_id} training_kernel violates C4(i)")
    for axis_id in axis_ids:
        if axis_id not in AXES_BY_ID:
            raise RuntimeError(f"unknown axis {axis_id!r}")

    git_sha = git_head(repo_root)
    if git_sha is None:
        raise RuntimeError("cannot resolve git HEAD")

    block_dir = args.train_dir / args.block_id
    out_records = args.out_dir / "records"
    validate_existing_record_ids(out_records)
    out_records.mkdir(parents=True, exist_ok=True)

    started = time.time()
    written_rc1 = 0
    written_rc2 = 0
    written_rc4 = 0
    dup_written_total = 0
    skipped_existing = 0
    stopped_early = False

    for seed_root in seeds:
        seed_started = time.time()
        if stopped_early:
            break

        # C2(b) mechanism cadence: build_inference_mechanism is constructed
        # FRESH per (cell, axis, horizon, draw) record at the use site below,
        # so every record consumes the kernel:k substream from position 0 in
        # record order -- draw k replays identically across cells, axes,
        # horizons and resume boundaries (a shared advancing stream would make
        # the realized randomness depend on evaluation order and skip history).

        # corpus episodes per corpus-axis (kswap shares the id tree)
        episodes_by_corpus_axis: dict[str, tuple[list[dict[str, Any]], str]] = {}
        for axis_id in axis_ids:
            corpus_axis = AXES_BY_ID[axis_id]["corpus_axis"]
            if corpus_axis not in episodes_by_corpus_axis:
                episodes_by_corpus_axis[corpus_axis] = load_eval_episodes(
                    args.corpus_root, corpus_axis, seed_root
                )

        # RC4 probes first (cheap; abort the seed if the instrument fails)
        for axis_id in axis_ids:
            axis = AXES_BY_ID[axis_id]
            episodes, fixture_sha = episodes_by_corpus_axis[axis["corpus_axis"]]
            probe = run_probe(surface, episodes[PROBE_EPISODE_INDEX]["dir"])
            if not probe["replay_ok"]:
                raise RuntimeError(
                    f"G6 probe failed axis={axis_id} seed={seed_root}: {probe['mismatch']}"
                )
            episodes, fixture_sha = episodes_by_corpus_axis[axis["corpus_axis"]]
            record = make_record(
                record_key=record_key(
                    args.block_id, "RC4", "id", axis_id, 1, "engine-replay-probe",
                    seed_root, 0,
                ),
                record_class="RC4",
                run_id=f"{args.block_id}.probe.{axis_id}.{seed_root}",
                block_id=args.block_id,
                lineage=lineage,
                dgp_variant="lab-asset-v3",
                seed=seed_root,
                cell_id="engine-replay-probe",
                axis=axis_id,
                horizon=1,
                draw_index=0,
                condition="id",
                config_sha256=sha256_bytes(canonical_bytes({
                    "runtime": RUNTIME_ID, "probe": True,
                    "episode_index": PROBE_EPISODE_INDEX,
                })),
                git_sha=git_sha,
                fixture_manifest_sha256=fixture_sha,
                schema_version="lab-asset-v3",
                stream_hashes=stream_hashes_for(surface, seed_root),
                checkpoint_lock_sha256=None,
                allocation_rule=TRAINING_KERNEL,
                n_draws=K_INFERENCE_DRAWS,
                metrics={
                    "replay_ok": probe["replay_ok"],
                    "events_replayed": probe["events_replayed"],
                    "probe_episode_index": PROBE_EPISODE_INDEX,
                    "finite": True,
                },
                pre_best_bid=episodes[PROBE_EPISODE_INDEX]["boundaries"]["pre_best_bid"],
                pre_best_ask=episodes[PROBE_EPISODE_INDEX]["boundaries"]["pre_best_ask"],
                post_best_bid=episodes[PROBE_EPISODE_INDEX]["boundaries"]["post_best_bid"],
                post_best_ask=episodes[PROBE_EPISODE_INDEX]["boundaries"]["post_best_ask"],
                conservation_violation_steps={"volume": 0, "cash": 0},
                pre_state_hash=episodes[PROBE_EPISODE_INDEX]["boundaries"]["pre_state_hash"],
                post_state_hash=episodes[PROBE_EPISODE_INDEX]["boundaries"]["post_state_hash"],
                pre_aggregate_state_hash=episodes[PROBE_EPISODE_INDEX]["boundaries"]["pre_aggregate_state_hash"],
                post_aggregate_state_hash=episodes[PROBE_EPISODE_INDEX]["boundaries"]["post_aggregate_state_hash"],
            )
            probe_path = out_records / f"{record['record_key']}.json"
            if probe_path.exists():
                skipped_existing += 1
            else:
                write_record(out_records, record)
                written_rc4 += 1

        # RC1 grid: 4 arms x 2 inference enforcements x axes x horizons x K
        for arm_id in arm_ids:
            arm = arms[arm_id]
            model, checkpoint_lock_sha256 = load_arm_surface(
                surface, block_dir, arm_id, seed_root
            )

            for inference_enforcement in INFERENCE_ENFORCEMENTS:
                cell_id = f"{arm['coordinate']}-{arm['enforcement']}-{inference_enforcement}"
                for axis_id in axis_ids:
                    axis = AXES_BY_ID[axis_id]
                    if inference_enforcement == "raw" and axis_id == "kswap":
                        continue  # C4(iii) duplicates emitted after the grid
                    episodes, fixture_sha = episodes_by_corpus_axis[axis["corpus_axis"]]
                    for horizon in horizons:
                        window = horizon_window(episodes, horizon, args.horizon_mode)
                        hashes = window_hash(episodes, window)
                        for draw_index in range(1, K_INFERENCE_DRAWS + 1):
                            key = record_key(
                                args.block_id, "RC1", "id", axis_id, horizon,
                                cell_id, seed_root, draw_index,
                            )
                            if (out_records / f"{key}.json").exists():
                                skipped_existing += 1
                                continue
                            mechanism = (
                                surface["build_inference_mechanism"](
                                    _inference_config(surface, axis["deployment_kernel"]),
                                    seed_root=seed_root,
                                    draw_index=draw_index,
                                )
                                if inference_enforcement == "through_m" else None
                            )
                            result = evaluate_cell(
                                surface, model, mechanism, episodes, window,
                                inference_enforcement=inference_enforcement,
                                coordinate=arm["coordinate"],
                            )
                            y = endpoint_y(result["error"], scales)
                            error = result["error"]
                            record = make_record(
                                record_key=key,
                                record_class="RC1",
                                run_id=(
                                    f"{args.block_id}.eval.{arm_id}.{axis_id}.{cell_id}."
                                    f"{seed_root:05d}.{draw_index:02d}"
                                ),
                                block_id=args.block_id,
                                lineage=lineage,
                                dgp_variant="lab-asset-v3",
                                seed=seed_root,
                                cell_id=cell_id,
                                axis=axis_id,
                                horizon=horizon,
                                draw_index=draw_index,
                                condition="id",
                                config_sha256=sha256_bytes(canonical_bytes({
                                    "runtime": RUNTIME_ID,
                                    "horizon_mode": args.horizon_mode,
                                    "coordinate": arm["coordinate"],
                                    "training_enforcement": arm["enforcement"],
                                    "inference_enforcement": inference_enforcement,
                                    "axis": axis_id,
                                    "horizon": horizon,
                                    "estimator": "straight_through",
                                    "mechanism_backend": "engine_bridge",
                                    "checkpoint_lock_sha256": checkpoint_lock_sha256,
                                    "scales_sha256": sha256_bytes(
                                        canonical_bytes(scales_payload)
                                    ),
                                })),
                                git_sha=git_sha,
                                fixture_manifest_sha256=fixture_sha,
                                schema_version="lab-asset-v3",
                                stream_hashes=stream_hashes_for(surface, seed_root),
                                checkpoint_lock_sha256=checkpoint_lock_sha256,
                                allocation_rule=(
                                    axis["deployment_kernel"]
                                    if inference_enforcement == "through_m"
                                    else TRAINING_KERNEL
                                ),
                                n_draws=K_INFERENCE_DRAWS,
                                metrics={
                                    "endpoint_y": y,
                                    "n_window_rounds": result["n_window_rounds"],
                                    "max_abs_error_volume_units": float(
                                        error[:, 0].abs().max().item()
                                    ),
                                    "max_abs_error_cash_ticks": float(
                                        error[:, 1].abs().max().item()
                                    ),
                                    "finite": bool(y == y),
                                },
                                pre_best_bid=result["boundaries"]["pre_best_bid"],
                                pre_best_ask=result["boundaries"]["pre_best_ask"],
                                post_best_bid=result["boundaries"]["post_best_bid"],
                                post_best_ask=result["boundaries"]["post_best_ask"],
                                conservation_violation_steps={
                                    "volume": result["volume_violations"],
                                    "cash": result["cash_violations"],
                                },
                                pre_state_hash=hashes["pre_state_hash"],
                                post_state_hash=hashes["post_state_hash"],
                                pre_aggregate_state_hash=hashes["pre_aggregate_state_hash"],
                                post_aggregate_state_hash=hashes["post_aggregate_state_hash"],
                            )
                            write_record(out_records, record)
                            written_rc1 += 1
                            if args.max_records and written_rc1 >= args.max_records:
                                stopped_early = True
                                break
                        if stopped_early:
                            break
                    if stopped_early:
                        break
                if stopped_early:
                    break
            if stopped_early:
                break
        if stopped_early:
            break

        # C4(iii) duplicates: raw-inference kswap records copy their ID twins
        dup_written, dup_skipped = emit_kswap_duplicates(
            out_records, args.block_id, seed_root, axis_ids, arms, horizons
        )
        written_rc1 += dup_written
        dup_written_total += dup_written
        skipped_existing += dup_skipped

        # RC2 truncation deployment passes (ID axis, PR §3.4 secondary family):
        # same 8-cell grid, conditions trunc_lag/trunc_cap, one pinned W each.
        if rc2_conditions:
            episodes_id, id_fixture_sha = episodes_by_corpus_axis[RC2_AXIS]
            trunc_cache: dict[str, list[dict[str, Any]]] = {}
            for condition in rc2_conditions:
                w = RC2_W[condition]
                trunc_episodes = trunc_cache.get(condition)
                if trunc_episodes is None:
                    trunc_episodes = trunc_session_episodes(
                        surface, repo_root, seed_root, episodes_id, w
                    )
                    trunc_cache[condition] = trunc_episodes
                for arm_id in arm_ids:
                    arm = arms[arm_id]
                    model, checkpoint_lock_sha256 = load_arm_surface(
                        surface, block_dir, arm_id, seed_root
                    )
                    for inference_enforcement in INFERENCE_ENFORCEMENTS:
                        cell_id = f"{arm['coordinate']}-{arm['enforcement']}-{inference_enforcement}"
                        for horizon in horizons:
                            window = horizon_window(trunc_episodes, horizon, args.horizon_mode)
                            hashes = window_hash(trunc_episodes, window)
                            for draw_index in range(1, K_INFERENCE_DRAWS + 1):
                                key = record_key(
                                    args.block_id, "RC2", condition, RC2_AXIS, horizon,
                                    cell_id, seed_root, draw_index,
                                )
                                if (out_records / f"{key}.json").exists():
                                    skipped_existing += 1
                                    continue
                                mechanism = (
                                    surface["build_inference_mechanism"](
                                        _inference_config(surface, TRAINING_KERNEL),
                                        seed_root=seed_root,
                                        draw_index=draw_index,
                                    )
                                    if inference_enforcement == "through_m" else None
                                )
                                result = evaluate_cell(
                                    surface, model, mechanism, trunc_episodes, window,
                                    inference_enforcement=inference_enforcement,
                                    coordinate=arm["coordinate"],
                                )
                                y = endpoint_y(result["error"], scales)
                                error = result["error"]
                                record = make_record(
                                    record_key=key,
                                    record_class="RC2",
                                    run_id=(
                                        f"{args.block_id}.eval.{arm_id}.{condition}.{cell_id}."
                                        f"{seed_root:05d}.{draw_index:02d}"
                                    ),
                                    block_id=args.block_id,
                                    lineage=lineage,
                                    dgp_variant="lab-asset-v3",
                                    seed=seed_root,
                                    cell_id=cell_id,
                                    axis=RC2_AXIS,
                                    horizon=horizon,
                                    draw_index=draw_index,
                                    condition=condition,
                                    config_sha256=sha256_bytes(canonical_bytes({
                                        "runtime": RUNTIME_ID,
                                        "horizon_mode": args.horizon_mode,
                                        "coordinate": arm["coordinate"],
                                        "training_enforcement": arm["enforcement"],
                                        "inference_enforcement": inference_enforcement,
                                        "axis": RC2_AXIS,
                                        "condition": condition,
                                        "truncation_window": w,
                                        "horizon": horizon,
                                        "estimator": "straight_through",
                                        "mechanism_backend": "engine_bridge",
                                        "checkpoint_lock_sha256": checkpoint_lock_sha256,
                                        "scales_sha256": sha256_bytes(
                                            canonical_bytes(scales_payload)
                                        ),
                                    })),
                                    git_sha=git_sha,
                                    fixture_manifest_sha256=id_fixture_sha,
                                    schema_version="lab-asset-v3",
                                    stream_hashes=stream_hashes_for(surface, seed_root),
                                    checkpoint_lock_sha256=checkpoint_lock_sha256,
                                    allocation_rule=TRAINING_KERNEL,
                                    n_draws=K_INFERENCE_DRAWS,
                                    metrics={
                                        "endpoint_y": y,
                                        "n_window_rounds": result["n_window_rounds"],
                                        "max_abs_error_volume_units": float(
                                            error[:, 0].abs().max().item()
                                        ),
                                        "max_abs_error_cash_ticks": float(
                                            error[:, 1].abs().max().item()
                                        ),
                                        "finite": bool(y == y),
                                    },
                                    pre_best_bid=result["boundaries"]["pre_best_bid"],
                                    pre_best_ask=result["boundaries"]["pre_best_ask"],
                                    post_best_bid=result["boundaries"]["post_best_bid"],
                                    post_best_ask=result["boundaries"]["post_best_ask"],
                                    conservation_violation_steps={
                                        "volume": result["volume_violations"],
                                        "cash": result["cash_violations"],
                                    },
                                    pre_state_hash=hashes["pre_state_hash"],
                                    post_state_hash=hashes["post_state_hash"],
                                    pre_aggregate_state_hash=hashes["pre_aggregate_state_hash"],
                                    post_aggregate_state_hash=hashes["post_aggregate_state_hash"],
                                )
                                write_record(out_records, record)
                                written_rc2 += 1
                                if args.max_records and written_rc2 >= args.max_records:
                                    stopped_early = True
                                    break
                            if stopped_early:
                                break
                        if stopped_early:
                            break
                    if stopped_early:
                        break
                if stopped_early:
                    break
            if stopped_early:
                break

        print(
            f"[{RUNTIME_ID}] seed {seed_root} rc1={written_rc1} (dupes={dup_written_total}) "
            f"rc2={written_rc2} rc4={written_rc4} skipped={skipped_existing} "
            f"wall={time.time() - seed_started:.0f}s",
            flush=True,
        )

    manifest = {
        "schema_version": RUNTIME_SCHEMA,
        "campaign_id": CAMPAIGN_ID,
        "runtime_id": RUNTIME_ID,
        "block_id": args.block_id,
        "seeds": f"{seed_start}:{seed_stop}",
        "arms": arm_ids,
        "axes": axis_ids,
        "horizons": horizons,
        "rc2_conditions": rc2_conditions,
        "horizon_mode": args.horizon_mode,
        "scales": scales_payload,
        "production_decision": args.production_decision,
        "production_decision_sha256": production_decision_sha256,
        "freeze_commit": FREEZE_COMMIT,
        "git_sha": git_sha,
        "pinned_constants": {
            "record_literals": {
                "record_class": ["RC1", "RC2", "RC4"],
                "condition": ["id", "trunc_lag", "trunc_cap"],
                "schema_version": "lab-asset-v3",
                "lineage": lineage,
                "dgp_variant": "lab-asset-v3",
            },
            "run_id_formats": {
                "rc1": "{block}.eval.{arm}.{axis}.{cell}.{seed:05d}.{draw:02d}.h{horizon:02d}",
                "rc2": "{block}.eval.{arm}.{condition}.{cell}.{seed:05d}.{draw:02d}.h{horizon:02d}",
                "probe": "{block}.probe.{axis}.{seed}",
                "kswap_duplicate_suffix": ".kswap",
                "g8_exempt_fields": ["record_key", "run_id", "axis"],
            },
            "rc2_truncation": {
                "conditions_w": dict(RC2_W),
                "operator": (
                    "D_trunc^W: initial resting orders with arrival_clock > W removed "
                    "from the deployed book, then the recorded request stream replayed "
                    "from the truncated prestate (lemma writeup kt_g4_g5 section 4)"
                ),
                "axis": RC2_AXIS,
                "truth_side": (
                    "truncated session's own re-executed channels_cumulative "
                    "(pop_2x-axis treatment)"
                ),
                "fixture_binding": "ID-axis stream manifest sha256 (kswap precedent)",
                "guards": [
                    "episode_canonical_json_sha256 hash guard on every re-derivation",
                    "E-4 conservation + settlement gates re-run on every truncated tape",
                ],
                "kswap_duplicates": "none (ID axis only)",
            },
            "stream_hashes": (
                "sha256(canonical_json({data,init,minibatch,train_kernel} "
                "sub-dict of derive_substream_seeds(seed_root))) -- training's recipe"
            ),
            "fixture_manifest_sha256": (
                "sha256 of the per-(corpus-axis, seed) stream_manifest.json file"
            ),
            "window_hash": (
                "sha256(canonical_json([{episode_index, rounds, **boundaries}])) "
                "over the window, same digest in all four hash fields"
            ),
            "bbo_scope": "last window episode's session boundaries",
            "config_sha256": (
                "per-record canonical dict: runtime, horizon_mode, coordinate, "
                "training/inference enforcement, axis, horizon, estimator, "
                "mechanism_backend, checkpoint_lock_sha256, scales_sha256"
            ),
            "mechanism_cadence": (
                "fresh build_inference_mechanism per (cell, axis, horizon, draw) "
                "record; kernel:k substream consumed from position 0 in record order"
            ),
            "probe_conventions": {
                "cell_id": "engine-replay-probe",
                "draw_index": 0,
                "horizon": 1,
                "n_draws": 16,
                "checkpoint_lock_sha256": None,
                "allocation_rule": "fifo",
                "episode_index": PROBE_EPISODE_INDEX,
            },
            "estimator": "straight_through",
            "mechanism_backend": "engine_bridge",
            "through_m_coordinate_composition": (
                "engine-increment cumulation from a per-episode zero base "
                "(both coordinates; the abs head is not read on the through-M path)"
            ),
            "conservation_check": (
                "per-step float integrality of the volume and cash increments "
                "(raw cells carry zeros: G7 does not apply)"
            ),
            "freeze_pins": "3-file sha256 pins + FREEZE_COMMIT ancestry "
                           "(see FREEZE_FILE_PINS in this driver)",
        },
        "env": {
            "torch": torch.__version__,
            "numpy": __import__("numpy").__version__,
            "python": sys.version.split()[0],
            "device": "cpu",
            "num_threads": 1,
        },
        "counts": {
            "rc1_written": written_rc1,
            "rc1_kswap_duplicates": dup_written_total,
            "rc2_written": written_rc2,
            "rc4_written": written_rc4,
            "skipped_existing": skipped_existing,
            "stopped_early": stopped_early,
        },
        "wall_seconds": time.time() - started,
    }
    atomic_write_bytes(args.out_dir / "eval_manifest.json", canonical_bytes(manifest))
    print(f"[{RUNTIME_ID}] manifest written counts={manifest['counts']}", flush=True)
    return 0


def emit_kswap_duplicates(out_records: Path, block_id: str, seed_root: int,
                          axis_ids: list[str], arms: dict[str, dict[str, Any]],
                          horizons: list[int]) -> tuple[int, int]:
    """C4(iii): raw-inference kswap records are payload-identical ID copies.

    Differing fields: record_key, axis, run_id (G2 uniqueness).  allocation_rule
    is pinned to the training-time kernel field (fifo) per G10/C4(iii); every
    payload field including n_draws stays identical -- the analyzer's
    duplicate byte-identity check reads exactly that.

    Returns (written, skipped_existing_duplicates).
    """

    if "kswap" not in axis_ids or "id" not in axis_ids:
        return 0, 0
    written = 0
    skipped = 0
    for arm in arms.values():
        cell_id = f"{arm['coordinate']}-{arm['enforcement']}-raw"
        for horizon in horizons:
            for draw_index in range(1, K_INFERENCE_DRAWS + 1):
                source_key = record_key(
                    block_id, "RC1", "id", "id", horizon, cell_id, seed_root, draw_index
                )
                source_path = out_records / f"{source_key}.json"
                if not source_path.exists():
                    continue
                dup_key = record_key(
                    block_id, "RC1", "id", "kswap", horizon, cell_id, seed_root, draw_index
                )
                dup_path = out_records / f"{dup_key}.json"
                if dup_path.exists():
                    skipped += 1
                    continue
                record = json.loads(source_path.read_text())
                record["record_key"] = dup_key
                record["axis"] = "kswap"
                record["run_id"] = record["run_id"] + ".kswap"
                write_record(out_records, record)
                written += 1
    return written, skipped


def _inference_config(surface: dict[str, Any], deployment_kernel: str) -> Any:
    """FactSurrogateTrainConfig consumed by build_inference_mechanism.

    The inference mechanism is selected by (estimator, kernel) -- not the
    training-enforcement axis (frozen docstring).  Kernel is per-axis: fifo
    on id/pop_2x/tick_2x through-M deployments, random_unit_within_price on
    kswap (C4(ii)).  Estimator is STRAIGHT_THROUGH for every cell: the KT-A4
    primary (raw arms carry estimator null; PAM is the A10 audit only).
    build_inference_mechanism forces enforcement=THROUGH_M internally.
    """

    from ecomd.training.train_fact_surrogate import (
        EstimatorKind,
        FactSurrogateTrainConfig,
        Kernel,
        MechanismBackend,
    )

    return FactSurrogateTrainConfig(
        enforcement=surface["Enforcement"].THROUGH_M,
        estimator=EstimatorKind.STRAIGHT_THROUGH,
        kernel=Kernel(deployment_kernel),
        mechanism_backend=MechanismBackend.ENGINE_BRIDGE,
    )


if __name__ == "__main__":
    raise SystemExit(main())
