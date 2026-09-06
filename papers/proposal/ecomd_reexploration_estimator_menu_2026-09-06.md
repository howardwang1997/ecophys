---
note: >-
  D-1 component deliverable (PI decision D1_07 / killer test KT-A4), authored 2026-09-06 on branch
  paper-d-iclr-2027-completion. Companion to ecomd_reexploration_experiment_plan_2026-09-06.md,
  ecomd_reexploration_contract_v1_2026-09-06.md (§2a, C1-C15) and
  ecomd_reexploration_d1_killer_tests_and_ops_2026-09-06.md (KT-A4). This document freezes the
  through-M estimator menu; nothing here authorizes GPU training, confirmatory measurement, or any
  mutation of the frozen A-2 bundle.
---

# Through-M estimator menu, pinning rules, and the KT-A4 two-estimator audit protocol

## 0. Why an estimator menu is load-bearing

The through-M training arms place the exact combinatorial clearing layer M inside the training
path. M is a piecewise-constant integer map (volume/cash conservation, unit integrality, tick
lattice, priority kernel), so the true objective has zero gradient almost everywhere in the
model parameters — the documented LP/integer zero-gradient obstruction (Minimizing Surrogate
Losses for DFL, 2025; adjudicated in the D-2 evidence map as an implementation constraint, row
"Minimizing Surrogate Losses for DFL (2025) — adjacent, low — LP zero-gradients a.e."). The
same evidence map flags estimator bias as "a confound we must control" (Does "Do Differentiable
Simulators Give Better Policy Gradients?", ICLR 2026 — aliased "Onoda ICLR 2026" in the D-1
contract/ops documents). Contract v1 §2a item 3 therefore requires: the surrogate family is
**preregistered and frozen at D0, never tuned on outcomes**. This document is that
preregistration. KT-A4 (kill probability 0.30, the joint-highest with KT-A1/KT-M2) is the
frozen audit that the cube's through-M attribution results are not artifacts of one surrogate
choice.

## 1. The frozen two-estimator menu

Both estimators are implemented in `ecomd/mechanisms/through_m.py` (new package
`ecomd/mechanisms/`, `__init__.py` present), CPU-only, type-annotated, `mypy --strict` clean.

### 1.1 Primary: straight-through through-M, pinned scale

```python
straight_through_through_m(
    quantities: torch.Tensor,   # resting quantities of the touched level's queue (engine lattice)
    demand: int,                # incoming executable demand at that level
    kernel: Kernel,             # FIFO | RANDOM_UNIT_WITHIN_PRICE
    draws: Sequence[int] | None = None,   # kernel draw stream (required for random_unit)
) -> torch.Tensor
```

- **Forward** = the exact integer clearing `M` (bit-identical to `ReferenceEngine._select_maker`
  in `scripts/lab_asset/matching.py`; FIFO fills by queue position to the cumulative threshold,
  random-unit consumes the recorded draw stream unit by unit with per-draw probability
  proportional to remaining quantity). No relaxation, no smoothing.
- **Backward** = `PINNED_STRAIGHT_THROUGH_SCALE * grad_output` on cleared/executed coordinates,
  **exactly zero** on never-cleared coordinates (bitwise, asserted in tests).
- **Scale** is a module-level frozen constant, `PINNED_STRAIGHT_THROUGH_SCALE = 1.0`. There is
  no learned scale and no caller-configurable scale (a test asserts `scale` is absent from the
  public signature).

### 1.2 Audit: perturb-and-MAP through-M, pinned noise

```python
perturb_and_map_through_m(
    quantities: torch.Tensor,
    demand: int,
    kernel: Kernel,
    seed: int = PINNED_PERTURB_AND_MAP_SEED,   # 20260906 default; overridden by RNG-tree seed
) -> torch.Tensor
```

- **Forward** = exact M applied to perturbed priority scores. The priority score is a
  **kernel-fixed frozen function of the raw flow**: `-queue_position` for FIFO (stable
  descending argsort), the depleting remaining quantity for random-unit (per-draw argmax with
  unit depletion — the perturb-argmax surrogate of probability-proportional-to-remaining draws).
