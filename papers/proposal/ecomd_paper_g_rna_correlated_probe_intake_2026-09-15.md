# Paper G: correlated RNA probing intake

PRIVATE / INTERNAL — 2026-09-15. Selected primary-text assessment, excluded from public evidence.

Within-molecule correlations, conformer clustering and state-specific contact inference already have direct parents. A potentially useful distinction is between pre-existing heterogeneity and chemical-probe-induced coupling, but no original learning question is qualified by this intake. In particular, a concentration-dependent inferred cluster is not by itself an independent measurement of a changed native conformer population.

## Primary comparisons and actual reading depth

- [Homan et al., 2014, RING-MaP](https://pmc.ncbi.nlm.nih.gov/articles/PMC4183288/): selected indexed main text describes correlated modifications, spectral clustering, several RNA targets and ligand/magnesium-dependent ensembles. Generic exploitation of joint modification patterns is occupied. Full supplementary controls were not read; published validation is preserved.
- [Olson et al., 2022, DANCE-MaP](https://pmc.ncbi.nlm.nih.gov/articles/PMC9081252/): selected indexed main/methods describe modified Bernoulli-mixture fitting with missing-data handling, followed by state-specific PAIR/RING analysis. Adenine-riboswitch titration and a stabilizing mutant provide controls. Here the paper's abbreviation ML means maximum likelihood. Replacing average reactivity by mixture inference or adding state-specific contacts is not new. Full supplements and software were not audited.
- [Ehrhardt and Weeks, 2020, time-resolved RING-MaP](https://pmc.ncbi.nlm.nih.gov/articles/PMC7917579/): selected main text explicitly describes probe-induced sequential unfolding as the basis for correlated modification. TMO supports seconds-scale probing; magnesium initiates RNase P folding, and a loop-disrupting mutant tests a folding mechanism. TMO and DMS have some site-specific reactivity differences, so switching reagents is not a pure clock intervention. Published concentration/structure controls remain valid within their scope. The supplementary kinetic details were not read.
- [Arnold et al., 2025](https://academic.oup.com/nar/article/53/7/gkaf290/8114316): selected indexed methods and results compare 2.5 versus 5.0 mM NMIA on a 236-nt RRE construct. DRACO reports two clusters at the lower concentration and an additional 9% cluster at the higher concentration. Separate RT-stop/Rsample results also vary with probe concentration. The selected NMR experiments address smaller hairpins and imino-water exchange; they are not independent same-condition population measurements of this RRE cluster. These observations motivate further discrimination but do not alone separate structural redistribution, altered emissions and finite-data clustering. No raw reads or full supplementary validation were accessed.

These are four retained primary lineages at unequal selected depth. Review articles, DREEM/DRACO method citations and 2026 nanopore results appeared as search leads only; they are not additional retained works. Published outcomes are development evidence. No article's entire empirical claim has been independently checked.

## C1: two distinct sources of correlation

For modification indicators X_i and X_j, and a latent pre-probe conformer Z,

\[
\operatorname{Cov}(X_i,X_j)
=\operatorname{Cov}_Z(r_i(Z),r_j(Z))
+\mathbb E_Z[\operatorname{Cov}(X_i,X_j\mid Z)].
\]

For two states, the first term is pi(1−pi)(r_i1−r_i0)(r_j1−r_j0). The second term can include within-state reaction coupling. The distinction is elementary total covariance, not a new theorem. Dose-dependent r_i values can change observed correlations even when pi is constant. This neither proves a DANCE-MaP failure nor says its read-assignment strategy ignores all within-state information.

## C2: quadratic low-dose scaling is not a unique mechanism signature

Let d denote integrated probe exposure in a deliberately restricted model where reaction hazards scale with probe concentration. Under a static conformer mixture with conditionally independent reactions and rates a_Z,b_Z,

\[
P(X_i=1)=\mathbb E[a_Z]d+O(d^2),\quad
P(X_j=1)=\mathbb E[b_Z]d+O(d^2),
\]
\[
\operatorname{Cov}(X_i,X_j)=\operatorname{Cov}(a_Z,b_Z)d^2+O(d^3).
\]

Alternatively start from one conformer with initial reaction rates a,b. Modification of i changes the rate at j to b+gamma, and modification of j changes the rate at i to a+eta, with nonnegative rates. Summing the two possible reaction orders gives

\[
P(X_i=X_j=1)
=\tfrac12[a(b+\gamma)+b(a+\eta)]d^2+O(d^3),
\]
\[
\operatorname{Cov}(X_i,X_j)
=\tfrac12(a\gamma+b\eta)d^2+O(d^3).
\]

Thus a positive quadratic covariance can arise either from pre-existing heterogeneity or sequential reaction coupling. For an explicit leading-order match, take equal mixture weights with a_Z=a±u and b_Z=b±v, where 0<u<a and 0<v<b. The static covariance coefficient is uv. The sequential model with eta=0 and gamma=2uv/a has the same first-order marginals and second-order covariance coefficient. Higher-order probabilities and second-order marginal terms are not asserted equal. A sufficiently informative full dose/time experiment can still distinguish these models.

This hand control rules out a proposed shortcut: observing d² scaling alone does not assign the mechanism. It is not a calibrated model of a particular RNA, a universal identifiability result, or a standalone ML contribution. Intrinsic folding, probe hydrolysis, noncovalent probe binding and readout effects can introduce additional clocks; equal nominal concentration-times-duration is then not automatically an equal intervention.

## Decision

Do not advance generic correlated-read clustering, dose-aware correction or probe-induced unfolding as original contributions. Existing papers already contain the central inference operations and physical mechanism. The retained 236-nt concentration pair is a concrete development lead, but a distinctive learning operation and a matched discriminator of population versus emission changes are not established. The small-RNA NMR observations and RNase P TMO experiments cannot silently supply that missing same-target reference.

A substantive next step must name the same RNA construct, supported intervention, independent structural or reaction-kinetic observable, and prediction that distinguishes the alternatives. It must also explain value beyond mixture fitting and existing contact analyses. No full final truth contract is required at this early stage; the present limitation is the absence of that concrete increment, not a failed late-stage threshold. No broad RNA or probing-method closure follows.

Four new primary works, two analytic controls, zero raw questions/cycles/status changes/forecasts/cards. No scientific implementation, simulation, training, outcome payload or laboratory work. Paper G remains 89 formulations / 29 cycles / 0 qualified cards; evidence1336 and graph333/279/1995 after recording. ICLR/ICML objective incomplete.
