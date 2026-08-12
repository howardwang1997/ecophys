# Experiment 144 — theory-reduction witnesses

**Frozen:** 2026-08-12  
**Branch:** `theory-exploration-nmi-ncs-v1`  
**Parent theory audit:** `67acfb077`  
**Scientific role:** adversarial negative controls only; no theorem, novelty or venue gate can pass

## 1. Questions

Experiment 144 checks two exact calculations before more theory time is spent:

1. Does the simplest multi-mechanism “identifiability gain” reduce exactly to a stacked observability Gramian?
2. Can fixed memoryless stochastic operators produce a nonzero swapped-order response with no adaptive state?

The first witness attacks NMI-T1. The second falsifies the naive version of NCS-M1. Confirming either witness is a
negative result for novelty/identification, not evidence for a paper claim.

## 2. Frozen fixtures

All values are fixed in `config.yaml` and evaluated in float64.

### W1 — stacked observability

Use a two-dimensional state and two one-row observation/mechanism matrices

\[
C_1=(1,0),\qquad C_2=(0,1).
\]

Compute `Gamma_i=C_i^T C_i` and `Gamma_stack=Gamma_1+Gamma_2`. Expected exact properties:

- `rank(Gamma_1)=rank(Gamma_2)=1`;
- `rank(Gamma_stack)=2`;
- eigenvalues of `Gamma_stack` are `(1,1)`;
- `Gamma_stack` equals the ordinary Gramian of vertically stacking `C_1,C_2`.

This fixture deliberately supplies no distinction between a “mechanism excitation margin” and standard stacked
observability. The outcome is `CONFIRMED_GENERIC_REDUCTION` only if every property holds at absolute tolerance
`1e-12`.

### W2 — order effect without adaptation

Use row-distribution convention with

\[
P_A=\begin{bmatrix}0.9&0.1\\0.2&0.8\end{bmatrix},\quad
P_B=\begin{bmatrix}0.6&0.4\\0.05&0.95\end{bmatrix},\quad
p_0=(1,0),\quad y=(0,1)^\top.
\]

Both matrices must be nonnegative and row stochastic. Compute

\[
r_{AB}=p_0P_AP_By,\qquad r_{BA}=p_0P_BP_Ay,\qquad
\Delta_{AB}=r_{AB}-r_{BA}.
\]

Expected values are `r_AB=0.455`, `r_BA=0.38` and `Delta_AB=0.075`. The fixture has no learned parameters, hidden
adaptive update or time-varying transition law. The outcome is `CONFIRMED_ORDER_EFFECT_WITHOUT_ADAPTATION` only if
valid stochasticity and all expected values hold at absolute tolerance `1e-12`.

## 3. Frozen decision rule

| W1 | W2 | Overall decision | Interpretation |
|---|---|---|---|
| confirmed | confirmed | `NEGATIVE_CONTROLS_CONFIRMED` | toy rank gain is generic; raw order effect cannot identify adaptation |
| otherwise | any | `IMPLEMENTATION_OR_SPEC_FAILURE` | diagnose code/specification; do not reinterpret candidate status |
| any | otherwise | `IMPLEMENTATION_OR_SPEC_FAILURE` | diagnose code/specification; do not reinterpret candidate status |

There is no scientific `PASS` state. A confirmed result leaves NMI-T1 and NCS-M1 in `ATTACKING`; it does not by
itself retire the narrowed candidates because their stricter formulations include non-equivalence and
excess-over-frozen obligations.

## 4. Artifact and reproducibility contract

- Runner path: `experiments/144_theory_reduction_witnesses/run_witnesses.py` (implemented only after this freeze).
- Raw output: `experiments/144_theory_reduction_witnesses/artifacts/raw/witnesses.json`.
- Manifest: SHA-256, git SHA, dirty-tree flag, Python/NumPy versions, platform, seed and wall time.
- The formal runner must refuse a dirty checkout and a git SHA different from its implementation freeze.
- The formal result is executed once. A repair uses Experiment 145; raw Experiment 144 is never overwritten.

## 5. Resource and data boundary

- Data: constants in `config.yaml` only; no market, user, paid, R2, sealed or historical experiment data.
- Network: forbidden during the run.
- Compute: Mac CPU, one process, expected under one second; zero GPU-hours.
- V100-A, V100-B and RTX2060 are not contacted.
- No stochastic result is inferred from the single declared seed; the seed exists only for manifest completeness.