- **Noise**: Gaussian `N(0,1)`, drawn up-front from a seeded CPU `torch.Generator`; sigma is the
  module-level frozen constant `PINNED_PERTURB_AND_MAP_SIGMA = 1.0`. No caller-configurable
  sigma (asserted); the internal `_perturbed_clearing(..., sigma=..., seed=...)` exists solely
  so the frozen σ→0 recovery test can drive the limit.
- **Backward** = unit-scale selection-masked identity (perturb-argmax family surrogate):
  identity on coordinates the perturbed MAP selected, exactly zero elsewhere.
- **Determinism**: identical seeds give bitwise-identical allocations (asserted).

The two estimators are related by design: on deterministic arms (FIFO) the straight-through
estimator is exactly the σ→0 limit of perturb-and-MAP (asserted at σ ∈ {1e-3, 1e-6, 1e-9, 0}),
so a disagreement between them on the audit cell measures the effect of the stochastic
surrogate's smoothing at pinned σ, not an arbitrary hyperparameter gap.

### 1.3 Grounding precedent (in-repo): Paper D's projected-training gauge

Paper D already trained **through a rank-one integer projection** with an exact-forward /
surrogate-backward discipline:

- `scripts/run_constraint_iclr_pde.py` (MLP.forward, `mode == "hard"`):
  `return inputs + raw - raw.mean(dim=-1, keepdim=True)` — forward is the exact projection;
  autograd supplies the surrogate Jacobian.
- `scripts/run_constraint_iclr_pdebench_fno.py`: `project_mass(previous, prediction)` at lines
  484/732/760 (inference-side projection discipline).
- `papers/paper_d_constraints/main.tex`, Proposition "Projected-training gauge" (Prop.
  `prop:gauge`, proof in the appendix): `Π_x(z) = z − P(z − x)` with `Π_x(z + αa) = Π_x(z)`,
  i.e. the enforcement Jacobian is exactly `I − P` — identity on the constraint complement,
  zero on the rank-one gauge direction `span(a)`.
- `scripts/analyze_constraint_iclr_pdebench_enforcement_cube.py`: the R/A cell vocabulary
  (trained × inference enforcement, surgery on locked checkpoints) that the ALPHA cube
  inherits.

