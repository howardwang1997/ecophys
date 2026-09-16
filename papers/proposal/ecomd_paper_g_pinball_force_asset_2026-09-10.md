# Paper G: actuated fluidic-pinball force reference

PRIVATE / INTERNAL. Infrastructure preflight; `public_evidence_eligible: false`.
Decision: `not_trigger`. Partial capability for measured mean force under
constant actuation. No scientific implementation, outcome access or new topic.

## What this asset changes

The source supplies a physical force measurement channel, an explicit native
control and an uncertainty procedure. It is more specific than an archive of
flow images alone. Retain it as a prospective observation bridge for the
repository's neural-PDE/flow-surrogate work; see the existing observation-truth
and VIV preflights. No Paper D results were used.

The next bottleneck is a distinct, quantitative model disagreement. We should
not keep collecting constant-actuation archives merely because this one does
not provide instantaneous force truth: a mean-response claim would not require
that estimand. Conversely, mean-force data cannot qualify transient feedback
or arbitrary intervention responses. None of this removes the closed route's
elementary-certificate or direct-parent blockers.

## Primary sources and exact access

[Zenodo 20794709](https://zenodo.org/records/20794709) advertises experimental
flow fields, drag and uncertainty, plus a separate URANS archive. Its API
identifies record DOI 10.5281/zenodo.20794709, open access and CC BY 4.0.
Publication date is 23 June 2026; the record was created and modified on
24 June. The page displays v1; the API metadata has no version string. The
exact record ID and cached metadata are the identity anchors. This is an
existing release newly located here, not a post-closure acquisition.

Only metadata and the 3,692-byte [README](https://zenodo.org/records/20794709/files/README.txt?download=1)
were downloaded. The README hash matches the advertised MD5. It describes
experimental `p`, `CD` and `Uncertainty`; velocity files carry case/actuation
attributes, pixel displacements and coordinates. A `_zero_` suffix identifies
unactuated measurements immediately preceding an actuated case. Dimensional
conversion and fluctuation-centering instructions are supplied. The numerical
archive describes `p`, `Cd` and ten chronologically ordered vorticity frames
per field sequence. No MAT, HDF5, field frame or archive payload was inspected.
Embedded conversion expressions were read only, never executed.

The two archive sizes advertised by the API are 1,333,197,134 and 226,542,913
bytes. Their MD5 values remain publisher metadata, not locally verified
payload checksums. No archive preview or listing was requested.

[Rodríguez-Asensio et al., arXiv v1](https://arxiv.org/html/2602.17713v1),
16 February 2026, sections 2 and Appendix A describe constant symmetric
rotation, Arduino-triggered acquisition, three load cells and known-load
calibration. The native input is p=(b3-b2)/2 with b_i=Omega_i D/(2 U_infty),
b1=0 and b2=-b3. Reported uncertainty combines force statistics, calibration,
sensor specifications and inflow measurement; temporal correlation enters
through an effective sample count. The measured response is not error-free.
The study also defines a two-dimensional URANS comparison calibrated at the
unactuated case, with a different actuation grid. Sections 3.4 and 4 already
compare force trends and offer a qualitative reduced-state interpretation.
These establish direct prior scope, not a new Paper G result. No reported
force value, performance improvement or discrepancy is adopted as evidence.

The [published article](https://doi.org/10.1016/j.expthermflusci.2026.111798),
Experimental Thermal and Fluid Science 177 (2026), was separately checked at
publisher-indexed selected passages and the institution's bibliographic record.
Those passages retain the steady symmetric-actuation scope and explicitly
describe the reduced-order account as qualitative, rather than a quantitative
predictive model. Full publisher text and institutional PDF were not read;
do not assume version identity for every calibration detail.

## Capability boundaries

| Target | Present support | Still required before a scientific comparison |
|---|---|---|
| Released mean drag at a specified constant p | Independent load-cell modality, control definition, uncertainty method and summary schema | Exact mean/median aggregation contract, calibration version, joint uncertainty and matched evaluation states |
| Flow reconstruction under those conditions | Case-labelled measured fields and conversion specification | Frozen observation/mask/domain contract and untouched run partitions |
| Instantaneous force from a flow sequence | Paper reports synchronized acquisition | A released raw-force/time correspondence has not been qualified from the README |
| Transient branch switching or feedback value | Actuation apparatus is documented | Executed input history, pre-state, transient observations and independent confirmation |
| Exact continuum or volumetric derivative truth | Not supplied by the above summaries | A separate same-target truth contract |

The load-cell channel is not obtained by integrating the released PIV field.
However, the drag coefficient uses a PIV-derived inflow normalization, and
campaign-baseline/calibration terms can be shared across conditions. Different
sensors therefore do not imply independent errors in every derived quantity.
The published uncertainty procedure must retain its own assumptions; a listed
uncertainty is not automatically a simultaneous confidence band or a certified
bound on every control contrast. No new error-propagation theorem is claimed.

A preceding unactuated reference supports measurement accounting. It does not
by itself establish a randomized intervention, identical hidden pre-state,
independent replication, or an untouched confirmation run. Likewise, matched
geometry and Reynolds number do not make two-dimensional URANS a replay of
the complete experimental state. These are contract distinctions, not claims
of invalid experiments or implementation failures.

## Frozen eight-part preflight

1. **Named blocker and estimand:** contribution novelty remains blocked by
   `supplied_reference_certificate_is_elementary_error_propagation` and
   `exact_and_stochastic_physical_supervision_have_direct_parents`. Retain
   prospective mean-force observation support, without reopening that claim.
2. **Assignment/interference:** three cylinders share a coupled wake; hold the
   full rotation vector, inflow, geometry and preparation protocol explicit.
3. **Lifecycle/replay:** distinguish campaign baseline, immediately preceding
   unactuated reference, actuated acquisition and reported summary. Executed
   rotation records, raw synchronization and array provenance remain unqualified.
4. **Rights/ethics/release:** data CC BY 4.0; preprint CC BY-NC-ND 4.0. No
   participant work, outreach, hardware use or public artifact authorization.
5. **Confirmation:** all scientific payloads untouched locally. Published
   examples and numerical calibration cases are not fresh confirmation.
6. **Replication:** one apparatus and its companion URANS comparison do not
   establish independent experimental replication or identical native state.
7. **Cost:** this preflight reads metadata, README and selected primary text.
   No acquisition/compute budget; both archives remain unmaterialized.
8. **Stop:** stop generic drag-optimum, wake-bifurcation, three-coordinate ROM,
   uncertainty-certificate or simulator-ranking harvesting. Before further
   archive work, identify a quantitative same-condition primary disagreement
   with a distinct contribution; otherwise use a genuinely blocker-removing
   asset. Another constant-input archive alone is not the next decisive update.

No raw questions, search cycle, forecast, hostile audit or machine card were
opened. No publication probability is inferred from access or schema quality.
The full ICML-main/NMI/NCS Paper G objective remains unachieved.
