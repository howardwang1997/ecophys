# Paper G: fluid-injection fault truth-asset scope

PRIVATE / INTERNAL. 2026-09-14 NZ. Infrastructure preflight before question selection. No new raw question, search cycle, route, forecast or execution authorization.

**Outcome:** retain two useful public resource locators, but do not qualify a common post-shut-in mechanism/prediction dataset. The reviewed experiments have different controls, mechanical boundary conditions and rupture targets. An independent scientific ML contribution remains unspecified; asset availability alone is insufficient.

## Bounded evidence

| Source | What the selected reading supports | Scope retained |
|---|---|---|
| [Passelègue et al., Science Advances2026](https://doi.org/10.1126/sciadv.aeb0234) | Pressure transducers and strain gauges track fluid and aseismic-slip propagation during controlled pressurization and stress relaxation. | Full pressure fields are reconstructed with a parameterized diffusion inversion; slip-front timing uses a specified geometric fit. These are model-supported reconstructions, not dense independent ground truth. |
| [Direct versus indirect fault injection,2024](https://doi.org/10.1098/rsta.2023.0186) | Indexed primary methods/results compare injection into a fault with injection through adjacent rock; hydraulic fracture can accompany indirect injection. | Different flow paths and fracture creation affect the state. The abstract's shutdown recommendation does not itself establish a controlled shutdown comparison. Full supplement not reviewed. |
| [Random-forest hydraulic-fracture forecasting,2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12622230/) | Indexed primary methodology describes acoustic features and fourteen Barre Granite hydraulic-fracturing experiments. | Target is time to specimen-scale fracture, distinct from fault-slip-front motion or post-shutdown seismic hazard. No independent rerun or full split audit performed. |
| [Zenodo19255031](https://zenodo.org/records/19255031) | v1 metadata lists Data_Figure.zip,38.1MB, for reproducing experimental figures. | No archive preview/download. Complete event histories, independent specimen count, inner-file schema and exact reuse conditions unqualified. |
| [FORGE/GDR1775](https://gdr.openei.org/submissions/1775) | Official indexed metadata describes fifteen granitoid reactivation experiments, mechanical and acoustic records, injection rates0.05/0.25/0.75mL/min, and uniform/nonuniform pressure conditions. | Constant-shear loading differs from stress relaxation. Fifteen experiments are not automatically fifteen independent specimens or a crossed design. No README or outcome payload opened. |

Three primary works and two metadata records, at explicitly unequal reading depth. Other search hits are intake only. No claim that the resources are globally insufficient for every useful question.

## C1: stopping flow, holding pressure and depressurizing are different interventions

An elementary hydraulic storage model is

\[
C\dot p=Q-(p-p_b)/R,
\]

with compliance C>0, resistance R>0 and boundary pressure p_b. If the pump stops at t_s and Q=0, pressure follows p(t)=p_b+[p(t_s)-p_b]exp[-(t-t_s)/(RC)]. Holding p above p_b instead requires Q=(p-p_b)/R. Imposing a new pressure boundary is a third action.

Thus a zero-flow command does not instantaneously erase stored pressure, and a flat pressure trace does not imply zero injection. A distributed fault requires its actual spatial pressure and boundary history; this lumped example establishes no observed post-shutdown earthquake mechanism. Record valve state, commanded/measured pressure and flow, storage, outlet condition and mechanical loading before comparing shutdown policies.

## C2: equal mean pressure does not fix fault reactivation

Use a two-patch Coulomb threshold toy with normal stress10MPa, friction coefficient0.6 and shear stresses5MPa and2MPa. Both pressure fields (2,0)MPa and (0,2)MPa have mean1MPa. In the first field, patch1 exceeds its threshold0.6(10-2)=4.8MPa; in the second, it remains below threshold6MPa. Patch2 remains below threshold in both.

This local threshold comparison holds the labelled prestress field fixed and changes pressure placement. It proves neither dynamic rupture nor event magnitude. It explains why a pump scalar or spatial mean cannot substitute for a resolved pressure/stress contract. Sensor locations, spatial coverage and inference uncertainty matter. Front position must also retain its pressure threshold and geometric convention; a visual propagation curve is not an intervention label.

## Frozen asset requirements

- **Estimands:** separately define pressure at observed sensors, model-supported pressure/slip fronts, macroscopic shear reactivation, first hydraulic fracture and subsequent acoustic events. Select a response and fixed horizon before outcome access; do not pool these labels.
- **Assignment and interference:** require core/specimen/run identities, prior loading and accumulated slip, fault geometry/roughness, pressure-path treatment, prestress, fluid, machine stiffness and boundary control. Cross-patch coupling is part of the physical system. Repeated runs on a changed fault are not fresh randomized units.
- **Lifecycle and replay:** freeze initial loading, saturation, shear mobilization, unloading, injection commands and measurements, stop/hold/bleed action, post-action recording duration, timestamps, calibration, censoring and event-definition logic. Complete post-shut-in coverage is unqualified in the inspected descriptions.
- **Observation truth:** distinguish measured sensor values from derived fields and front picks. A model trained against an inversion cannot use agreement with that same inversion as independent validation of its physical assumptions. Preserve uncertainty and prediction-time availability of inputs.
- **Untouched confirmation:** no partition selected or accessed. Hold out independent specimens and full intervention histories as appropriate; windows from one specimen do not create independent replications. Cross-rock or cross-apparatus evaluation requires matched targets and control support.
- **Rights, ethics and release:** metadata reading only. Archive-specific licenses and permitted derivatives must be verified before reuse. No sample work, new fluid injection, field operation, outreach or release is authorized.
- **Independent replication and cost:** neither common units nor matched shutdown regimes across resources are qualified. Record source processing, sensor calibration, reference reconstruction and full validation cost before any proposed scientific run. No field-hazard claim follows from this preflight.
- **Stop:** end this bounded source chain. Resume only for a contribution-changing native question or a specific asset/control result removing the named post-shut-in/independence blocker. This record cannot authorize candidate harvesting or turn a generic calibration-transfer problem into a new route.

These two hand controls are standard physical/statistical scope checks, not new scientific findings. They guide source qualification rather than claim publication novelty. The front-propagation parent already incorporates loading-state and control dependence; replacing it with a neural model is not, by itself, a contribution.

## Accounting

Paper G remains88 formulations/28 cycles/0 cards; detailed ledger35/172; inclusive44/228. Complete graph unchanged:332 nodes/279 edges/1965 locators, candidate0/parked13. Five source records bring evidence to1232. No new topic/cycle/status, F2/F3/forecast/card, outcome payload, implementation, simulation/training/GPU, laboratory activity, delegation, outreach or publication. Broad ICLR/ICML goal incomplete; another unsaturated native question is the next action unless a concrete matched asset changes this assessment.
