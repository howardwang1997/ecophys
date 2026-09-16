# Paper G: cryo-EM population calibration review

PRIVATE / INTERNAL — exploratory analysis and allocation decision; excluded from public builds.
2026-09-13 NZ. Route `g36_cryo_population_acquisition_transfer`.

## Decision

**Park the candidate nonterminally.** The question of population-calibration transfer across acquisition conditions remains scientifically meaningful. This allocation did not qualify an economical independent particle-level comparison, a calibrated observation contract or a distinct method contribution. Published maps and useful resampling source improve resource knowledge, but do not by themselves support the proposed transfer experiment. This decision does not establish that calibration is useless or that no public particle release exists.

The frozen follow-up allowed two new primary works: RECOVAR and black-box label-shift estimation. Cycle36 now uses its original cap of ten. The six direct neighbors are the Cas9 resource, its classification benchmark, Evans et al., Tang et al., RECOVAR and BBSE. This is a targeted contribution/applicability review, not a completed full F2 truth qualification or an F3 audit. No new cycle, formulation, forecast, card or scientific execution.

## Direct methods and their assumptions

[RECOVAR, Gilles and Singer (PNAS 2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11892586/) estimates a regularized covariance, computes latent uncertainty for each particle, and recovers conformational density using an uncertainty-dependent deconvolution model. Sections 1.1–1.4 explicitly fix previously estimated pose/CTF operators and state that the density-convolution relation uses assumptions in the supplement. Consequently, “account for per-particle uncertainty when estimating populations” is already a direct contribution. Selected main sections were read; the complete supplement and current source implementation were not audited. A new acquisition regime must satisfy or replace the relevant observation assumptions; this review is not a refutation of the paper.

[BBSE, Lipton, Wang and Smola (ICML 2018)](https://proceedings.mlr.press/v80/lipton18a.html) estimates target label proportions using source confusion statistics and unlabeled target predictions. The selected assumptions and main result require invariant class-conditional observations, target label support covered by source data, and an invertible confusion matrix. A classifier need not already be calibrated. A change in microscopy acquisition can change class-conditional observations, so it is not automatically label shift. Applying confusion correction in a regime where its assumptions fail would not constitute a new failure of BBSE.

The [Cycle36 report](ecomd_paper_g_topic_cycle36_2026-09-13.md) records the four earlier direct neighbors. In particular, the Cas9 classification paper already performs balanced defocus-window comparisons and proposes comparing counting with ensemble reweighting. Generic nuisance stratification, population-versus-classification accuracy and inverse-confusion correction cannot carry a novelty claim here.

## What the public resources now establish

| Resource inspected | Established | Still unqualified |
|---|---|---|
| [EMD-76391](https://www.ebi.ac.uk/emdb/EMD-76391), mixed 2–14 bp extensions | The map was released on 29 July 2026. The experimental XML specifies a TFS KRIOS, Falcon IV detector, graphene grid and nominal defocus range. | Particle-stack locations, individual acquisition/label joins and independently replicated instrument domains. |
| [EMD-76396](https://www.ebi.ac.uk/emdb/EMD-76396), 13 bp extension | Same release date; corresponding deposited experimental metadata available. | This entry is another encoded composition, not by itself a repeat of every class on a second instrument. |
| [Author resampling source](https://raw.githubusercontent.com/lkinman/benchmark_datasets/main/generate_distributions.py) | Reads STAR particle/optics information, optionally selects `_ConformationalLabel`, derives origin from `_rlnImageName`, samples requested counts without replacement and creates particle halfsets. | Actual path-to-class manifest, per-particle acquisition keys and disjoint confirmation groups. Halfsets used for reconstruction do not establish independent acquisition-domain validation. |

Only source and header metadata were downloaded. No particle image, map, half-map, occupancy CSV, embedding or weight was opened. Source bytes are hashed in the structured record; a moving `main` URL plus a byte hash is not a verified repository commit pin. The source was not executed. The two inspected XML headers contain no EMPIAR cross-reference; this is a statement about these headers, not an exhaustive archive search. The earlier paper's deposition announcement remains insufficient to qualify an accessible complete stack contract in this bounded review. Code and dataset rights must be checked separately.

## Analytic applicability controls

All following statements are elementary hand-derived controls, not new theorems or empirical findings. Let Y be an encoded class, S an observed acquisition stratum and H the output of a fixed predictor. Write the column-stochastic matrix `C_d(s)[h,y] = P_d(H=h | Y=y,S=s)`, class proportions `pi_d(s)` and stratum frequency `w_d(s)`, for domain d.

The observed prediction distribution in a stratum is `q_d(s) = C_d(s) pi_d(s)`. If C is stable across domains and invertible within each stratum, then

`pi_target = sum_s w_target(s) C_source(s)^(-1) q_target(s)`.

This is ordinary stratified moment inversion. It also requires source class/stratum support and a predictor and representation fixed across domains. Estimated poses are observations used to define S; they are not independent physical orientation truth.

**Pooling can destroy information.** Let S be equally likely 0 or 1 and independent of Y, with `C(0)=I` and `C(1)` swapping two labels. The pooled C has every entry 1/2 and is singular, while each conditional matrix is invertible. Keeping S permits recovery that pooled hard predictions cannot provide. This establishes a possible value of conditioning, not that these extreme rates occur in the Cas9 data or that a new algorithm is required.

**Matching marginal acquisition statistics is insufficient.** In that same observation model, independent uniform Y and S give a uniform H. If Y=S instead, both Y and S remain marginally uniform, but H is always 0. Thus balancing the marginal distribution of acquisition metadata alone does not preserve class-conditional acquisition or the pooled confusion matrix. Knowing the joint encoded labels can support conditional validation; their absence cannot be repaired by an unconditional metadata balance certificate.

**More target particles do not remove calibration misspecification.** With ideal source calibration and exact target prediction frequencies, write `C_target(s)=C_source(s)+Delta(s)`. The population error of source-based inversion is exactly

`sum_s w_target(s) C_source(s)^(-1) Delta(s) pi_target(s)`.

Its norm is at most the corresponding weighted sum of products of the three norms. Finite-source/target sampling contributes additional error. If `Delta` remains unknown, shrinking a sampling interval alone does not establish coverage for the true target fraction. This is a standard inverse-problem sensitivity statement, not a distribution-free remedy.

**Average uncertainty also needs a joint observation model.** For a schematic additive measurement `V=Z+epsilon_S`, let both Z and S be uniform on {0,1}, with epsilon_0=0 and epsilon_1=1. If Z and S are independent, V has probabilities (1/4,1/2,1/4) at (0,1,2). If S=Z, V instead has probabilities (1/2,0,1/2), despite unchanged marginal state and noise-kernel distributions. Replacing a state-dependent observation mixture by an average-kernel convolution needs justification. This toy is not a cryo-EM simulation and makes no claim that RECOVAR's stated assumptions are violated in its reported experiments.

## What would make revisiting worthwhile

Keep the target as the encoded composition of a declared selected particle pool. Recovery of pre-vitrification biological populations, continuous breathing-state densities or causal detector effects would require different truth. A meaningful empirical contribution could compare population error and interval coverage across genuinely separate acquisition domains, with the same images/poses/masks/structural priors and matched label budgets. It need not be a new theorem, but it must resolve a question beyond the existing balanced-stratum and counting studies.

The required asset must join immutable particle IDs, source class, micrograph/movie, preparation/grid, instrument and processing lineage, with sufficient per-class support in independent domains and an untouched confirmation partition. Within-run classification seeds are not independent acquisitions. Target labels used for calibration create a supervised recalibration regime; they cannot simultaneously serve as untouched confirmation truth. Public maps are useful structural priors but cannot replace these particle-level joins.

Resume only on a concrete contribution-changing result or a qualified economical truth/comparison asset, with a new bounded allocation and any required re-entry review. Stop the generic cryo-EM citation/source chain. Next authorized work is an unsaturated scientific-ML screen. The broad ICLR/ICML objective remains active and incomplete.

Paper G remains 77 formulations / 20 cycles / 0 cards. This follow-up adds two primary works and three metadata/source records. Administrative validation is separate from scientific evidence.
