"""Training surface for the L2 recurrent fact-surrogate (build items L2-2/3/4).

Code-only pre-D0 build (PI decision D1_13): a CPU-runnable trainer that wires
the four existing fact-surrogate losses (:mod:`ecomd.training.fact_surrogates`,
composed through :func:`ecomd.training.losses.multi_fact_terms` — the same path
L1 uses) plus the supervised conserving-channel rollout error of contract C5,
the RNG-tree seeding surface of contract C1/C2, and a checkpoint format adopted
verbatim from ``train_distributed`` (``format_version`` 2 payload keys,
``torch.load(..., map_location="cpu", weights_only=False)``-loadable, carrying
the recurrent hidden state at the save boundary per simulator contracts 3.5).

Validation scope: CPU smoke (forward + a single synthetic-batch gradient step)
only. No persisted checkpoints for reuse, no real training run, no GPU.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import subprocess
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, cast

import numpy as np
import torch
from torch import Tensor

from ..mechanisms.through_m import (
    Kernel,
    perturb_and_map_through_m,
    straight_through_through_m,
)
from ..models.fact_surrogate import (
    FactSurrogateBatch,
    FactSurrogateOutput,
    MechanismEstimator,
    RecurrentFactSurrogate,
)
from .losses import LossWeights, MomentTargets, multi_fact_terms

__all__ = [
    "K_INFERENCE_DRAWS",
    "SUBSTREAM_NAMES",
    "Coordinate",
    "Enforcement",
    "EstimatorKind",
    "FactSurrogateTrainConfig",
    "build_mechanism",
    "checkpoint_execution_metadata",
    "config_payload",
    "config_sha256",
    "derive_substream_seeds",
    "engine_draw_supplier",
    "fact_targets_from_config",
    "fact_weights_from_config",
    "load_fact_surrogate_checkpoint",
    "save_fact_surrogate_checkpoint",
    "substream_generator",
    "train_fact_surrogate",
]


# ─────────────────────────────────────────────────────────────────────────────
# RNG-tree seeding surface (contract C1/C2; simulator contracts 3.4)
# ─────────────────────────────────────────────────────────────────────────────


K_INFERENCE_DRAWS = 16
"""K = 16 inference-kernel draws per seed (contract C2(b) amendment (11):
the K-preflight returned ``none_in_set`` and the PI selected K = 16)."""

SUBSTREAM_NAMES: tuple[str, ...] = (
    "data",
    "init",
    "minibatch",
    "train_kernel",
    *(f"kernel:{index}" for index in range(1, K_INFERENCE_DRAWS + 1)),
)
"""Named substreams of the seed root (contract C1): data / init / minibatch /
train_kernel / kernel:1..16. Derivation (frozen): ``numpy.random.SeedSequence(
root).spawn(20)`` in exactly this name order; child ``i`` → name ``i``; the
integer seed is the first ``uint32`` of ``generate_state(1)``. Library+version
pin: numpy 2.4.4 of the frozen ``ecophys`` env (ops plan section 3 item 3)."""


def derive_substream_seeds(seed_root: int) -> dict[str, int]:
    """Derive all named substream seeds from one seed root (deterministic)."""

    children = np.random.SeedSequence(int(seed_root)).spawn(len(SUBSTREAM_NAMES))
    seeds = {
        name: int(child.generate_state(1, dtype=np.uint32)[0])
        for name, child in zip(SUBSTREAM_NAMES, children, strict=True)
    }
    if len(set(seeds.values())) != len(seeds):
        raise RuntimeError("substream seed collision in RNG-tree derivation")
    return seeds


def substream_generator(seed_root: int, name: str) -> torch.Generator:
    """A fresh CPU generator seeded from the named substream of ``seed_root``."""

    if name not in SUBSTREAM_NAMES:
        raise ValueError(f"unknown substream {name!r}; expected one of {SUBSTREAM_NAMES}")
    generator = torch.Generator(device="cpu")
    generator.manual_seed(derive_substream_seeds(seed_root)[name])
    return generator


# ─────────────────────────────────────────────────────────────────────────────
# Arm / estimator configuration (contract C3 cube vocabulary)
# ─────────────────────────────────────────────────────────────────────────────


class Coordinate(Enum):
    """Trained prediction coordinate (contract C3 axis c)."""

    ABSOLUTE = "absolute"
    INCREMENT = "increment"


class Enforcement(Enum):
    """Training-time mechanism enforcement (contract C3 axis t)."""

    RAW = "raw"
    THROUGH_M = "through_m"


class EstimatorKind(Enum):
    """Which frozen through-M estimator feeds the mechanism hook (KT-A4 menu)."""

    STRAIGHT_THROUGH = "straight_through"
    PERTURB_AND_MAP = "perturb_and_map"


@dataclass(frozen=True)
class FactSurrogateTrainConfig:
    """CPU training-loop configuration. The four ``w_*`` fact weights and
    matching ``*_target`` fields wire :mod:`ecomd.training.fact_surrogates`
    exactly as ``LossWeights``/``MomentTargets`` do for L1 (a term is active
    iff its weight > 0 and its target is not ``None``)."""

    n_iters: int = 8
    lr: float = 3e-4
    grad_clip: float = 1.0
    coordinate: Coordinate = Coordinate.INCREMENT  # R00 pinned to increment (amendment (3))
    enforcement: Enforcement = Enforcement.RAW
    estimator: EstimatorKind = EstimatorKind.STRAIGHT_THROUGH
    kernel: Kernel = Kernel.FIFO
    channel_scales: tuple[float, ...] = (1.0, 1.0)  # s_ch, frozen DGP-native per C5
    w_supervised: float = 1.0
    w_gain_loss: float = 0.0
    gain_loss_skew_target: float | None = None
    w_agg_gauss: float = 0.0
    agg_gaussianity_target: float | None = None
    w_fano: float = 0.0
    fano_target: float | None = None
    w_dfa_hurst: float = 0.0
    dfa_hurst_target: float | None = None
    agg_gauss_scale_large: int = 50
    fano_quantile: float = 0.99
    fano_n_windows: int = 50
    dfa_min_scale: int = 16
    dfa_max_scale_frac: float = 0.1


def fact_targets_from_config(config: FactSurrogateTrainConfig) -> MomentTargets:
    """Build the multi-fact ``MomentTargets`` from the trainer config."""

    return MomentTargets(
        acf_sq_mean=0.0,
        leverage_sum=0.0,
        hill_alpha=0.0,
        gain_loss_skew=config.gain_loss_skew_target,
        agg_gaussianity=config.agg_gaussianity_target,
        fano=config.fano_target,
        dfa_hurst=config.dfa_hurst_target,
    )


def fact_weights_from_config(config: FactSurrogateTrainConfig) -> LossWeights:
    """Build the multi-fact ``LossWeights`` from the trainer config."""

    return LossWeights(
        w_acf_sq=0.0,
        w_leverage=0.0,
        w_hill=0.0,
        w_gain_loss=config.w_gain_loss,
        w_agg_gauss=config.w_agg_gauss,
        agg_gauss_scale_large=config.agg_gauss_scale_large,
        w_fano=config.w_fano,
        fano_quantile=config.fano_quantile,
        fano_n_windows=config.fano_n_windows,
        w_dfa_hurst=config.w_dfa_hurst,
        dfa_min_scale=config.dfa_min_scale,
        dfa_max_scale_frac=config.dfa_max_scale_frac,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Through-M mechanism hookup (estimator menu interface; through_m.py untouched)
# ─────────────────────────────────────────────────────────────────────────────


def engine_draw_supplier(generator: torch.Generator) -> MechanismEstimator:
    """Random-unit draw stream mirroring ``ReferenceEngine._select_maker``.

    Per executed unit: ``draw ~ randrange(sum(remaining))`` over the depleting
    remaining quantities (matching.py:592-604), consumed from the caller's
    ``train_kernel`` substream generator. Returned as a partial-applied
    straight-through estimator; the engine-bridge wrapper (build item E-3)
    supersedes this with the identical call shape at D0.
    """

    def mechanism(quantities: Tensor, demand: int) -> Tensor:
        resting = [int(value) for value in quantities.detach().round().to(torch.int64).tolist()]
        if any(value < 0 for value in resting):
            raise ValueError("resting quantities must be nonnegative")
        executed = min(demand, sum(resting))
        remaining = list(resting)
        draws: list[int] = []
        for _ in range(executed):
            eligible = sum(remaining)
            if eligible <= 0:
                break
            selected = int(
                torch.randint(eligible, (1,), generator=generator).item()
            )
            draws.append(selected)
            cumulative = 0
            for index, quantity in enumerate(remaining):
                cumulative += quantity
                if selected < cumulative:
                    remaining[index] -= 1
                    break
        return straight_through_through_m(
            quantities, demand, Kernel.RANDOM_UNIT_WITHIN_PRICE, draws
        )

    return mechanism


def build_mechanism(
    config: FactSurrogateTrainConfig,
    *,
    train_kernel_generator: torch.Generator,
) -> MechanismEstimator | None:
    """The through-M hook for one arm, or ``None`` for the raw arm.

    straight_through + fifo needs no draws; straight_through + random_unit
    consumes the engine-law draw stream from the ``train_kernel`` substream;
    perturb_and_map takes its seed from the same substream so the audit retrain
    sees paired kernel randomness within the seed (estimator menu section 2).
    """

    if config.enforcement is Enforcement.RAW:
        return None
    if config.estimator is EstimatorKind.STRAIGHT_THROUGH:
        if config.kernel is Kernel.FIFO:
            return lambda quantities, demand: straight_through_through_m(
                quantities, demand, Kernel.FIFO
            )
        return engine_draw_supplier(train_kernel_generator)
    seed = int(torch.randint(2**31 - 1, (1,), generator=train_kernel_generator).item())
    return lambda quantities, demand: perturb_and_map_through_m(
        quantities, demand, config.kernel, seed=seed
    )


# ─────────────────────────────────────────────────────────────────────────────
# Training loop (train.py conventions: Adam, grad clip, history records)
# ─────────────────────────────────────────────────────────────────────────────


def _predicted_channels(
    output: FactSurrogateOutput, batch: FactSurrogateBatch, config: FactSurrogateTrainConfig
) -> tuple[Tensor, Tensor]:
    """(prediction, target) for the C5 conserving-channel loss under ``config``.

    ABSOLUTE reads the ABS head against the observed post-round channels;
    INCREMENT reads the INC head against ``channels[:, t-1] + increment`` (the
    observed pre-round base; ``channels_init`` at ``t = 0``). Under through-M
    enforcement the channel prediction is the mechanism-decoded cumulation —
    the exact-integer arm of contract C5 — and the heads' gradient reaches the
    parameters only through the frozen estimator.
    """

    target = batch.channels
    if config.enforcement is Enforcement.THROUGH_M:
        assert output.mechanism_channels is not None
        return output.mechanism_channels, target
    if config.coordinate is Coordinate.ABSOLUTE:
        return output.abs_channels, target
    base = (
        batch.channels_init.unsqueeze(1)
        if batch.channels_init is not None
        else torch.zeros_like(target[:, :1])
    )
    previous = torch.cat((base, target[:, :-1]), dim=1)
    return previous + output.inc_channels, target


def _fact_terms(
    output: FactSurrogateOutput, config: FactSurrogateTrainConfig
) -> dict[str, Tensor]:
    """Average :func:`multi_fact_terms` over the batch's decoded return series."""

    weights = fact_weights_from_config(config)
    targets = fact_targets_from_config(config)
    totals: dict[str, list[Tensor]] = {}
    for episode in range(output.returns.shape[0]):
        terms = multi_fact_terms(output.returns[episode], targets, weights)
        for key, value in terms.items():
            totals.setdefault(key, []).append(value)
    return {key: torch.stack(values).mean() for key, values in totals.items()}


