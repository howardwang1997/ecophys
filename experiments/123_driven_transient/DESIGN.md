# Exp 123 — Driven-transient: is the heavy tail non-equilibrium physics, or a t=0 artifact?

**Status:** DESIGN (pre-registered). Author: reviewer-2 partner, 2026-06-18.
**Depends on:** `papers/paper_a_methods/burnin_artifact_finding_2026-06-18.md` (the refutation),
`papers/paper_a_methods/phase0_burnin_blastradius_2026-06-18.md` (blast radius = project-wide).
**Decides:** whether Paper A can make the positive frontier claim
*"market fat tails are a non-equilibrium / driven transient; the stationary state is light-tailed."*

---

## 1. The one question this experiment answers

Phase 0 established: the model's heavy tail (Hill ≈ 1.3) is a ~20-step transient; the stationary
tail is light (Hill ≈ 4–12). Two mutually exclusive readings:

- **(P) Physics.** The heavy tail is a genuine *non-equilibrium relaxation* phenomenon — it appears
  whenever the system is **driven out of its steady state**, and crashes are exactly such driving.
  → cube law is a signature of being off-equilibrium. **Publishable frontier result. C2+C3.**
- **(A) Artifact.** The heavy tail only appears **once**, at t=0, because the model is initialized
  far from its attractor (`init_state_scale=0.1`, an arbitrary startup). It never recurs. → it is a
  numerical startup artifact; dressing it as physics is overclaiming. **No frontier claim.**

The discriminator: **drive the system out of steady state with a controlled shock and see whether
the cube-law tail re-emerges and then relaxes — with the SAME ζ_ED signature as the t=0 burn-in.**

If the shock-driven transient reproduces the burn-in transient ⇒ same relaxation mechanism ⇒ (P).
If a steady-state system never reproduces the heavy tail under driving ⇒ (A).

---

## 2. Protocol

Single-rollout-with-mid-shock (avoids hidden-state carry across `run()` calls; `run()` re-inits
`price_state`/`h_regime`/`h_agent`/`h_global`/`_fundamental` each call, so a fresh call cannot
"continue" steady state — the shock must be injected *inside* one rollout).

```
t ∈ [0,        T_burn)      equilibration   — DISCARD (the known artifact)
t ∈ [T_burn,   T_shock)     steady state    — CONTROL window  (expect light tails)
t = T_shock                 SHOCK injected
t ∈ [T_shock,  T_shock+τ)   relaxation      — TEST window     (does the heavy tail revive?)
t ∈ [T_shock+τ, T_end)      re-equilibration— RECOVERY window (does it relax back to light?)
```

Defaults: `T_burn=500`, `T_shock=2000`, `T_end=8000` (≥3 independent shock-relaxation cycles also
allowed: inject at 2000/4000/6000 to get 3 transients per rollout, cheaper statistics).

### Shock channels (physically motivated; primary = news, run all three as arms)

| arm | knob | meaning | how |
|---|---|---|---|
| **S1 news** (primary) | `self._fundamental` | information shock | add Δf = m·σ_f at T_shock |
| **S2 liquidity** | γ / `asym_drag_alpha` | liquidity vacuum (crash) | drop γ→γ/κ_L for a window |
| **S3 coordinated** | state s | herding kick | displace a fraction q of agents by Δs |

Dose: each arm at magnitudes m ∈ {1, 3, 10} (in units of the relevant scale) → dose-response.
A shock that is too small to perturb the steady state is the implicit null at the low end.

### Control (pre-registered surrogate-kill analog)

A **no-shock** rollout of identical length and seeds. The TEST/RECOVERY windows must look like the
CONTROL windows under the null. Any "revival" must beat the no-shock window's own fluctuation.

### Measurement

