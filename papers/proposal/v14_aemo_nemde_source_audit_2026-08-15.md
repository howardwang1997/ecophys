# AEMO historical NEMDE source audit

**Date:** 2026-08-15

**Decision:** `PROMISING_DEVELOPMENT_SOURCE_WITH_REDISTRIBUTION_AND_ACTION_PROVENANCE_LIMITS`

## Bottom line

The earlier statement that “production NEMDE is not open” was too coarse. Three assets must be separated:

1. AEMO publicly exposes historical, day-partitioned **production NEMDE format files**. Each five-minute case
   contains the applied input state, production output and price-setting analysis.
2. AEMO does not thereby publish the NEMDE executable, full formulation or an independently runnable exact solver.
3. Counterfactual execution through **NEMDE Queue** remains a paid, participant-restricted service.

The audit files are therefore a materially stronger free development source than a loose join of monthly MMSDM
tables. They can test whether a model maps the real dispatch state to the real solution and can benchmark an open
reconstruction against production outputs. They do not reveal why a participant chose an offer, every rejected
submission, or the exact counterfactual solution under a modified rule.

## Official evidence

- [AEMO NEMDE Queue Users' Guide](https://www.aemo.com.au/-/media/files/electricity/nem/it-systems-and-change/nemde-queue/nemde_queue_users_guide.pdf?la=en)
  states that one hierarchical XML combines `NemSpdInputs`, `NemSpdOutputs` and `SolutionAnalysis`; the production
  files are published daily, one for each of 288 five-minute intervals.
- [AEMO market-solver help](https://markets-portal-help.docs.public.aemo.com.au/Content/InformationSystems/Electricity/Market_solver.htm?TocPath=Information+Systems%7CNational+Electricity+Market+IT+systems%7C_____8)
  describes the input submitted to the linear-program solver and its output/price-setter files.
- [Historical NEMDE archive](https://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/NEMDE/2021/)
  exposes monthly directories containing daily `NemSpdOutputs_*_loaded.zip` objects. The frozen 2021-01-01 and
  2021-12-01 objects are 116,002,085 and 132,455,595 bytes.
- [Current AEMO copyright permissions](https://www.aemo.com.au/privacy-and-legal-notices/copyright-permissions)
  grant general use of publicly available AEMO material with accurate attribution. However, the archived
  [DVD disclaimer](https://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/NEMDE/2021/NEMDE_2021_12/NEMDE_Market_Data/disclaimer.htm)
  contains older personal-use language. EcoPhys will not redistribute raw files until AEMO clarifies which terms
  govern this archive.

## Observable mechanism interface

The official guide identifies the following input groups: regional demand forecasts, SCADA constraint data,
dispatchable-unit parameters and initial conditions, time-varying trader data, interconnectors, generic equations
and constraints. Its scenario editor can change offer-band prices and availability, maximum availability and ramp
rates. Output groups contain solver status/objective/violations, regional prices and dispatch, unit energy/FCAS
targets, interconnector flows and constraint marginal values. The price-setting section gives marginal-band
contributions but explicitly need not identify a unique price-setting unit.

This supports the scientifically useful pair

`applied production dispatch case -> production optimization solution`.

It does **not** by itself support

`participant information set -> intended/submitted/rejected action -> adaptation rationale`.

The XML's offers are applied solver inputs. Submission history, rejection/default reasons, ownership intervals and
strategic intent still require MMSDM/participant records or collaboration. Calling the audit file a raw behavioral
action log would be an overclaim.

## Consequences for the main paper

The source can strengthen the NCS route in three ways:

1. **Synchronized real mechanism cases.** Inputs and outputs share one interval artifact, reducing cross-table
   clock/version ambiguity.
2. **Production-grounded replay benchmark.** `nempy`, a reduced equilibrium layer and learned surrogates can be
   scored against targets, prices, binding constraints, objective values and violations from the real engine.
3. **Mechanism/action decomposition.** Applied-case replay error can be separated from errors in participant-policy
   and population modules. This makes the limits of each layer measurable rather than rhetorical.

It does not rescue the flagship claim alone. NCS still needs replicated real adaptation around a rule change and
a frozen prediction. NMI still needs a transferable learning principle that improves unseen-mechanism prediction
outside this single market. An accurate NEMDE emulator by itself is an engineering result.

## Staged data and compute

| Gate | Data | Compute | Unlocks |
|---|---:|---:|---|
| ZIP-tail inventory | 2 MiB total | Mac CPU, seconds | exact member offsets only |
| two-interval XML conformance | at most 4 MiB range per regime by frozen cap | Mac CPU, minutes | schema/section audit |
| one-day alignment | 116--132 MB/day plus small MMSDM identity tables | CPU, `<16 GB` RAM | 288-case replay design |
| 8--30 development days | roughly 1--4 GB compressed before measurement | CPU parsing; optional V100 only for learned baselines | replay error distribution |
| learned mechanism surrogate | derived tensors, not raw ZIP hot reads | initially one V100; scale only after baselines | NMI-method gate, not a claim |

No current step needs the two V100s or the 2060. Bulk acquisition, GPU training and paid Queue access remain
inadmissible until the metadata and XML conformance gates pass.

## Immediate protocol

The frozen metadata-only audit is
`experiments/v14_aemo_nemde_tail_inventory/PREREGISTRATION.md`. If it passes, freeze exact member names, offsets,
compressed sizes and CRCs in a new manifest before requesting XML bytes. Do not inspect an interval ad hoc and do
not replace a failed date.

## Executed conformance update

The tail and XML gates subsequently passed on interval 144 in both selected regimes. The applied inputs expose
participant/unit identifiers, offer dates/version, price bands, band availability, maximum availability, ramp
rates, SCADA/initial conditions and full constraint families in the same case as production outputs. Output fields
cover solver version/status/objective, prices, unit targets, flows, marginal values and violations.

The input tag and attribute sets are identical across the two sampled cases. Output structure is also identical
except that the post-5MS case adds `FSTargetModeTime`, consistent with the independent fast-start state-version
audit. This materially reduces historical bridge risk, but two cases do not prove daily stability or exact replay.
Summary SHA-256: `f48d86b8f7837956fa5813e8719a712d543ade3e795fa1ad691036bd096bb7cd`.
