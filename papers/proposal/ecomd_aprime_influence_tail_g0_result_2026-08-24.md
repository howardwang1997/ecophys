# A′ exchange influence-tail certificate — G0 result

**Date:** 2026-08-24

**Verdict:** **FAIL / RED at T0--T1**

**Machine record:** `configs/empirical_physics/ecomd_aprime_influence_tail_g0_v1.yaml`

**Resource boundary:** paper-and-pencil arguments, primary literature and official platform/source metadata only.
No agent was downloaded or installed; no implementation, simulator outcome, model API, EcoMD run, GPU or remote
compute was used.

## Decision

The parked composition-generalizing path-kernel card is closed. The proposed implication

\[
q_H^{(1)}<1
\quad\Longrightarrow\quad
\text{population-uniform high-order interaction tail}
\]

is false. A normalized replace-one influence controls a first finite difference. It does not control all higher
mixed differences of a composition-indexed probability law. Two explicit market kernels satisfy
\(q_H^{(1)}<1\) while defeating every proposed raw Newton/Möbius tail argument. Conversely, a kernel can have
\(q_H^{(1)}>1\) and terminate exactly at second order, so \(q_H=1\) is not a necessary phase boundary.

A sound repair is possible only after adding a bounded composition-affine generator, a genuine polymer activity
condition, stochastic domination of causal clusters or an equivalent high-order analyticity assumption. Those
The specific repairs enumerated here fall within established semigroup-perturbation,
Dobrushin/disagreement-percolation or spacetime-cluster theory families. They do not leave the frozen A′ central
theorem intact.

The proposed Power TAC--SCML transfer also fails before execution: population dose and platform are confounded,
and the two interventions do not preserve one scientific path-law estimand. This system failure is corroborating,
not the first terminal gate; the mathematical counterexample already requires stopping.

## 1. Formal object and the normalization obstruction

For a fixed population of \(N\) role slots, freeze agent versions, initialization, scheduler, tie-breaking,
exogenous shocks and an anonymous observation map. Let \(P^H_{N,\mathbf n}\) be the resulting finite-horizon path
law when \(\mathbf n\) gives the counts of non-reference agent types. Define

\[
\kappa^H_{N,\mathbf k}
=
\Delta_1^{k_1}\cdots\Delta_d^{k_d}P^H_{N,\mathbf 0}.
\]

The exact multivariate Newton identity is

\[
P^H_{N,\mathbf n}
=
\sum_{\mathbf k\leq\mathbf n}
{\mathbf n\choose\mathbf k}\kappa^H_{N,\mathbf k}.
\]

These \(\kappa\)'s are signed Möbius interaction coefficients. They are not automatically connected
Ursell/cumulant coefficients. A truncation of the displayed sum has total mass one but can assign negative mass,
so it is not generally a probability kernel and Wasserstein or KL distance to it need not be defined.

There is an additional obstruction if the coefficient is instead defined once on the unbounded lattice,
\(C_\alpha=\Delta^\alpha F(0)\), and the proposed shell bound is required uniformly over all compositions:

\[
\sum_{|\alpha|=k,\,\alpha\leq n}
{n\choose\alpha}\lVert C_\alpha\rVert
\leq Mq^k.
\]

Fix a nonzero \(\alpha\) and take \(n=m\alpha\). Since
\({m\alpha\choose\alpha}\to\infty\), the bound forces \(C_\alpha=0\). Requiring it for every order above
\(K\) therefore assumes exact degree at most \(K\), rather than proving approximate population-uniform decay.
Restricting \(n\) to a fixed finite box avoids the contradiction but removes unseen-population extrapolation.

Add/delete Newton differences and fixed-\(N\) replace-one differences are also distinct interventions. They agree
only after specifying a null-agent embedding and projective consistency across \(N\); neither was available from
the exchange semantics.

## 2. Decisive counterexamples

### 2.1 Small replace-one influence, constant truncation error

