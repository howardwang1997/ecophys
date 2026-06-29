"""Mac smoke for exp 125 — the two new dynamics-level shock channels.

Validates temperature_spike / liquidity_drop on a small UNTRAINED sim (plumbing
only, not realism). Run: conda run -n ecophys python scripts/smoke_exp125_channels.py

  T7 temp spike   : a firing temperature_spike at K perturbs only from K onward
                    (no backward leak) and RAISES post-shock return volatility.
  T8 liq drop     : a firing liquidity_drop at K perturbs only from K onward and
                    RAISES post-shock return volatility (thinner market).
  T9 reset        : after a firing dynamics shock, a fresh non-firing rollout is
                    bit-identical to baseline → _shock_dyn resets per rollout.
  T10 duration    : dur>1 keeps the multiplier active across the window (a longer
                    dur perturbs at least as early and persistently as dur=1).
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import torch
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from ecomd.models.ecomd import EcoMDConfig, EcoMDSimulator  # noqa: E402

torch.set_num_threads(1)  # Mac determinism (see memory: mac-blas-determinism)
CFG_YAML = ROOT / "experiments/114_concave_confirm/config_btcusdt_concave_d045_seed0.yaml"
N_STEPS, ROLL_SEED, PARAM_SEED, K = 600, 7, 123, 300


def build(n_agents: int = 200) -> EcoMDSimulator:
    cfg_d = yaml.safe_load(CFG_YAML.read_text())["simulator"]
    cfg_d["n_agents"] = n_agents
    torch.manual_seed(PARAM_SEED)
    np.random.seed(PARAM_SEED)
    return EcoMDSimulator(EcoMDConfig(**cfg_d))


def run(shock: dict | None = None):
    sim = build()
    sim._shock_schedule = shock
    sim.eval()
    with torch.no_grad():
        return sim.run(n_steps=N_STEPS, seed=ROLL_SEED, lightweight=True).log_returns_np()


def post_vol(r):
    return float(np.std(r[K:K + 80]))


def first_diff(rb, rs):
    d = np.where(rb != rs)[0]
    return int(d[0]) if d.size else -1


def main() -> None:
    base = run(None)
    bvol = post_vol(base)

    # ── T7: temperature_spike ────────────────────────────────────────────────
    temp = run({K: {"type": "temperature_spike", "mult": 6.0, "dur": 1}})
    fd = first_diff(base, temp)
    assert fd >= K - 1, f"T7 FAIL: temperature_spike leaked backward (first diff @ {fd} < {K})"
    assert post_vol(temp) > bvol + 1e-9, \
        f"T7 FAIL: temperature_spike did not raise post-shock vol ({post_vol(temp):.3g} vs {bvol:.3g})"
    print(f"T7 temp OK : first diff @ {fd}, post-vol {post_vol(temp):.3g} > baseline {bvol:.3g}")

    # ── T8: liquidity_drop (dose 10 → γ × 0.1) ───────────────────────────────
    liq = run({K: {"type": "liquidity_drop", "mult": 0.1, "dur": 1}})
    fd = first_diff(base, liq)
    assert fd >= K - 1, f"T8 FAIL: liquidity_drop leaked backward (first diff @ {fd} < {K})"
    assert post_vol(liq) > bvol + 1e-9, \
        f"T8 FAIL: liquidity_drop did not raise post-shock vol ({post_vol(liq):.3g} vs {bvol:.3g})"
    print(f"T8 liq OK  : first diff @ {fd}, post-vol {post_vol(liq):.3g} > baseline {bvol:.3g}")

    # ── T9: per-rollout reset (the shock does not leak into the next rollout) ──
    nofire = run({10**9: {"type": "temperature_spike", "mult": 6.0, "dur": 50}})
    assert np.array_equal(base, nofire), \
        "T9 FAIL: a non-firing dynamics schedule changed the output (or _shock_dyn leaked)"
    print("T9 reset OK: non-firing dynamics schedule bit-identical to baseline (per-rollout reset)")

    # ── T10: duration — dur=20 stays active across the window ─────────────────
    temp_d1 = run({K: {"type": "temperature_spike", "mult": 3.0, "dur": 1}})
    temp_d20 = run({K: {"type": "temperature_spike", "mult": 3.0, "dur": 20}})
    assert not np.array_equal(temp_d1, temp_d20), \
        "T10 FAIL: dur=20 produced the same series as dur=1 (window not applied)"
    # the dur=20 run should differ from baseline across more of [K, K+20] than dur=1
    span_d1 = int(np.sum(base[K:K + 20] != temp_d1[K:K + 20]))
    span_d20 = int(np.sum(base[K:K + 20] != temp_d20[K:K + 20]))
    assert span_d20 >= span_d1, f"T10 FAIL: dur=20 perturbed fewer steps ({span_d20}) than dur=1 ({span_d1})"
    print(f"T10 dur OK : dur=20 perturbs ≥ dur=1 over [K,K+20] ({span_d20} ≥ {span_d1} steps)")

    print("\nALL exp-125 CHANNEL SMOKE TESTS PASSED.")


if __name__ == "__main__":
    main()
