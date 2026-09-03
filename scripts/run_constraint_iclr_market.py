"""Run the corrected FIFO market family in the frozen ICLR constraint audit."""

from __future__ import annotations

import json
import time
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import hydra
import numpy as np
import torch
from constraint_iclr_common import (
    SCHEMA_VERSION,
    append_jsonl,
    canonical_run_id,
    count_trainable_parameters,
    provenance,
    seed_everything,
    stable_seed,
    validate_selection_lock,
)
from omegaconf import DictConfig, OmegaConf
from torch import nn

Side = Literal["buy", "sell"]


@dataclass(frozen=True)
class Order:
    agent: int
    side: Side
    price: float
    sequence: int


@dataclass(frozen=True)
class Trade:
    buyer: int
    seller: int
    price: float
    maker: int
    taker: int


class FIFOBook:
    """Unit-quantity price-time-priority limit order book."""

    def __init__(self) -> None:
        self.bids: list[Order] = []
        self.asks: list[Order] = []

    def cancel(self, agent: int, side: Side) -> None:
        target = self.bids if side == "buy" else self.asks
        target[:] = [order for order in target if order.agent != agent]

    def best_bid(self) -> Order | None:
        return min(self.bids, key=lambda order: (-order.price, order.sequence), default=None)

    def best_ask(self) -> Order | None:
        return min(self.asks, key=lambda order: (order.price, order.sequence), default=None)

    def submit(self, order: Order) -> Trade | None:
        self.cancel(order.agent, order.side)
        if order.side == "buy":
            resting = self.best_ask()
            if resting is not None and order.price >= resting.price:
                self.asks.remove(resting)
                return Trade(order.agent, resting.agent, resting.price, resting.agent, order.agent)
            self.bids.append(order)
            return None
        resting = self.best_bid()
        if resting is not None and order.price <= resting.price:
            self.bids.remove(resting)
            return Trade(resting.agent, order.agent, resting.price, resting.agent, order.agent)
        self.asks.append(order)
        return None


@dataclass(frozen=True)
class MarketRegime:
    imbalance: float
    volatility: float
    aggression: float


REGIMES = {
    "in_support": MarketRegime(imbalance=0.0, volatility=1.0, aggression=1.0),
    "mild_buy": MarketRegime(imbalance=0.35, volatility=1.2, aggression=1.2),
    "mild_sell": MarketRegime(imbalance=-0.35, volatility=0.8, aggression=0.9),
    "high_imbalance": MarketRegime(imbalance=0.9, volatility=1.0, aggression=1.2),
    "vol_shock": MarketRegime(imbalance=0.0, volatility=3.0, aggression=1.8),
}


