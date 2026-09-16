# Paper G Cycle37: injection fidelity in astronomical detection

PRIVATE / INTERNAL — source-informed topic screening, not publication evidence.
Date: 2026-09-13. Scope: scientific ML for ICLR/ICML main under the current PI
cross-domain decision. The cycle start was recorded before new-domain searching;
individual questions were formed during source reading, not prospectively frozen
experimental hypotheses. No scientific execution or outcome payload was accessed.

## Decision

Retain **g37_kepler_injection_rank_transfer** at F1: can a small calibration panel
of pixel-injected Kepler light curves improve the choice of downstream ML transit
detectors when most validation uses cheaper flux injections? Three generic
formulations close. No F2 qualification, F3 audit, forecast or machine card.

This is a measurement question, not a claim that injection-stage differences,
completeness estimation, spatial vetting, or quantum noise control are new.
The weakest link is incremental method/decision value beyond direct calibration
and ordinary multifidelity estimators. A useful public resource entry is now
identified; its mere existence does not settle that weakness.

## Four questions and dispositions

| ID suffix | Archetype | Native fork and discriminator | Decision |
|---|---|---|---|
| kepler_injection_rank_transfer | measurement_method | Fixed upstream photometry, declared stars and injected transit parameters: does a small pixel-injection calibration panel improve downstream detector selection at a fixed false-alarm criterion beyond flux-only, direct-panel and simple correction baselines? Test selection regret and calibration on untouched stars/epochs. | F1 deferred; empirical increment and exact joins unresolved. |
| channelwise_joint_safety_certificate | measurement_method | Given strain and auxiliary witnesses, does marginal signal independence of each witness certify preservation by an arbitrary joint nonlinear subtractor? A joint-dependence counterexample separates it from full counterfactual witness invariance. | Quick-close the generic certificate. Do not attribute this weaker assumption to LIGO. |
| frequency_rotation_noise_advantage | empirical_intervention | At fixed nominal squeezing strength, does a physically realizable frequency-dependent quadrature rotation improve broadband strain sensitivity compared with a fixed phase, or is strength alone sufficient? | Quick-close the generic advantage: directly demonstrated; an ML optimizer without a distinct control result adds no established contribution. |
| offtarget_spatial_vetting_advantage | empirical_intervention | At matched summed transit photometry, move an injected dimming source within a declared aperture: can spatial diagnostic inputs improve on-target/off-target classification, or does the summed light curve suffice? | Quick-close the generic spatial-information advantage: direct neural-vetting parents and an elementary observation argument. |

For the retained question, a positive answer would support cheaper, better
detector selection; a null answer would limit reuse of the cheap validation
procedure and identify when direct pixel-panel evaluation is preferable. For the
other questions, the corresponding positive/null values are economical safety
certification versus requiring a joint check; useful phase control versus a
strength-only regime; and source localization versus a declared unresolved
spatial regime. These are values of the questions, not new findings claimed here.

Route-graph keyword/native-object checks found no exact astronomical formulation.
General observation or calibration closures remain relevant controls, but no old
route is reopened. The two measurement/two empirical sampling target is met;
there is no advancement quota. Raw intake also encountered other observing-run
pages, squeezing demonstrations and transit-search papers; they are not separate
questions or an exhaustive literature review.

## Public truth entry and the estimand it supports