Consider a one-step global batch auction with binary output \(Y\). If \(m\) of the \(N\) agents have type one,
let

\[
\Pr(Y=1\mid m)
=
\frac12+\frac{q}{2N}(-1)^m,
\qquad 0<q<1.
\]

Every adjacent composition has

\[
d_{\mathrm{TV}}(P_{m+1},P_m)=\frac qN,
\]

so the normalized replace-one quantity \(N\sup_m d_{\mathrm{TV}}(P_{m+1},P_m)\) is exactly \(q<1\). However,

\[
\Delta^r p(0)=\frac q{2N}(-2)^r.
\]

For even \(N\), the first-order Newton approximation at \(m=N\) is

\[
p_{\leq1}(N)=\frac12-q+\frac q{2N},
\]

whereas the true value is \(p(N)=\frac12+q/(2N)\). The error is exactly \(q\), not
\(O(q^2)\). Higher differences grow as \(2^r\), and the truncated signed reconstruction can leave
\([0,1]\). The complete law remains valid only because its high-order terms cancel.

This is a valid event-driven market kernel, not a pathology excluded by the frozen question: a global auction or
batch rule may depend on a parity, threshold or other collective statistic. Excluding it requires a locality or
analyticity assumption stronger than first-order replace-one influence.

### 2.2 A first active agent and divergent raw Newton shells

Let \(P_0=\delta_0\) and, for every \(m\geq1\),

\[
P_m=(1-\varepsilon_N)\delta_0+\varepsilon_N\delta_1,
\qquad \varepsilon_N=\frac1{2N}.
\]

This models a small event triggered by the first active agent. The composition-level definition gives
\(q_N=N\sup_m d_{\mathrm{TV}}(P_{m+1},P_m)=N\varepsilon_N=1/2\). Yet for every \(k\geq1\),

\[
C_{N,k}=(-1)^{k+1}\varepsilon_N(\delta_1-\delta_0),
\]

and at \(m=N\),

\[
{N\choose k}\lVert C_{N,k}\rVert
\asymp \frac{N^{k-1}}{2k!}.
\]

For any fixed \(k\geq2\), that shell diverges with population. For \(1\leq K<N\), the exact remainder after
order \(K\) is proportional to \(\varepsilon_N{N-1\choose K}\), again contradicting a population-independent
geometric bound.

### 2.3 Influence above one with exact finite order

Let \(P_m\) be Bernoulli with

\[
p_N(m)=4\frac mN\left(1-\frac mN\right).
\]

Then

\[
N\max_m|p_N(m+1)-p_N(m)|=4\frac{N-1}{N}>1
\]

for \(N>1\), while \(p_N\) is a quadratic polynomial and every Newton coefficient above order two is zero.
Thus a fixed second-order approximation is exact despite \(q_H^{(1)}>1\). A Dobrushin-type norm is a sufficient
small-coupling condition, not a universal necessary boundary.

### 2.4 Mean offspring below one is not a geometric cluster certificate

Suppose every affected event independently produces \(M\) affected children with probability \(q/M\) and none
otherwise, where \(q<1\). Its expected offspring is \(q\), but already in the first generation

\[
\Pr(|\mathcal C|\geq M+1)=\frac qM.
\]

For any fixed \(C<\infty\) and \(\rho<1\) that depend only on \(q\), taking \(M\) sufficiently large gives
\(q/M>C\rho^M\). Thus the mean alone supplies no uniform exponential cluster tail. A subcritical mean can bound
expected cluster size under suitable independence, but the frozen path-law tail needs bounded offspring, a
uniform exponential moment or stochastic domination. Those are additional mechanism assumptions, not
consequences of a measured first-order response.

## 3. The strongest sound repair and why it does not rescue A′

Assume instead that the lifted observable process has a composition-affine Markov generator throughout the
composition simplex,

\[
L_{N,\theta}=L_{N,0}+\sum_{a=1}^d\theta_aW_{N,a},
\qquad \theta_a=n_a/N,
\]

