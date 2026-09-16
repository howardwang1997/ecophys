# Paper G cryo-EM damage source intake

PRIVATE / INTERNAL — 2026-09-14. Selection reasoning, not public scientific evidence.

No distinct raw question is counted. Two primary works were examined at unequal depth, together with two author metadata records. The newer Bayesian damage-model preprint was located through syndicated abstract text, but its primary methods were not independently read. It is not counted as a completed primary review or relied on for detailed algorithm claims.

This intake concerns changes within an electron exposure and recovery of pre-irradiation structure. It does not reopen the parked g36 acquisition-population calibration route or the closed STEM scan/fractionation formulations. Their decisions and the narrow calibration-transfer guard remain unchanged.

| Primary source / depth | Established selection evidence |
| --- | --- |
| [Naydenova et al., Science 2020](https://pubmed.ncbi.nlm.nih.gov/33033219/), author abstract and Figure 4 caption | Movement-free imaging and extrapolation to zero-exposure structure factors already exist. The caption describes exponential fits for real/imaginary components and amplitudes, and linear phase fits. Full fitting details and supplements were not audited. |
| [Kato et al., Communications Biology 2021](https://www.nature.com/articles/s42003-021-01919-3), selected results, discussion, methods and availability | Restricting the same movie to early frames reduces sensitive-site damage. The reported low/high-dose maps have resolutions 2.08/1.95 angstrom at 3.3/83 electrons per square angstrom. Residual damage and reference/refinement uncertainty remain. The comparison already shows why overall resolution cannot stand in for local structural fidelity. |
| [0dose author release](https://zenodo.org/records/3944689), indexed metadata | Python software is deposited for the 2020 method. No archive read or execution. |
| [2026 atomic-series author deposit](https://zenodo.org/records/21107538), metadata and file listing | Five archives are described as atomic-model time series. Derived model outputs are not an independent observation of undamaged structure. No file or preview opened. |

The 2021 paper deposits high/low-dose coordinates and maps as 7D1T/7D1U and EMD-30547/30548. This statement does not qualify a complete raw-movie release. Crystal XFEL and solution cryo-EM are different physical preparations, and a low-dose reconstruction is not automatically a zero-dose reference. Same-movie dose windows share particles. These scope distinctions limit a proposed validation, without proving a universal lack of usable truth.

An elementary extrapolation control

Consider a positive scalar signal from equal populations with independent first-order damage rates ln(2) and ln(4), with dimensionless dose D:

    S(D) = (1/2) 2^(-D) + (1/2) 4^(-D).
    S(0) = 1, S(1) = 3/8, S(2) = 5/32.

A single exponential A exp(-kD) can fit both positive-dose observations exactly. Its extrapolated intercept is

    A = S(1)^2 / S(2) = 9/10,

rather than the true initial value 1. The log of a positive exponential mixture is convex; agreement at two sampled doses does not establish a correct zero-dose intercept. This simple control assumes no noise, no phase changes, no motion and no microscope transfer function. It is not a cryo-EM simulator, a novel theorem, or evidence that an actual reconstruction failed.

The toy also does not assert that the published zero-dose method fits only two points. Additional doses, earlier observations or justified kinetic restrictions can distinguish this example. A multiexponential or hierarchical fit is an ordinary baseline; replacing it with a neural network would not by itself create a contribution.

Decision

Stop the generic zero-dose/dose-conditioned reconstruction chain. The physical measurement issue is real, but a new scientific ML contribution requires a specific operation or empirical contrast beyond existing extrapolation and site-level dose comparisons. No such increment has yet been specified here. Full final truth qualification is not demanded just to form F1; neither an invented architecture nor a new theorem is necessary for an empirical contribution.

The next intake should start from a named physical intervention and rival explanations in another unsaturated lane. Do not create a new family-wide closure, re-entry gate or extra topic merely from this source chain. A future concrete pre-irradiation question can be assessed on its own merits.

Paper G remains 89 formulations / 29 cycles / 0 cards; detailed ledger 36 cycles / 173 raw; inclusive history 45 cycles / 229 raw. Graph unchanged: 333 nodes / 279 edges / 1980 locators. Evidence records 1250 to 1254; candidate 0 / parked 14. No scientific implementation, outcomes, simulation, training, hardware, delegation, outreach, forecast or machine card. Administrative completion is recorded separately; broad goal incomplete.
