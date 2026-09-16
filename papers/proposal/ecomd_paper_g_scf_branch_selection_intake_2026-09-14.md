# Paper G electronic SCF branch-selection intake

PRIVATE / INTERNAL — 2026-09-14. Excluded from public evidence.

The generic proposal is already substantially occupied. Retain one concrete source lead, TRIP50, for a bounded comparison of branch-selection cost. No distinct new question or executable research card is established.

| Primary work | Selected reading | Consequence |
| --- | --- | --- |
| [SAIL, 2026](https://arxiv.org/html/2604.21657v1) | Main methods, gradient loss, effective iteration cost, experiments and RKS appendix scope | Solver-aligned initialization learning is a direct parent. The fine-tuning loss averages orbital-gradient norms along SCF trajectories; supervised pretraining is also used. Total Fock-build cost matters. |
| [NeuralSCF, 2026](https://www.nature.com/articles/s41524-026-02110-0) | Indexed framework, training and QM9 results | Learning the density map and iterating to a fixed point already has a parent. Full spin/branch coverage was not audited. |
| [Thom and Head-Gordon, 2008](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.101.193001) | Publisher abstract | Density-distance bias to seek additional SCF solutions is established, including H4 and nitrogen examples. Generic multi-branch search is not a new mechanism. |
| [TRIP50, 2026](https://pubs.acs.org/doi/10.1021/acs.jctc.6c00144) | Indexed selected main text, Figure 3 caption, Table 1 surrounding discussion and conclusions | Same-structure triplet calculations with varied initial guesses provide a concrete comparison lead. Classical guesses and cross-functional density transfer are necessary baselines. |

A standard conditional control separates convergence from selection. Suppose two admissible fixed points of the same electronic approximation satisfy R(Pa)=R(Pb)=0 but E(Pa)<E(Pb). A residual-only stopping rule cannot rank them. If the chosen iteration map preserves both states, an orbital-gradient trajectory loss also vanishes on either constant trajectory. This is not a new theorem, nor evidence that SAIL or NeuralSCF selects an undesired state. A stationary excited determinant need not be a fixed point of an Aufbau update; occupations and solver history matter.

TRIP50 describes up to three densities under varied initial guesses in a selected subset, and reports that some conventional guesses and density transfer reach the desired branch. Its metadynamics recommendation is therefore a serious comparator. The selected cases are already development evidence. Neither exact table-cell replication nor complete independent reference coverage was established here. Published numerical comparisons do not constitute a newly observed result by this project.

The next source check should distinguish two reference targets: the lowest supported branch within one fixed functional/basis/spin space, and reaction-energy accuracy against a higher-level correlated calculation. Agreement with the latter does not certify the former. A best-found minimum also needs that label unless a stronger certificate exists. Changing restricted to unrestricted ansatz or changing spin multiplicity cannot serve as a same-space counterexample.

A useful later comparison would count all initialization and search costs, including density-transfer solves and any target-state inspection used to choose a reference density. Training and inference cost must be included at an explicit amortization scale. Merely adding a learned ranking of starts does not establish a distinctive contribution. No matched primary disagreement or demonstrated learning advantage was found in this intake; no final F3 truth contract was demanded at this stage.

Four primary works at unequal depth and one standard analytic control were retained. No new question, cycle, status, forecast, machine card or family saturation. Paper G 89 formulations / 29 cycles / 0 qualified cards; evidence 1283; graph 333 nodes / 279 edges / 1980 locators. No outcome payload, scientific implementation, simulation, training, hardware, outreach, delegation or publication. The ICLR/ICML topic goal remains incomplete.