whose semigroup is contractive in a signed-measure Banach norm, with
\(\sup_{N,a}\lVert W_{N,a}\rVert\leq v\). Duhamel/Dyson--Phillips expansion and the finite-difference integral
formula give

\[
\lVert\kappa^H_{N,\mathbf k}\rVert
\leq\left(\frac{Hv}{N}\right)^{|\mathbf k|}.
\]

Writing \(m=\sum_an_a\) and using multivariate Vandermonde,

\[
\left\lVert
P^H_{N,\mathbf n}-P^{H,\leq K}_{N,\mathbf n}
\right\rVert
\leq
\sum_{r=K+1}^m{m\choose r}\left(\frac{Hv}{N}\right)^r
\leq
e^{Hv}\frac{(Hv)^{K+1}}{(K+1)!}.
\]

Here \(P^{H,\leq K}_{N,\mathbf n}\) is the Newton truncation defined above, and the finite-difference integral
argument requires the continuous \(\theta\)-interpolation on the full simplex. The lemma is mathematically useful
but not the proposed theorem. State-dependent inventory, priority and threshold rules can be encoded inside the
operators, but the assumption excludes the non-affine or population-unbounded composition dependence through
which they and global schedulers generate the counterexamples. The truncated signed measure is still not
necessarily a probability kernel; projection or resummation would need a separate error analysis. The lemma also
does not identify an unseen \(N\) if \(L_{N,0}\) may vary arbitrarily with \(N\); projective consistency or a
mean-field limit is still required.

Replacing affine perturbations with causal clusters leads to the same conclusion. One must derive a
Kotecký--Preiss activity bound, weighted Dobrushin contraction, disagreement domination or comparable exponential
cluster condition. The certificate is then the mature cluster condition, not ordinary replace-one influence.

## 4. Direct theory collisions

The failed logical implication is decisive on its own. The closest primary literature shows that its viable
repairs are also occupied theory families:

