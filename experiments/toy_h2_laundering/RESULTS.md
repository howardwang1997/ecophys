# Toy probe results: conservation-constraint attribution under data flatness

Date: 2026-08-27

Status: **bounded CPU probe under the PI's 2026-08-27 blanket authorization (all public data,
three servers); generated data only; Mac CPU; engineering probe for the out-of-scope question
contract — not route evidence, not a confirmation asset**

Provenance: `scripts/toy_h2_laundering.py`; results JSON in this directory (`results_lam30.json`,
`results_lam3.json`, `results.json` first run); git SHA and full config embedded in each JSON.
Design: 8-cell relaxation chain `A = I + 0.1·L`; MLP(8→64→64→8, tanh); Adam 3e-3, 400 epochs,
batch 512, 4096 samples, 5 seeds per cell; training data flat along the smoothest non-uniform
mode (`σ_f` swept); OOD probes along rich mode, flat mode, and a mass-shifted input.

## Factorial arms

`free` (absolute output), `free_res` (residual output, no constraint), `soft` (absolute +
λ·mass-residual²), `soft_res` (residual + penalty), `hard` (residual + tangent projection:
exact conservation by architecture), `projection` (post-hoc uniform correction of `free`).

## Headline numbers (σ_f = 0.03, OOD along the flat mode; conserving-channel error norm;
target mass drift = 0)

| Arm | λ=30 | λ=3 | mass drift (λ30/λ3) |
|---|---:|---:|---:|
| free | 0.800 | 0.800 | 0.074 / 0.074 |
| free_res | 0.093 | 0.093 | 0.002 / 0.002 |
| soft | **1.277** | 0.852 | 0.030 / 0.045 |
| soft_res | 0.091 | 0.094 | 0.001 / 0.000 |
| hard | 0.096 | 0.096 | 0.000 / 0.000 |
| projection | 0.800 | 0.800 | 0.000 / 0.000 |

## Verdicts against the frozen hypotheses

1. **H1 (constraint as inductive bias): REFUTED in this class — by a confound.** The hard
   arm's 10× flat-channel advantage is fully reproduced by `free_res` (0.093 vs 0.096); the
   constraint's marginal contribution over residual parameterization is only exact zero drift
   (vs `free_res`'s 0.002). This is a matched-pair attribution (identical ID error ~0.002,
   identical architecture).
2. **H2 (error laundering): SURVIVES in a narrower form than formulated.** Only the
   strong-penalty absolute-output combination launders (1.277 vs 0.800 conserving error while
   cutting drift 0.074→0.030); at λ=3 the signature vanishes; in residual form it never
   appears. Laundering is a *penalty-strength × parameterization* phenomenon, not generic.
3. **H3 (mechanism-level sign): replaced.** The dominant causal variable for OOD
   conserving-channel error is **output parameterization (absolute vs residual), not constraint
   mechanism**; constraint level governs only the constraint observable itself.
4. **Decoupling theorem (linear case): empirically confirmed.** `projection` reproduces
   `free`'s conserving error to the third decimal at every σ_f while zeroing drift — the exact
   prediction of the closed-form decoupling argument; a built-in negative control.
5. **ID-matching caveat**: `free` (0.0076) vs residual family (0.002) are not ID-matched;
   cross-parameterization claims must await the frontier protocol. Within the residual family
   all arms are ID-matched, which is where verdicts 1--3 live.

## Consequence for the F3 subject (revision, not overwrite)

The frozen F3 predicted mechanism-level redistribution with a flatness onset. The probe shows
the redistribution exists but the driver is parameterization, with constraint effects confined
to (a) the constraint observable and (b) a strong-soft-penalty laundering channel. Revised F3
(child v2): **"In learned simulators with exact known invariants, matched-pair attribution
separates the OOD benefit attributed to conservation constraints into an output-parameterization
component (dominant, ~10× on data-flat channels in the toy) and a constraint component
(constraint observable only); widely used absolute-output soft penalties can launder error into
conserving channels at strong penalty weights. The audit measures this decomposition across ≥3
system families at matched ID error and budget."** First collision check on the revised claim
(2026-08-27): the residual/skip-connection literature concerns deep-net training generally; no
matched-pair attribution of constraint benefits in learned simulators was found.

## Re-estimated full-T0 (uncalibrated)

Toy-to-real transfer of the attribution design (validated in toy): higher confidence now
(~75%); novelty of the *revised* claim survived first check; remaining risks: PDE-family
idiosyncrasies where constraints bind differently (e.g., non-negativity, flux forms),
frontier-overlap adequacy, solo completion on the authorized servers, and sign decisiveness at
matched-ID. **Revised interval: lower 15% / point 30% / upper 45%.** The lower bound now
reaches the activation brake, conditional on the three-family audit protocol passing its D0
freeze (frontier matching, pre-registered decomposition, seeds ≥5/cell, OOD families fixed
before outcomes).

Next action (authorized by the PI's blanket grant, cheapest-first): write the D0 freeze for the
three-family audit (families: PDEBench-class PDE surrogates; small-mesh MeshGraphNets-class;
diffrax analytic systems), then execute on the three servers with public data only.
