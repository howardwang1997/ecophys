"""Family M audit: accounting-conservation attribution in a learned CDA simulator.

Executes the Family-M freeze
`papers/proposal/ecomd_constraint_attribution_family_m_freeze_2026-08-28.md`.
Synthetic Gode-Sunder-class CDA with exact settlement is the analytic truth; the learner
predicts one-step per-agent (cash, inventory) plus book features; six constraint arms;
conserving/non-conserving error decomposition on frozen OOD regimes.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
import torch
from torch import nn


class CDA:
    def __init__(
        self,
        n_agents: int,
        n_steps: int,
        fee: float,
        tick: float,
        rng: np.random.Generator,
        regime: dict,
    ) -> None:
        self.rng = rng
        self.n_agents = n_agents
        self.fee = fee
        self.tick = tick
        half = n_agents // 2
        values = rng.uniform(40.0, 60.0, size=n_agents)
        self.is_buyer = np.zeros(n_agents, dtype=bool)
        self.is_buyer[:half] = True
        self.values = values
        self.cash = np.full(n_agents, 100.0)
        self.inv = np.zeros(n_agents)
        self.inv[half:] = 10.0
        self.best_bid = 0.0
        self.best_ask = 100.0
        self.imbalance = float(regime["imbalance"])
        self.aggr = float(regime["aggr"])
        self.n_steps = n_steps

    def step(self) -> None:
        side_p_buy = 0.5 * self.imbalance
        if self.rng.random() < side_p_buy:
            actor = int(self.rng.choice(np.where(self.is_buyer)[0]))
            side_buy = True
        else:
            actor = int(self.rng.choice(np.where(~self.is_buyer)[0]))
            side_buy = False
        edge = self.values[actor]
        noise = self.rng.normal(0.0, 1.0)
        if side_buy:
            limit = edge - self.aggr * self.rng.uniform(0.0, 5.0) + noise
            if limit >= self.best_ask and self.best_ask < 100.0:
                shares = min(5, max(1, int(self.rng.integers(1, 6))))
                price = self.best_ask
                seller_pool = np.where((~self.is_buyer) & (self.inv > 0))[0]
                if seller_pool.size:
                    seller = int(self.rng.choice(seller_pool))
                    q = min(shares, int(self.inv[seller]))
                    self.cash[actor] -= q * (price + self.fee)
                    self.cash[seller] += q * price
                    self.inv[actor] += q
                    self.inv[seller] -= q
                    self.best_ask = min(100.0, price + self.tick)
            else:
                self.best_bid = max(self.best_bid, limit)
        else:
            limit = edge + self.aggr * self.rng.uniform(0.0, 5.0) + noise
            if limit <= self.best_bid and self.best_bid > 0.0:
                shares = min(5, max(1, int(self.rng.integers(1, 6))))
                price = self.best_bid
                buyer_pool = np.where(self.is_buyer)[0]
                if buyer_pool.size:
                    buyer = int(self.rng.choice(buyer_pool))
                    q = min(shares, int(self.inv[actor]))
                    self.cash[buyer] -= q * (price + self.fee)
                    self.cash[actor] += q * price
                    self.inv[buyer] += q
                    self.inv[actor] -= q
                    self.best_bid = max(0.0, price - self.tick)
            else:
                self.best_ask = min(self.best_ask, limit)

    def features(self) -> np.ndarray:
        book = np.array([self.best_bid / 100.0, self.best_ask / 100.0, self.imbalance, self.aggr])
        agents = np.concatenate([self.cash / 100.0, self.inv / 10.0, self.values / 100.0, self.is_buyer.astype(float)])
        return np.concatenate([book, agents])


def episode(regime: dict, n_agents: int, n_steps: int, rng: np.random.Generator):
    m = CDA(n_agents, n_steps, fee=0.0, tick=0.1, rng=rng, regime=regime)
    states = []
    for _ in range(n_steps):
        x = m.features()
        m.step()
        y = m.features()
        states.append((x, y))
    return states


REGIMES = {
    "in_support": {"imbalance": 0.5, "aggr": 1.0},
    "high_imbalance": {"imbalance": 0.95, "aggr": 1.0},
    "vol_shock": {"imbalance": 0.5, "aggr": 2.5},
}


BOOK_DIMS = 4


class MLP(nn.Module):
    def __init__(self, n_in: int, n_out: int, hidden: int, mode: str) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_in, hidden), nn.Tanh(),
            nn.Linear(hidden, hidden), nn.Tanh(),
            nn.Linear(hidden, n_out),
        )
        self.mode = mode

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.mode in ("hard", "free_res"):
            return x + self._zero_sum(self.net(x))
        return self.net(x)

    def _zero_sum(self, delta: torch.Tensor) -> torch.Tensor:
        n = (delta.shape[-1] - BOOK_DIMS) // 4
        cash = delta[..., BOOK_DIMS : BOOK_DIMS + n]
        inv = delta[..., BOOK_DIMS + n : BOOK_DIMS + 2 * n]
        if self.mode == "hard":
            cash = cash - cash.mean(dim=-1, keepdim=True)
            inv = inv - inv.mean(dim=-1, keepdim=True)
        rest = delta[..., BOOK_DIMS + 2 * n :]
        return torch.cat([delta[..., :BOOK_DIMS], cash, inv, rest], dim=-1)


def sum_violation(x: torch.Tensor, out: torch.Tensor, n: int) -> torch.Tensor:
    dcash = out[..., BOOK_DIMS : BOOK_DIMS + n].sum(dim=-1) - x[..., BOOK_DIMS : BOOK_DIMS + n].sum(dim=-1)
    dinv = out[..., BOOK_DIMS + n : BOOK_DIMS + 2 * n].sum(dim=-1) - x[..., BOOK_DIMS + n : BOOK_DIMS + 2 * n].sum(dim=-1)
    return dcash**2 + dinv**2


@dataclass
class CaseMetrics:
    rmse: float
    mass_drift: float
    conserving_err: float


def eval_case(model: MLP, x: torch.Tensor, y: torch.Tensor, n: int, projected: bool) -> CaseMetrics:
    with torch.no_grad():
        out = model(x)
        if projected:
            out = out.clone()
            for sl in (slice(BOOK_DIMS, BOOK_DIMS + n), slice(BOOK_DIMS + n, BOOK_DIMS + 2 * n)):
                shift = (x[..., sl].sum(-1) - out[..., sl].sum(-1)) / n
                out[..., sl] = out[..., sl] + shift.unsqueeze(-1)
        err = out - y
        drift_terms = []
        cons_sq = torch.zeros(err.shape[0], device=err.device)
        for sl in (slice(BOOK_DIMS, BOOK_DIMS + n), slice(BOOK_DIMS + n, BOOK_DIMS + 2 * n)):
            e = err[..., sl]
            drift_terms.append(e.sum(dim=-1).abs().mean())
            cons = e - e.mean(dim=-1, keepdim=True)
            cons_sq = cons_sq + cons.pow(2).sum(dim=-1)
        return CaseMetrics(
            rmse=float(err.pow(2).mean().sqrt()),
            mass_drift=float(torch.stack(drift_terms).mean()),
            conserving_err=float(cons_sq.sqrt().mean()),
        )


@dataclass
class RunRecord:
    system: str
    sigma_flat: float
    mechanism: str
    hidden: int
    epochs: int
    seed: int
    id_rmse: float = 0.0
    cases: dict[str, CaseMetrics] = field(default_factory=dict)


def collect(regimes: dict, n_agents: int, n_steps: int, episodes: int, rng: np.random.Generator):
    xs, ys = [], []
    for reg in regimes.values():
        for _ in range(episodes):
            for x, y in episode(reg, n_agents, n_steps, rng):
                xs.append(x)
                ys.append(y)
    return (
        torch.tensor(np.stack(xs), dtype=torch.float32),
        torch.tensor(np.stack(ys), dtype=torch.float32),
    )


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--n-agents", type=int, default=16)
    p.add_argument("--n-steps", type=int, default=120)
    p.add_argument("--episodes", type=int, default=40)
    p.add_argument("--sigma-flat", type=float, default=1.0)
    p.add_argument("--hidden-grid", type=int, nargs="+", default=[64, 128])
    p.add_argument("--epochs-grid", type=int, nargs="+", default=[400, 800])
    p.add_argument("--lam-grid", type=float, nargs="+", default=[3.0, 30.0])
    p.add_argument("--seeds", type=int, default=5)
    p.add_argument("--batch", type=int, default=512)
    p.add_argument("--lr", type=float, default=3e-3)
    p.add_argument("--device", default="cpu")
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    device = torch.device(args.device)
    n = args.n_agents

    def build(regimes: dict, episodes: int, seed: int):
        rng = np.random.default_rng(seed)
        x, y = collect(regimes, args.n_agents, args.n_steps, episodes, rng)
        return x.to(device), y.to(device)

    train_regimes = {"in_support": REGIMES["in_support"], "mild": {"imbalance": 0.65, "aggr": 1.2}}
    x_tr, y_tr = build(train_regimes, args.episodes, 1)
    x_id, y_id = build(train_regimes, 8, 2)
    ood = {
        name: build({name: REGIMES[name]}, 12, 3 + i)
        for i, name in enumerate(("high_imbalance", "vol_shock", "in_support"))
    }

    records: list[RunRecord] = []
    for hidden in args.hidden_grid:
        for epochs in args.epochs_grid:
            for seed in range(args.seeds):
                for mechanism in ("free", "free_res", "soft", "soft_res", "hard"):
                    lam_list = args.lam_grid if mechanism in ("soft", "soft_res") else [0.0]
                    for lam in lam_list:
                        torch.manual_seed(seed)
                        mode = (
                            "hard" if mechanism == "hard"
                            else "free_res" if mechanism in ("free_res", "soft_res")
                            else "abs"
                        )
                        model = MLP(x_tr.shape[-1], y_tr.shape[-1], hidden, mode).to(device)
                        model.mode = mode
                        opt = torch.optim.Adam(model.parameters(), lr=args.lr)
                        ns = x_tr.shape[0]
                        for _ in range(epochs):
                            perm = torch.randperm(ns, device=device)
                            for s in range(0, ns, args.batch):
                                idx = perm[s : s + args.batch]
                                xb, yb = x_tr[idx], y_tr[idx]
                                out = model(xb)
                                loss = ((out - yb) ** 2).mean()
                                if mechanism in ("soft", "soft_res"):
                                    loss = loss + lam * sum_violation(xb, out, n).mean()
                                opt.zero_grad()
                                loss.backward()
                                opt.step()
                        rec = RunRecord(
                            system="cda", sigma_flat=args.sigma_flat,
                            mechanism=f"{mechanism}@{lam}" if lam else mechanism,
                            hidden=hidden, epochs=epochs, seed=seed,
                        )
                        rec.id_rmse = eval_case(model, x_id, y_id, n, False).rmse
                        for name, (xo, yo) in ood.items():
                            rec.cases[name] = eval_case(model, xo, yo, n, False)
                        records.append(rec)
                        if mechanism == "free":
                            rec_p = RunRecord(
                                system="cda", sigma_flat=args.sigma_flat,
                                mechanism="projection", hidden=hidden, epochs=epochs, seed=seed,
                            )
                            rec_p.id_rmse = eval_case(model, x_id, y_id, n, True).rmse
                            for name, (xo, yo) in ood.items():
                                rec_p.cases[name] = eval_case(model, xo, yo, n, True)
                            records.append(rec_p)

    try:
        sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, check=True).stdout.strip()
    except subprocess.CalledProcessError:
        sha = "unknown"
    payload = {
        "config": {kk: (str(vv) if isinstance(vv, Path) else vv) for kk, vv in vars(args).items()},
        "git_sha": sha,
        "records": [
            {**{k2: v2 for k2, v2 in asdict(r).items() if k2 != "cases"},
             "cases": {cn: asdict(cm) for cn, cm in r.cases.items()}}
            for r in records
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2))
    print(f"wrote {args.out} with {len(records)} records")


if __name__ == "__main__":
    main()