class ContinuousDoubleAuction:
    def __init__(
        self,
        *,
        n_agents: int,
        fee_rate: float,
        tick_size: float,
        regime: MarketRegime,
        rng: np.random.Generator,
    ) -> None:
        if n_agents < 4 or n_agents % 2:
            raise ValueError("n_agents must be even and at least four")
        self.n_agents = n_agents
        self.fee_rate = fee_rate
        self.tick_size = tick_size
        self.regime = regime
        self.rng = rng
        self.book = FIFOBook()
        self.sequence = 0
        half = n_agents // 2
        self.is_buyer = np.zeros(n_agents, dtype=bool)
        self.is_buyer[:half] = True
        self.values = np.concatenate([rng.normal(102.0, 2.0, half), rng.normal(98.0, 2.0, half)])
        self.cash = np.full(n_agents, 2_000.0, dtype=np.float64)
        self.inventory = np.concatenate(
            [np.zeros(half, dtype=np.float64), np.full(half, 10.0, dtype=np.float64)]
        )
        self.fee_account = 0.0

    def invariant_totals(self) -> tuple[float, float]:
        return float(self.cash.sum() + self.fee_account), float(self.inventory.sum())

    def _round_price(self, price: float) -> float:
        return max(self.tick_size, round(price / self.tick_size) * self.tick_size)

    def _quote(self, agent: int, side: Side) -> float:
        distance = self.rng.exponential(2.0 / self.regime.aggression)
        noise = self.rng.normal(0.0, self.regime.volatility)
        raw = (
            self.values[agent] - distance + noise if side == "buy" else self.values[agent] + distance + noise
        )
        return self._round_price(float(raw))

    def _eligible_agents(self, side: Side) -> np.ndarray:
        if side == "buy":
            return np.flatnonzero(self.is_buyer & (self.cash > 2.0 * self.tick_size))
        return np.flatnonzero((~self.is_buyer) & (self.inventory >= 1.0))

    def _settle(self, trade: Trade) -> bool:
        fee = self.fee_rate * trade.price
        if self.cash[trade.buyer] < trade.price + fee or self.inventory[trade.seller] < 1.0:
            return False
        self.cash[trade.buyer] -= trade.price + fee
        self.cash[trade.seller] += trade.price - fee
        self.inventory[trade.buyer] += 1.0
        self.inventory[trade.seller] -= 1.0
        self.fee_account += 2.0 * fee
        return True

    def step(self) -> Trade | None:
        probability_buy = float(np.clip(0.5 * (1.0 + self.regime.imbalance), 0.05, 0.95))
        side: Side = "buy" if self.rng.random() < probability_buy else "sell"
        eligible = self._eligible_agents(side)
        if eligible.size == 0:
            return None
        actor = int(self.rng.choice(eligible))
        self.sequence += 1
        order = Order(actor, side, self._quote(actor, side), self.sequence)
        trade = self.book.submit(order)
        if trade is not None and not self._settle(trade):
            return None
        return trade

    def observation(self, layout: MarketLayout) -> np.ndarray:
        best_bid = self.book.best_bid()
        best_ask = self.book.best_ask()
        dynamic = np.concatenate(
            [
                self.cash / layout.cash_scale,
                self.inventory / layout.inventory_scale,
                np.array([self.fee_account / layout.cash_scale]),
                np.array(
                    [
                        (best_bid.price if best_bid is not None else 0.0) / layout.price_scale,
                        (best_ask.price if best_ask is not None else 2.0 * layout.price_scale)
                        / layout.price_scale,
                        len(self.book.bids) / self.n_agents,
                        len(self.book.asks) / self.n_agents,
                    ]
                ),
            ]
        )
        static = np.concatenate(
            [
                self.values / layout.price_scale,
                self.is_buyer.astype(np.float64),
                np.array([self.regime.imbalance, self.regime.volatility / 3.0, self.regime.aggression / 2.0]),
            ]
        )
        return np.concatenate([dynamic, static])


@dataclass(frozen=True)
class MarketLayout:
    n_agents: int
    cash_scale: float = 2_000.0
    inventory_scale: float = 10.0
    price_scale: float = 100.0

    @property
    def cash_slice(self) -> slice:
        return slice(0, self.n_agents)

    @property
    def inventory_slice(self) -> slice:
        return slice(self.n_agents, 2 * self.n_agents)

    @property
    def fee_index(self) -> int:
        return 2 * self.n_agents

    @property
    def dynamic_dim(self) -> int:
        return 2 * self.n_agents + 5

    @property
    def input_dim(self) -> int:
        return self.dynamic_dim + 2 * self.n_agents + 3


def project_market_delta(delta: torch.Tensor, layout: MarketLayout) -> torch.Tensor:
    projected = delta.clone()
    cash_fee = torch.cat(
        [projected[..., layout.cash_slice], projected[..., layout.fee_index : layout.fee_index + 1]],
        dim=-1,
    )
    cash_fee = cash_fee - cash_fee.mean(dim=-1, keepdim=True)
    projected[..., layout.cash_slice] = cash_fee[..., :-1]
    projected[..., layout.fee_index] = cash_fee[..., -1]
    inventory = projected[..., layout.inventory_slice]
    projected[..., layout.inventory_slice] = inventory - inventory.mean(dim=-1, keepdim=True)
    return projected


def project_market_output(
    inputs: torch.Tensor,
    outputs: torch.Tensor,
    layout: MarketLayout,
) -> torch.Tensor:
    current = inputs[..., : layout.dynamic_dim]
    return current + project_market_delta(outputs - current, layout)