def train_fact_surrogate(
    model: RecurrentFactSurrogate,
    batch: FactSurrogateBatch,
    config: FactSurrogateTrainConfig,
    *,
    seed_root: int,
) -> list[dict[str, Any]]:
    """CPU training loop for one (arm, seed) smoke/production run.

    Every stochastic consumer draws from a named substream of ``seed_root``:
    the minibatch-order permutation from ``minibatch``, the through-M kernel
    stream from ``train_kernel``. Parameter init is expected to have used the
    ``init`` substream at construction. The same (model construction,
    ``seed_root``, ``batch``) triple reproduces byte-identical training.
    """

    if batch.features.device.type != "cpu":
        raise ValueError("the L2 training loop is CPU-only (PI decision D1_13)")
    seeds = derive_substream_seeds(seed_root)
    minibatch_generator = torch.Generator(device="cpu")
    minibatch_generator.manual_seed(seeds["minibatch"])
    train_kernel_generator = torch.Generator(device="cpu")
    train_kernel_generator.manual_seed(seeds["train_kernel"])
    mechanism = build_mechanism(config, train_kernel_generator=train_kernel_generator)
    scales = torch.tensor(config.channel_scales, dtype=torch.float32)

    optimizer = torch.optim.Adam(model.parameters(), lr=config.lr)
    history: list[dict[str, Any]] = []
    episodes = batch.features.shape[0]
    for iteration in range(config.n_iters):
        optimizer.zero_grad()
        order = torch.randperm(episodes, generator=minibatch_generator)
        shuffled = FactSurrogateBatch(
            features=batch.features[order],
            channels=batch.channels[order],
            slot_prices=batch.slot_prices[order],
            channels_init=(
                batch.channels_init[order] if batch.channels_init is not None else None
            ),
        )
        output = model(shuffled, mechanism=mechanism)
        prediction, target = _predicted_channels(output, shuffled, config)
        channel_loss = (((prediction - target) / scales) ** 2).mean()
        facts = _fact_terms(output, config)
        total = config.w_supervised * channel_loss + facts["_total"]

        torch.autograd.backward(total)
        with torch.no_grad():
            grad_sq = torch.tensor(0.0)
            for parameter in model.parameters():
                if parameter.grad is not None:
                    grad_sq = grad_sq + parameter.grad.detach().pow(2).sum()
            grad_norm = grad_sq.sqrt()
        torch.nn.utils.clip_grad_norm_(model.parameters(), config.grad_clip)
        optimizer.step()

        record: dict[str, Any] = {
            "iter": iteration,
            "total": float(total.item()),
            "channel_loss": float(channel_loss.item()),
            "grad_norm": float(grad_norm.item()),
            "coordinate": config.coordinate.value,
            "enforcement": config.enforcement.value,
        }
        for key, value in facts.items():
            if key != "_total":
                record[key] = float(value.item())
        history.append(record)
    return history


