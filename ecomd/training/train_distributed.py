"""Distributed training entry point for EcoMD research configurations.

Launched by ``torchrun``; the code is ``world_size``-agnostic.

Parallelism strategy: **data parallelism over training iterations**. Each
rank runs its own complete BPTT chunk with a different seed; at the end of
each iteration, losses and gradients are all-reduced. This is the
standard DDP pattern but wrapped around our custom train_ecomd loop.

Why data-parallel not tensor-parallel:
- Each rank owns a complete rollout and contributes one gradient estimate.
- Independent rank-local generators preserve distinct stochastic paths.
- Tensor parallelism is outside the current implementation.

Checkpointing:
- Every ``checkpoint_every_s`` seconds (default 1800 = 30 min)
- Save: simulator state_dict, optimizer state_dict, scheduler state,
  RNG state, iter index
- W&B resume="allow" if wandb enabled

Usage:
    torchrun --nproc_per_node=4 --standalone \\
        -m ecomd.training.train_distributed \\
        --config experiments/006_ecomd_v1/config_h20.yaml

    # Dry-run single-rank:
    torchrun --nproc_per_node=1 --standalone -m ecomd.training.train_distributed \\
        --config experiments/006_ecomd_v1/config_h20.yaml --smoke
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import random
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
import torch.distributed as dist
import yaml
from torch import Tensor
from torch.amp.autocast_mode import autocast

from ..eval.stylized_facts import log_returns_from_prices
from ..models.ecomd import EcoMDConfig, EcoMDSimulator, SimulatorState
from .losses import LossWeights, MomentTargets, build_targets_from_returns, compute_loss

log = logging.getLogger("train_distributed")

RELEASE_TRAINING_CONTRACT_VERSION = 1


def validate_release_training_contract(
    simulator_config: dict[str, Any],
    training_config: dict[str, Any],
) -> None:
    """Reject configurations that violate the versioned release semantics."""
    errors: list[str] = []
    version = training_config.get("release_contract_version")
    if version != RELEASE_TRAINING_CONTRACT_VERSION:
        errors.append(
            "training.release_contract_version must equal "
            f"{RELEASE_TRAINING_CONTRACT_VERSION}"
        )
    if training_config.get("state_complete") is not True:
        errors.append("training.state_complete must be true")
    if training_config.get("persistent_state") is not True:
        errors.append("training.persistent_state must be explicitly true")
    if simulator_config.get("jump_legacy_train_proxy") is not False:
        errors.append("simulator.jump_legacy_train_proxy must be explicitly false")
    if int(simulator_config.get("bptt_checkpoint_every", 0)) != 0:
        errors.append("simulator.bptt_checkpoint_every must be 0")
    if bool(simulator_config.get("bptt_custom_function", False)):
        errors.append("simulator.bptt_custom_function must be false")
    if errors:
        detail = "\n- ".join(errors)
        raise ValueError(f"EcoMD release training contract violation:\n- {detail}")


# ─────────────────────────────────────────────────────────────────────────────
# Distributed helpers
# ─────────────────────────────────────────────────────────────────────────────


def setup_dist() -> tuple[int, int, int]:
    """Init torch.distributed via torchrun env vars.

    Returns (rank, world_size, local_rank). Works on single-rank too
    (NPROC=1) for Mac dry-run.
    """
    rank = int(os.environ.get("RANK", 0))
    world_size = int(os.environ.get("WORLD_SIZE", 1))
    local_rank = int(os.environ.get("LOCAL_RANK", 0))
    if world_size > 1:
        backend = os.environ.get("DIST_BACKEND", "nccl" if torch.cuda.is_available() else "gloo")
        init_method = os.environ.get("DIST_INIT_METHOD")
        kwargs: dict[str, Any] = {}
        if init_method:
            kwargs["init_method"] = init_method
        dist.init_process_group(
            backend=backend,
            rank=rank,
            world_size=world_size,
            **kwargs,
        )
        if torch.cuda.is_available():
            torch.cuda.set_device(local_rank)
    return rank, world_size, local_rank


def cleanup_dist() -> None:
    if dist.is_available() and dist.is_initialized():
        dist.destroy_process_group()


def _is_main(rank: int) -> bool:
    return rank == 0


def all_reduce_mean(x: torch.Tensor) -> torch.Tensor:
    """All-reduce a scalar tensor, then divide by world_size."""
    if dist.is_available() and dist.is_initialized():
        dist.all_reduce(x, op=dist.ReduceOp.SUM)
        x = x / dist.get_world_size()
    return x


def broadcast_bool(
    value_on_rank_zero: bool,
    *,
    rank: int,
    world_size: int,
    device: torch.device,
) -> bool:
    if world_size <= 1:
        return value_on_rank_zero
    collective_device = (
        device if dist.get_backend() == "nccl" else torch.device("cpu")
    )
    flag = torch.tensor(
        int(value_on_rank_zero if _is_main(rank) else False),
        dtype=torch.int32,
        device=collective_device,
    )
    dist.broadcast(flag, src=0)
    return bool(flag.item())


def broadcast_module_state(module: torch.nn.Module, world_size: int) -> None:
    """Match DDP's initial parameter/buffer broadcast for manual all-reduce."""
    if world_size <= 1:
        return
    for parameter in module.parameters():
        dist.broadcast(parameter.data, src=0)
    for buffer in module.buffers():
        dist.broadcast(buffer.data, src=0)


# ─────────────────────────────────────────────────────────────────────────────
# Data loading (rank 0 loads, broadcasts target tensor scalars to all)
# ─────────────────────────────────────────────────────────────────────────────


def load_spx_returns_any_rank(repo_root: Path) -> np.ndarray:
    return load_yfinance_daily_any_rank(repo_root, "^GSPC")