def market_violation(
    inputs: torch.Tensor,
    outputs: torch.Tensor,
    layout: MarketLayout,
) -> torch.Tensor:
    current = inputs[..., : layout.dynamic_dim]
    delta = outputs - current
    cash = delta[..., layout.cash_slice].sum(dim=-1) + delta[..., layout.fee_index]
    inventory = delta[..., layout.inventory_slice].sum(dim=-1)
    return cash.square() + inventory.square()


def market_metrics(
    prediction: torch.Tensor,
    target: torch.Tensor,
    layout: MarketLayout,
) -> dict[str, float]:
    error = prediction - target
    conserving = project_market_delta(error, layout)
    cash_drift = error[..., layout.cash_slice].sum(dim=-1) + error[..., layout.fee_index]
    inventory_drift = error[..., layout.inventory_slice].sum(dim=-1)
    drift = torch.sqrt((cash_drift.square() + inventory_drift.square()) / 2.0)
    return {
        "total_rmse": float(error.square().mean().sqrt().cpu()),
        "invariant_drift": float(drift.mean().cpu()),
        "conserving_rmse": float(conserving.square().mean().sqrt().cpu()),
    }


class MarketMLP(nn.Module):
    def __init__(self, layout: MarketLayout, hidden: int, mode: str) -> None:
        super().__init__()
        self.layout = layout
        self.mode = mode
        self.net = nn.Sequential(
            nn.Linear(layout.input_dim, hidden),
            nn.Tanh(),
            nn.Linear(hidden, hidden),
            nn.Tanh(),
            nn.Linear(hidden, layout.dynamic_dim),
        )

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        raw = self.net(inputs)
        if self.mode == "absolute":
            return raw
        current = inputs[..., : self.layout.dynamic_dim]
        if self.mode == "hard":
            raw = project_market_delta(raw, self.layout)
        return current + raw


def collect_market_samples(
    *,
    regimes: list[MarketRegime],
    n_samples: int,
    n_agents: int,
    warmup_steps: int,
    episode_steps: int,
    fee_rate: float,
    tick_size: float,
    seed: int,
) -> tuple[torch.Tensor, torch.Tensor]:
    rng = np.random.default_rng(seed)
    layout = MarketLayout(n_agents)
    inputs: list[np.ndarray] = []
    targets: list[np.ndarray] = []
    while len(inputs) < n_samples:
        regime = regimes[int(rng.integers(0, len(regimes)))]
        engine = ContinuousDoubleAuction(
            n_agents=n_agents,
            fee_rate=fee_rate,
            tick_size=tick_size,
            regime=regime,
            rng=rng,
        )
        for _ in range(warmup_steps):
            before = engine.invariant_totals()
            engine.step()
            after = engine.invariant_totals()
            if not np.allclose(before, after, atol=1e-10, rtol=0.0):
                raise AssertionError(f"market invariant failure during warmup: {before} != {after}")
        for _ in range(episode_steps):
            observation = engine.observation(layout)
            before = engine.invariant_totals()
            engine.step()
            after = engine.invariant_totals()
            if not np.allclose(before, after, atol=1e-10, rtol=0.0):
                raise AssertionError(f"market invariant failure: {before} != {after}")
            inputs.append(observation)
            targets.append(engine.observation(layout)[: layout.dynamic_dim])
            if len(inputs) >= n_samples:
                break
    return (
        torch.tensor(np.stack(inputs), dtype=torch.float32),
        torch.tensor(np.stack(targets), dtype=torch.float32),
    )


