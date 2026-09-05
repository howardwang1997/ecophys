"""Bounded CPU probe: does a conservation constraint launder OOD error into conserving channels?

Engineering-only toy for the D-1 hostile audit of the constraint-inductive-bias question
contract (papers/proposal/ecomd_constraint_inductive_bias_d1_hostile_audit_2026-08-27.md).
Linear case is solved in closed form by the decoupling argument; this script tests the
nonlinear (MLP) case. No route evidence, no confirmation asset, no GPU, public/generated
data only.
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

torch.set_num_threads(1)


def build_chain_operator(n: int, k: float) -> torch.Tensor:
    lap = torch.zeros(n, n)
    for i in range(n):
        lap[i, i] = -2.0
        if i > 0:
            lap[i, i - 1] = 1.0
        if i < n - 1:
            lap[i, i + 1] = 1.0
    lap[0, 0] = -1.0
    lap[-1, -1] = -1.0
    return torch.eye(n) + k * lap


def pick_modes(lap: torch.Tensor) -> tuple[torch.Tensor, int, int]:
    evals, evecs = torch.linalg.eigh(lap)
    order = torch.argsort(evals.abs())
    basis = evecs[:, order]
    flat_idx = 1
    rich_idx = basis.shape[1] // 2
    return basis, flat_idx, rich_idx


def make_data(
    basis: torch.Tensor,
    op: torch.Tensor,
    n: int,
    n_samples: int,
    sigma_flat: float,
    rng: np.random.Generator,
    flat_idx: int,
    rich_idx: int,
) -> tuple[torch.Tensor, torch.Tensor]:
    sigmas = np.full(n, 0.5, dtype=np.float64)
    sigmas[0] = 1.0
    sigmas[rich_idx] = 1.0
    sigmas[flat_idx] = sigma_flat
    x = rng.normal(0.0, 1.0, size=(n_samples, n)) * sigmas
    u0 = torch.tensor(x, dtype=torch.float32) @ basis.T
    u1 = u0 @ op.T
    return u0, u1


class MLP(nn.Module):
    def __init__(self, n: int, hidden: int, mode: str) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n, hidden),
            nn.Tanh(),
            nn.Linear(hidden, hidden),
            nn.Tanh(),
            nn.Linear(hidden, n),
        )
        self.mode = mode

    def forward(self, u: torch.Tensor) -> torch.Tensor:
        if self.mode == "hard":
            delta = self.net(u)
            return u + delta - delta.mean(dim=-1, keepdim=True)
        if self.mode == "free_res":
            return u + self.net(u)
        return self.net(u)


def project_output(u: torch.Tensor, out: torch.Tensor) -> torch.Tensor:
    drift = (u.mean(dim=-1, keepdim=True) - out.mean(dim=-1, keepdim=True))
    return out + drift


def mass_residual(u: torch.Tensor, out: torch.Tensor) -> torch.Tensor:
    return out.mean(dim=-1) - u.mean(dim=-1)


def train_one(
    u0: torch.Tensor,
    u1: torch.Tensor,
    n: int,
    hidden: int,
    mechanism: str,
    lam: float,
    epochs: int,
    batch: int,
    lr: float,
    seed: int,
) -> MLP:
    torch.manual_seed(seed)
    residual = mechanism in ("hard", "free_res", "soft_res")
    mode = "hard" if mechanism == "hard" else "free_res" if residual else "abs"
    model = MLP(n, hidden, mode=mode)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    n_samples = u0.shape[0]
    for _ in range(epochs):
        perm = torch.randperm(n_samples)
        for start in range(0, n_samples, batch):
            idx = perm[start : start + batch]
            xb, yb = u0[idx], u1[idx]
            out = model(xb)
            loss = ((out - yb) ** 2).mean()
            if mechanism in ("soft", "soft_res"):
                loss = loss + lam * (mass_residual(xb, out) ** 2).mean()
            opt.zero_grad()
            loss.backward()
            opt.step()
    return model


@dataclass
class CaseResult:
    rmse: float
    mass_drift: float
    conserving_err: float


def evaluate_case(model: MLP, u: torch.Tensor, target: torch.Tensor, projected: bool) -> CaseResult:
    with torch.no_grad():
        out = model(u)
        if projected:
            out = project_output(u, out)
        err = out - target
        drift = err.mean(dim=-1)
        cons = err - drift.unsqueeze(-1)
        return CaseResult(
            rmse=float(err.pow(2).mean().sqrt()),
            mass_drift=float(drift.abs().mean()),
            conserving_err=float(cons.norm(dim=-1).mean()),
        )


@dataclass
class RunRecord:
    sigma_flat: float
    seed: int
    mechanism: str
    id_rmse: float
    cases: dict[str, CaseResult] = field(default_factory=dict)
    soft_mass_residual_id: float = 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=8)
    parser.add_argument("--k", type=float, default=0.1)
    parser.add_argument("--n-samples", type=int, default=4096)
    parser.add_argument("--hidden", type=int, default=64)
    parser.add_argument("--epochs", type=int, default=400)
    parser.add_argument("--batch", type=int, default=512)
    parser.add_argument("--lr", type=float, default=3e-3)
    parser.add_argument("--lam", type=float, default=30.0)
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--sigma-flat-grid", type=float, nargs="+", default=[1.0, 0.3, 0.1, 0.03])
    parser.add_argument("--out", type=Path, default=Path("experiments/toy_h2_laundering/results.json"))
    args = parser.parse_args()

    op = build_chain_operator(args.n, args.k)
    basis, flat_idx, rich_idx = pick_modes(op - torch.eye(args.n))
    n = args.n

    def ood_input(coords: dict[int, float]) -> torch.Tensor:
        x = np.zeros((1, n), dtype=np.float64)
        for idx, val in coords.items():
            x[0, idx] = val
        return torch.tensor(x, dtype=torch.float32) @ basis.T

    cases: dict[str, tuple[torch.Tensor, torch.Tensor]] = {
        "ood_rich": (u := ood_input({rich_idx: 2.5}), u @ op.T),
        "ood_flat": (u := ood_input({flat_idx: 2.5}), u @ op.T),
        "ood_mass": (u := ood_input({rich_idx: 1.0, 0: 2.0}), u @ op.T),
    }

    records: list[RunRecord] = []
    for sigma_flat in args.sigma_flat_grid:
        for seed in range(args.seeds):
            rng = np.random.default_rng(10_000 * seed + int(sigma_flat * 1000))
            u0, u1 = make_data(basis, op, n, args.n_samples, sigma_flat, rng, flat_idx, rich_idx)
            u0t, u1t = make_data(basis, op, n, 1024, sigma_flat, rng, flat_idx, rich_idx)
            for mechanism in ("free", "free_res", "soft", "soft_res", "hard"):
                model = train_one(
                    u0, u1, n, args.hidden, mechanism, args.lam, args.epochs, args.batch, args.lr, seed
                )
                rec = RunRecord(sigma_flat=sigma_flat, seed=seed, mechanism=mechanism, id_rmse=0.0)
                rec.id_rmse = evaluate_case(model, u0t, u1t, projected=False).rmse
                with torch.no_grad():
                    rec.soft_mass_residual_id = float(
                        mass_residual(u0t, model(u0t)).abs().mean()
                    )
                for name, (u_ood, target) in cases.items():
                    rec.cases[name] = evaluate_case(model, u_ood, target, projected=False)
                if mechanism == "free":
                    rec_proj = RunRecord(
                        sigma_flat=sigma_flat, seed=seed, mechanism="projection", id_rmse=rec.id_rmse
                    )
                    rec_proj.id_rmse = evaluate_case(model, u0t, u1t, projected=True).rmse
                    for name, (u_ood, target) in cases.items():
                        rec_proj.cases[name] = evaluate_case(model, u_ood, target, projected=True)
                    records.append(rec_proj)
                records.append(rec)

    try:
        sha = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except subprocess.CalledProcessError:
        sha = "unknown"

    payload = {
        "config": {**{k: v if not isinstance(v, Path) else str(v) for k, v in vars(args).items()},
                   "git_sha": sha, "torch_version": torch.__version__},
        "records": [
            {
                "sigma_flat": r.sigma_flat,
                "seed": r.seed,
                "mechanism": r.mechanism,
                "id_rmse": r.id_rmse,
                "soft_mass_residual_id": r.soft_mass_residual_id,
                "cases": {k: asdict(v) for k, v in r.cases.items()},
            }
            for r in records
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2))

    mechanisms = ("free", "free_res", "soft", "soft_res", "hard", "projection")
    print(f"{'sigma_f':>8} {'mech':>10} {'id_rmse':>9} | " + " | ".join(f"{c:>21}" for c in cases))
    for sigma_flat in args.sigma_flat_grid:
        for mech in mechanisms:
            rows = [r for r in records if r.sigma_flat == sigma_flat and r.mechanism == mech]
            idm = float(np.mean([r.id_rmse for r in rows]))
            parts = []
            for name in cases:
                tot = float(np.mean([r.cases[name].rmse for r in rows]))
                cons = float(np.mean([r.cases[name].conserving_err for r in rows]))
                drift = float(np.mean([r.cases[name].mass_drift for r in rows]))
                parts.append(f"{tot:.3f}/{cons:.3f}/{drift:.4f}")
            print(f"{sigma_flat:>8.2f} {mech:>10} {idm:>9.4f} | " + " | ".join(f"{p:>21}" for p in parts))
    print("(each cell: rmse / conserving_err / mass_drift; target mass drift = 0)")


if __name__ == "__main__":
    main()
