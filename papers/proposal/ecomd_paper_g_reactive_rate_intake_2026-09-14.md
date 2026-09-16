# Paper G reaction-rate source intake

PRIVATE / INTERNAL — 2026-09-14. Selection reasoning only; not public scientific evidence.

Three selected primary works establish a demanding baseline for reaction-path learning. No distinct raw question or new search cycle is counted. The allocation allowed up to four raw questions, two quick screens and six new primary works; it stops after three selected readings. Initial indexed hits, including Gen-COMPAS and diffusion path samplers, are not counted as reviewed works.

| Primary work | Verified scope and reading limit |
| --- | --- |
| [den Hollander and Jansen, 2013](https://arxiv.org/pdf/1309.1305), selected Sections 1.2–1.4 and Appendix A.5 | Dirichlet trial potentials give capacity upper bounds; admissible unit flows give Thomson lower bounds. Berman–Konsowa path/flow principles can sharpen lower bounds. The stated jump-process assumptions and flow conservation matter. These are classical baselines. |
| [Aggarwal et al., 2026](https://arxiv.org/html/2606.06295v1), selected framework, time convention and Appendix F.2 | Reactive Flux Matching learns current velocity and a potential from reactive trajectories. Its learned coordinate is already used with weighted ensemble for molecular rate estimation. Learning a path coordinate followed by rate sampling is therefore occupied. This work uses timing and additional dynamics; it does not infer physical rates from untimed geometry alone. |
| [Petersen et al., 2026](https://arxiv.org/html/2608.02536v1), selected equations 1–14, S6–S8 | Sliced committors have a variational flux bound and enrichment diagnostic. Exact flux-weighted fidelity is distinguished from its empirical basin-average substitution. Energy recovered by refinement lower-bounds earlier error; that inequality alone does not upper-bound remaining error. No molecular failure is independently established here. |

No full literature neighborhood, complete supplement or payload audit was performed. Source interpretations retain the distinction between exact identities and implemented estimators.

A standard counterexample to stopping from apparent stability

Take a connected reversible finite network with nodes A, B, x, y, z. Count each undirected edge once in E(u)=sum c_ij(u_i-u_j)^2. Set conductances c_Ax=c_xB=1, c_Ay=c_yB=M>0, c_Az=w>0, and boundary values u_A=0, u_B=1. This is realizable as a reversible continuous-time chain by choosing positive stationary masses and rates Q_ij=c_ij/pi_i.

The exact committor has q_x=q_y=1/2 and q_z=0, so capacity C=(1+M)/2. Consider a trial family fixing u_x=1/2, u_y=0 and allowing u_z=theta. Its energy is

    E(u) = 1/2 + M + w theta^2.

Enlarging the family strictly from theta=0 to theta in [0,1] leaves the optimized value U=M+1/2 unchanged. Yet its error is U-C=M/2, which can be arbitrarily large. Thus zero improvement under an uninformative enrichment is compatible with large unresolved error. This does not contradict the valid lower bound on error supplied by recovered energy; a zero lower bound makes no accuracy guarantee.

For comparison, a unit flow entirely through A-x-B has dissipation 2 and hence L=1/2. The valid two-sided interval [L,U] remains wide, U-L=M. If the y branch is omitted when evaluating the upper functional, the result concerns a different, reduced network and is not a full-network upper bound. All edges were known in this analytic control: it is not a finite-data impossibility theorem or evidence of an actual molecular sampler missing a channel. A direct linear solve is the required baseline on such a small network.

Physical time and model scope

For a reversible continuous-time generator Q, replacing Q by cQ with c>0 preserves the stationary distribution, committor and embedded jump chain. Capacity scales by c and hitting times scale by 1/c. Therefore untimed path geometry alone does not identify physical rates. Timed trajectories can distinguish these systems; this control does not refute methods that use them.

A valid capacity interval requires the full target functional, correct boundary values and an admissible unit flow. Replacing integrals by sample averages requires a separate justification of uncertainty and support. Conversion to a reported rate must specify its population and physical-time convention; capacity is not universally an inverse mean first-passage time. A tight valid interval can bound rate uncertainty without naming every path, but constructing one affordably in a high-dimensional physical model remains unqualified here.

Decision and next update

Do not escalate a neural parameterization of classical primal/dual formulas, or ordinary convergence reporting, as a new ML contribution. No concrete admissible integration/flow operation with a distinctive benefit has yet been specified. This is narrower than closing reaction-rate learning: a particular operation could still create a useful measurement-method question. A full final truth contract or new theorem is not required just to form F1. The current generic learned-MC re-entry restriction remains in force; no proposal-selection candidate was harvested.

Stop this bounded source chain and move to another unsaturated intervention unless a concrete operation changes the assessment. There is no new family-wide saturation or re-entry gate. No scientific implementation, outcome payload, simulation, training, GPU work, delegation, forecast or machine card.

Accounting: Paper G 89 formulations / 29 cycles / 0 cards; detailed ledger 36 cycles / 173 raw; inclusive history 45 cycles / 229 raw. Graph unchanged at 333 nodes / 279 edges / 1980 locators. Three source records bring evidence accounting to 1250; candidate 0 / parked 14. Validation is recorded in a separate completion receipt. Broad goal incomplete.
