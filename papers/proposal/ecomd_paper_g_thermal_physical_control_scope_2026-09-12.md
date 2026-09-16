# Paper G: physical thermal-control capability audit

PRIVATE / INTERNAL. Source-only re-entry capability audit for the closed g31_thermal_budget_intervention formulation. **Decision: partial_capability, not a qualified trigger.** No candidate harvesting, new question/cycle, F2, forecast or experiment. The direct PI continuation prompted a bounded check of the named physical-assignment gap left by cycle31's two numerical anchors.

## Decision-changing primary evidence

**Physical control exists, and a relevant control comparison has a direct predecessor.** [Tang and Bau, JFM 363 (1998), 153–171](https://www.cambridge.org/core/journals/journal-of-fluid-mechanics/article/experiments-on-the-stabilization-of-the-nomotion-state-of-a-fluid-layer-heated-from-below-and-cooled-from-above/25C2D1E934E4607677228B5B12BED030) reports distributed physical heaters and midheight temperature sensors. Selected indexed passages of the [institutional manuscript, §4, pp.165–167](https://repository.upenn.edu/bitstreams/ca90047a-a7d0-4aa7-aaa6-9ba23fe9b50d/download) specify a proportional power update every 50 seconds. They also describe switching feedback off and holding each heater at its previously measured time-average power. Thus the generic comparison of dynamic feedback against static spatial heating redistribution is already present in a physical experiment. These are two locations for one work. This audit reads the publisher abstract and selected indexed method passages, not a complete PDF or raw experimental records.

[Vial and Hernández, Physics of Fluids 29 (2017), 074103](https://repositorio.uchile.cl/handle/2250/149027), DOI 10.1063/1.4991909, reports a physical glycerol-water convection cell with independent hot/cold-wall feedback, local temperatures and heat-transfer measurements. Its institutional abstract describes turning the cell through 180 degrees while maintaining a temperature difference. This supplies a different physical intervention and measurement precedent, not the distributed equal-power assignment of cycle31. Only the institutional abstract/metadata were inspected; full methods, raw release and calibration are unqualified.

These two primary works are new to the project registry. They establish historical physical capability, not newly available reusable data or newly discovered physics. Other search hits were not promoted into evidence. The source discovery narrows the next action: physical existence is no longer the useful search target; the remaining task is an exact intervention/response contract with reusable calibrated observations and a substantive contribution.

## What the power controls identify

The following is an elementary paper-only reading check, not a new theorem or an executed model. Abstract the inspected proportional law over heater channels as
\[
p_{i,j}=p_{i,0}-k_p(T_{i,j}-T_{i,c}).
\]
For multiplicities \(w_i>0\) where a channel drives several heaters, total power is
\[
P_j=\sum_iw_i p_{i,0}-k_p\sum_iw_i(T_{i,j}-T_{i,c}).
\]
Consequently a fixed nominal setting does not impose constant instantaneous total power unless the weighted temperature-error sum vanishes. Physical saturation or other actuator constraints require their own complete law; no such uninspected details are inferred here.

Freezing each channel at its controlled-run average can preserve the corresponding observed mean spatial power profile. It does not preserve the instantaneous power history, feedback dependence, initial thermal state or complete trajectory distribution. That distinction limits the estimand, without invalidating the authors' stated comparison. In particular, it cannot be relabelled as an independently randomized, constant-power learned-controller trial.

For the previously declared thermal-system boundary, retain the balance
\[
\frac{dH}{dt}=P_{\rm in}-Q_{\rm top}-Q_{\rm other}.
\]
Matched mean input power and negligible mean storage imply matched mean top throughput only when other losses are also matched. For an equal-power comparison, temperature drop or thermal resistance can be informative. Apparatus and controller energy belong in any broader efficiency claim. These are the existing balance controls, not new thermal effects.

## Capability contract and stop

| Required item | Supported now | Still unqualified |
| --- | --- | --- |
| Estimand | Historical physical stabilization and a feedback-versus-frozen-profile comparison | Distinct learned-controller contribution at equal total energy and calibrated temperature-drop/flux precision |
| Assignment/interference | Physical feedback actuation is documented | Randomized or otherwise justified matched intervention; thermal carryover, equilibration and whole-cell interference control |
| Lifecycle and state | Selected update law and sensor/actuator roles | Trial IDs, time-aligned commands/actual power/temperatures, resets, controller state, clipping and complete sequence |
| Truth/calibration | Published temperature and heat-transfer observations exist | Inspectable raw uncertainties, parasitic-loss correction and traceable calibration for the proposed response |
| Rights/release | Reading primary publications | File-specific raw-data/software/derived-release rights; no license inferred from other repository items |
| Confirmation | Two independent historical author groups | Untouched confirmation partition or independently governed replication of the same intervention and estimand |
| Cost/ethics | Paper reading only | Qualified access, execution and total acquisition/control cost; no participant or hardware activity authorized |

No current raw dataset, executable apparatus access, rights package or same-estimand replication was qualified. This is a limitation of the inspected evidence, not a claim that none exists anywhere. No data were downloaded and no published effect was reproduced.

The original closure remains. Generic physical feedback and the basic frozen-average comparison are not independent novelty claims. No blocker was removed at the resolution of the recorded combined early-truth/contribution gate, so candidate_harvest_authorized remains false. Stop generic physical-existence searches and unmotivated variants of this control.

A useful next review must identify a concrete resource containing the matched intervention, calibrated response and reusable lifecycle needed by a substantive question, or a precise new model disagreement over that same contract. Historical apparatus descriptions alone do not qualify. This audit adds two primary records, one partial-capability re-entry entry and five graph locators; it adds no topic or cycle. Paper G remains 55 formulations, 15 cycles and zero cards.

Administrative verification: discovery and graph validators, protected history and four targeted tests passed. Protected original protocol, forecast, search-cycle and closure artifacts remain unchanged. These checks validate the records, not the physical hypotheses. The structured receipt is research/paper_g/thermal_physical_control_scope_20260912.yaml.