def load_yfinance_daily_any_rank(
    repo_root: Path, symbol: str,
    year_lo: int | None = None, year_hi: int | None = None,
) -> np.ndarray:
    """Generic yfinance daily loader. Optional year-range filter for crash OOS.

    Looks for `data/raw/yfinance/interval=1d/symbol={symbol}/year=*.parquet`
    (falls back to data/sample/). Returns log returns from adjusted_close
    (or close) prices. ``year_lo`` and ``year_hi`` are inclusive end-points
    on the parquet shard's `year=YYYY` partition; both None = use all.
    """
    for root in (repo_root / "data" / "raw", repo_root / "data" / "sample"):
        d = root / "yfinance" / "interval=1d" / f"symbol={symbol}"
        if d.exists():
            shards = sorted(d.glob("year=*.parquet"))
            # Filter by year if requested
            if year_lo is not None or year_hi is not None:
                kept = []
                for p in shards:
                    yr_str = p.stem.split("=")[-1]
                    try:
                        yr = int(yr_str)
                    except ValueError:
                        continue
                    if year_lo is not None and yr < year_lo:
                        continue
                    if year_hi is not None and yr > year_hi:
                        continue
                    kept.append(p)
                shards = kept
            frames = [pd.read_parquet(p) for p in shards]
            if frames:
                df = pd.concat(frames, ignore_index=True).sort_values("timestamp").reset_index(drop=True)
                col = "adjusted_close" if "adjusted_close" in df.columns else "close"
                return log_returns_from_prices(df[col].to_numpy())
    raise FileNotFoundError(f"no {symbol} yfinance data found in data/raw or data/sample")


def load_binance_1m_returns_any_rank(repo_root: Path, symbol: str) -> np.ndarray:
    for root in (repo_root / "data" / "raw", repo_root / "data" / "sample"):
        d = root / "binance" / "market=spot" / "interval=1m" / f"symbol={symbol}" / "year=2024"
        if d.exists():
            frames = [pd.read_parquet(p) for p in sorted(d.glob("month=*.parquet"))]
            if frames:
                df = pd.concat(frames, ignore_index=True).sort_values("open_time").reset_index(drop=True)
                return log_returns_from_prices(df["close"].to_numpy())
    raise FileNotFoundError(f"no {symbol} Binance data found in data/raw or data/sample")


def load_btc_1m_returns_any_rank(repo_root: Path) -> np.ndarray:
    return load_binance_1m_returns_any_rank(repo_root, "BTCUSDT")


def load_eth_1m_returns_any_rank(repo_root: Path) -> np.ndarray:
    return load_binance_1m_returns_any_rank(repo_root, "ETHUSDT")


_YFINANCE_DAILY_SYMBOL = {
    "spx":         "^GSPC",
    "spy":         "SPY",
    "qqq":         "QQQ",
    "iwm":         "IWM",
    "dax":         "^GDAXI",
    "stoxx50":     "^STOXX50E",
    "hsi":         "^HSI",
    "nikkei":      "^N225",
    "gold":        "GLD",
    "eurusd":      "EURUSD=X",
    "ndx":         "^NDX",
}


def _parse_period(period: str) -> tuple[int | None, int | None]:
    """Return (year_lo, year_hi) inclusive bounds parsed from a period string.

    Supported:
      'daily', '2015-2026_daily', '2015-2019_daily', 'all', '' → (None, None)
      'YYYY-YYYY_daily' → (YYYY, YYYY)
      Otherwise: (None, None) — caller falls back to all data.
    """
    if not period or period in ("daily", "all", "2015-2026_daily"):
        return (None, None)
    body = period.split("_")[0]
    if "-" in body:
        try:
            lo_s, hi_s = body.split("-", 1)
            return (int(lo_s), int(hi_s))
        except ValueError:
            return (None, None)
    return (None, None)


