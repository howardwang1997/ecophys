# EcoMD HFT-proxy truth-asset trigger audit — 2026-09-05

## Decision

`not_trigger`; no candidate harvesting, outcome access, implementation, simulation, SSH, or GPU.

Ibikunle et al. v2 (arXiv:2608.00858) is a valuable predictive measurement study, not the missing
participant truth asset. It trains ExtraTrees on proprietary 2009 Nasdaq HFT counterparty labels
and 24 public TAQ stock-day variables, promises public predicted HFT supply/demand measures for
2010--2023, and validates the approach with proprietary Euronext labels and event checks. The
labelled Nasdaq and Euronext records remain proprietary; no first-party model/data/code endpoint
was linked on the arXiv record or located in a title/identifier GitHub search during the audit.

## Lasting scientific results

- If `Hhat=g(X)` is a fixed learned proxy, then two worlds with the same law of public inputs `X`
  have the same law of `(X,Hhat)`. Adding `Hhat` after matching the full `X` law cannot shrink the
  latent equivalence class. With independent algorithmic randomness `U`,
  `I(Z;A(X,U)|X)=0`.
- Source labels plus unlabelled target features cannot identify target conditional label transport.
  The Euronext exercise trains a separate Euronext mapping; it does not directly score the fitted
  Nasdaq mapping on Euronext. Its reported post-fixed-effect within-R2 is 0.07%--0.34%.
- `HFT_D=(V_HH+V_HN)/Vtot` and `HFT_S=(V_HH+V_NH)/Vtot`; `V_HH` is counted twice. These are
  overlapping execution-volume roles, not mutually exclusive persistent trader populations.
- Current EcoMD uses uniformly sampled persistent latent type labels and aggregate price/volume
  formation without participant-resolved order/cancel/fill identity. Naming latent types after the
  HFT measures would impose, not identify, their semantics.
- Domain-adaptation impossibility and observation-aware SBI occupy the generic repairs; OASIS also
  requires a correctly specified observation model and identifiability.

## Re-entry

Require lawful participant-resolved labels, complete lifecycle and inventory state, a frozen
persistent-status-versus-execution-role observation map, target-labelled error under a complete
intervention, two independently governed systems, and a sharp identification result beyond domain
adaptation and observation-aware SBI. A prediction CSV, more dates, proxy cross-validation, or a
GPU fit is not a trigger.

Formal result:
`papers/proposal/ecomd_hft_proxy_truth_asset_trigger_audit_2026-09-05.md`.

Validated totals after this audit: 596 evidence records and 78 trigger audits, zero qualified; all
workers idle. The focused discovery and route-graph suite passed 78 tests.
