# Paper G magnetic potential and measure intake

PRIVATE / INTERNAL — 2026-09-14. Excluded from public evidence.

No distinctive new question formed. Existing work covers magnetic-state potentials, longitudinal fluctuations, integration measures and canonical sampling. The useful outcome is a sharper separation of energy accuracy, ensemble correctness and physical dynamics.

[Chapman and Ma (2022)](https://www.nature.com/articles/s41598-022-25682-5) already combine a magnetic ML potential with generalized Langevin dynamics allowing moment magnitude to vary. Conventional fixed-magnitude LLG is not the entire prior class.

[TSPIN, current v3 (2026)](https://arxiv.org/abs/2506.12877v3) introduces an auxiliary canonical spin momentum and inertia for NVT/NpT sampling. Its main text explains that integrating momentum removes that inertia from configurational equilibrium. It also reports thermodynamic comparisons; those findings are not refuted by our clock control below. The older search-index title must not replace the current paper's scope.

[Khmelevskyi (2018)](https://doi.org/10.1016/j.jmmm.2018.04.023) directly studies scalar, vector and linear longitudinal measures and motivates the latter through a classical-limit state-counting argument. That argument is not a universal microscopic derivation for every itinerant magnet. Comparing Fe/Ni and Co/BiFeO3 is not a matched scientific disagreement.

[Quarenta et al. (2024)](https://arxiv.org/abs/2310.05621v2) supply a physical bath-induced-inertia parent. Only its primary abstract and publication metadata were reviewed. It does not establish a bath model for an arbitrary magnetic potential or turn an adjustable sampling mass into a measured physical parameter.

Two standard analytic controls suffice to rule out generic overinterpretations:

1. Let m>=0, U(m)=kappa*m^2/2 and radial measure (m/m_ref)^q dm/m_ref, q>-1. The partition-integral ratio gives E[m^2]=(q+1)*k_B*T/kappa. Scalar, linear and Cartesian-radial choices produce coefficients 1, 2 and 3 despite identical energy. To use the Cartesian q=2 reference for a general q, set U_eff=U+(2-q)*k_B*T*log(m/m_ref) for m>0. The resulting probability measure agrees; a consistently transformed coordinate representation creates no physical discrepancy. Holding U fixed while changing state counts changes the model.
2. For H=p^2/(2*mu)+kappa*s^2/2, the canonical variance is k_B*T/kappa for every mu, but Hamiltonian evolution from that ensemble has correlation C_mu(t)=(k_B*T/kappa)*cos(sqrt(kappa/mu)*t). Thus a correct equilibrium distribution alone cannot certify a physical relaxation clock. This scalar example is not a complete spin equation.

These are elementary controls, not new theorems or material-specific results. A future learning task needs a concrete same-material response/state-count contrast and useful gain over existing methods. No final F3 truth contract was demanded at intake. Stop generic spin-variable, reweighting and auxiliary-sampler expansion; the broader field remains open.

Four primaries at unequal depth and two controls retained. No raw question/cycle/status/F2/F3/forecast/card/saturation. Paper G89/29/0; graph333/279/1986; evidence1309. No outcomes, weights, scientific implementation/simulation/training, hardware, outreach or delegation. Published results are development evidence. The ICLR/ICML objective remains incomplete.
