# Paper G Cycle42 — learned moves inside a fixed polymer knot sector

PRIVATE / INTERNAL. Exploratory F0/F1 record, 2026-09-14 NZ. One provisional simulator-method question; no F2 qualification or execution authority.

## Question and scientific value

Can a learned proposal over certified topology-preserving segment moves reduce the total cost of estimating equilibrium collapse statistics of a closed polymer with fixed knot type, compared with tuned geometric move selection and conventional enhanced sampling using the same moves and Hamiltonian?

The native state is a closed self-avoiding polygon, declared monomer count, knot convention, embedding space and interaction energy. The controlled action is the proposal distribution over legal moves. The response is error and effective sample cost for energy, radius-of-gyration distributions and a declared knot-localization statistic across a frozen temperature range. No inference about real-time folding kinetics follows from Monte Carlo mixing.

H1: learned state-dependent selection exploits repeatable geometric bottlenecks, improving decorrelation beyond simple steric screening and hand-designed proposal weights. H0: hard geometric filtering, established enhanced sampling and ordinary tuning explain the benefit; learned proposals add training cost or move among similar configurations without improving the target observables. A positive answer identifies a transferable sampling mechanism. A null answer identifies when direct geometry suffices for fixed-topology thermodynamics. A classification score or visually correct knot is not the discriminator.

The first reference problem should use a specified lattice polygon model, where small cases may admit enumeration and move checks can have explicit scope. A continuum model is an independent later extension, not interchangeable truth. Exact reachable-component coverage, reference mixing and usable size remain unqualified. This is a method-efficiency question, not a new universality law or a contradiction between published systems.

## Bounded primary screen

Three works retained, at selected rather than full-review depth:

1. Zhang et al., [Generating knotted polymer and protein structures by machine learning](https://doi.org/10.1038/s42004-026-02082-8), 2026. Indexed version-of-record conclusions and selected [article-in-press methods](https://www.nature.com/articles/s42004-026-02082-8_reference.pdf) describe knot-classifier-guided diffusion on bond vectors, trained on Langevin ring ensembles. The authors report structural distributions, including radius and knot size; they must not be represented as testing only classification. This is a direct topology-conditioned generation parent. Selected reading does not establish the proposed matched-budget sampler comparison or any observed failure. Version-of-record supplement details remain to be reconciled before a full methods claim.
2. Chiarantoni et al., [Generative Modeling of Entangled Polymers with a Distance-Based Variational Autoencoder](https://arxiv.org/html/2512.10131v1), 2025, selected section II. A single polyethylene globule is modeled using an SDK chain, distance-matrix VAE, coordinate embedding and short dynamics. Energy, size and entanglement are studied. The chain setup is not a certified fixed-knot ring ensemble. Its generation/relaxation pipeline is an adjacent baseline, not a matched physical disagreement with the ring study.
3. Zhao and Ferrari, [A numerical technique for preserving the topology of polymer knots: The case of short-range attractive interactions](https://arxiv.org/pdf/1212.6569), arXiv v1 2012 / publication DOI [10.5506/APhysPolB.44.1193](https://doi.org/10.5506/APhysPolB.44.1193), 2013. Selected introduction and sampling method combine lattice pivot moves, excluded-area topology checks and Wang–Landau density-of-states sampling for thermal knot observables. The text restricts exactness of its topology check to moves involving a small number of segments. Do not generalize that guarantee to arbitrary learned deformations or infer global ergodicity. Fixed-knot thermodynamic sampling itself is established.

Earlier nucleation intake concerned different Ising/ice systems and pointwise committor versus rate targets; no matched disagreement or complete raw question was formed. FlowBack and other polymer search hits were intake, not additional reviewed works. One question was allocated after this intake and before the selected methods/controls. This was not a twelve-program cycle; measurement and intervention sampling targets were unmet, with no broad source-scarcity claim.

## C1 — correct topology does not identify the conditional measure

For two equal-energy microstates x and y in the same knot sector K, the canonical conditional probabilities are 1/2 each. A generator with probabilities 0.9 and 0.1 is 100% correct on knot type while estimating the indicator of x as 0.9. Filtering out other knot sectors leaves this discrepancy unchanged. This elementary finite-state control proves only that support correctness is insufficient. It is not a polymer observation or a diagnosis of either neural architecture. Ideal conditional diffusion can reproduce the correct conditional distribution; approximate classifier guidance is not intrinsically biased by definition.

Likewise, short relaxation is not an algebraic guarantee of equilibration. If a two-state reversible kernel has nontrivial eigenvalue lambda, its initial probability deviation is multiplied by lambda^t after t steps. An initially biased distribution remains biased for finite t when lambda is near one. No claim about the papers' actual relaxation times follows.

## C2 — learned legal moves have a standard exact correction

For a frozen proposal q_theta(y|x) over a declared finite fixed-knot state set and target pi(x) proportional to exp(-beta E(x)), accept a proposed move with

\[
\alpha(x,y)=\min\{1,\exp[-\beta(E(y)-E(x))]\,q_\theta(x|y)/q_\theta(y|x)\}.
\]

Both directions then carry probability flux min{pi(x)q_theta(y|x), pi(y)q_theta(x|y)}. This proves detailed balance, not fast mixing or coverage of disconnected communicating classes. Geometric rejection can be represented as self-loops; any state-dependent resampling until a valid move must account for its normalization in q. Multiple move labels producing the same y require the full proposal probability or a valid auxiliary-variable construction. Freeze adaptation for this argument. These are standard requirements, not a new theorem.

A concrete tentative design is to learn a probability distribution over an explicit library of segment pivots, with a no-change option and a small baseline-proposal mixture. Such a mixture preserves the baseline's support but cannot cure its missing connectivity. Compare learned selection with geometric feasibility masks, length-weighted pivot policies, local moves and a matched enhanced-sampling variant. Compare corrected neural proposals too when their proposal probabilities and target contract are available. Adding Metropolis correction alone has no novelty; acceptance rate alone is not effective sampling gain.

## F1 disposition and next decisive check

Retain `g42_fixed_knot_learned_moves` provisionally at F1. The native obstacle is sampling within constrained embedded-chain configurations; it is not the saturated calibration-transfer template or a revival of market weighted-ensemble universality. Direct knot generation and classical sampling parents rule out broad first-method claims. The three-work screen is insufficient to establish a distinctive proposal-selection contribution.

Next, perform a bounded learned-Monte-Carlo/pivot-policy collision review and hand-check a move library whose forward/reverse probabilities and topology guarantee are explicit. Require a concrete source of decorrelation advantage over geometric heuristics. Park if only generic neural move weighting plus Metropolis remains. No full fifteen-work audit or publication probability is warranted yet.

The early truth contract must freeze the exact Hamiltonian, move support, knot/chirality convention, chain length, boundary conditions, temperature and target measure. Use separate chain/seed ensembles for training and untouched confirmation; correlated frames are not independent splits. Any small-state enumeration must establish the covered component. Larger references need independent samplers, convergence checks and uncertainty; count reference generation, training, topology checks, rejection and correction in total cost. Source rights, payload schema, confirmation assets, independent replication and feasible run cost are not yet qualified. No code, data or model payload was accessed, and no simulations or scientific implementation were run.

Paper G totals: 86 formulations / 26 cycles / 0 machine cards. Detailed ledger: 33 cycles / 170 raw questions; inclusive history: 42 / 226. Graph: 330 nodes / 279 edges / 1,938 locators; source registry: 1,209 records. One candidate, eleven parked routes. These counts do not measure scientific quality. The broader ICLR/ICML objective remains incomplete.