def build_datasets(
    cfg: Mapping[str, Any],
    seed: int,
    device: torch.device,
) -> tuple[
    torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, dict[str, tuple[torch.Tensor, torch.Tensor]]
]:
    common = {
        "n_agents": int(cfg["n_agents"]),
        "warmup_steps": int(cfg["warmup_steps"]),
        "episode_steps": int(cfg["episode_steps"]),
        "fee_rate": float(cfg["fee_rate"]),
        "tick_size": float(cfg["tick_size"]),
    }
    train = collect_market_samples(
        regimes=[REGIMES["in_support"], REGIMES["mild_buy"], REGIMES["mild_sell"]],
        n_samples=int(cfg["n_train"]),
        seed=stable_seed(seed, "market-train"),
        **common,
    )
    identifier = collect_market_samples(
        regimes=[REGIMES["in_support"], REGIMES["mild_buy"], REGIMES["mild_sell"]],
        n_samples=int(cfg["n_id"]),
        seed=stable_seed(seed, "market-id"),
        **common,
    )
    cases = {
        name: collect_market_samples(
            regimes=[REGIMES[name]],
            n_samples=int(cfg["n_ood"]),
            seed=stable_seed(seed, f"market-{name}"),
            **common,
        )
        for name in ("high_imbalance", "vol_shock", "in_support")
    }

    def move(pair: tuple[torch.Tensor, torch.Tensor]) -> tuple[torch.Tensor, torch.Tensor]:
        return pair[0].to(device), pair[1].to(device)

    train_inputs, train_targets = move(train)
    id_inputs, id_targets = move(identifier)
    return (
        train_inputs,
        train_targets,
        id_inputs,
        id_targets,
        {key: move(value) for key, value in cases.items()},
    )


def train_model(
    *,
    model: MarketMLP,
    mechanism: str,
    inputs: torch.Tensor,
    targets: torch.Tensor,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    order_seed: int,
) -> None:
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    generator = torch.Generator(device=inputs.device)
    generator.manual_seed(order_seed)
    model.train()
    for _ in range(epochs):
        order = torch.randperm(inputs.shape[0], generator=generator, device=inputs.device)
        for start in range(0, inputs.shape[0], batch_size):
            index = order[start : start + batch_size]
            batch_inputs = inputs[index]
            prediction = model(batch_inputs)
            loss = (prediction - targets[index]).square().mean()
            if mechanism == "soft30":
                loss = loss + 30.0 * market_violation(batch_inputs, prediction, model.layout).mean()
            if not torch.isfinite(loss):
                raise FloatingPointError("non-finite market training loss")
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()


def _existing_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    ids: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "run_id" in record:
            ids.add(str(record["run_id"]))
    return ids


