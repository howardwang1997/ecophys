# Paper G: synchronized VIV observation asset

PRIVATE / INTERNAL. Infrastructure preflight; `public_evidence_eligible: false`.
Decision: `not_trigger`, partial observation capability. No new topic or experiment.

This resource provides a concrete experimental observation bridge for the
repository's neural-PDE and flow-surrogate work. The connection is to the
observation/constraint truth contract recorded in
`ecomd_paper_g_observation_constraint_truth_preflight_2026-09-09.md`, not to
Paper D outcomes. A usable experimental archive alone does not remove the
closed numerical-teacher route's elementary-certificate and direct-parent
blockers. The preceding record-only turn was no progress toward topic selection.

## Verified source scope

The [official dataset](https://doi.org/10.57745/HPA87O) is version 1.0,
released 27 February 2026. Its versioned API lists 17 NPZ files, a README and
one image, all unrestricted under Etalab 2.0. Metadata explicitly associates
PIV timestamps with synchronized cylinder displacement measured by a Keyence
laser sensor. This is an existing release newly located here. Metadata was
downloaded; all NPZ files and the image remain untouched. The listing's file
checksums identify advertised payloads; they have not been verified locally.

The [README, file DOI GKMAUX](https://entrepot.recherche.data.gouv.fr/file.xhtml?persistentId=doi:10.57745/GKMAUX&version=1.0)
documents per-case velocity arrays, a moving-body mask, spatial coordinates,
time, displacement and normalization extrema. Coordinates are documented in
millimetres and displacement in metres. These fields permit a planned
observation-alignment contract. The README's embedded loading examples were
read, never executed. Its illustrative printed values are not inspected
experimental outcomes and are not adopted as evidence. Neither the archive's
actual arrays nor normalization provenance was checked.

[VIVALDy v3](https://arxiv.org/html/2509.24965v3), dated 10 April 2026,
describes a freely vibrating cylinder, 17 operating conditions and 10 Hz
planar PIV. Sections 3.1–3.3 already specify masked flow reconstruction from
displacement using a generative latent representation and bidirectional
sequence attention. Section 5.2 already identifies limited observability at
small displacement and proposes additional pressure sensors and numerical
data. Generic displacement-to-flow reconstruction, sensor augmentation and
hybrid training therefore have direct parents. Selected v1 passages were
initially read; the decision uses v3. The arXiv record links the published
article, Physical Review Fluids 11, 044902; publisher full text was not read.
No reported performance magnitude or failure is adopted as Paper G evidence.

The apparatus parent, [Schmider et al. (2024)](https://doi.org/10.1016/j.oceaneng.2024.116668),
describes motor-applied virtual damping and stiffness. The publisher-indexed
abstract and data-availability statement were inspected: data are offered
on request. That establishes a physical intervention capability in the
published apparatus, but does not establish that HPA87O contains intervention
commands, execution records or matched force measurements. No request was sent.

## Supported and unsupported uses

| Estimand | Present support | Additional requirement |
|---|---|---|
| Predict the released planar PIV observable from a declared displacement window | Synchronized channels and array schema documented | Frozen time information, observation units, masks, preprocessing and whole-run partitions |
| Measure error against noise-free velocity or PDE derivatives | Not qualified | Same-target calibration/uncertainty and relevant unobserved fluxes |
| Predict response to changing stiffness or damping | Apparatus exists; public observation archive does not qualify the action loop | Run-linked assigned command, executed force, pre-state, timing and observation records |
| Validate online control or harvested power | Not qualified by flow reconstruction | Causal information set, physical power definition, independent action/response confirmation |

The independent displacement sensor measures another quantity; it is not an
independent reference for PIV velocity. A measured plane is not automatically
a closed two-dimensional fluid state. The existing observation-truth audit
already supplies this distinction; no new theorem is claimed here.

Bidirectional window reconstruction also requires an explicit prediction-time
contract. An interior output can use measurements later than its own timestamp;
the final window output has no within-window future. Neither fact alone proves
leakage or an invalid published task. Online forecasting, delayed reconstruction
and feedback intervention must have separate information sets. Changing the
attention mask alone is not a qualified innovative contribution.

## Eight-part preflight contract

1. **Blocker and estimand:** retain the two recorded contribution blockers;
   support only a prospective measured-observation benchmark, not exact
   continuum truth or policy value.
2. **Assignment/interference:** cylinder motion and flow are coupled. An
   observed displacement is not an externally assigned displacement. Operating
   condition labels do not establish randomized stiffness/damping interventions.
3. **Lifecycle/replay:** case/time/mask/displacement correspondence is documented.
   Acquisition order, initialization, independent repeats, physical actuation
   and calibration-to-array lineage remain unqualified in the inspected set.
4. **Rights/ethics/release:** data Etalab 2.0; v3 manuscript CC BY-SA 4.0.
   No participant work, payload access, implementation or republication authority.
5. **Confirmation:** arrays are untouched locally; that does not make published
   benchmark cases pristine confirmation. Require an outcome-blind whole-run
   partition and an independent replication source before stronger claims.
6. **Replication:** two modalities in one apparatus are not two independent
   physical system lineages, nor replicated truth for the same target.
7. **Cost:** metadata and README only in this preflight. Listed NPZ sizes total
   17,058,013,136 bytes; no download or compute budget is authorized.
8. **Stop:** stop generic reconstruction, observability and sensor-addition
   harvesting. Re-entry requires a specific unresolved same-condition model
   disagreement or a public intervention/calibration asset removing a named
   blocker. The apparatus citation alone is insufficient. No code crawl follows.

This audit improves the reusable asset map but does not qualify an ICML-main,
NMI or NCS topic. No forecast, full hostile audit, machine card or new search
cycle was opened. The full Paper G objective remains unachieved.
