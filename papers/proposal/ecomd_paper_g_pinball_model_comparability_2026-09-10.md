# Paper G: pinball model comparability

PRIVATE / INTERNAL. `public_evidence_eligible: false`.
Bounded primary-model-disagreement audit. Decision: `not_trigger`.

The inspected models do not supply conflicting quantitative predictions for
the newly located turbulent force experiment. Their physical conditions,
observations and outputs differ. This is a concrete exclusion of a proposed
source pairing, not closure of all fluid-control research. No raw candidate,
new cycle, simulator, implementation or outcome analysis was opened.

The repository connection remains neural-PDE/flow-surrogate model assessment
and the measured mean-force bridge in the preceding pinball asset preflight.
The closed numerical-teacher formulation and its contribution blockers remain
unchanged. No Paper D outcomes were accessed or used.

## Primary comparison

| Work | Physical setting and action | Inputs or coordinates | Quantity actually supplied |
|---|---|---|---|
| Deng et al., Galerkin force model, JFM 2021 | Two-dimensional unforced pinball; examples at Re=30,80,100 | Amplitudes of a specified velocity-mode expansion | Instantaneous lift/drag expression, with calibrated reduced models |
| Marra et al., actuation manifold, JFM 2024 | Two-dimensional Re=30; three independent constant rotations; post-transient snapshots | Three actuation parameters plus lift and delayed lift, or two wake velocities | Reconstruction of a present flow snapshot through five latent coordinates |
| Marra et al., self-tuning MPC, JFM 2024 | Two-dimensional Re=150; time-varying three-cylinder control | Drag, lift and their time derivatives; selected future control sequence | Short-horizon force dynamics used in feedback optimization |
| Rodríguez-Asensio et al., turbulent experiment, 2026 | Re=9100; constant symmetric rear-cylinder rotation | Control parameter, wake-deflection description and drag-related coordinate | Calibrated measured force summaries and qualitative reduced-state interpretation |

[Deng et al.](https://doi.org/10.1017/jfm.2021.299), published online
5 May 2021, derive constant-linear-quadratic force dependence on the amplitudes
of a specified Galerkin expansion (section 2, especially equation 2.18).
The physical coordinates are velocity modes, not arbitrary learned latent
variables. The inspected examples use unforced flow; a coordinate-free,
control-independent polynomial force law is not established. Section 5 and
Appendix C already discuss limits of the selected reduced representation.
No reported accuracy or source-model limitation is adopted as a new finding.

[Actuation manifold](https://doi.org/10.1017/jfm.2024.593), published online
30 September 2024, uses 343 steady actuation settings and post-transient
snapshots (sections 2–3). Section 4.2 explicitly adds two sensor inputs: lift
with a quarter-period delay, or two wake velocities. The five-coordinate
embedding includes both actuation and flow information. The decoder is
restricted to interpolation in the sampled control range. It is not a claim
that the current actuation alone determines arbitrary transient flow.
Initial arXiv v1 reading was followed by selected final publisher sections;
v2 metadata and selected conclusion were also checked. These are one work.

[Self-tuning MPC](https://doi.org/10.1017/jfm.2024.47), published online
18 March 2024, defines the pinball plant state as
(Cd,Cl,dCd/dt,dCl/dt), with a quadratic SINDYc library and prescribed input
history (section 3.1). The online local-polynomial estimator uses past sensor
measurements. Its tested system is Re=150, not the Re=9100 experiment. The
discussion already qualifies coordinate selection at higher Reynolds number
and the scope of the assumed noise model. Noise-aware force feedback is
therefore an existing parent, not a fresh contribution from this comparison.

The experimental source and archive retain the scope established in
`ecomd_paper_g_pinball_force_asset_2026-09-10.md`. Their README documents
control-indexed mean drag and uncertainty. It does not qualify the complete
time-resolved lift/drag/derivative interface required by the MPC model. This
does not prove those quantities were never measured or are absent elsewhere.

## Why the apparent forks do not survive

1. **Three versus five coordinates:** qualitative regime coordinates,
   a sensor-conditioned snapshot embedding and an ODE state have different
   meanings. Dimensions alone give no opposed physical prediction.
2. **Snapshot reconstruction versus feedback dynamics:** a measured current
   field conditional on sensor data is not a forecast under a future action.
   Neither source claims these tasks are identical.
3. **Polynomial force versus latent representation:** a force polynomial in
   specified Galerkin amplitudes is not necessarily polynomial in nonlinear
   embedding coordinates. Changing coordinates is not evidence of a new
   physical force law. No coordinate-change theorem is claimed here.
4. **Laminar versus turbulent response:** changing Reynolds number, control
   family and available measurements does not produce a matched primary
   disagreement. A transfer experiment would require its own contribution
   and cannot be justified solely by different source headlines.

No pair above fixes the same state, legal input, information set, response
and conditioning variables while predicting distinguishable outcomes.
Absence of that pair does not prove universal agreement of the models.

## Contract and next gate

- **Named blocker/estimand:** elementary-certificate and direct-supervision
  parents remain; no new mean-force or transient-force rival prediction.
- **Assignment/interference:** preserve the complete cylinder inputs, flow
  regime and preparation. Do not substitute one scalar actuation for a
  three-input controller outside the symmetric subfamily.
- **Lifecycle/replay:** identify snapshot time, allowed sensor lag/derivative,
  prediction horizon, input path and physical initialization for each model.
- **Rights/ethics/release:** selected primary HTML reading only; no source
  program, model, archive, hardware, participant or publication access.
- **Confirmation:** existing mean-force archives remain untouched; published
  cases cannot by declaration become untouched independent confirmation.
- **Replication:** no matched physical-system replication established by
  multiple publications on the same geometric benchmark.
- **Cost:** three newly registered primary works, no downloads, computation
  or expanded fifteen-work review.
- **Stop:** stop this local dimension/reconstruction/force-model pairing.
  Re-enter only with a quantitative rival pair at common conditions or a
  theorem that removes a recorded blocker. Do not manufacture a transient
  counterexample outside a snapshot model's declared domain, or recast the
  existing polynomial/coordinate distinction as novelty.

The reusable result is the comparability matrix and the precise information
required by each model. No new theorem, diagnostic toy, forecast or machine
card was created. The full Paper G publication objective remains unachieved.
