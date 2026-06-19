"""Mac smoke for exp 123 Stage-0 plumbing — raw-ED logging (P1) + shock hook + windows.

Validates the code paths on a small UNTRAINED sim (plumbing only, not stylized-fact
realism). Run: conda run -n ecophys python scripts/smoke_exp123_plumbing.py

  T1 P1            : log_raw_excess_demand flips the LOGGED ED post→pre-impact WITHOUT
                     changing the dynamics (returns bit-identical), meta stamped.
  T2 no-op         : no schedule (None) and a non-firing schedule are bit-identical to
                     baseline → zero behaviour change to existing runs.
  T3 shock effect  : a state_kick at step K perturbs the series only from K onward
                     (no backward leak).
  T4 windows       : writes shocked npz so the --windows estimator can be run on it.
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
N_STEPS, ROLL_SEED, PARAM_SEED = 600, 7, 123


def build(log_raw: bool, n_agents: int = 200) -> EcoMDSimulator:
    cfg_d = yaml.safe_load(CFG_YAML.read_text())["simulator"]
    cfg_d["n_agents"] = n_agents
    cfg_d["price_formation_kwargs"]["log_raw_excess_demand"] = log_raw
    torch.manual_seed(PARAM_SEED)  # identical weights across builds → flag is logging-only
    np.random.seed(PARAM_SEED)
    return EcoMDSimulator(EcoMDConfig(**cfg_d))


def run(sim: EcoMDSimulator, shock: dict | None = None):
    sim._shock_schedule = shock
    sim.eval()
    with torch.no_grad():
        return sim.run(n_steps=N_STEPS, seed=ROLL_SEED, lightweight=True)


def ed_np(t):
    return t.excess_demand.detach().cpu().numpy()


def main() -> None:
    # ── T1: P1 raw-ED logging is dynamics-neutral ────────────────────────────
    t_post = run(build(log_raw=False))
    t_raw = run(build(log_raw=True))
    assert np.array_equal(t_post.log_returns_np(), t_raw.log_returns_np()), \
        "T1 FAIL: raw-ED flag changed the returns (must only change the LOGGED ED)"
    assert not np.allclose(ed_np(t_post), ed_np(t_raw)), \
        "T1 FAIL: logged raw==post (concave impact should make them differ)"
    assert int(t_raw.meta.get("ed_is_raw", -1)) == 1 and int(t_post.meta.get("ed_is_raw", -1)) == 0, \
        "T1 FAIL: ed_is_raw meta not stamped correctly"
    print("T1 P1 OK   : returns bit-identical, logged ED differs (post vs raw), meta stamped")

    # ── T2: shock hook is a no-op unless it fires ────────────────────────────
    base = run(build(log_raw=False), shock=None)
    base2 = run(build(log_raw=False), shock=None)
    assert np.array_equal(base.log_returns_np(), base2.log_returns_np()), \
        "T2 FAIL: rollout is nondeterministic (can't validate no-op)"
    nofire = run(build(log_raw=False), shock={10**9: {"type": "state_kick"}})
    assert np.array_equal(base.log_returns_np(), nofire.log_returns_np()), \
        "T2 FAIL: a schedule with no firing step changed the output"
    print("T2 no-op OK: None and non-firing schedule are bit-identical to baseline")

    # ── T3: a firing state_kick perturbs only from K onward ──────────────────
    K = 300
    shocked = run(build(log_raw=False), shock={K: {"type": "state_kick", "frac": 0.2, "mag": 5.0}})
    rb, rs = base.log_returns_np(), shocked.log_returns_np()
    diff = np.where(rb != rs)[0]
    assert diff.size > 0, "T3 FAIL: state_kick had no effect on the series"
    assert diff[0] >= K - 1, f"T3 FAIL: shock leaked backward (first diff at {diff[0]} < {K})"
    print(f"T3 shock OK: identical before step {K}, perturbed after (first diff @ {diff[0]})")

    # ── T5: price_jump (Stage 2b) injects an exogenous gap, no backward leak ──
    pj = run(build(log_raw=False), shock={K: {"type": "price_jump", "mag": 8.0, "sign": -1.0}})
    rpj = pj.log_returns_np()
    djdiff = np.where(rb != rpj)[0]
    assert djdiff.size > 0, "T5 FAIL: price_jump had no effect on the series"
    assert djdiff[0] >= K - 1, f"T5 FAIL: price_jump leaked backward (first diff @ {djdiff[0]} < {K})"
    sl = slice(K - 2, K + 3)
    gap_amp, base_amp = np.abs(rpj[sl]).max(), np.abs(rb[sl]).max()
    assert gap_amp > 5.0 * base_amp + 1e-9, \
        f"T5 FAIL: no visible gap at K (shocked |r|max {gap_amp:.3g} vs baseline {base_amp:.3g})"
    print(f"T5 price_jump OK: exogenous gap at step {K} "
          f"(|r|max {gap_amp:.3g} ≫ baseline {base_amp:.3g}), no backward leak")

    # ── T4: write shocked npz (raw-ED) for the --windows estimator ───────────
    out = ROOT / "experiments/123_driven_transient/_smoke/results_spx"
    out.mkdir(parents=True, exist_ok=True)
    for i in range(3):  # a few rollouts so windowed means aggregate
        sim = build(log_raw=True)
        sim._shock_schedule = {K: {"type": "state_kick", "frac": 0.2, "mag": 5.0}}
        sim.eval()
        with torch.no_grad():
            tr = sim.run(n_steps=N_STEPS, seed=ROLL_SEED + i, lightweight=True)
        np.savez_compressed(
            out / f"trajectory_rank0_r{i}.npz",
            seed=ROLL_SEED + i, n_steps=N_STEPS, rank=0,
            log_returns=tr.log_returns_np()[1:], volumes=tr.volumes_np()[1:],
            log_prices=tr.log_prices.detach().cpu().numpy(),
            excess_demand=ed_np(tr), ed_is_raw=int(tr.meta.get("ed_is_raw", 0)),
        )
    print(f"T4 wrote   : 3 shocked raw-ED rollouts → {out.relative_to(ROOT)}")
    print("\nALL SMOKE TESTS PASSED. Next: "
          f"score_transfer_law.py --windows {out.parent.relative_to(ROOT)} "
          f"--window 150 --stride 25 --shock-step {K}")


if __name__ == "__main__":
    main()