**Generalization statement.** The straight-through backward here is the structural
generalization of that `I − P` Jacobian: identity on cleared/executed coordinates (the
constraint-complement analogue), exactly zero on never-cleared coordinates — which are
precisely the fiber directions `U(τ)` of the T2/T3 theory package (theory appendix Part II:
Paper D's rank-one projection gauge is the `|U| = 1` special case). Paper D pinned the scale at
1 (unit Jacobian on the complement); the menu inherits λ = 1.0 as the pinned scale for exactly
that reason — it is the same unit-Jacobian convention under the fiber generalization, chosen
by precedent, frozen before any training, and not tunable.

### 1.4 Relationship to adjudicated external work (D-2 evidence map only)

- Perturb-Argmax/Softmax statistical representation properties (Cohen Indelman & Hazan, 2024,
  arXiv:2406.02180) — cleared collision, high relevance: state-free argmax family, noise law
  alone. The PAM estimator here is the queue/clearing analogue: the perturbation lives on
  kernel-fixed priority scores, not on a simplex, and the forward map is the exact multi-unit
  rationing engine rather than a single argmax.
- Minimizing Surrogate Losses for DFL (2025) — adjacent, low: the LP/integer zero-gradient
  obstruction that makes preregistered surrogate handling mandatory.
- Does "Do Differentiable Simulators Give Better Policy Gradients?" (ICLR 2026; "Onoda ICLR
  2026" in D-1 docs) — adjacent, low: estimator bias as the confound KT-A4 controls.
- Gumbel-Softmax (2016) — background only; not used (Gumbel noise on a simplex is not the
  engine's draw law; the engine's random-unit law is probability-proportional-to-remaining,
  mirrored by the depleting-score PAM).

No citation outside the D-2 evidence map is used in this document.

## 2. Pinning rules (frozen constants)

| Constant | Value | Rationale (frozen, not tuned) |
|---|---|---|
| `PINNED_STRAIGHT_THROUGH_SCALE` (λ) | 1.0 | unit Jacobian on cleared coordinates; inherits Paper D's scale-1 projection Jacobian `I − P` (§1.3) |
| `PINNED_PERTURB_AND_MAP_SIGMA` (σ) | 1.0 | one lattice unit of the priority-score scale (queue positions and remaining quantities are integer lattices; σ = 1 perturbs scores within one priority step) |
| Noise law | `N(0,1)` per score | standard normal on the score lattice; drawn up-front from a seeded CPU generator |
| `PINNED_PERTURB_AND_MAP_SEED` | 20260906 | standalone default only; production seeds come from the frozen RNG tree (below) |
| Priority-score maps | kernel-fixed | FIFO: `-queue_position` (stable descending argsort); random-unit: depleting remaining quantity (per-draw argmax, unit depletion) — frozen functions of the raw flow, not learned, not tuned |

**Seed discipline (contract v1 §2a item 3, verbatim requirement).** The training-time kernel
stream is "one seed-spawned stream, replayed across all through-M arms within the seed (arms
share minibatch order, so draw alignment is exact)". The ST estimator consumes the draw stream
itself (the engine's recorded integer draws); the PAM estimator consumes the stream only
through its seed — the Gaussian noise for the audit retrain is drawn from the same seed-spawned
training-time stream position, so the two estimators see paired kernel randomness within each
seed. The module default `20260906` is a fixture/replay default; any D0-frozen run config must
pass the seed derived from the frozen RNG tree (`spawn(seed_root, ...)` per contract v1 C2) and
that config is hashed before D0. Library+version pin for the generator is torch's CPU
`torch.Generator` (2.11.0, the frozen `ecophys` env), recorded in the run manifest.

**Immutability.** These constants are frozen with this document (D-1). After D0 they are
immutable; any change is a new frozen, hash-recorded amendment per contract v1 C13/C15.

## 3. Fixture competence gate (unit-test evidence)

`tests/test_through_m_estimators.py` — a read-only gate on the **frozen A-2 exit bundle**
`experiments/lab_asset_a2/a2_exit_20260905/` (manifest `fea8b136...9581c`). The suite first
re-verifies the sha256 of all 7 manifest files before any estimator claim, replays both arms in
memory only, and writes nothing. No training, no models, no GPU; the reference engine runs on
CPU exactly as the frozen conformance suite does.

Result: **20 passed in 0.58s** (`conda run -n ecophys python -m pytest
tests/test_through_m_estimators.py -q`); `mypy ecomd/mechanisms/through_m.py` → "Success: no
issues found in 1 source file" (strict); `ruff check` on the new files → "All checks passed!".

| # | Test (pytest node id) | Gate | Result |
|---|---|---|---|
| 1 | `test_frozen_bundle_integrity_read_only` | read-only contract: all 7 manifest sha256 re-verified; record counts 21/22 | PASSED |
| 2 | `test_forward_exactness_reproduces_recorded_allocations[fixture_fifo]` | forward exactness vs recorded execution payloads (maker id, quantity, maker_remaining) | PASSED |
| 3 | `test_forward_exactness_reproduces_recorded_allocations[fixture_random_unit_within_price]` | as above, incl. `allocation_draw` fields (eligible_units, selected_unit) | PASSED |
| 4 | `test_straight_through_forward_is_tape_exact[fixture_fifo]` | public ST forward == recorded per-maker allocation | PASSED |
| 5 | `test_straight_through_forward_is_tape_exact[fixture_random_unit_within_price]` | as above on the random-unit arm | PASSED |
| 6 | `test_perturb_and_map_forward_on_fixtures[fixture_fifo]` | PAM forward reproduces recorded allocation (single-maker touched levels — documented property) | PASSED |
| 7 | `test_perturb_and_map_forward_on_fixtures[fixture_random_unit_within_price]` | as above | PASSED |
| 8 | `test_straight_through_gradient_identity_on_cleared_zero_on_uncleared` | ST gradient semantics: grad = λ·w on cleared, bitwise 0 on uncleared | PASSED |
| 9 | `test_straight_through_random_unit_mask_and_draw_exactness` | ST mask + draw-stream exactness under random-unit kernel | PASSED |
| 10 | `test_straight_through_scale_pinned_no_learned_scale` | no `scale` parameter exists; λ = 1.0; unit backward | PASSED |
| 11 | `test_perturb_and_map_sigma_limit_recovers_exact_mechanism_on_deterministic_arm` | σ ∈ {1e-3, 1e-6, 1e-9, 0} recovers exact FIFO clearing (allocations, fill quantities, queue indices) | PASSED |
| 12 | `test_perturb_and_map_sigma_limit_on_fifo_fixture_recovers_recorded_allocation` | σ→0 on the frozen FIFO fixture reproduces the recorded tape allocation | PASSED |
| 13 | `test_perturb_and_map_same_seed_same_output_and_conservation` | same-seed bitwise determinism; conservation `sum = min(demand, total)` for both kernels | PASSED |
| 14 | `test_perturb_and_map_sigma_pinned` | no `sigma` parameter exists; public == internal at pinned σ | PASSED |
| 15 | `test_perturb_and_map_backward_is_masked_identity` | PAM backward = unit-scale selection-masked identity; zero on unselected | PASSED |
| 16 | `test_cpu_device_guard` | non-CPU tensors raise `ValueError("CPU-only")` for both estimators | PASSED |
| 17 | `test_determinism_repeated_calls_bitwise` | repeated-call bitwise determinism (both kernels, both estimators) | PASSED |
| 18 | `test_random_unit_draw_stream_validation` | draw-stream length/bounds validation errors | PASSED |
| 19 | `test_exact_clearing_matches_engine_multi_maker_rationed_level[fifo-Kernel.FIFO]` | beyond fixtures: exact clearing == live engine on a 3-maker rationed level | PASSED |
| 20 | `test_exact_clearing_matches_engine_multi_maker_rationed_level[random_unit_within_price-Kernel.RANDOM_UNIT_WITHIN_PRICE]` | as above under the random-unit kernel with the engine's own draws | PASSED |

Scope honesty: the two frozen fixtures' touched levels are single-maker, so fixture-forward
exactness for PAM (rows 6-7) is a documented property of those fixtures, not a general
exactness claim; the multi-maker rationed-level cross-check against the live engine (rows
19-20) carries the general forward-exactness burden for `exact_clearing`, and the ST public
estimator shares that forward.

## 4. KT-A4 two-estimator audit protocol (frozen)

**Attack being controlled.** "Through-M results are surrogate artifacts" — the ALPHA family's
joint-highest kill probability (0.30). Skipping the audit hands a hostile referee a guaranteed
kill later (killer-tests doc, KT-A4).

**Audit cell (frozen definition).** Retrain, under the audit estimator (PAM), the mandatory
audit cell:

- **Cell**: the **increment-coordinate, through-M-train, raw-infer** cell — `A10` in the
  Paper-D vocabulary of the killer-tests/ops docs, `Y_increment,through-M,raw` in contract v1
  C3 notation — on the **D1 lab-asset-v3 block, L1 lineage**.
- **Paired seeds**: all **30 paired seeds 11000–11029** (D1_10 namespaces; B1/B2 range),
  sharing data_seed/init_seed/train_seed and the training-time kernel stream with the primary
  (ST) run of the same cell, so the only manipulated factor is the estimator.
- **Everything else inherited verbatim from contract v1**: request-level CRN (C2), K = 8
  inference-kernel draws replayed per cell (same seed-owned streams), conserving-channel
  endpoints (C5), SESOI δ_s = 0.1·Ȳ_R00(s) (C6), 50,000-draw paired seed bootstrap (C1),
  checkpoint hash-lock (C11), one-shot analyzers (C13), record coverage (C14).
- **Compute authorization**: inside the D1_07 envelope — "the two-estimator retrain of the
  audit cell inside the compute envelope [AUTH at D0]". No execution before D0 freeze plus
  explicit PI authorization.

**Instability criteria (frozen, mechanical).** After the audit retrain, recompute the
attribution estimands of contract v1 C3 on the audited stratum (D_contrasts involving the
retrained cell, J = D_00 − D_10 − D_01 + D_11, φ_train, φ_infer) with the same frozen analyzer
macros. The audit fires the downgrade iff either:

1. **Sign-pattern instability**: any preregistered attribution contrast (J, φ_train, φ_infer,
   or the D-contrasts involving the retrained cell) **flips sign across the Holm-corrected
   significance bands** between the ST-trained and PAM-trained versions of the cell (i.e. the
   ST value is significantly positive and the PAM value significantly negative, or vice
   versa — a within-band sign difference is reported but does not fire); or
2. **Ordered-classification instability**: the ordered classification of any affected cell or
   contrast (C9 classes: material_nonadditivity / statistical_nonadditivity_below_or_crossing_
   sesoi / practical_additivity / unresolved) **changes class across the SESOI band** between
   the two estimator versions.

Both criteria are mechanical (no outcome-direction judgment); the comparison is itself outside
all Holm families — it is a preregistered robustness gate on the cube, not a confirmatory
superiority test between estimators.

## 5. Frozen downgrade rule

- **Audit stable** (no criterion fired): report the primary (ST) cube as preregistered; the
  audit result enters the paper as the KT-A4 control (one table/paragraph, both estimators'
  values shown).
- **Audit fires**: the through-M attribution claims are **downgraded to estimator-conditional
  reporting — both estimators' results shown side by side, no pooled or ST-only claim** for
  every estimand touching the retrained coordinate. The downgrade is reported in the
  deviations ledger; it does not silently invalidate the raw-train cells (R-family), which use
  no estimator.
- **Both estimators fail the fixture competence gate** (rows 1-20 above) at any point before or
  during the campaign: the through-M training arms lose their forward-exactness premise, the
  cube **collapses to surgery-only** (zero-training surgery cells on raw-trained checkpoints,
  C11), and the campaign **STOPs pending PI decision** — this is the risk-register route
  "through-M arm credibility" (killer-tests §6) with kill condition confirmed. No repair,
  re-tuning of λ/σ, or estimator substitution is permitted post-D0 without a new frozen,
  hash-recorded amendment.

## 6. Legality statement

This component executed only: reading in-repo files; authoring
`ecomd/mechanisms/__init__.py`, `ecomd/mechanisms/through_m.py`,
`tests/test_through_m_estimators.py`, and this document; and running the read-only CPU test
suite in the `ecophys` conda env. No GPU. No market data. No network fetch. No model training.
No confirmatory endpoint measurement or analyzer run. The frozen bundle
`experiments/lab_asset_a2/a2_exit_20260905/` was consumed strictly read-only (verified
in-suite by manifest sha256 of all 7 files, and by `git status` showing the bundle unmodified);
the estimators execute the reference engine on CPU exactly as the frozen conformance suite
does. No git commit was made; files are left in the working tree for the orchestrator.

## 7. new_references_needing_verification

None. Every external work referenced (Perturb-Argmax/Softmax 2024 arXiv:2406.02180; Minimizing
Surrogate Losses for DFL 2025; Does "Do Differentiable Simulators Give Better Policy
Gradients?" ICLR 2026; Gumbel-Softmax 2016) is already adjudicated in
`papers/proposal/ecomd_reexploration_d2_evidence_map_2026-09-06.md`; no new external source
was wanted or used.