def run(cfg: DictConfig) -> None:
    root = Path(__file__).resolve().parents[1]
    resolved = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(resolved, dict):
        raise TypeError("resolved Hydra config must be a mapping")
    output = Path(str(resolved["output"]))
    if not output.is_absolute():
        output = root / output
    device = torch.device(str(resolved["device"]))
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable")
    selection_lock_path = validate_selection_lock(root, resolved)
    layout = MarketLayout(int(resolved["n_agents"]))
    source_files = [
        Path(__file__),
        root / "scripts/constraint_iclr_common.py",
        root / "scripts/launch_constraint_iclr_pilot.py",
        root / "scripts/launch_constraint_iclr_confirmation.py",
        root / "configs/constraint_iclr/market.yaml",
        root / "configs/constraint_iclr/market_pilot.yaml",
        root / "configs/constraint_iclr/market_confirmation.yaml",
        root / "configs/constraint_iclr/pilot_manifest.yaml",
        root / "configs/constraint_iclr/pilot_manifest_ahm_expand.yaml",
        root / "configs/constraint_iclr/confirmation_manifest.yaml",
        root / "papers/proposal/ecomd_constraint_attribution_iclr_extension_freeze_2026-08-30.md",
        root
        / "papers/proposal/ecomd_constraint_attribution_iclr_compute_authority_amendment_2026-08-30.md",
    ]
    if selection_lock_path is not None:
        source_files.append(selection_lock_path)
    shared_provenance = provenance(
        root=root,
        resolved_config=resolved,
        source_files=source_files,
    )
    completed = _existing_ids(output)
    for seed in [int(value) for value in resolved["seeds"]]:
        train_inputs, train_targets, id_inputs, id_targets, cases = build_datasets(resolved, seed, device)
        for capacity in [int(value) for value in resolved["capacity_grid"]]:
            for epochs in [int(value) for value in resolved["epochs_grid"]]:
                for learning_rate in [float(value) for value in resolved["lr_grid"]]:
                    for mechanism in [str(value) for value in resolved["mechanisms"]]:
                        identity = {
                            "schema_version": SCHEMA_VERSION,
                            "stage": str(resolved["stage"]),
                            "family": "M2",
                            "system": "fifo_cda",
                            "seed": seed,
                            "mechanism": mechanism,
                            "capacity": capacity,
                            "epochs": epochs,
                            "learning_rate": learning_rate,
                            "n_train": int(resolved["n_train"]),
                            "protocol_sha256": shared_provenance["source_sha256"].get(
                                "papers/proposal/ecomd_constraint_attribution_iclr_extension_freeze_2026-08-30.md"
                            ),
                        }
                        if selection_lock_path is not None:
                            identity["selection_lock_sha256"] = str(
                                resolved["selection_lock_sha256"]
                            )
                        run_id = canonical_run_id(identity)
                        projection_id = canonical_run_id({**identity, "mechanism": "projection"})
                        if run_id in completed and (mechanism != "free" or projection_id in completed):
                            continue
                        seed_everything(stable_seed(seed, f"market-model:{capacity}"))
                        mode = (
                            "hard"
                            if mechanism == "hard"
                            else "residual"
                            if mechanism == "free_res"
                            else "absolute"
                        )
                        model = MarketMLP(layout, capacity, mode).to(device)
                        parameter_count = count_trainable_parameters(model)
                        if device.type == "cuda":
                            torch.cuda.reset_peak_memory_stats(device)
                        started = time.perf_counter()
                        train_model(
                            model=model,
                            mechanism=mechanism,
                            inputs=train_inputs,
                            targets=train_targets,
                            epochs=epochs,
                            batch_size=int(resolved["batch_size"]),
                            learning_rate=learning_rate,
                            order_seed=stable_seed(seed, "market-minibatch-order"),
                        )
                        runtime = time.perf_counter() - started
                        model.eval()
                        with torch.no_grad():
                            id_prediction = model(id_inputs)
                            id_metrics = market_metrics(id_prediction, id_targets, layout)
                            case_metrics = {
                                name: {"1": market_metrics(model(inputs), targets, layout)}
                                for name, (inputs, targets) in cases.items()
                            }
                        compute = {
                            "trainable_parameters": parameter_count,
                            "examples_seen": int(resolved["n_train"]) * epochs,
                            "proxy": parameter_count * int(resolved["n_train"]) * epochs,
                            "runtime_seconds": runtime,
                            "peak_gpu_memory_bytes": (
                                int(torch.cuda.max_memory_allocated(device))
                                if device.type == "cuda"
                                else None
                            ),
                        }
                        config_id = f"c{capacity}_e{epochs}_lr{learning_rate:g}"
                        record = {
                            **identity,
                            "run_id": run_id,
                            "config_id": config_id,
                            "derived_from": None,
                            "compute": compute,
                            "id_metrics": id_metrics,
                            "cases": case_metrics,
                            "provenance": shared_provenance,
                        }
                        if run_id not in completed:
                            append_jsonl(output, record)
                            completed.add(run_id)
                            print(f"completed {run_id} {mechanism} seed={seed} {config_id}", flush=True)
                        if mechanism == "free" and projection_id not in completed:
                            with torch.no_grad():
                                projected_id = market_metrics(
                                    project_market_output(id_inputs, model(id_inputs), layout),
                                    id_targets,
                                    layout,
                                )
                                projected_cases = {
                                    name: {
                                        "1": market_metrics(
                                            project_market_output(inputs, model(inputs), layout),
                                            targets,
                                            layout,
                                        )
                                    }
                                    for name, (inputs, targets) in cases.items()
                                }
                            append_jsonl(
                                output,
                                {
                                    **identity,
                                    "mechanism": "projection",
                                    "run_id": projection_id,
                                    "config_id": config_id,
                                    "derived_from": run_id,
                                    "compute": compute,
                                    "id_metrics": projected_id,
                                    "cases": projected_cases,
                                    "provenance": shared_provenance,
                                },
                            )
                            completed.add(projection_id)


@hydra.main(version_base=None, config_path="../configs/constraint_iclr", config_name="market")
def main(cfg: DictConfig) -> None:
    run(cfg)


if __name__ == "__main__":
    main()