# ─────────────────────────────────────────────────────────────────────────────
# Checkpoint contract (train_distributed format, adopted verbatim; L2-4)
# ─────────────────────────────────────────────────────────────────────────────


FACT_SURROGATE_CHECKPOINT_FORMAT_VERSION = 2


def config_payload(config: FactSurrogateTrainConfig) -> dict[str, Any]:
    """JSON-serializable config payload (enums by value, tuples as lists)."""

    payload = asdict(config)
    payload["coordinate"] = config.coordinate.value
    payload["enforcement"] = config.enforcement.value
    payload["estimator"] = config.estimator.value
    payload["kernel"] = config.kernel.value
    payload["channel_scales"] = list(config.channel_scales)
    return payload


def config_sha256(config: FactSurrogateTrainConfig) -> str:
    """sha256 of the canonical JSON of the config payload (freeze binding)."""

    encoded = json.dumps(config_payload(config), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def checkpoint_execution_metadata(
    repo_root: Path, config: FactSurrogateTrainConfig
) -> dict[str, Any]:
    """Git SHA + config hash binding (repo reproducibility standard)."""

    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return {
        "schema_version": 1,
        "lineage": "L2_fact_surrogate",
        "git_sha": sha,
        "config_sha256": config_sha256(config),
    }


def save_fact_surrogate_checkpoint(
    path: Path,
    *,
    model: RecurrentFactSurrogate,
    optimizer: torch.optim.Optimizer,
    iter_idx: int,
    config: FactSurrogateTrainConfig,
    hidden: Tensor,
    substream_generators: dict[str, torch.Generator],
    history: list[dict[str, Any]],
    execution_metadata: dict[str, Any],
) -> None:
    """Atomic save in the ``train_distributed`` payload vocabulary.

    Keys mirror ``save_checkpoint`` verbatim (``format_version`` 2,
    ``world_size`` 1, single-rank runtime in ``rank_runtimes``) with two L2
    additions per simulator contracts 3.5: the recurrent hidden state at the
    save boundary (top level and inside the rank runtime) and the named
    substream generator states.
    """

    payload = {
        "format_version": FACT_SURROGATE_CHECKPOINT_FORMAT_VERSION,
        "iter_idx": iter_idx,
        "world_size": 1,
        "state_complete": True,
        "sim_state_dict": model.state_dict(),
        "optim_state_dict": optimizer.state_dict(),
        "rank_runtimes": [
            {
                "rank": 0,
                "recurrent_hidden": hidden.detach().cpu(),
                "substream_generator_states": {
                    name: generator.get_state().detach().cpu().clone()
                    for name, generator in substream_generators.items()
                },
                "torch_cpu_rng_state": torch.get_rng_state().detach().cpu().clone(),
                "numpy_rng_state": np.random.get_state(),
                "python_rng_state": random.getstate(),
                "history": list(history),
            }
        ],
        "recurrent_hidden": hidden.detach().cpu(),
        "targets": {},
        "sim_config": config_payload(config),
        "train_config": {"config_sha256": config_sha256(config)},
        "execution_metadata": execution_metadata,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    torch.save(payload, temporary)
    os.replace(temporary, path)


def load_fact_surrogate_checkpoint(
    path: Path,
    *,
    model: RecurrentFactSurrogate,
    optimizer: torch.optim.Optimizer | None = None,
) -> dict[str, Any]:
    """CPU-load a checkpoint (``map_location="cpu"``) into ``model``.

    Returns the full payload after validating the format version. Raises
    ``ValueError`` on any format mismatch, mirroring
    ``try_load_checkpoint``'s validation posture.
    """

    ckpt = cast(
        dict[str, Any],
        torch.load(path, map_location="cpu", weights_only=False),
    )
    version = int(ckpt.get("format_version", -1))
    if version != FACT_SURROGATE_CHECKPOINT_FORMAT_VERSION:
        raise ValueError(f"unsupported checkpoint format_version={version}")
    if int(ckpt.get("world_size", -1)) != 1:
        raise ValueError("L2 smoke checkpoints are single-rank (world_size=1)")
    runtimes = ckpt.get("rank_runtimes")
    if not isinstance(runtimes, list) or len(runtimes) != 1:
        raise ValueError("checkpoint is missing its single rank runtime")
    model.load_state_dict(ckpt["sim_state_dict"])
    if optimizer is not None:
        optimizer.load_state_dict(ckpt["optim_state_dict"])
    return ckpt
