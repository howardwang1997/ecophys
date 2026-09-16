# Paper G photon photophysics intake

PRIVATE / INTERNAL — 2026-09-14. Excluded from public evidence.

Generic photon classification and selection correction do not supply a distinct contribution. A specific indexed mechanism lead is retained for the next bounded primary audit, not promoted to a candidate.

[Harris et al., mpH2MM (2022)](https://www.nature.com/articles/s41467-022-28632-x) already exploit excitation/emission information to distinguish conformational changes from dye-state transitions. Different laser settings on different specimens do not establish a matched illumination intervention.

[FENNEC (2026 preprint)](https://www.biorxiv.org/content/10.64898/2026.07.14.737247v1.full) directly classifies photon bursts for dynamics, blinking and bleaching using simulated training calibrated to the instrument. It presents classification and filtering, not kinetic-rate estimation. Our control below is not evidence that its actual downstream use fails.

[Dingeldein and Covino (2026 preprint)](https://arxiv.org/html/2608.21061v1) already formulate differentiable continuous-landscape photon likelihoods. Its stated model uses equilibrium one-dimensional constant-diffusion dynamics under continuous illumination, fixed calibrated Forster radius/crosstalk, and fitted detection/background quantities. The reviewed validation is simulated. Extending fitted amplitudes to dynamic dye states is not automatic, but merely adding hidden states is also not an established contribution.

[Feng et al., three-color burstML (2025)](https://doi.org/10.1016/j.bpj.2025.07.033) already account for photon-threshold selection, diffusion and background when estimating state populations and transition rates. Selection-dependent normalization has a direct native parent. Arbitrary neural acceptance rules differ from the reviewed threshold rule; this difference alone does not prove an effective new method.

A standard exact control separates event classification from kinetic inference. Let a symmetric two-state continuous-time Markov chain leave either state at rate k. In a fixed window T, the fully observed transition count N is Poisson(kT). An oracle selecting N>=1 has perfect precision for realized transition events. Nevertheless,

E[N/T | N>=1] = k / (1-exp(-kT)) > k.

All molecules have the same kinetics: zero observed transitions do not make a molecule a static species. The selected-only density for a frozen rule S is p_theta(y)1[S(y)=1]/P_theta(S=1). Observed rejection counts contribute further likelihood terms; full-data inference is a required comparator when all records remain available. This is ordinary truncation/conditioning, not a new theorem, an actual FENNEC error estimate or a claim that every classifier causes bias.

The [model-free photon analysis paper (2025)](https://www.nature.com/articles/s41467-025-60764-8) surfaced as an indexed lead: its discussion associates a fast Holliday-junction signal with alternatives involving incompletely explained dye behavior and possible rapid molecular motion. The sample, controls and discriminating predictions have not been audited. This is not a fifth reviewed primary, a confirmed controversy or a qualified new question. The next allocation should examine that exact component and stop if the apparent fork disappears on matching conditions.

Four selected primaries and one standard control retained. No raw question/cycle/status/F2/F3/forecast/card/saturation or generic calibration-transfer reopening. Paper G89/29/0; graph333/279/1986; evidence1303. No outcome payload, implementation, simulation, training, hardware, outreach or delegation. Published results are development evidence; the ICLR/ICML objective remains incomplete.
