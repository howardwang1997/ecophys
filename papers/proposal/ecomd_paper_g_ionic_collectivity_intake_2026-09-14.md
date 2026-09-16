# Paper G ionic collectivity intake

PRIVATE / INTERNAL — 2026-09-14. Excluded from public evidence.

No distinctive new question formed. Collective ion migration, correlation-aware graph analysis, potential-based screening and systematic ML-potential transport comparison all have direct parents. Merely replacing a self-diffusion conductivity proxy with a charge-current observable is insufficient as a new learning contribution.

[He et al. (2017)](https://www.nature.com/articles/ncomms15893) already study concerted low-barrier migration and mobile-ion interactions in LGPS, LLZO and LATP. Selected indexed primary results were read. Their correlation factor must not be silently equated to every convention called a Haven ratio.

[Sato et al., online 2025 / issue 2026](https://pubs.acs.org/doi/10.1021/acs.chemmater.5c02374) connect hopping events into directed graphs and compare graph-derived conductivity against Green-Kubo and Nernst-Einstein estimates. Local loops and overlapping branches are explicitly treated, and parameter checks are reported. Selected indexed main sections were read, without a supplement or code audit. Agreement within these simulated systems does not alone identify a unique causal mechanism. Fixed-framework methods constrain host motion and use mobile-ion Langevin dynamics with specified starting structures; interpreting this as a pure change of vibration speed would require additional matching.

[Maevskiy et al., v1 (2024)](https://arxiv.org/html/2411.06804v1) already rank materials with descriptors of a frozen-framework potential landscape. Selected methods show that simulated diffusion labels and AIMD validation use Nernst-Einstein conversion. This makes the target distinction relevant, but does not demonstrate that their rankings fail. No parity with the later journal version was assumed.

[Shaaban Kabakibo et al., v1 (2026)](https://arxiv.org/html/2603.28012v1) already benchmark MACE-driven and first-principles dynamics on 21 experimental electrolyte entries. Selected main methods use self diffusion, Nernst-Einstein conversion and high-temperature Arrhenius extrapolation. This is a direct benchmark parent; full collective transport is a different estimand. Analysis is pinned to the arXiv version. An indexed OpenReview header was seen, but no acceptance-decision or version-parity audit was performed, so venue status is not used to qualify this intake.

Two standard controls are retained:

1. For equal mobile charges q in a fixed nonconducting host, charge conductivity uses the long-time quantity E[|sum_i q Delta_r_i|^2]/(2 d V kBT t). Nernst-Einstein uses sum_i q^2 E[|Delta_r_i|^2] instead. The missing cross terms can have either sign. For a one-dimensional statistical example X1=sqrt(2D)W and X2=+sqrt(2D)W or -sqrt(2D)W, each self diffusivity is D. The total-charge variance is respectively 8 q^2 D t or zero; conductivity divided by its NE proxy is 2 or 0. This is a Gaussian information-loss control, not a realistic stable crystal or an empirical ranking reversal.
2. In a periodic cell with lattice matrix A, the sum of lifted edge displacements around a closed cycle is A w, with integer winding w. Only a contractible cycle has w=0. Closed modulo-cell geometry alone therefore cannot certify zero charge displacement. Unwrapped paths/image offsets matter. The graph paper already treats local loops; its actual winding implementation was not audited, and no source defect is claimed.

A useful future mechanism question would need a specified same-material intervention separating host dynamics from static bottlenecks and ensemble changes, plus a concrete learning increment beyond the cited parents. No final F3 truth contract was demanded at intake. Stop generic transport-predictor expansion; the broader field remains open.

Four primary lineages and two standard controls retained. No raw question/cycle/status/F2/F3/forecast/card/saturation. Paper G89/29/0; graph333/279/1986; evidence1319. Published results are development evidence. No outcome/model payload, scientific implementation, simulation, training, hardware, outreach or delegation. ICLR/ICML goal incomplete.
