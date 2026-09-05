"""Family-A audit: conservation-constraint attribution on analytic spectral systems.

Executes the D0 freeze `papers/proposal/ecomd_constraint_attribution_audit_d0_freeze_2026-08-27.md`.
One-step learned simulators of advection / diffusion / viscous Burgers on a periodic grid;
six constraint arms; Fourier-mode data-flatness control; JSON records per run.
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


def spectral_step_advection(u: torch.Tensor, c: float, dt: float) -> torch.Tensor:
    n = u.shape[-1]
    k = torch.fft.fftfreq(n, d=1.0 / n)
    phase = torch.exp(-1j * 2.0 * torch.pi * c * k * dt / n)
    uhat = torch.fft.fft(u, dim=-1)
    return torch.fft.ifft(uhat * phase.to(u.device), dim=-1).real


def spectral_step_diffusion(u: torch.Tensor, nu: float, dt: float) -> torch.Tensor:
    n = u.shape[-1]
    k = torch.fft.fftfreq(n, d=1.0 / n)
    decay = torch.exp(-nu * (2.0 * torch.pi * k / n) ** 2 * dt)
    uhat = torch.fft.fft(u, dim=-1)
    return torch.fft.ifft(uhat * decay.to(u.device), dim=-1).real


def burgers_step(u: torch.Tensor, nu: float, dt: float, substeps: int = 64) -> torch.Tensor:
    n = u.shape[-1]
    k = torch.fft.fftfreq(n, d=1.0 / n)
    ik = (1j * 2.0 * torch.pi * k / n).to(u.device)
    ksq = ((2.0 * torch.pi * k / n) ** 2).to(u.device)

    def rhs(x: torch.Tensor) -> torch.Tensor:
        uh = torch.fft.fft(x, dim=-1)
        conv = torch.fft.ifft(torch.fft.fft(x * x, dim=-1) * ik * (-0.5), dim=-1).real
        lin = torch.fft.ifft(uh * (-nu * ksq), dim=-1).real
        return conv + lin

    h = dt / substeps
    out = u
    for _ in range(substeps):
        a = rhs(out)
        b = rhs(out + 0.5 * h * a)
        c = rhs(out + 0.5 * h * b)
        d = rhs(out + h * c)
        out = out + (h / 6.0) * (a + 2 * b + 2 * c + d)
    return out


def build_system(name: str, n: int, nu: float | None = None, dt: float | None = None):
    if name == "advection":
        return lambda u: spectral_step_advection(u, c=1.0, dt=dt or 0.1)
    if name == "diffusion":
        return lambda u: spectral_step_diffusion(u, nu=nu if nu is not None else 0.02, dt=dt or 0.1)
    if name == "burgers":
        return lambda u: burgers_step(u, nu=nu if nu is not None else 0.01, dt=dt or 0.1)
    raise ValueError(name)


def mode_sigma(n: int, flat_idx: int, rich_idx: int, sigma_flat: float) -> np.ndarray:
    sig = np.full(n, 0.5, dtype=np.float64)
    k = np.fft.fftfreq(n, d=1.0 / n).astype(int)
    sig[np.abs(k) == 0] = 1.0
    sig[np.abs(k) == rich_idx] = 1.0
    sig[np.abs(k) == flat_idx] = sigma_flat
    return sig


def make_samples(
    n: int, n_samples: int, sigma: np.ndarray, rng: np.random.Generator
) -> torch.Tensor:
    coeffs = (rng.normal(size=(n_samples, n)) + 1j * rng.normal(size=(n_samples, n))) * (sigma / np.sqrt(2.0))
    u = np.fft.ifft(coeffs, axis=-1).real
    return torch.tensor(u, dtype=torch.float32)


class MLP(nn.Module):
    def __init__(self, n: int, hidden: int, mode: str) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n, hidden), nn.Tanh(),
            nn.Linear(hidden, hidden), nn.Tanh(),
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


def mass_residual(u: torch.Tensor, out: torch.Tensor) -> torch.Tensor:
    return out.mean(dim=-1) - u.mean(dim=-1)


@dataclass
class CaseMetrics:
    rmse: float
    mass_drift: float
    conserving_err: float


def eval_case(model: MLP, u: torch.Tensor, target: torch.Tensor, projected: bool, inv: torch.Tensor) -> CaseMetrics:
    with torch.no_grad():
        out = model(u)
        if projected:
            out = out + (u.mean(dim=-1, keepdim=True) - out.mean(dim=-1, keepdim=True))
        err = (out - target) @ inv.T
        drift = err.mean(dim=-1)
        cons = err - drift.unsqueeze(-1)
        return CaseMetrics(
            rmse=float(err.pow(2).mean().sqrt()),
            mass_drift=float(drift.abs().mean()),
            conserving_err=float(cons.norm(dim=-1).mean()),
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


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--system", choices=["advection", "diffusion", "burgers"], required=True)
    p.add_argument("--n", type=int, default=64)
    p.add_argument("--n-samples", type=int, default=4096)
    p.add_argument("--sigma-flat", type=float, required=True)
    p.add_argument("--hidden-grid", type=int, nargs="+", default=[64, 128])
    p.add_argument("--epochs-grid", type=int, nargs="+", default=[400, 800])
    p.add_argument("--lam-grid", type=float, nargs="+", default=[3.0, 30.0])
    p.add_argument("--seeds", type=int, default=5)
    p.add_argument("--batch", type=int, default=512)
    p.add_argument("--lr", type=float, default=3e-3)
    p.add_argument("--device", default="cpu")
    p.add_argument("--nu", type=float, default=None)
    p.add_argument("--dt", type=float, default=None)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    torch.manual_seed(0)
    device = torch.device(args.device)
    system = build_system(args.system, args.n, nu=args.nu, dt=args.dt)
    n = args.n
    flat_idx, rich_idx = 1, 8

    def to_device(t: torch.Tensor) -> torch.Tensor:
        return t.to(device)

    k = np.fft.fftfreq(n, d=1.0 / n).astype(int)

    def mode_vector(idx: int) -> torch.Tensor:
        v = np.zeros((1, n))
        v[0, np.where(k == idx)[0][0]] = 1.0
        v[0, np.where(k == -idx)[0][0]] = 1.0
        return torch.tensor(v / np.linalg.norm(v), dtype=torch.float32).to(device)

    cases: dict[str, tuple[torch.Tensor, torch.Tensor]] = {
        "ood_rich": (u := to_device(mode_vector(rich_idx) * 2.5), system(u.cpu()).to(device)),
        "ood_flat": (u := to_device(mode_vector(flat_idx) * 2.5), system(u.cpu()).to(device)),
        "ood_mass": (u := to_device(mode_vector(rich_idx) + 2.0), system(u.cpu()).to(device)),
    }
    inv = torch.eye(n, device=device)

    records: list[RunRecord] = []
    sig = mode_sigma(n, flat_idx, rich_idx, args.sigma_flat)
    for hidden in args.hidden_grid:
        for epochs in args.epochs_grid:
            for seed in range(args.seeds):
                rng = np.random.default_rng(100_000 * seed + int(args.sigma_flat * 1000) + hidden + epochs)
                u0 = to_device(make_samples(n, args.n_samples, sig, rng))
                u1 = system(u0.cpu()).to(device)
                u0t = to_device(make_samples(n, 1024, sig, rng))
                u1t = system(u0t.cpu()).to(device)
                for mechanism in ("free", "free_res", "soft", "soft_res", "hard"):
                    lam_list = args.lam_grid if mechanism in ("soft", "soft_res") else [0.0]
                    for lam in lam_list:
                        torch.manual_seed(seed)
                        residual = mechanism in ("hard", "free_res", "soft_res")
                        mode = "hard" if mechanism == "hard" else ("free_res" if residual else "abs")
                        model = MLP(n, hidden, mode).to(device)
                        opt = torch.optim.Adam(model.parameters(), lr=args.lr)
                        ns = u0.shape[0]
                        for _ in range(epochs):
                            perm = torch.randperm(ns, device=device)
                            for s in range(0, ns, args.batch):
                                idx = perm[s : s + args.batch]
                                xb, yb = u0[idx], u1[idx]
                                out = model(xb)
                                loss = ((out - yb) ** 2).mean()
                                if mechanism in ("soft", "soft_res"):
                                    loss = loss + lam * (mass_residual(xb, out) ** 2).mean()
                                opt.zero_grad()
                                loss.backward()
                                opt.step()
                        rec = RunRecord(
                            system=args.system, sigma_flat=args.sigma_flat,
                            mechanism=f"{mechanism}@{lam}" if lam else mechanism,
                            hidden=hidden, epochs=epochs, seed=seed,
                        )
                        rec.id_rmse = eval_case(model, u0t, u1t, False, inv).rmse
                        for name, (u_ood, target) in cases.items():
                            rec.cases[name] = eval_case(model, u_ood, target, False, inv)
                        records.append(rec)
                        if mechanism == "free":
                            rec_p = RunRecord(
                                system=args.system, sigma_flat=args.sigma_flat,
                                mechanism="projection", hidden=hidden, epochs=epochs, seed=seed,
                            )
                            rec_p.id_rmse = eval_case(model, u0t, u1t, True, inv).rmse
                            for name, (u_ood, target) in cases.items():
                                rec_p.cases[name] = eval_case(model, u_ood, target, True, inv)
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
