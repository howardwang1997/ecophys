# EcoMD improvement paths — beyond v4

This file tracks the **remaining** physical / framework / model improvements
the user can pursue after the v4 batch (069-076) completes. Items listed
in priority order (impact × tractability). All Tier-A items shipped in v4 —
see commits on `feature/gradient-potential-v4` and `feature/adiabatic-collective`.

Last updated: 2026-05-04 evening, after pivot from "implement scalar potential"
discovery (gradient-of-potential force was already in v0 by design).

## Status snapshot

| Tier | Item | Status |
|---|---|---|
| A1 | gradient-of-potential force `F = -∇U_θ(s)` | **DONE in v0** (potentials.py:502-520) |
| A2 | γ·dt regime tuning to overdamped | **DONE in 069/074/075/076** (γ=10 = γ·dt=0.1) |
| A3 | FDT diagnostic code | **DONE part 1** (U(t) logging in feature/gradient-potential-v4); part 2 below |
| A4 | energy conservation sanity test | **DONE** (tests/test_energy_logging.py:test_T0_no_dissipation_potential_drift) |
| A5 | AR(1)-residual honest reporting framework | **DONE** (scripts/diagnose_ar1_residual_*.py) |
| **B1** | **Adiabatic timescale separation** | **DONE in v4** (commit on feature/adiabatic-collective) |
| **B2** | **Collective coordinate price formation** | **DONE in v4** (CollectivePrice in price_formation.py) |
| B3 | Underdamped Langevin (explicit velocity) | TODO |
| B4 | BAOAB symmetric splitting integrator | TODO |
| B5 | FDT-respecting correlated noise | TODO |
| C1 | Tensor-parallel sharding on N | TODO (paper-A scaling story) |
| C2 | Stratonovich + Milstein integrator | TODO |
| C3 | Equivariant GNN redo (MACE-lite v2) | TODO |
| C4 | Hopfield-style associative memory | TODO |
| C5 | Surrogate baselines (IID/GARCH/shuffled) | TODO (Paper-A required) |
| D | Stochastic field theory (DDFT) — paradigm switch | TODO (kills Paper A) |

---

## B3 — Underdamped Langevin (explicit velocity variable)

Currently: overdamped form `s_{t+1} = s + F/γ·dt + √(2T·dt/γ)·ε`. No
momentum. Per-step relaxation `γ·dt = 0.01` (or 0.1 with the v4 γ fix)
puts the system in an effectively-ballistic regime *without* the formal
momentum / kinetic-energy bookkeeping that real underdamped Langevin has.
This is the worst of both worlds physically.

**Right form**:
```
v_{t+1} = v_t + (F − γ v_t)/m · dt + √(2γT/m²·dt)·ε
s_{t+1} = s_t + v_{t+1} · dt
```
The (s, v) joint state is Markovian. Total energy `E = U(s) + ½ m v²` is
the right book-keeping quantity. T_eff naturally appears as the
fluctuation-dissipation coefficient.

**Effort**: 1 week Mac engineering.
- New `UnderdampedLangevin` integrator class in `ecomd/physics/integrator.py`
- `IntegratorStep` adds `v` field
- `EcoMDConfig.integrator: str = "overdamped"` defaults preserve back-compat
- `EcoMDConfig.mass: float = 1.0` (per-agent or scalar)
- Tests: total energy conservation in T=0 limit (KE+U), FDT relation in
  thermal equilibrium

**Benefit**: Paper-B physics chain becomes textbook-standard. T_eff(ω)
measurement via FDT is well-posed. Critical scaling claims (A1 in plan v3)
get clean physical interpretation.

**Risk**: BPTT memory ~2× (carrying v alongside s). May force chunk_steps
reduction unless tensor-parallel is also done.

## B4 — BAOAB symmetric splitting integrator

Leimkuhler & Matthews 2013. Replaces Euler-Maruyama with a 5-stage
symmetric splitting:
```
B: v ← v + F/m · dt/2          (half kick)
A: s ← s + v · dt/2             (half drift)
O: v ← v · exp(-γ·dt/m) + √(T(1-exp(-2γ·dt/m))/m) · ε   (Ornstein-Uhlenbeck)
A: s ← s + v · dt/2             (half drift)
B: v ← v + F/m · dt/2           (half kick)
```
Configurational error O(dt²) instead of O(dt) for Euler-Maruyama.

**Effort**: 3 days Mac (after B3 underdamped is done).

**Benefit**:
- Long-rollout stability (no spurious heating)
- FDT relation numerically more accurate
- Simulator output less sensitive to dt choice

**Coupling**: requires B3 (underdamped) first; doesn't apply to overdamped.

## B5 — FDT-respecting correlated noise

Currently: noise η ~ N(0, I) iid per step. For full FDT consistency in
non-Markovian or memory-dependent dissipation, the noise should have
correlation structure matching the dissipation kernel:
```
⟨η(t) η(t')⟩ = (2T/γ) · K(t-t')
```
where K is the memory kernel. With Markovian γ (no memory), K = δ → iid is correct.

**Effort**: 1 week if we want to add memory kernel; trivial if Markovian
(already correct).

**Benefit**: only matters if we add memory (e.g. fractional Langevin).
Skip for now.

## C1 — Tensor-parallel sharding on N

Currently `train_distributed.py` is data-parallel-over-iterations: each
rank runs full N×chunk; gradients all-reduced. **Per-card memory ≡
NPROC=1.** Hard ceiling at N=10K, chunk=24 on H20 96GB.

True tensor-parallel: shard the agent axis across cards. Pair forces
require cross-card all-reduce of partial pair sums. Communication cost
~ O(N·d/√P) per step where P = number of cards, modest on NVLink.