| Primary work | Direct relation to a repaired A′ |
|---|---|
| [Dobrushin 1970](https://doi.org/10.1137/1115049) and [Föllmer 1982](https://doi.org/10.1016/0022-1236(82)90053-2) | conditional-kernel influence matrices, comparison and geometric propagation through \((I-C)^{-1}\) |
| [Dobrushin--Shlosman 1987](https://doi.org/10.1007/BF01011153) | complete analyticity and truncated-correlation decay; stronger high-order assumptions than a one-step norm |
| [Rebeschini--van Handel 2014](https://doi.org/10.1007/s10955-014-1087-7) | block and one-sided comparison, including dynamic/local marginal bounds beyond classical single-site criteria |
| [van den Berg--Maes 1994](https://doi.org/10.1214/aop/1176988728) | disagreement clusters linking a local perturbation to its propagated effect |
| [Kotecký--Preiss 1986](https://doi.org/10.1007/BF01211762) and [Fernández--Procacci 2007](https://doi.org/10.1007/s00220-007-0279-2) | absolute convergence and cluster-weight bounds under explicit polymer-activity hypotheses and a convergence margin |
| [Maes--Netočný 2002](https://doi.org/10.1088/0305-4470/35/13/303) | the closest dynamic methodological precedent: spacetime/Gibbs expansion for weakly coupled interacting-particle path laws, not a composition-indexed raw-Möbius truncation theorem |
| [Jansen 2019](https://doi.org/10.1017/APR.2019.46) and [Zass 2022](https://www.math-mprf.org/journal/articles/id1643/) | factorial cumulants/log-Laplace clusters and path-marked Gibbs/Langevin cluster expansions; raw laws are not connected cumulants |
| [Hawkes--Oakes 1974](https://doi.org/10.2307/3212693) and [Brémaud--Massoulié 1996](https://doi.org/10.1214/aop/1065725193) | cluster representation for linear self-exciting processes and sufficient subcritical stability conditions, not a necessary composition-tail threshold |
| [Braun--Hepp 1977](https://doi.org/10.1007/BF01611497) | Vlasov limit and propagation of chaos under explicit mean-field scaling |
| [Dobrushin 1979](https://doi.org/10.1007/BF01077243) | Wasserstein stability for the Vlasov limit |
| [Lacker 2023](https://doi.org/10.2140/pmp.2023.4.377) | finite-\(k\) marginal entropy bounds, not unrestricted global path-law total variation |
| [Féray 2018](https://doi.org/10.1214/18-EJP222) | spanning-tree control of connected cumulants conditional on first establishing a weighted dependency graph |
| [Yang et al. 2018](https://proceedings.mlr.press/v80/yang18d.html) and [Khora 2026](https://arxiv.org/abs/2608.08600) | task-level adjacent prior on large-population approximation and population-scalable world modeling, not an exact theorem reduction or an A′ certificate |

The exact theorem shape was not found as a single named market result. That does not save it: its frozen premise
is insufficient, while each non-circular repair maps to established weak-dependence, cluster or mean-field theory.

## 5. Power TAC--SCML contract audit

The two platforms are real and useful external systems, but they do not instantiate one low-dose-to-high-dose
test.

The outcome-blind audit identified a version-pinned, source-only starting registry:

| Component | Frozen source | Licence/status |
|---|---|---|
| [Power TAC server 1.9.0](https://github.com/powertac/powertac-server/tree/b217951b9ab00274d296f60cf7faee17935d31dd) | `b217951b9ab00274d296f60cf7faee17935d31dd` | Apache-2.0 |
| [Power TAC sample broker 1.9.0](https://github.com/powertac/sample-broker/tree/00024c750665d22887d01bc42be27e3d069e1b6e) | `00024c750665d22887d01bc42be27e3d069e1b6e` | Apache-2.0 declared in its POM; no root licence text |
| [SCML 0.8.3](https://github.com/yasserfarouk/scml/tree/c0cbc5d19df7e1161982b802106462b9cd8254fa) | `c0cbc5d19df7e1161982b802106462b9cd8254fa` | GPL-2.0-only repository licence |
| [SCML agents 0.5.0](https://github.com/yasserfarouk/scml-agents/tree/a0cf1e20ff365df74f2cde9406f6965301f9189e) | `a0cf1e20ff365df74f2cde9406f6965301f9189e` | GPL-2.0-only repository licence |
| [NegMAS 0.15.6](https://github.com/yasserfarouk/negmas/tree/5f9cb684d84ff397d382fb600b8baa4c7d417c0b) | `5f9cb684d84ff397d382fb600b8baa4c7d417c0b` | pinned core dependency; not a complete transitive lock |

The independent-agent inventory is concrete but not executable-qualified:

- Power TAC: [TUC](https://github.com/StavrosOrf/PowerTacAgent/tree/0ef5d611c6a8ebf4aeb379b49354eb61b8f60472)
  has a root Apache-2.0 licence and a `1.8.0-SNAPSHOT` dependency;
  [VidyutVanika](https://github.com/iamsanjay97/VidyutVanika/tree/cf35a24b388f1ce3ddaf377591c9f8d1a2e5009c)
  has Apache metadata in its POM but no root licence text and uses `1.9.0-SNAPSHOT`; and
  [SoPa 2023](https://github.com/raptis-p/SoPa-Agent-2023/tree/7b64d3e9354ec68a3250f803050332d4d4f091c5)
  has a root MIT licence and uses `1.9.0-SNAPSHOT`. These are three versionable source inventories, not three
  dependency-closed executable artifacts. The official sample broker is not an independent-team artifact.
- Under the central SCML-agents licence, the frozen tree contains independent Standard-track source for
  [Coyote](https://github.com/yasserfarouk/scml-agents/blob/a0cf1e20ff365df74f2cde9406f6965301f9189e/scml_agents/scml2024/standard/coyoteteam/group2.py),
  [Team 178](https://github.com/yasserfarouk/scml-agents/blob/a0cf1e20ff365df74f2cde9406f6965301f9189e/scml_agents/scml2024/standard/team_178/ax.py)
  and [Team Penguin](https://github.com/yasserfarouk/scml-agents/blob/a0cf1e20ff365df74f2cde9406f6965301f9189e/scml_agents/scml2024/standard/team_penguin/penguinagent.py).
  This is source-inventory qualification only; agent-level dependencies, RNG behavior and executability were not
  verified under the no-run contract.

Power TAC supplies a server-side
[`RandomSeedRepo`](https://github.com/powertac/powertac-server/blob/b217951b9ab00274d296f60cf7faee17935d31dd/server-interface/src/main/java/org/powertac/common/repo/RandomSeedRepo.java)
plus seed, weather and bootstrap replay controls, but these do not cover third-party broker RNGs, clocks, threads
or network timing. SCML can freeze a generated world
configuration and assignment but has no documented seed contract spanning the world and every third-party agent.
Consequently, end-to-end or bitwise replay was not established under this no-run audit; statistical
reproducibility remains a future engineering question.

- In Power TAC, adding a broker changes competition in a global electricity retail, wholesale and balancing
  system. The path contains tariffs, customer switching, auction activity and settlement under one global game.
- In SCML, adding a factory manager at a supply-chain layer changes bilateral negotiations, production and
  contracts. The default generator can also change opponent degree, profiles and exogenous contract allocation
  as population changes. Setting `random_agent_types=False` and freezing exact world configurations can control
  type and layer assignment and some of these covariates; even then, the local bilateral supply-chain mechanism
  remains different from Power TAC's global auction, tariff and balancing mechanism.

Training only on low broker counts in Power TAC and testing only on high manager counts in SCML therefore changes
both system and dose. No result from these two cells alone can distinguish population extrapolation from platform
shift. A generic label such as “price path” or “welfare” does not make the intervention, state, filtration or
endpoint the same.

A valid invariance claim would need a prespecified dose map \(d_s(c)\), history map \(\Phi_s\) and common kernel
\(K_d^\star\) satisfying a strong-lumpability condition such as

\[
K_{s,c}\!\left(x,\Phi_s^{-1}(B)\right)
=
K_{d_s(c)}^\star\!\left(\Phi_s(x),B\right),
\qquad\forall x,B.
\]

The official mechanisms do not supply this relation. With only the Power-TAC-low and SCML-high cells, the observed
contrast contains an unidentified mechanism effect, dose effect and mechanism-by-dose interaction. At minimum a
four-cell design \((P_L,P_H,S_L,S_H)\) is required. It can estimate each platform's within-system low-to-high
contrast and a system-by-nominal-dose interaction, but it does not automatically make the two interventions one
estimand. Platform and source availability are not an experiment contract.

The only honest cross-system alternative would estimate a separate intensive influence/cluster certificate in
each system and test a theorem stated on that common abstract object. That is algorithmic transfer, not a numeric
Power TAC low-dose prediction of an SCML high-dose path. It would require a new theorem; the frozen first-order
influence candidate for such a theorem has already failed above.

## 6. Binding closure and reusable result

The following claims are closed for this research program:

- raw Newton/Möbius truncation of a market path law is a new connected many-body method;
- \(q_H^{(1)}<1\) alone certifies a population-uniform high-order tail;
- \(q_H=1\) is a universal transition separating low-order predictability from failure; and
- Power TAC low dose to SCML high dose is one no-retuning population-generalization experiment.

The finite counterexamples, probability-kernel check, fixed-\(N\) intervention discipline and external-system
estimand audit remain reusable as vetoes for future cards.

Reopening requires a genuinely new route, not a normalization tweak: specify a valid resummed probability object
or an intensive local observable; derive a non-circular exchange-specific causal-cluster condition; prove a
result strictly beyond spacetime polymer/comparison theory; and freeze a projectively consistent two-system
estimand before any outcome access. The honest prior for such a top-venue route is below 1%. No implementation or
empirical acquisition is authorized from A′.