The [NASA simulated-product documentation](https://exoplanetarchive.ipac.caltech.edu/docs/KeplerSimulated.html)
distinguishes pixel-injected light curves processed through PA/PDC, downstream
search/vetting products, and separate per-target flux-injection products. INJ1
provides one on-target injection per selected star, while INJ2/INJ3 have different
source constructions. The page provides download-manifest links. We read the
documentation, not the light curves, injection-result tables or downloads.

The [FLTI technical report](https://exoplanetarchive.ipac.caltech.edu/docs/KSCI-19109-002.pdf)
specifies two additional design choices: preprocessing is reused and the search
is localized around injected parameters. Consequently a raw PLTI-versus-FLTI
recovery-rate difference combines injection stage, preprocessing and search.
It cannot isolate a failure of an ML detector. This is a declared protocol
distinction, not an implementation-error narrative.

The candidate instead fixes an upstream photometric operator P and compares the
**same blind downstream detector** R_m on P(x + delta_theta) and
P(x) + s_theta. The former denotes an existing pixel-injection product; the
latter would be a deliberately specified new flux-injection construction.
Legacy FLTI results are a parent and reference, not automatically the latter arm.
Signal parameters must be hidden from R_m and used only by the evaluator.

The supported target is detection under the declared injected-signal distribution
and fixed archived upstream processing. It does not cover a new pixel pipeline,
all true planets, a physical change to a star, or automatically a planet
occurrence rate. A recovered-TCE-only sample estimates a different conditional
quantity from all-injection recovery. Noise-only inversion/scrambling controls
also do not by themselves establish astrophysical catalog reliability.

Before execution, qualify KIC/quarter/cadence and pipeline-version joins between
nominal and injected products, injected-parameter provenance, missingness and
quality masks, star/epoch separation, data rights and a compact subset cost.
Untouched confirmation must not share source stars with calibration, and temporal
blocks must prevent future information leakage. Multiple trials on one star are
not independent stars. No exact paired payload or final confirmation partition
has yet been inspected or authorized.

The [GWOSC O3 documentation](https://gwosc.org/O3/o3a_inj/) separately names
continuous-wave and detector-characterization injection resources and states
that O3 has no CBC/burst hardware injections. Therefore the presence of an
observing-run archive alone does not qualify a CBC validation panel or public
auxiliary witnesses. This is not an archive-wide absence claim.

## Six analytic controls

All controls below are hand-derived applicability checks, not new theorems,
simulations, observed astrophysical effects or empirical failures of authors' methods.

1. **Marginal versus joint safety.** For independent equiprobable signs H,U, let
   W1=U and W2=UH. Each witness is individually independent of H, but W1 W2=H.
   A joint predictor can recover H. This abstract construction defeats only
   marginal independence as a universal certificate; it is not a demonstrated
   physical coupling in LIGO.
2. **Counterfactual witness invariance.** For a frozen subtractor C(h,w)=h-F(w),
   if injecting s leaves the complete witness record w unchanged, then
   C(h+s,w)-C(h,w)=s exactly. If w changes by B s, the residual changes by
   s-[F(w+B s)-F(w)]. Hardware testing of couplings and this stronger assumption
   must not be replaced by a marginal-correlation caricature.
3. **Injection placement.** For fixed linear P, the two inputs coincide when
   s_theta=P delta_theta. Otherwise their difference is
   P delta_theta-s_theta. With P=I-vv^T, ||v||=1, delta_theta=v and s_theta=v,
   a unit injected component vanishes in one arm and survives in the other.
   Nonlinearity is unnecessary for a mismatch; a correctly transported linear
   template removes this particular counterexample. A generic mismatch is not
   the candidate's novelty.
4. **Selection conditioning.** If T is search recovery and V is vetter acceptance,
   Pr(T and V | theta,z)=Pr(T | theta,z) Pr(V | T,theta,z).
   Equal vetter recall among TCEs permits different full-pipeline completeness.
   All injections, including nonrecoveries, belong in the candidate denominator.
5. **Quadrature orientation.** For covariance
   V_phi=R_phi diag(exp(-2r),exp(2r)) R_phi^T, readout noise is
   a(f)^T V_phi a(f). Fixed r does not fix this noise. Nonparallel readout
   directions need not share an optimal fixed phase. A physical filter-cavity
   controller constrains the realizable frequency rotations; arbitrary
   frequency-by-frequency choices are not a legal hardware policy.
6. **Same summed flux, different source.** Two resolved sources each of flux F
   at positions 0 and r have the same total 2F-d when either loses d. Their
   centroid shifts from r/2 are respectively +dr/[2(2F-d)] and
   -dr/[2(2F-d)]. Summed flux cannot distinguish the cases. Unresolved PRFs or
   insufficient signal-to-noise can remove useful localization; the algebra
   neither promises an empirical gain nor defeats an information-matched baseline.

## Exact primary anchors (nine retained works)

- Ormiston et al., [DeepClean, PRR 2020](https://arxiv.org/abs/2005.06534): neural witness regression already includes signal-preservation validation; abstract/method context read.
- Reissel et al., [Coherence DeepClean, v2, 2025](https://arxiv.org/html/2501.04883v2): selected sections describe safe channels established with photon-calibrator injections and automated witness selection. We have not established failure of that safety procedure.
- Biwer et al., [hardware injection system, PRD 2017](https://arxiv.org/abs/1612.07864): end-to-end injection and recovery/coupling validation is an existing parent.
- Burke and Catanzarite, [KSCI-19109-002, 2017](https://exoplanetarchive.ipac.caltech.edu/docs/KSCI-19109-002.pdf): introduction, injection/search methods and schema outline distinguish the cheap validation protocol. This is counted as one primary technical work.
- Christiansen et al., [Kepler recovery IV, 2020](https://arxiv.org/abs/2010.04796): pixel-level completeness and stellar/noise dependence already investigated; abstract read. Its predecessor KSCI-19110 report is not counted as another independent work.
- Thompson et al., [DR25 catalog, 2018](https://arxiv.org/abs/1710.06758): joint completeness/reliability and simulated-data vetting already form the scientific parent; abstract read.
- Valizadegan et al., [ExoMiner++, v4, 2025](https://arxiv.org/html/2502.09790v4): selected difference-image design and ablation sections directly occupy the generic spatial-input benefit.
- Martinho et al., [ExoMiner++ 2.0, v2, 2026](https://arxiv.org/abs/2601.14877): current FFI extension; abstract only, not a full collision audit or verified new benchmark result here.
- Ganapathy et al., [PRX 2023](https://journals.aps.org/prx/abstract/10.1103/PhysRevX.13.041021): full-scale frequency-dependent squeezing directly occupies the generic broadband-control headline; abstract read.

Each F1 question uses at most three anchors. This is nine retained primary works
under the frozen cap ten, not a fifteen-work neighborhood. Additional project
pages and search snippets were intake, not independently verified evidence.

## Next decisive update

Use the remaining primary slot for the closest general multifidelity
calibration/model-selection parent and inspect official product schema/manifest
metadata only. Compare any proposed estimator against a paired difference or
control-variate estimate, direct small-panel ranking, SNR/stellar-noise mapping,
and matched-budget recalibration. Separate bias correction from variance reduction.
If the residual is only an ordinary correction with no consequential new
measurement or selection result, park it; do not expand a generic citation chain.

An F1 survivor is not a ready ICLR/ICML paper. No probability forecast is invented
after reading, and no computational or data authority follows from this record.
The broad publication objective remains active and incomplete.