**Effort**: 2-3 weeks Mac engineering + H20 testing.

**Benefit**: N → 10⁵ on 8×H20 NVLink. **Paper-A scaling demonstration**
becomes the unique selling point vs Tóth-Lux-Sornette 2018 (their N=10⁴).

**Priority**: HIGH for Paper-A flagship if tier B improvements don't
themselves move stylized facts pass count meaningfully.

## C2 — Stratonovich + Milstein integrator

Currently Itô interpretation, additive noise. With multiplicative noise
(e.g., `sigma_ed > 0`), Itô vs Stratonovich differ by an O(dt) drift
correction. Milstein integrator is needed for weak-2.0 accuracy with
multiplicative noise.

**Effort**: 1 week (mostly numerical care + tests).

**Benefit**: clean physical interpretation when σ_ed is enabled.

## C3 — Equivariant GNN redo (MACE-lite v2)

v1 MACE-lite tried in 2026-04-22, **failed at 0-4/11 across 8 ablations**
because:
- force magnitude 60-190× too small (per-node readout averaged out
  contributions)
- k-NN gave biased local force estimator (vs SPS's unbiased random-pair)

These are fixable now that we have the v4 architecture details:
- F = -∇U readout via autograd (not per-edge MLP readout)
- k-NN with graph-attention weights (learned, not Euclidean)
- Message-passing with gradient-respecting aggregation

**Effort**: 2 weeks Mac.

**Benefit**: SE(3)-like equivariance for the latent space. May help
permutation+translation symmetry argument in Paper A.

**Risk**: same failure modes as v1 if not careful. Lower priority unless
v4 fixes don't move pass count.

## C4 — Hopfield-style associative memory replacing GRU regime

Current regime GRU (`regime_latent.py`) is a black box. Modern Hopfield
networks (Ramsauer et al. 2020) are interpretable: regime states are
attractors of an energy landscape. Same expressivity, transparent dynamics.

**Effort**: 1 week Mac.

**Benefit**: Paper-B regime-transition analysis becomes physical (regime
transitions = saddle-point crossings on the Hopfield energy surface).

## C5 — Surrogate baselines (Paper-A required)

Plan v3 §6.2 commits to: IID Gaussian, GARCH(1,1), shuffled returns.
Each must score ≤2/11 stylized facts for EcoMD to be non-trivial.

**Effort**: 2 days. Mostly: implement scoring on these synthetic series.

**Status**: NOT STARTED. **Must be done before any paper draft.**

## D — Stochastic field theory / DDFT (paradigm switch)

Replace N-particle MD with stochastic PDE on density field ρ(s, t):
```
∂ρ/∂t = ∇·(D ∇ρ + ρ ∇U_eff[ρ]) + noise
```
Standard non-equilibrium statistical mechanics. Connects directly to:
- Mantegna & Stanley 1995 (volatility scaling)
- Tóth-Lux-Sornette 2018 (Boltzmann form)
- Phase transitions & MIPS (motility-induced phase separation)

**Effort**: 2-3 months. Major rewrite.

**Benefit**: Paper B Nature Physics flagship becomes textbook-standard.

**Cost**: kills Paper A's "differentiable simulator" angle. Might force
splitting Paper A into two papers (architecture + scaling baseline).

**Recommendation**: only do if v4 + B3/B4/C1 still don't get Paper B's
A1 claim above 70% confidence by Wk 30.

---

## Recommended sequencing

**Wk 19-22 (now → 4 weeks)**: collect 069-076 results. Decide based on
Branch A/B/C scoreboards which v4 improvement (γ-damping, rr_s120,
adiabatic, collective) actually moves the AR(1)-residual pass count
(not just the raw pass count).

**Wk 23-24 (5-6 weeks)**: if v4 isn't enough, implement **B3 underdamped
Langevin** as the next force multiplier. This is the highest-leverage
remaining structural change.

**Wk 25-28 (7-10 weeks)**: implement **C1 tensor-parallel** if N becomes
the binding constraint. Paper A arXiv preprint at Wk 28 (per plan v3 M3).

**Wk 29-34**: **C5 surrogate baselines** (mandatory) + cross-asset
replication on BTC/ETH (mandatory for Paper A main table).

**Wk 35+**: if Paper B physics measurements (T_eff scaling, Jarzynski)
need it: **B4 BAOAB integrator**, then **D field theory** as the
Nature-Physics-grade reformulation.

---

## What v4 (this overnight batch) actually changes

Branches launched 2026-05-04 evening:
- **Branch A** (`diagnostics/autocorr-ar1`, 410 cfgs): config sweeps to
  confirm γ damping at 30 seeds + rr_s120 at 30 seeds + ablate Hawkes/jumps.
- **Branch B** (`feature/gradient-potential-v4`, 150 cfgs + code): U(t)
  energy logging end-to-end + clean-physics ablation matrix.
- **Branch C** (`feature/adiabatic-collective`, 210 cfgs + code): adiabatic
  timescale separation + collective coordinate price formation.

Total tonight: **770 configs across 3 branches**, est ~6-9h on 8-card H20.

Expected outcomes (one of):
- **Best case**: v4 improvements (γ damping + adiabatic + collective +
  clean-physics) push honest (AR(1)-residual) pass count from current 4.15/11
  to 6-7/11. Paper A becomes a real submission.
- **Realistic case**: 4.5-5.5/11 honest. Architecture is honest but not
  beating GARCH by enough for top-tier ML venue. Pivot to ICML 2027 +
  workshop submission for NeurIPS 2026.
- **Worst case**: 4.0/11 or lower. v4 fixes don't matter. Need B3+C1 then
  re-evaluate.