- **Plumbing P1 (required first):** log the **raw pre-impact** excess demand. The finding showed
  `price_formation.py:340-357` overwrites `excess_demand` with the post-impact value before it is
  recorded (line 454). Add an aux field `excess_demand_raw` (pre-`_concave_impact`) and thread it
  through `TrajectoryRecorder` → `EcoMDTrajectory` → `run_large --save-trajectory`. ζ_ED must be
  measured on the raw quantity (the theory's ζ_ED), with α_ret on returns as the transfer check.
- **Windowed tail estimator:** sliding-window Hill α(t) over both |raw_ED| and |ret|, window
  W=500 steps, stride 100, using the upgraded `scripts/score_transfer_law.py::measure_zeta_mode`
  (Hill α-vs-k curve + 200-bootstrap 95% CI + transfer ratio α_ret/α_raw). Extend it to accept a
  time-window argument (new `--windows` mode) — small wrapper, no new estimator.
- **Burn-in template:** the t∈[0,T_burn) Hill-vs-time curve is the **reference transient**. The
  post-shock curve is compared to it (H4).

---

## 3. Pre-registered hypotheses + decision gate

Bands chosen before the run. ζ_ED cube-law target = 3/2; "light" = α ≥ 4.

| | claim | pass condition |
|---|---|---|
| **H1** | steady state is light (control) | CONTROL-window α_raw ≥ 4, bootstrap CI lower bound > 2, reproducible over ≥30 seeds |
| **H2** | shock revives the heavy tail | TEST-window α_raw dips to ≤ 2 (toward 3/2), CI excludes the CONTROL value; effect grows with dose m |
| **H3** | the revival is transient | RECOVERY-window α_raw returns to ≥ 4 within τ_relax; heavy tail is not a new steady state |
| **H4** | same mechanism as t=0 burn-in | shock-driven α_raw(t) trajectory matches the burn-in template in value (3/2±) and relaxation shape (τ within 2×) |
| **H5** | transfer law operates in-regime | during TEST, α_ret ≈ α_raw/δ (δ=0.5 ⇒ ratio ≈ 2), the lemma where it matters |

**Decision:**

- **H1 ∧ H2 ∧ H3 ∧ H4 pass → reading (P).** The heavy tail is a genuine driven non-equilibrium
  transient. **Positive frontier paper is EARNED.** Spine: stationary-light + driven-cube-law +
  α=ζ/δ as the decomposition + crash = the driving (C3). H5 is the bonus that ties the lemma in.
- **H2 fails (no revival at any dose) → reading (A).** Heavy tail is a t=0 startup artifact. Fall
  back to the honest diagnostic frontier (no transient-physics claim); the burn-in finding becomes
  a rigor/methods section, not the headline.
- **H2 passes but H4 fails (revival ≠ burn-in template) → ambiguous.** Two different heavy-tail
  origins; needs a mechanism study before any claim. Do not publish the unification.

This gate is binding (per `feedback_preregistration`): no post-hoc band widening; if it lands in
the ambiguous cell, escalate via the A→B→C ladder, do not narrate it as a pass.

---

## 4. Scale, cost, sequencing

Per `project_h20_fleet_scheduling`: ~62 min/cfg/card at N=10⁴, n_steps=4000 (exp 114). This run is
n_steps=8000 (≈2×) ⇒ ~124 min/cfg/card.

- **Stage 0 (plumbing, Mac):** P1 raw-ED logging + the `--windows` estimator mode + a smoke test
  at N≤500 to confirm the burn-in template renders and the windowed Hill runs. No GPU.
- **Stage 1 (earns-or-kills, GPU, ~1 asset):** spx, S1-news, m∈{1,3,10} + no-shock control,
  n=30 seeds ⇒ 4 cells × 30 = 120 cfg × 124 min / (8 cards) ≈ **31 h**. Answers H1–H4 for the
  primary arm. **This is the decision run** — do it before anything else GPU.
- **Stage 2 (only if Stage 1 → P):** add S2-liquidity + S3-coordinated arms and a 2nd asset
  (ndx or gold) for robustness + dose-response figure. ~another 40–60 h.
- **R1 piggyback:** re-run the existing 114 cells (baseline + concave, 5 assets) with
  `--save-trajectory` + warmup discard to nail the Phase-0 magnitude. Independent of 123; same
  driver. ~one fleet window.

Trim if a window is tight: Stage 1 with the 3-shocks-per-rollout variant (inject at 2000/4000/6000)
gives 3 transients/cfg ⇒ n=30 seeds × 1 dose still yields 90 transients from 30 cfg ≈ 8 h.

---

## 5. Prerequisites checklist (before any GPU)

- [ ] P1: `excess_demand_raw` logged pre-impact (`price_formation.py`), threaded to npz.
- [ ] Shock-injection hook in `EcoMDSimulator.step()` — a scheduled `{step: shock_spec}` map or a
      callback; must be a no-op when unset (zero behaviour change to all existing runs).
- [ ] `--windows` mode in `score_transfer_law.py` (sliding-window Hill + CI + transfer ratio).
- [ ] Mac smoke (N≤500): burn-in template + one injected shock renders a Hill-vs-time dip-and-recover.
- [ ] Config family `experiments/123_driven_transient/config_*` generated (asset × arm × dose × seed).
- [ ] Pre-register this DESIGN.md (commit SHA) before the GPU run — arXiv-style timestamp per
      `feedback_preregistration`.

---

## 6. Why this is the right experiment (reviewer-2 note to self)

It is falsifiable in the direction that hurts: if the model has no driven heavy tail, H2 fails and
we cannot claim the physics — and that outcome is fully possible (the model may genuinely relax to
a light-tailed Gaussian-by-CLT steady state with no mechanism to re-fatten under driving, since
`het_mass` is off). The experiment is designed so the *attractive* story must survive a control and
a dose-response and a template-match before we are allowed to write it. That is the bar that turns
the burn-in finding from a retraction into a result.