def load_real_returns(repo_root: Path, dataset: str, period: str) -> np.ndarray:
    """Dispatch data loading by target_dataset/target_period fields in config.

    Daily yfinance: `dataset` ∈ {spx, spy, qqq, iwm, dax, stoxx50, hsi,
    nikkei, gold, eurusd}; `period` ∈ {2015-2026_daily, 2015-2019_daily,
    2015-2021_daily, ...}. Period parses to a (year_lo, year_hi) filter
    on the parquet shard partition.

    Crypto 1-minute: `dataset` ∈ {btcusdt, ethusdt}; `period == 2024Q1_1m`.
    """
    # Daily yfinance dispatch
    if dataset in _YFINANCE_DAILY_SYMBOL:
        symbol = _YFINANCE_DAILY_SYMBOL[dataset]
        if period.endswith("_daily") or period in ("daily", "all"):
            year_lo, year_hi = _parse_period(period)
            return load_yfinance_daily_any_rank(repo_root, symbol,
                                                 year_lo=year_lo, year_hi=year_hi)
        raise ValueError(
            f"unsupported period {period!r} for daily dataset {dataset!r}; "
            "expected '*_daily', 'daily', or 'all'"
        )
    # Crypto 1m dispatch (existing)
    if dataset == "btcusdt" and period == "2024Q1_1m":
        return load_btc_1m_returns_any_rank(repo_root)
    if dataset == "ethusdt" and period == "2024Q1_1m":
        return load_eth_1m_returns_any_rank(repo_root)
    raise ValueError(
        f"unsupported target dataset/period combination: dataset={dataset!r}, "
        f"period={period!r}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Checkpoint
# ─────────────────────────────────────────────────────────────────────────────


CHECKPOINT_FORMAT_VERSION = 2


def _optimizer_to(
    optim: torch.optim.Optimizer,
    device: torch.device,
) -> None:
    for state in optim.state.values():
        for key, value in state.items():
            if isinstance(value, Tensor):
                state[key] = value.to(device=device)


def capture_rank_runtime(
    *,
    rank: int,
    simulator_state: SimulatorState,
    generator: torch.Generator,
    auxiliary_generator: torch.Generator,
    history: list[dict[str, Any]],
    device: torch.device,
) -> dict[str, Any]:
    """Capture one rank's exact continuation state on CPU."""
    if simulator_state.rng_state is None:
        raise ValueError("state-complete checkpoint requires SimulatorState.rng_state")
    generator_state = generator.get_state().detach().cpu().clone()
    if not torch.equal(simulator_state.rng_state.detach().cpu(), generator_state):
        raise RuntimeError(
            "SimulatorState RNG and explicit rollout generator diverged before checkpoint"
        )
    return {
        "rank": rank,
        "simulator_state": simulator_state.detached().to("cpu").to_checkpoint(),
        "generator_state": generator_state,
        "auxiliary_generator_state": (
            auxiliary_generator.get_state().detach().cpu().clone()
        ),
        "torch_cpu_rng_state": torch.get_rng_state().detach().cpu().clone(),
        "torch_cuda_rng_state": (
            torch.cuda.get_rng_state(device).detach().cpu().clone()
            if device.type == "cuda"
            else None
        ),
        "numpy_rng_state": np.random.get_state(),
        "python_rng_state": random.getstate(),
        "history": list(history),
    }


def restore_rank_runtime(
    runtime: dict[str, Any],
    *,
    rank: int,
    generator: torch.Generator,
    auxiliary_generator: torch.Generator,
    device: torch.device,
) -> tuple[SimulatorState, list[dict[str, Any]]]:
    """Restore one rank's exact continuation state and all RNG streams."""
    if int(runtime.get("rank", -1)) != rank:
        raise ValueError(
            f"checkpoint runtime rank={runtime.get('rank')} cannot restore rank={rank}"
        )
    generator.set_state(runtime["generator_state"].detach().cpu())
    auxiliary_generator.set_state(
        runtime["auxiliary_generator_state"].detach().cpu()
    )
    torch.set_rng_state(runtime["torch_cpu_rng_state"].detach().cpu())
    if device.type == "cuda":
        cuda_state = runtime.get("torch_cuda_rng_state")
        if cuda_state is None:
            raise ValueError("CUDA resume requires a saved local CUDA RNG state")
        torch.cuda.set_rng_state(cuda_state.detach().cpu(), device=device)
    np.random.set_state(runtime["numpy_rng_state"])
    random.setstate(runtime["python_rng_state"])
    simulator_state = SimulatorState.from_checkpoint(
        runtime["simulator_state"]
    ).to(device)
    return simulator_state, list(runtime.get("history", []))


def gather_rank_runtimes(
    local_runtime: dict[str, Any],
    *,
    rank: int,
    world_size: int,
) -> list[dict[str, Any]] | None:
    """Collect CPU runtime records on rank zero in rank order."""
    if world_size <= 1:
        return [local_runtime]
    gathered: list[dict[str, Any] | None] | None = (
        [None] * world_size if _is_main(rank) else None
    )
    dist.gather_object(local_runtime, gathered, dst=0)
    if gathered is None:
        return None
    if any(item is None for item in gathered):
        raise RuntimeError("distributed checkpoint gather returned a missing rank")
    runtimes = [item for item in gathered if item is not None]
    runtimes.sort(key=lambda item: int(item["rank"]))
    return runtimes


def _atomic_torch_save(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    torch.save(payload, temporary)
    os.replace(temporary, path)


def save_checkpoint(
    path: Path,
    *,
    sim: EcoMDSimulator,
    optim: torch.optim.Optimizer,
    iter_idx: int,
    targets: MomentTargets | list[tuple[str, MomentTargets, float]],
    sim_config: dict[str, Any],
    train_config: dict[str, Any],
    world_size: int = 1,
    state_complete: bool = False,
    rank_runtimes: list[dict[str, Any]] | None = None,
) -> None:
    if isinstance(targets, MomentTargets):
        targets_serialised: Any = asdict(targets)
    else:
        targets_serialised = [
            {"label": lbl, "targets": asdict(t), "weight": w}
            for lbl, t, w in targets
        ]
    if state_complete:
        if rank_runtimes is None or len(rank_runtimes) != world_size:
            raise ValueError(
                "state-complete checkpoint requires one runtime per rank: "
                f"got {0 if rank_runtimes is None else len(rank_runtimes)}, "
                f"expected {world_size}"
            )
        observed_ranks = {int(runtime["rank"]) for runtime in rank_runtimes}
        expected_ranks = set(range(world_size))
        if observed_ranks != expected_ranks:
            raise ValueError(
                f"runtime ranks {sorted(observed_ranks)} != {sorted(expected_ranks)}"
            )
    payload = {
        "format_version": CHECKPOINT_FORMAT_VERSION,
        "iter_idx": iter_idx,
        "world_size": world_size,
        "state_complete": state_complete,
        "sim_state_dict": sim.state_dict(),
        "optim_state_dict": optim.state_dict(),
        "rank_runtimes": rank_runtimes,
        "targets": targets_serialised,
        "sim_config": sim_config,
        "train_config": train_config,
    }
    _atomic_torch_save(payload, path)


def try_load_checkpoint(
    path: Path,
    *,
    sim: EcoMDSimulator,
    optim: torch.optim.Optimizer,
    rank: int = 0,
    world_size: int = 1,
    state_complete: bool = False,
    device: torch.device | None = None,
) -> tuple[int, dict[str, Any] | None, bool]:
    if not path.exists():
        return 0, None, False
    ckpt = torch.load(path, map_location="cpu", weights_only=False)
    sim.load_state_dict(ckpt["sim_state_dict"])
    optim.load_state_dict(ckpt["optim_state_dict"])
    _optimizer_to(optim, device or sim.device)
    version = int(ckpt.get("format_version", 1))
    if version == 1:
        if state_complete:
            raise ValueError(
                "legacy format-v1 checkpoint has no per-rank simulator/RNG state"
            )
        return int(ckpt["iter_idx"]), None, False
    if version != CHECKPOINT_FORMAT_VERSION:
        raise ValueError(f"unsupported checkpoint format_version={version}")
    saved_world_size = int(ckpt.get("world_size", -1))
    if saved_world_size != world_size:
        raise ValueError(
            f"checkpoint world_size={saved_world_size} != current world_size={world_size}"
        )
    saved_state_complete = bool(ckpt.get("state_complete", False))
    if saved_state_complete != state_complete:
        raise ValueError(
            "checkpoint state_complete="
            f"{saved_state_complete} != requested state_complete={state_complete}"
        )
    if not state_complete:
        return int(ckpt["iter_idx"]), None, False
    runtimes = ckpt.get("rank_runtimes")
    if not isinstance(runtimes, list) or len(runtimes) != world_size:
        raise ValueError("checkpoint is missing a complete rank runtime list")
    by_rank = {int(runtime["rank"]): runtime for runtime in runtimes}
    if set(by_rank) != set(range(world_size)):
        raise ValueError("checkpoint rank runtime IDs do not match world size")
    return int(ckpt["iter_idx"]), by_rank[rank], True


# ─────────────────────────────────────────────────────────────────────────────
# Rollout regularization (057) — long-horizon SF supervision
# ─────────────────────────────────────────────────────────────────────────────


def _compute_rollout_reg_loss(
    sim: EcoMDSimulator,
    targets_list: list[tuple[str, MomentTargets, float]],
    weights: LossWeights,
    gen: torch.Generator,
    *,
    steps: int,
    chunk: int,
    warmup_steps: int,
    use_amp: bool,
    amp_device_type: str,
    amp_dtype: torch.dtype,
    target_returns_map: dict[str, Tensor] | None = None,
    state_complete: bool = False,
) -> Tensor | None:
    """Multi-chunk truncated-BPTT rollout from fresh init, with SF loss
    computed on the concatenated returns. State is detached at each chunk
    boundary, but all chunk graphs remain reachable from the concatenated
    loss until backward; activation memory therefore grows with the number
    of chunks.

    Returns the SF loss (already in fp32) or None if no usable returns.
    """
    simulator_state = (
        sim.init_simulator_state(generator=gen) if state_complete else None
    )
    if not state_complete:
        s = sim.init_state(generator=gen)
        s_prev = s.detach().clone()
        price_state = sim.init_price()
        h_regime = sim.init_regime()

    all_returns: list[Tensor] = []
    n_done = 0
    while n_done < steps:
        n_step = min(chunk, steps - n_done)
        with autocast(device_type=amp_device_type, dtype=amp_dtype, enabled=use_amp):
            if state_complete:
                if simulator_state is None:
                    raise RuntimeError("missing state-complete rollout state")
                simulator_state, traj = sim.rollout_state(
                    simulator_state,
                    n_steps=n_step,
                    generator=gen,
                    create_graph=True,
                )
            else:
                s_new, price_state_new, traj, h_regime_new = sim.rollout_chunk(
                    s, s_prev, price_state,
                    n_steps=n_step, generator=gen, create_graph=True,
                    h_regime=h_regime,
                )
        # Skip warmup only at the very first chunk (state is fresh-init).
        # Subsequent chunks have a state that's continuous from prior chunks.
        start = 1 + min(warmup_steps, max(0, n_step - 4)) if n_done == 0 else 1
        if start < traj.log_returns.shape[0]:
            all_returns.append(traj.log_returns[start:])
        # Detach state at boundary — gradient barrier between chunks.
        if state_complete:
            if simulator_state is None:
                raise RuntimeError("missing state-complete rollout state")
            simulator_state = simulator_state.detached()
        else:
            s = s_new.detach()
            s_prev = traj.states[-2].detach() if n_step >= 2 else s_new.detach()
            from .train import _detach_price

            price_state = _detach_price(price_state_new)
            h_regime = h_regime_new.detach() if h_regime_new is not None else None
        n_done += n_step

    if not all_returns:
        return None
    sim_returns = torch.cat(all_returns, dim=0)
    if use_amp:
        sim_returns = sim_returns.float()

    total = None
    for lbl, ts, w in targets_list:
        # compute_loss fast-paths to moment_matching_loss for the legacy
        # (moments/l1/soft_hill) combo → bit-exact; otherwise honours
        # distance_mode / multi-fact weights. This long rollout is the ONLY
        # site where the distribution-distance families (mmd/wasserstein/
        # sinkhorn, exp 104) get enough samples, so the real series is threaded
        # here via target_returns_map; moments runs leave it None (ignored).
        tr = target_returns_map.get(lbl) if target_returns_map else None
        out = compute_loss(sim_returns, tr, ts, weights)
        term = w * out["total"]
        total = term if total is None else (total + term)
    return total


# ─────────────────────────────────────────────────────────────────────────────
# Training loop (data-parallel)
# ─────────────────────────────────────────────────────────────────────────────


def train_distributed(
    sim: EcoMDSimulator,
    targets: MomentTargets | list[tuple[str, MomentTargets, float]],
    weights: LossWeights,
    *,
    n_iters: int,
    chunk_steps: int,
    lr: float,
    grad_clip: float,
    seed: int,
    persistent_state: bool,
    warmup_steps: int,
    lr_warmup_iters: int,
    rank: int,
    world_size: int,
    checkpoint_path: Path | None,
    checkpoint_every_s: float,
    mixed_precision: str = "fp32",
    rollout_reg_cfg: dict[str, Any] | None = None,
    target_returns_map: dict[str, Tensor] | None = None,
    state_complete: bool = False,
    sim_config: dict[str, Any] | None = None,
    train_config: dict[str, Any] | None = None,
    stop_after_iter: int | None = None,
) -> list[dict[str, Any]]:
    """Each rank runs train_ecomd-style iterations with its own seed.

    Gradients are all-reduced after each iter's backward. Loss metrics
    logged here are per-rank (mean over world reduced separately for
    printing).

    Multi-asset training: ``targets`` may be a single MomentTargets
    (backwards-compatible single-asset path) OR a list of
    (label, MomentTargets, weight) tuples (joint training across assets).
    In the multi-asset case, each iter does ONE rollout and computes a
    weighted-sum loss against all assets' targets — the simulator learns
    a Pareto-compromise distribution that minimises avg deviation across
    markets.
    """
    # Normalise targets into list-of-tuples for uniform handling
    if isinstance(targets, MomentTargets):
        targets_list: list[tuple[str, MomentTargets, float]] = [("default", targets, 1.0)]
    else:
        targets_list = list(targets)
        # normalise weights to sum to 1
        total_w = sum(w for _, _, w in targets_list)
        if total_w > 0:
            targets_list = [(lbl, t, w / total_w) for lbl, t, w in targets_list]

    device = sim.device
    broadcast_module_state(sim, world_size)
    optim = torch.optim.Adam(sim.parameters(), lr=lr)
    if state_complete and int(getattr(sim.cfg, "bptt_checkpoint_every", 0)) > 0:
        raise NotImplementedError(
            "state-complete distributed training does not yet support grouped "
            "BPTT checkpointing"
        )
    if state_complete and bool(getattr(sim.cfg, "bptt_custom_function", False)):
        raise NotImplementedError(
            "state-complete distributed training does not yet support the custom "
            "autograd step"
        )

    # fp16 needs GradScaler (not implemented); bf16 needs no scaler because
    # its exponent range matches fp32.
    use_amp = mixed_precision in ("bf16", "bfloat16")
    amp_dtype = torch.bfloat16 if use_amp else torch.float32
    amp_device_type = "cuda" if device.type == "cuda" else "cpu"
    if use_amp and _is_main(rank):
        log.info(f"[amp] mixed_precision={mixed_precision} dtype={amp_dtype} device={amp_device_type}")

    start_iter = 0
    saved_runtime: dict[str, Any] | None = None
    exact_resume = False
    if checkpoint_path is not None:
        start_iter, saved_runtime, exact_resume = try_load_checkpoint(
            checkpoint_path,
            sim=sim,
            optim=optim,
            rank=rank,
            world_size=world_size,
            state_complete=state_complete,
            device=device,
        )
        if start_iter > 0 and _is_main(rank):
            log.info(
                f"[rank 0] resumed from {checkpoint_path} at iter {start_iter} "
                f"exact={exact_resume}"
            )

    # Each rank gets a distinct seed so independent trajectories are explored
    gen = torch.Generator(device=device)
    auxiliary_gen = torch.Generator(device=device)
    rank_seed = seed + rank * 10000
    gen.manual_seed(rank_seed if state_complete else rank_seed + start_iter)
    auxiliary_gen.manual_seed(rank_seed + 5_000_000)
    if saved_runtime is None:
        torch.manual_seed(rank_seed)
        if device.type == "cuda":
            torch.cuda.manual_seed(rank_seed)
        np.random.seed(rank_seed % (2**32))
        random.seed(rank_seed)

    history: list[dict[str, Any]] = []
    simulator_state: SimulatorState | None = None
    if state_complete:
        if saved_runtime is not None:
            simulator_state, history = restore_rank_runtime(
                saved_runtime,
                rank=rank,
                generator=gen,
                auxiliary_generator=auxiliary_gen,
                device=device,
            )
            if history and int(history[-1]["iter"]) != start_iter - 1:
                raise ValueError(
                    "checkpoint history does not end at the saved iteration"
                )
        elif persistent_state:
            simulator_state = sim.init_simulator_state(generator=gen)
    else:
        s = sim.init_state(generator=gen)
        s_prev = s.detach().clone()
        price_state = sim.init_price()
        h_regime = sim.init_regime()

    last_ckpt_time = time.time()

    from .scheduled_sampling import state_from_config
    from .train import _detach_price, _lr_factor

    ss_state = state_from_config(sim.cfg)
    if ss_state is not None and _is_main(rank):
        log.info(
            f"[ss] scheduled sampling enabled: max_prob={ss_state.max_prob} "
            f"sigma_mult={ss_state.sigma_mult} ramp={ss_state.ramp_schedule} "
            f"warmup_iters={ss_state.warmup_iters}"
        )

    end_iter = n_iters if stop_after_iter is None else min(n_iters, stop_after_iter)
    if end_iter < start_iter:
        raise ValueError(
            f"stop_after_iter={end_iter} precedes resumed iteration {start_iter}"
        )
    for it in range(start_iter, end_iter):
        lr_factor = _lr_factor(it, n_iters, lr_warmup_iters)
        for g in optim.param_groups:
            g["lr"] = lr * lr_factor

        optim.zero_grad()

        if state_complete:
            if not persistent_state or simulator_state is None:
                simulator_state = sim.init_simulator_state(generator=gen)
            else:
                simulator_state = simulator_state.detached()
            ss_prob = ss_state.get_prob(it) if ss_state is not None else 0.0
            ss_sigma_mult = ss_state.sigma_mult if ss_state is not None else 1.0
            with autocast(
                device_type=amp_device_type,
                dtype=amp_dtype,
                enabled=use_amp,
            ):
                simulator_state, traj = sim.rollout_state(
                    simulator_state,
                    n_steps=chunk_steps,
                    generator=gen,
                    create_graph=True,
                    ss_prob=ss_prob,
                    ss_sigma_mult=ss_sigma_mult,
                )
            s = simulator_state.s
        else:
            if not persistent_state:
                s = sim.init_state(generator=gen)
                s_prev = s.detach().clone()
                price_state = sim.init_price()
                h_regime = sim.init_regime()
            else:
                s = s.detach()
                s_prev = s_prev.detach()
                price_state = _detach_price(price_state)
                if h_regime is not None:
                    h_regime = h_regime.detach()

            ss_prob = ss_state.get_prob(it) if ss_state is not None else 0.0
            ss_sigma_mult = ss_state.sigma_mult if ss_state is not None else 1.0
            with autocast(
                device_type=amp_device_type,
                dtype=amp_dtype,
                enabled=use_amp,
            ):
                s, price_state, traj, h_regime = sim.rollout_chunk(
                    s,
                    s_prev,
                    price_state,
                    n_steps=chunk_steps,
                    generator=gen,
                    create_graph=True,
                    h_regime=h_regime,
                    ss_prob=ss_prob,
                    ss_sigma_mult=ss_sigma_mult,
                )
        # When BPTT checkpointing is on, the generator's state gets rewound
        # by recompute on backward. Snapshot the post-forward state here and
        # restore it after backward to keep the noise stream coherent across
        # iterations.
        bptt_k = int(getattr(sim.cfg, "bptt_checkpoint_every", 0))
        gen_state_after_forward = (
            gen.get_state().clone()
            if (not state_complete and bptt_k > 0 and gen is not None)
            else None
        )

        if not state_complete:
            s_prev = traj.states[-2].detach() if chunk_steps >= 2 else s.detach()

        start = 1 + warmup_steps
        if start >= traj.log_returns.shape[0]:
            start = max(1, traj.log_returns.shape[0] - 4)
        sim_returns = traj.log_returns[start:]

        # Multi-asset weighted-sum loss. Loss kept in fp32 — autocast
        # promotes back automatically on the cross-entropy / MSE-like ops,
        # but we explicitly cast sim_returns to fp32 first to avoid bf16
        # precision loss in the moment statistics.
        if use_amp:
            sim_returns = sim_returns.float()
        per_asset_outs: dict[str, dict[str, Tensor]] = {}
        total: Tensor | None = None
        out: dict[str, Tensor] = {}
        for lbl, ts, w in targets_list:
            out_a = compute_loss(sim_returns, None, ts, weights)
            per_asset_outs[lbl] = out_a
            term = w * out_a["total"]
            total = term if total is None else (total + term)
        if total is None:
            raise ValueError("training requires at least one target")
        # For logging, expose per-asset acf_sim/leverage_sim/hill_sim under the
        # default-asset name so existing log readers still work; also store
        # all assets as <metric>_<label>.
        # In single-asset mode (targets_list len 1), out is the per-asset dict.
        first_lbl = targets_list[0][0]
        out = dict(per_asset_outs[first_lbl])  # acf_sim etc. from first asset
        out["total"] = total

        # Long-horizon rollout regularization (057): every K iters, compute
        # SF loss over a fresh-init multi-chunk rollout. State gradients stop
        # at each boundary, but the concatenated loss retains every chunk's
        # activation graph until backward. Goal: reduce the train/eval horizon
        # mismatch by giving the model supervision on a longer trajectory.
        reg_loss_val = 0.0
        if rollout_reg_cfg and rollout_reg_cfg.get("enabled") and \
                (it % max(1, rollout_reg_cfg.get("every", 5)) == 0):
            reg_steps = int(rollout_reg_cfg["steps"])
            reg_chunk = int(rollout_reg_cfg["chunk"])
            reg_weight = float(rollout_reg_cfg["weight"])
            reg_total = _compute_rollout_reg_loss(
                sim, targets_list, weights,
                auxiliary_gen if state_complete else gen,
                steps=reg_steps, chunk=reg_chunk, warmup_steps=warmup_steps,
                use_amp=use_amp, amp_device_type=amp_device_type,
                amp_dtype=amp_dtype, target_returns_map=target_returns_map,
                state_complete=state_complete,
            )
            if reg_total is not None:
                total = total + reg_weight * reg_total
                reg_loss_val = float(reg_total.detach().item())

        # exp 110 — MoE expert load-balance regularizer (anti-collapse). Evaluated
        # on the current state; gradient flows to router params directly.
        moe_lb = getattr(sim, "moe_load_balance", None)
        if moe_lb is not None:
            lb = moe_lb(s.detach())
            if lb is not None:
                w_lb = float(getattr(sim.cfg, "moe_load_balance_w", 0.0))
                total = total + w_lb * lb

        torch.autograd.backward(total)

        # Post-backward: restore the generator state to where forward ended.
        # Without this, with BPTT checkpointing on, gen would be rewound by
        # the recompute pass and the next iter's noise stream would diverge
        # from the no-checkpoint baseline.
        if gen_state_after_forward is not None and gen is not None:
            gen.set_state(gen_state_after_forward)

        # All-reduce gradients across ranks (standard DDP-style mean)
        if world_size > 1:
            for p in sim.parameters():
                if p.grad is not None:
                    dist.all_reduce(p.grad.data, op=dist.ReduceOp.SUM)
                    p.grad.data /= world_size

        with torch.no_grad():
            grad_sq = torch.tensor(0.0, device=device)
            for p in sim.parameters():
                if p.grad is not None:
                    grad_sq = grad_sq + p.grad.detach().pow(2).sum()
            grad_norm = grad_sq.sqrt()
        torch.nn.utils.clip_grad_norm_(sim.parameters(), grad_clip)
        optim.step()

        # Reduced-across-ranks loss for logging
        total_mean = all_reduce_mean(total.detach().clone())

        rec = {
            "iter": it,
            "lr": lr * lr_factor,
            "total_rank0": float(total.item()),
            "total_world_mean": float(total_mean.item()),
            "acf_sim": float(out["acf_sim"].item()),
            "leverage_sim": float(out["leverage_sim"].item()),
            "hill_sim": float(out["hill_sim"].item()),
            "grad_norm": float(grad_norm.item()),
            "gamma": float(sim.gamma.item()),
            "temperature": float(sim.temperature.item()),
            "reg_loss": reg_loss_val,
        }
        history.append(rec)

        if _is_main(rank) and (it == start_iter or (it + 1) % max(1, n_iters // 20) == 0):
            log.info(
                f"it={it:4d} lr={rec['lr']:.2e} loss_world={rec['total_world_mean']:.4f} "
                f"grad={rec['grad_norm']:.2e} gamma={rec['gamma']:.3f} "
                f"T={rec['temperature']:.4f}"
            )

        # Checkpoint
        now = time.time()
        checkpoint_due = checkpoint_path is not None and (
            _is_main(rank) and (now - last_ckpt_time) > checkpoint_every_s
        )
        checkpoint_due = broadcast_bool(
            checkpoint_due,
            rank=rank,
            world_size=world_size,
            device=device,
        )
        if checkpoint_path is not None and checkpoint_due:
            rank_runtimes = None
            if state_complete:
                if simulator_state is None:
                    raise RuntimeError("missing simulator state at checkpoint boundary")
                local_runtime = capture_rank_runtime(
                    rank=rank,
                    simulator_state=simulator_state,
                    generator=gen,
                    auxiliary_generator=auxiliary_gen,
                    history=history,
                    device=device,
                )
                rank_runtimes = gather_rank_runtimes(
                    local_runtime,
                    rank=rank,
                    world_size=world_size,
                )
            if _is_main(rank):
                save_checkpoint(
                    checkpoint_path,
                    sim=sim,
                    optim=optim,
                    iter_idx=it + 1,
                    targets=targets,
                    sim_config=sim_config or {},
                    train_config=train_config or {},
                    world_size=world_size,
                    state_complete=state_complete,
                    rank_runtimes=rank_runtimes,
                )
                log.info(
                    f"[rank 0] checkpointed to {checkpoint_path} at iter {it + 1}"
                )
            last_ckpt_time = now

    # Final checkpoint
    if checkpoint_path is not None:
        rank_runtimes = None
        if state_complete:
            if simulator_state is None:
                raise RuntimeError("missing simulator state at final checkpoint")
            local_runtime = capture_rank_runtime(
                rank=rank,
                simulator_state=simulator_state,
                generator=gen,
                auxiliary_generator=auxiliary_gen,
                history=history,
                device=device,
            )
            rank_runtimes = gather_rank_runtimes(
                local_runtime,
                rank=rank,
                world_size=world_size,
            )
        if _is_main(rank):
            save_checkpoint(
                checkpoint_path,
                sim=sim,
                optim=optim,
                iter_idx=end_iter,
                targets=targets,
                sim_config=sim_config or {},
                train_config=train_config or {},
                world_size=world_size,
                state_complete=state_complete,
                rank_runtimes=rank_runtimes,
            )

    return history


# ─────────────────────────────────────────────────────────────────────────────
# Main entry
# ─────────────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--out-dir", default=None,
                        help="override config's out_dir (default: experiments/<exp>/results)")
    parser.add_argument("--smoke", action="store_true",
                        help="tiny run (3 iters) for dry-run validation")
    parser.add_argument("--resume", action="store_true",
                        help="resume from checkpoint in out_dir if present")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

    rank, world_size, local_rank = setup_dist()
    if _is_main(rank):
        log.info(f"[dist] rank={rank} world_size={world_size} local_rank={local_rank} "
                 f"cuda_available={torch.cuda.is_available()}")

    cfg = yaml.safe_load(Path(args.config).read_text())
    sim_cfg_dict = dict(cfg["simulator"])
    train_cfg = dict(cfg["training"])

    if "release_contract_version" in train_cfg:
        validate_release_training_contract(sim_cfg_dict, train_cfg)
    elif not bool(train_cfg.get("state_complete", False)) and _is_main(rank):
        log.warning(
            "legacy state-incomplete training path enabled; this run is not eligible "
            "for a model release"
        )

    if args.smoke:
        train_cfg["n_iters"] = min(train_cfg["n_iters"], 3)
        train_cfg["chunk_steps"] = min(train_cfg["chunk_steps"], 16)
        if _is_main(rank):
            log.info("SMOKE MODE — overriding n_iters=3 chunk=16")

    config_path = Path(args.config).resolve()
    exp_dir = config_path.parent
    out_dir = Path(args.out_dir) if args.out_dir else exp_dir / "results"
    if _is_main(rank):
        out_dir.mkdir(parents=True, exist_ok=True)

    repo_root = Path(__file__).resolve().parents[2]

    # Build targets (each rank loads independently — data is small).
    # Multi-asset: train_cfg["joint_assets"] is a list of dicts with
    # {dataset, period, weight}. If absent, fall back to single
    # target_dataset/target_period.
    weights = LossWeights(**train_cfg["loss_weights"])
    # Raw real-return series per asset label, threaded into the long rollout-reg
    # so distribution-distance losses (mmd/wasserstein/sinkhorn, exp 104) have a
    # target. None for moments-family runs (compute_loss ignores it there).
    target_returns_map: dict[str, Tensor] = {}
    joint_assets = train_cfg.get("joint_assets")
    if joint_assets:
        targets_list: list[tuple[str, MomentTargets, float]] = []
        for asset_cfg in joint_assets:
            ds = asset_cfg["dataset"]
            pd_ = asset_cfg.get("period", "daily")
            w = float(asset_cfg.get("weight", 1.0))
            real_r = load_real_returns(repo_root, ds, pd_)
            ts = build_targets_from_returns(
                real_r, max_lag=weights.max_lag, k_frac=weights.hill_k_frac,
                agg_gauss_scale_large=weights.agg_gauss_scale_large,
                fano_quantile=weights.fano_quantile, fano_n_windows=weights.fano_n_windows,
                dfa_min_scale=weights.dfa_min_scale, dfa_max_scale_frac=weights.dfa_max_scale_frac,
            )
            label = f"{ds}/{pd_}"
            targets_list.append((label, ts, w))
            target_returns_map[label] = torch.as_tensor(real_r, dtype=torch.float32)
            if _is_main(rank):
                log.info(f"[multi-asset] {label}: n={len(real_r):,}  "
                         f"acf_sq={ts.acf_sq_mean:+.3f}  lev={ts.leverage_sum:+.3f}  "
                         f"hill={ts.hill_alpha:.2f}  weight={w}")
        targets: MomentTargets | list[tuple[str, MomentTargets, float]] = targets_list
    else:
        target_dataset = train_cfg.get("target_dataset", "spx")
        target_period = train_cfg.get("target_period", "daily")
        real_r = load_real_returns(repo_root, target_dataset, target_period)
        if _is_main(rank):
            log.info(f"loaded {len(real_r):,} returns for {target_dataset}/{target_period}")
        targets = build_targets_from_returns(
            real_r, max_lag=weights.max_lag, k_frac=weights.hill_k_frac,
            agg_gauss_scale_large=weights.agg_gauss_scale_large,
            fano_quantile=weights.fano_quantile, fano_n_windows=weights.fano_n_windows,
            dfa_min_scale=weights.dfa_min_scale, dfa_max_scale_frac=weights.dfa_max_scale_frac,
        )
        target_returns_map["default"] = torch.as_tensor(real_r, dtype=torch.float32)
        if _is_main(rank):
            log.info(f"targets: acf_sq={targets.acf_sq_mean:.3f} "
                     f"leverage_sum={targets.leverage_sum:+.3f} "
                     f"hill_alpha={targets.hill_alpha:.2f}")

    # Build simulator
    simulator_config = EcoMDConfig(**sim_cfg_dict)
    torch.manual_seed(train_cfg["seed"])
    sim = EcoMDSimulator(simulator_config)
    if torch.cuda.is_available():
        sim = sim.cuda(local_rank)

    if _is_main(rank):
        n_params = sum(p.numel() for p in sim.parameters())
        log.info(f"EcoMDSimulator built: {n_params} parameters (device={sim.device})")

    checkpoint_path = out_dir / "checkpoint.pt" if args.resume or not args.smoke else None

    t0 = time.time()
    history = train_distributed(
        sim, targets, weights,
        n_iters=train_cfg["n_iters"],
        chunk_steps=train_cfg["chunk_steps"],
        lr=train_cfg["lr"],
        grad_clip=train_cfg["grad_clip_max_norm"],
        seed=train_cfg["seed"],
        persistent_state=train_cfg.get("persistent_state", True),
        warmup_steps=train_cfg.get("warmup_steps", 0),
        lr_warmup_iters=train_cfg.get("lr_warmup_iters", 0),
        rank=rank,
        world_size=world_size,
        checkpoint_path=checkpoint_path,
        checkpoint_every_s=train_cfg.get("checkpoint_every_s", 1800.0),
        mixed_precision=train_cfg.get("mixed_precision", "fp32"),
        rollout_reg_cfg={
            "enabled": bool(train_cfg.get("rollout_reg_enabled", False)),
            "steps": int(train_cfg.get("rollout_reg_steps", 100)),
            "chunk": int(train_cfg.get("rollout_reg_chunk", 24)),
            "weight": float(train_cfg.get("rollout_reg_weight", 0.1)),
            "every": int(train_cfg.get("rollout_reg_every", 5)),
        },
        target_returns_map=target_returns_map,
        state_complete=bool(train_cfg.get("state_complete", False)),
        sim_config=sim_cfg_dict,
        train_config=train_cfg,
    )
    t_total = time.time() - t0

    # Peak HBM profile (CUDA only) — helps calibrate memory model for
    # configs across (N, chunk_steps, K). Captured per-rank; rank 0
    # writes to training_log.
    peak_hbm: dict[str, float] = {}
    if torch.cuda.is_available():
        try:
            dev = sim.device
            peak_hbm["alloc_gb"] = float(torch.cuda.max_memory_allocated(dev) / (1024 ** 3))
            peak_hbm["reserved_gb"] = float(torch.cuda.max_memory_reserved(dev) / (1024 ** 3))
        except Exception:
            pass

    if _is_main(rank):
        log.info(f"training finished in {t_total:.1f}s ({len(history)} iters, world_size={world_size})")
        if peak_hbm:
            log.info(f"[rank 0] peak HBM: alloc={peak_hbm.get('alloc_gb', 0):.2f} GB, "
                     f"reserved={peak_hbm.get('reserved_gb', 0):.2f} GB")
        if isinstance(targets, MomentTargets):
            targets_dump: Any = asdict(targets)
        else:
            targets_dump = [
                {"label": lbl, "targets": asdict(t), "weight": w}
                for lbl, t, w in targets
            ]
        (out_dir / "training_log.json").write_text(json.dumps({
            "config": {"simulator": sim_cfg_dict, "training": train_cfg},
            "targets": targets_dump,
            "history": history,
            "train_time_seconds": t_total,
            "world_size": world_size,
            "peak_hbm": peak_hbm,
        }, indent=2))
        log.info(f"[rank 0] wrote {out_dir}/training_log.json")

    cleanup_dist()


if __name__ == "__main__":
    main()
