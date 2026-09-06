"""Supervised rollout-error training surface for the L1 coordinate heads (L1-2).

Code-only pre-D0 build (PI decision D1_13). Closes the two simulator-contracts
section 2.4 gaps as part of the supervised loop:

- **init binding (i)**: the persistent-type-label seed surface
  (``EcoMDConfig.v2_type_seed``, default 42) gains an OPT-IN explicit binding
  to the named ``spawn(seed, "init")`` substream via :func:`bind_v2_type_seed`
  / :func:`init_substream_seed`. The existing default behavior is untouched —
  the new binding is selected only by callers of the new training path.
- **minibatch binding (ii)**: :class:`MinibatchOrderStream` is the shared
  minibatch-order stream of contract C1/G2, drawing its permutations solely
  from the ``spawn(seed, "minibatch")`` generator.

The supervised objective is contract C5's conserving-channel rollout error
against DGP truth, ``Y = sqrt(mean_ch mean_t ((x̂_ch,t - x_ch,t)/s_ch)^2)``,
evaluated in channel-state space for BOTH coordinate arms (the increment
decode is lifted by the observed pre-round base) so that contract C3's
``D_te = Ȳ_absolute,te - Ȳ_increment,te`` subtracts commensurate endpoints.
The training term is the mean squared scaled deviation (same minimizer as
``Y``; the square root is exposed as ``c5_endpoint`` for reporting). The loss
COMPOSES with the existing :func:`ecomd.training.losses.multi_fact_terms`
path — it does not replace it: :func:`combine_supervised_and_fact_terms`
merges the two term families into one ``total``.

RNG-tree derivation is the single frozen shared point
(:func:`ecomd.training.train_fact_surrogate.derive_substream_seeds`,
``numpy.random.SeedSequence(root).spawn(20)`` in the frozen name order);
this module defines no second derivation. Validation scope: CPU smoke (a
single synthetic-batch gradient step). No training runs, no persisted
checkpoints (L1-5 owns the checkpoint variant), no GPU.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from dataclasses import replace as dataclass_replace
from typing import Any

import torch
from torch import Tensor

from ..models.ecomd import EcoMDConfig
from ..models.fact_surrogate import FactSurrogateBatch
from ..models.l1_coordinate_heads import L1CoordinateHeads, L1CoordinateOutput
from .losses import LossWeights, MomentTargets, multi_fact_terms, smooth_dev
from .train_fact_surrogate import Coordinate, derive_substream_seeds

__all__ = [
    "CoordinateTargets",
    "L1SupervisedTrainConfig",
    "MinibatchOrderStream",
    "bind_v2_type_seed",
    "build_coordinate_targets",
    "combine_supervised_and_fact_terms",
    "coordinate_state_prediction",
    "init_substream_seed",
    "l1_supervised_terms",
    "train_l1_coordinate_heads",
]


# ─────────────────────────────────────────────────────────────────────────────
# Coordinate targets (contract C3: the two arms differ only in target coordinate)
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class CoordinateTargets:
    """The two coordinate target families over one observed channel sequence.

    ``base[t]`` is the observed pre-round state ``x_t`` (``channels_init`` at
    ``t = 0``, zero base when absent — matching the E-1 zero-base cumsum;
    ``channels[:, t-1]`` afterwards). The families are exact inverses on
    consecutive states: ``abs_targets == base + inc_targets`` identically.
    """

    base: Tensor         # (B, T, C) observed pre-round channel state x_t
    abs_targets: Tensor  # (B, T, C) observed post-round state x_{t+1}
    inc_targets: Tensor  # (B, T, C) observed increments x_{t+1} - x_t


def build_coordinate_targets(
    channels: Tensor,
    channels_init: Tensor | None = None,
) -> CoordinateTargets:
    """Build both coordinate target families from one observed channel path.

    ``channels[b, t]`` is the observed conserving-channel state AFTER round
    ``t`` (the :class:`FactSurrogateBatch` semantics); ``channels_init[b]``
    the pre-session state. Pure arithmetic — deterministic, no stochastic
    consumer.
    """

    if channels.ndim != 3 or channels.shape[2] < 1:
        raise ValueError(f"channels must be (B, T, C>=1), got {tuple(channels.shape)}")
    if channels_init is not None and (
        channels_init.ndim != 2 or channels_init.shape != channels.shape[:1] + channels.shape[2:]
    ):
        raise ValueError(
            f"channels_init must be {tuple(channels.shape[:1] + channels.shape[2:])}, "
            f"got {tuple(channels_init.shape)}"
        )
    first = channels_init.unsqueeze(1) if channels_init is not None else torch.zeros_like(channels[:, :1])
    base = torch.cat((first, channels[:, :-1]), dim=1)
    return CoordinateTargets(base=base, abs_targets=channels, inc_targets=channels - base)


def coordinate_state_prediction(
    output: L1CoordinateOutput,
    base: Tensor,
    coordinate: Coordinate,
) -> Tensor:
    """The coordinate arm's channel-STATE prediction ``x̂_{t+1}``.

    ABSOLUTE reads the ABS head directly; INCREMENT lifts the increment decode
    by the observed pre-round base (``x_t + Δx̂_t``) so both arms are compared
    against the same C5 endpoint scale.
    """

    if coordinate is Coordinate.ABSOLUTE:
        return output.abs_channels
    if coordinate is Coordinate.INCREMENT:
        return base.to(output.inc_channels.dtype) + output.inc_channels
    raise ValueError(f"unknown coordinate {coordinate!r}")


# ─────────────────────────────────────────────────────────────────────────────
# C5 supervised rollout-error terms (losses.py dict-of-terms idiom)
# ─────────────────────────────────────────────────────────────────────────────


def l1_supervised_terms(
    output: L1CoordinateOutput,
    targets: CoordinateTargets,
    coordinate: Coordinate,
    channel_scales: Tensor | Sequence[float],
    *,
    distance_mode: str = "mse",
) -> dict[str, Tensor]:
    """Scaled conserving-channel rollout-error terms (contract C5).

    ``channel_scales`` is ``s_ch`` (C,) — the frozen DGP-native per-event
    innovation std of C5; entries must be positive. ``distance_mode``
    dispatches through :func:`ecomd.training.losses.smooth_dev` (``mse`` is
    the C5-faithful default: the squared scaled deviation whose mean is
    ``Y^2``). Returns the ``losses.py`` term-dict shape: per-channel means,
    ``c5_endpoint`` (``sqrt`` of the mean — the exact C5 statistic ``Y`` only
    under ``mse``; reporting surface), and ``_total`` following the
    :func:`multi_fact_terms` convention.
    """

    prediction = coordinate_state_prediction(output, targets.base, coordinate)
    scales = torch.as_tensor(channel_scales, dtype=prediction.dtype, device=prediction.device)
    if scales.ndim != 1 or scales.numel() != prediction.shape[-1]:
        raise ValueError(
            f"channel_scales must have shape ({prediction.shape[-1]},), got {tuple(scales.shape)}"
        )
    if bool((scales <= 0).any()):
        raise ValueError(f"channel_scales must be positive, got {scales.tolist()}")
    truth = targets.abs_targets.to(prediction)

    deviation = smooth_dev(prediction / scales, truth / scales, mode=distance_mode)
    total = deviation.mean()
    terms: dict[str, Tensor] = {
        "_total": total,
        "c5_endpoint": total.clamp_min(0.0).sqrt(),
    }
    for channel in range(deviation.shape[-1]):
        terms[f"channel_{channel}"] = deviation[..., channel].mean()
    return terms


def combine_supervised_and_fact_terms(
    supervised: dict[str, Tensor],
    fact: dict[str, Tensor],
    *,
    w_supervised: float,
) -> dict[str, Tensor]:
    """Merge the supervised terms with :func:`multi_fact_terms` output.

    The composition point demanded by the L1-2 spec: the supervised rollout
    error ADDS to the existing multi-fact path (both ``_total``s sum into
    ``total``); the fact path is never replaced.
    """

    merged = dict(supervised)
    for key, value in fact.items():
        if key != "_total":
            merged[key] = value
    merged["total"] = w_supervised * supervised["_total"] + fact["_total"]
    return merged


# ─────────────────────────────────────────────────────────────────────────────
# RNG-tree bindings (contract C1; simulator contracts 2.4 gaps (i) and (ii))
# ─────────────────────────────────────────────────────────────────────────────


def init_substream_seed(seed_root: int) -> int:
    """The ``spawn(seed, "init")`` seed, from the single shared derivation.

    Equal to ``derive_substream_seeds(seed_root)["init"]`` (the frozen
    ``numpy.random.SeedSequence(root).spawn(20)`` name-order derivation shared
    with L2 and E-2) — there is deliberately no second derivation here.
    """

    return derive_substream_seeds(seed_root)["init"]


def bind_v2_type_seed(config: EcoMDConfig, seed_root: int) -> EcoMDConfig:
    """Opt-in init-substream binding for L1's persistent type labels.

    Returns a NEW config with ``v2_type_seed`` set to the init-substream seed
    of ``seed_root``; the passed config is untouched, and callers that never
    call this keep the existing default (42) behavior — the binding is active
    only through the new supervised training path.
    """

    return dataclass_replace(config, v2_type_seed=init_substream_seed(seed_root))


class MinibatchOrderStream:
    """The shared minibatch-order stream (contract C1/G2, section 2.4 gap (ii)).

    Permutations are drawn solely from a CPU generator seeded by the
    ``spawn(seed, "minibatch")`` substream — no global-RNG consumer. The same
    ``seed_root`` reproduces the identical permutation sequence; replaying
    across lineages within a seed is what makes the stream "shared".
    """

    def __init__(self, generator: torch.Generator) -> None:
        self._generator = generator

    @classmethod
    def from_seed_root(cls, seed_root: int) -> MinibatchOrderStream:
        generator = torch.Generator(device="cpu")
        generator.manual_seed(derive_substream_seeds(seed_root)["minibatch"])
        return cls(generator)

    def next_order(self, n: int) -> Tensor:
        if n < 1:
            raise ValueError(f"n must be >= 1, got {n}")
        return torch.randperm(n, generator=self._generator)


# ─────────────────────────────────────────────────────────────────────────────
# CPU supervised training loop (train.py conventions: Adam, grad clip, records)
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class L1SupervisedTrainConfig:
    """CPU training-loop configuration for the L1 coordinate arms.

    The ``w_*`` fact weights and matching ``*_target`` fields wire
    :func:`multi_fact_terms` exactly as :class:`LossWeights` /
    :class:`MomentTargets` do (a term is active iff its weight > 0 and its
    target is not ``None``). Through-M enforcement (the ``t`` axis of the
    cube) is build item E-3/L1-3a/b and is intentionally absent here.
    """

    n_iters: int = 8
    lr: float = 3e-4
    grad_clip: float = 1.0
    coordinate: Coordinate = Coordinate.INCREMENT
    channel_scales: tuple[float, ...] = (1.0, 1.0)  # s_ch, frozen DGP-native per C5
    distance_mode: str = "mse"
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


def _fact_weights(config: L1SupervisedTrainConfig) -> LossWeights:
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


def _fact_targets(config: L1SupervisedTrainConfig) -> MomentTargets:
    return MomentTargets(
        acf_sq_mean=0.0,
        leverage_sum=0.0,
        hill_alpha=0.0,
        gain_loss_skew=config.gain_loss_skew_target,
        agg_gaussianity=config.agg_gaussianity_target,
        fano=config.fano_target,
        dfa_hurst=config.dfa_hurst_target,
    )


def _shuffled(batch: FactSurrogateBatch, order: Tensor) -> FactSurrogateBatch:
    return FactSurrogateBatch(
        features=batch.features[order],
        channels=batch.channels[order],
        slot_prices=batch.slot_prices[order],
        channels_init=batch.channels_init[order] if batch.channels_init is not None else None,
    )


def train_l1_coordinate_heads(
    model: L1CoordinateHeads,
    batch: FactSurrogateBatch,
    config: L1SupervisedTrainConfig,
    *,
    seed_root: int,
    returns: Tensor | None = None,
) -> list[dict[str, Any]]:
    """CPU supervised training loop for one (coordinate arm, seed) run.

    Every stochastic consumer draws from a named substream of ``seed_root``:
    the minibatch-order permutation from ``minibatch``
    (:class:`MinibatchOrderStream`), and nothing else — decode is
    deterministic (C2(d)) and parameter init is expected to have used the
    ``init`` substream at construction (:func:`init_substream_seed`). The
    same (model construction, ``seed_root``, ``batch``) triple reproduces
    byte-identical training.

    ``returns`` is a precomputed rollout return series ``(n_returns,)`` for
    the multi-fact composition path (the existing L1 objective surface — a
    return series from :class:`ecomd.models.ecomd.EcoMDSimulator` rollouts or
    its target builder); ``None`` disables the fact terms and trains the
    supervised rollout error alone.
    """

    if batch.features.device.type != "cpu":
        raise ValueError("the L1 supervised training loop is CPU-only (PI decision D1_13)")
    if config.n_iters < 1:
        raise ValueError(f"n_iters must be >= 1, got {config.n_iters}")
    weights = _fact_weights(config)
    targets = _fact_targets(config)
    minibatch = MinibatchOrderStream.from_seed_root(seed_root)
    scales = torch.tensor(config.channel_scales, dtype=torch.float32)

    optimizer = torch.optim.Adam(model.parameters(), lr=config.lr)
    history: list[dict[str, Any]] = []
    episodes = batch.features.shape[0]
    for iteration in range(config.n_iters):
        optimizer.zero_grad()
        shuffled = _shuffled(batch, minibatch.next_order(episodes))
        output = model(shuffled)
        coordinate_targets = build_coordinate_targets(shuffled.channels, shuffled.channels_init)
        supervised = l1_supervised_terms(
            output, coordinate_targets, config.coordinate, scales,
            distance_mode=config.distance_mode,
        )
        if returns is not None:
            fact = multi_fact_terms(returns, targets, weights)
        else:
            fact = {"_total": torch.zeros((), dtype=torch.float32)}
        terms = combine_supervised_and_fact_terms(supervised, fact, w_supervised=config.w_supervised)
        total = terms["total"]

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
            "supervised": float(supervised["_total"].item()),
            "c5_endpoint": float(supervised["c5_endpoint"].item()),
            "grad_norm": float(grad_norm.item()),
            "coordinate": config.coordinate.value,
        }
        for key, value in fact.items():
            if key != "_total":
                record[key] = float(value.item())
        history.append(record)
    return history
