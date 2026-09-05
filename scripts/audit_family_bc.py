"""Families B and C of the conservation-constraint attribution audit.

Family B (PDEBench-class role): 1D U-Net surrogates at train resolution 128; OOD probes
include amplitude extrapolation and a band-limited resolution shift (evaluate at 256).
Family C (2D structured-grid role): 2D advection-diffusion on 32x32 periodic grids with a
2D U-Net. Arms, lambda grid, cells (channels {16,32} x epochs {400,800}), seeds and record
schema follow the D0 freeze; `hidden` records base channels for convnets.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as functional
from audit_family_analytic import build_system, make_samples, mode_sigma
from torch import nn


def conv_block(cin: int, cout: int, nd: int) -> nn.Module:
    conv = nn.Conv1d if nd == 1 else nn.Conv2d
    return nn.Sequential(
        conv(cin, cout, kernel_size=5, padding=2),
        nn.GroupNorm(8, cout),
        nn.SiLU(),
        conv(cout, cout, kernel_size=5, padding=2),
        nn.GroupNorm(8, cout),
        nn.SiLU(),
    )


class UNet(nn.Module):
    def __init__(self, channels: int, nd: int) -> None:
        super().__init__()
        convt = nn.ConvTranspose1d if nd == 1 else nn.ConvTranspose2d
        self.enc1 = conv_block(1, channels, nd)
        self.enc2 = conv_block(channels, channels * 2, nd)
        self.bottleneck = conv_block(channels * 2, channels * 2, nd)
        self.up2a = convt(channels * 2, channels * 2, kernel_size=2, stride=2)
        self.dec2 = conv_block(channels * 4, channels * 2, nd)
        self.up2b = convt(channels * 2, channels, kernel_size=2, stride=2)
        self.dec1 = conv_block(channels * 2, channels, nd)
        self.head = (nn.Conv1d if nd == 1 else nn.Conv2d)(channels, 1, kernel_size=1)
        self.mode = "abs"

    def forward(self, u: torch.Tensor) -> torch.Tensor:
        x = u.unsqueeze(1)
        pool = (lambda t: functional.avg_pool2d(t, 2)) if x.dim() == 4 else (lambda t: functional.avg_pool1d(t, 2))
        e1 = self.enc1(x)
        e2 = self.enc2(pool(e1))
        b = self.bottleneck(pool(e2))
        d2 = self.dec2(torch.cat([self.up2a(b), e2], dim=1))
        d1 = self.dec1(torch.cat([self.up2b(d2), e1], dim=1))
        delta = self.head(d1).squeeze(1)
        if self.mode == "hard":
            return u + delta - delta.mean(dim=tuple(range(1, delta.dim())), keepdim=True)
        if self.mode == "free_res":
            return u + delta
        return delta


def system_2d(u: torch.Tensor, c: float, nu: float, dt: float) -> torch.Tensor:
    h, w = u.shape[-2], u.shape[-1]
    ky = torch.fft.fftfreq(h, d=1.0 / h).to(u.device)
    kx = torch.fft.fftfreq(w, d=1.0 / w).to(u.device)
    ky = ky.view(-1, 1).expand(h, w)
    kx = kx.expand(h, w)
    lam = torch.exp((-nu * 4.0 * torch.pi**2 * (kx**2 + ky**2) - 1j * 2.0 * torch.pi * c * (kx + ky) * 0.5) * dt)
    uh = torch.fft.fft2(u, dim=(-2, -1))
    return torch.fft.ifft2(uh * lam, dim=(-2, -1)).real


def make_samples_2d(
    size: int, n_samples: int, sigma_flat: float, rng: np.random.Generator
) -> torch.Tensor:
    ky, kx = np.meshgrid(np.fft.fftfreq(size, d=1.0 / size), np.fft.fftfreq(size, d=1.0 / size), indexing="ij")
    knorm = np.sqrt(kx**2 + ky**2)
    sig = np.full(knorm.shape, 0.5)
    sig[(kx == 0) & (ky == 0)] = 1.0
    sig[(knorm >= 4.0) & (knorm <= 7.0)] = 1.0
    sig[((np.abs(kx) == 1) & (ky == 0)) | ((kx == 0) & (np.abs(ky) == 1))] = sigma_flat
    coeffs = (rng.normal(size=(n_samples, size, size)) + 1j * rng.normal(size=(n_samples, size, size))) * (sig / np.sqrt(2.0))
    return torch.tensor(np.fft.ifft2(coeffs, axes=(-2, -1)).real, dtype=torch.float32)


@dataclass
class CaseMetrics:
    rmse: float
    mass_drift: float
    conserving_err: float


def eval_case(model: nn.Module, u: torch.Tensor, target: torch.Tensor, projected: bool) -> CaseMetrics:
    with torch.no_grad():
        out = model(u)
        if projected:
            mean_dims = tuple(range(1, u.dim()))
            out = out + (u.mean(dim=mean_dims, keepdim=True) - out.mean(dim=mean_dims, keepdim=True))
        err = out - target
        mean_dims = tuple(range(1, err.dim()))
        drift = err.mean(dim=mean_dims)
        cons = err - drift.unsqueeze(-1).unsqueeze(-1) if err.dim() == 3 else err - drift.unsqueeze(-1)
        return CaseMetrics(
            rmse=float(err.pow(2).mean().sqrt()),
            mass_drift=float(drift.abs().mean()),
            conserving_err=float(cons.flatten(1).norm(dim=-1).mean()),
        )


def mass_residual(u: torch.Tensor, out: torch.Tensor) -> torch.Tensor:
    mean_dims = tuple(range(1, u.dim()))
    return out.mean(dim=mean_dims) - u.mean(dim=mean_dims)


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


def bandlimited_upsample(u: torch.Tensor, factor: int) -> torch.Tensor:
    n = u.shape[-1]
    uh = torch.fft.fft(u, dim=-1)
    uh_up = torch.zeros(*uh.shape[:-1], n * factor, dtype=uh.dtype, device=uh.device)
    half = n // 2
    uh_up[..., :half] = uh[..., :half]
    uh_up[..., -half:] = uh[..., -half:]
    return torch.fft.ifft(uh_up, dim=-1).real * factor


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--family", choices=["B", "C"], required=True)
    p.add_argument("--system", choices=["advection", "diffusion", "burgers", "ad2d"], required=True)
    p.add_argument("--n", type=int, default=None)
    p.add_argument("--n-samples", type=int, default=4096)
    p.add_argument("--sigma-flat", type=float, required=True)
    p.add_argument("--hidden-grid", type=int, nargs="+", default=[16, 32])
    p.add_argument("--epochs-grid", type=int, nargs="+", default=[400, 800])
    p.add_argument("--lam-grid", type=float, nargs="+", default=[3.0, 30.0])
    p.add_argument("--seeds", type=int, default=5)
    p.add_argument("--batch", type=int, default=512)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--device", default="cpu")
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    device = torch.device(args.device)
    nd = 1 if args.family == "B" else 2
    n = args.n or (128 if args.family == "B" else 32)
    systems = {
        "advection": build_system("advection", n),
        "diffusion": build_system("diffusion", n),
        "burgers": build_system("burgers", n),
        "ad2d": lambda u: system_2d(u, c=1.0, nu=0.02, dt=0.1),
    }
    system = systems[args.system]

    if nd == 1:
        flat_idx, rich_idx = 1, n // 8
        sig = mode_sigma(n, flat_idx, rich_idx, args.sigma_flat)

        def sample(num: int, rng: np.random.Generator) -> torch.Tensor:
            return make_samples(n, num, sig, rng).to(device)

        def single_mode(idx: int, scale: float) -> torch.Tensor:
            k = np.fft.fftfreq(n, d=1.0 / n).astype(int)
            v = np.zeros((1, n))
            for j in np.where(np.abs(k) == idx)[0]:
                v[0, j] = 1.0
            v /= np.linalg.norm(v)
            return torch.tensor(v * scale, dtype=torch.float32).to(device)

        rng_amp = np.random.default_rng(7)
        amp_ic = make_samples(n, 1, sig, rng_amp).to(device)
        cases: dict[str, tuple[torch.Tensor, torch.Tensor]] = {
            "ood_rich": (u := single_mode(rich_idx, 2.5), system(u.cpu()).to(device)),
            "ood_flat": (u := single_mode(flat_idx, 2.5), system(u.cpu()).to(device)),
            "ood_mass": (u := single_mode(rich_idx, 1.0) + 2.0, system(u.cpu()).to(device)),
            "ood_amp": (u := amp_ic * 2.5, system(u.cpu()).to(device)),
        }
        n_up = n * 2
        system_up = build_system(args.system, n_up)
        up_in = bandlimited_upsample(amp_ic * 2.5, 2).to(device)
        cases["ood_res"] = (up_in, system_up(up_in.cpu()).to(device))
    else:
        def sample(num: int, rng: np.random.Generator) -> torch.Tensor:
            return make_samples_2d(n, num, args.sigma_flat, rng).to(device)

        def single_mode_2d(kx0: int, ky0: int, scale: float) -> torch.Tensor:
            kyy, kxx = np.meshgrid(np.fft.fftfreq(n, d=1.0 / n), np.fft.fftfreq(n, d=1.0 / n), indexing="ij")
            v = np.zeros((n, n))
            for sign in (+1, -1):
                mask = (kxx == sign * kx0) & (kyy == sign * ky0)
                v[mask] = 1.0
            v /= np.linalg.norm(v)
            return torch.tensor(v * scale, dtype=torch.float32).unsqueeze(0).to(device)

        rich = next((int(kx), int(ky)) for kx in range(n) for ky in range(n)
                    if 4.0 <= np.sqrt((kx if kx < n / 2 else kx - n) ** 2 + (ky if ky < n / 2 else ky - n) ** 2) <= 7.0
                    and not (kx == 0 and ky == 0))
        cases = {
            "ood_rich": (u := single_mode_2d(*rich, 2.5), system(u.cpu()).to(device)),
            "ood_flat": (u := single_mode_2d(1, 0, 2.5), system(u.cpu()).to(device)),
            "ood_mass": (u := single_mode_2d(*rich, 1.0) + 2.0, system(u.cpu()).to(device)),
        }

    records: list[RunRecord] = []
    for hidden in args.hidden_grid:
        for epochs in args.epochs_grid:
            for seed in range(args.seeds):
                rng = np.random.default_rng(200_000 * seed + int(args.sigma_flat * 1000) + hidden + epochs)
                u0 = sample(args.n_samples, rng)
                u1 = system(u0.cpu()).to(device)
                u0t = sample(1024, rng)
                u1t = system(u0t.cpu()).to(device)
                for mechanism in ("free", "free_res", "soft", "soft_res", "hard"):
                    lam_list = args.lam_grid if mechanism in ("soft", "soft_res") else [0.0]
                    for lam in lam_list:
                        torch.manual_seed(seed)
                        model = UNet(hidden, nd).to(device)
                        model.mode = (
                            "hard" if mechanism == "hard"
                            else "free_res" if mechanism in ("free_res", "soft_res")
                            else "abs"
                        )
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
                        rec.id_rmse = eval_case(model, u0t, u1t, False).rmse
                        for name, (u_ood, target) in cases.items():
                            rec.cases[name] = eval_case(model, u_ood, target, False)
                        records.append(rec)
                        if mechanism == "free":
                            rec_p = RunRecord(
                                system=args.system, sigma_flat=args.sigma_flat,
                                mechanism="projection", hidden=hidden, epochs=epochs, seed=seed,
                            )
                            rec_p.id_rmse = eval_case(model, u0t, u1t, True).rmse
                            for name, (u_ood, target) in cases.items():
                                rec_p.cases[name] = eval_case(model, u_ood, target, True)
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
