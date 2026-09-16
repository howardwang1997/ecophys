# Paper G dynamic isotope exchange intake

PRIVATE / INTERNAL — 2026-09-14. Excluded from public evidence.

The generic operation has direct classical and ML parents. No distinctive raw question is established. Stop this formulation while retaining the native controls and source locators; metabolism remains an eligible domain.

| Primary source | Selected evidence | Consequence |
| --- | --- | --- |
| [INCA, 2014](https://academic.oup.com/bioinformatics/article/30/9/1333/236911) | Indexed transient simulation, parallel experiment and tracer-design methods | Dynamic isotope inversion and experiment design are established operations. |
| [Guppy et al., online 2024 / volume 2025](https://link.springer.com/article/10.1007/s11538-024-01386-x) | VOR abstract and preprint introduction/discussion | Concentration scaling, steady-state identifiability and fast-slow KFP analysis already have a theoretical parent. Full theorem assumptions were not audited. |
| [NeuralFlux, online 2025 / volume 2026](https://doi.org/10.1111/pbi.70470) | Indexed main framework, proof-of-concept and availability | Learns a forward map from fluxes/concentrations to isotope distributions, then optimizes against labeling observations. The discussed recovery study uses simulated labeling with compartment concentrations as input. Incomplete recovery is acknowledged. |
| [Nießer et al., 2026 preprint](https://arxiv.org/html/2605.25155v1) | Selected microliter methods, joint inference and supplement model description | Provides actual multi-tracer experiments. Net flux equality is imposed in joint fitting after separate-fit comparisons; selected pools remain dataset-specific. Extracellular rate measurements anchor inference. |

A standard scale control makes the information requirement explicit. For passive tracer balances

C_i dm_i/dt = F_i(v,m,u),

where F is homogeneous of degree one in the flux vector v, the transformation (v,C) to (a v,a C), a>0, preserves all fractional labeling trajectories for any fixed admissible tracer schedule u. Initial fractions, atom mapping and metabolic steady state are held fixed. The result concerns absolute scale, not the ability to distinguish relative pathway usage or net/exchange ratios. It is not a new theorem.

An absolute uptake, secretion or concentration measurement can break this symmetry. The microliter paper includes extracellular rates, so the control cannot be used to dismiss its absolute flux estimates. Nor does concentration variability by itself prove an unmodeled mechanism. In the joint model, narrower intervals are conditional on its shared-parameter assumptions; separate-fit consistency remains separate evidence. The study already discusses pool variability and model limitations.

NeuralFlux is not merely a direct inverse regressor, and its numerical proof-of-concept is not independent experimental flux truth. Its code/data locators were retained without accessing payloads. The microbial and plant studies concern different networks, inputs and observation models. Their different emphasis does not establish a matched primary disagreement.

A later question must name an intervention and response that separate competing native explanations beyond existing INST-MFA and forward-surrogate methods. Fix compartment pooling, atom transitions, concentrations treated as known versus fitted, absolute anchors, shared parameters and the cost of acquiring each observation. A generic uncertainty adjustment does not qualify re-entry into the separately saturated calibration family. No final F3 truth contract was imposed at this intake.

Four primary works at unequal depth, one standard control, no new question/cycle/status or family closure. Paper G89/29/0; detailed36/173; inclusive45/229; graph333/279/1980; evidence1289. No outcome payload, scientific implementation, simulation/training, hardware, outreach, delegation or publication. The ICLR/ICML goal remains incomplete.
