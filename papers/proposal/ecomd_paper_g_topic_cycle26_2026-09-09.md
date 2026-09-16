# Paper G Cycle 26: specify the measurement target before ranking methods

**PRIVATE / INTERNAL — exploratory topic selection, not public or
confirmatory evidence.** Literature cutoff: September 9, 2026.

Two measurement questions receive F1 screens and neither advances. A
vanishing dispatch-cost perturbation need not recover an emissions-minimizing
tie rule. A lower asymmetric basis-risk score need not improve an insured's
mean–variance objective. Both statements have elementary explanations and
directly relevant primary predecessors; neither is an independent Paper G
contribution or a refutation of the complete papers.

Record: `research/paper_g/cycle26_question_screen_20260909.yaml`. Source
reading and formulation were interleaved, with no prospective forecast.

## Questions and eligibility

The registry and evidence/trigger ledgers contained neither exact formulation.
These concern a dispatch selection rule and an insurance payment score,
respectively. They do not reopen CfD identification, nonconvex settlement,
generic simulator certification, hidden-account inference, carbon-inventory
condensation or the closed coissuer/buyback questions. No field causal
inference or new generic measurement algorithm was proposed.

| ID | Native object and rival explanations | Discriminator and two-sided value | Decision |
| --- | --- | --- | --- |
| G26-01, measurement | Emissions response to demand under tied economic dispatch. Tiny cost noise recovers the same target as emissions-minimizing tie selection, versus selecting a different dispatch response even as noise vanishes. | Solve a tied two-generator market and both perturbation signs. Agreement would support a common target; disagreement identifies the selection rule that must be frozen. | F1 closed: different dispatch targets and elementary optimizer selection; no new calibration or theorem. |
| G26-02, measurement | Ranking feasible parametric insurance payouts. A lower asymmetric squared basis-risk score certifies higher mean–variance welfare, versus premium and residual-risk changes reversing the ranking. | Compare exact score and welfare optima under the same loss law, trigger, premium rule and budget. Agreement would justify the score certificate; reversal defines its limits. | F1 closed: direct utility-weighting prior and objective mismatch; no new contract-design contribution. |

Both are our screening hypotheses. We found no verified conflict between
primary models with the same full target. This compact two-program cycle
samples two measurement questions; it is not a twelve-program quota cycle.

## A. A complete dispatch rule is part of emissions truth

Sun–Cote define a two-stage rule: minimize economic cost, then emissions
within the cost-optimal set. Gorka–Rhodes–Roald describe adding small cost
noise for duplicate generator costs before sensitivity calculation. These
are distinct selection procedures, not automatically interchangeable
estimators. [Sun–Cote, section 2.2](https://arxiv.org/html/2603.19530v1);
[Gorka et al., v3, Appendix A.2](https://arxiv.org/html/2411.06560v3).

Consider a declared single-node, one-hour model. Two generators have
capacities 2, zero minimum output, costs c=(1,1), and emissions rates
e=(0,1). Demand d lies strictly between 0 and 2. The economic dispatch is

\[
\min_{g_1,g_2}g_1+g_2,
\qquad g_1+g_2=d,\quad 0\leq g_i\leq2.
\]

Every feasible dispatch has cost d. Emissions-minimizing selection gives
g=(d,0), E(d)=0, and dE/dd=0. For every delta>0, costs (1+delta,1)
instead uniquely select g=(0,d), giving E_delta(d)=d and dE_delta/dd=1.
Costs (1,1+delta) select g=(d,0) and derivative zero. Thus

\[
\lim_{\delta\downarrow0} E_\delta(d)=d\ne E_{lex}(d)=0.
\]

For the perturbed minimizer g_delta and any feasible g in this fixture,
the absolute change in its objective value from the base cost is bounded
by delta*d. The economic perturbation therefore vanishes while the
emissions difference remains d. This is an exact selection boundary, not
a numerical experiment or a field emissions estimate.

As an additional paper-only comparison, let costs be
c_i=1+delta*xi_i, with independent identically distributed continuous
xi_i supported on [0,1], held fixed while demand is varied. Each generator
is cheaper with probability one half. Expected emissions are d/2 and the
expected marginal response is 1/2 for every delta>0. This expectation is
computed analytically; no random draws or solver were used. The uniform
distribution is unnecessary: exchangeability and zero tie probability suffice.

Away from a tie there is a useful positive boundary. If c_2-c_1=Delta>0
and each cost perturbation is bounded in absolute value by eta<Delta/2,
generator 1 remains cheaper and the interior dispatch is unchanged.
This elementary margin bound is not a new robustness theorem.

The unqualified transfer fails at tied costs. It does not follow that an
emissions-prioritizing tie rule describes any actual operator, or that
one published implementation is scientifically invalid. Repeatedly shrinking
analyst noise cannot establish a real dispatch-selection law. The parent
selection issue is already explicit in the cited work; close the proposed
independent measurement contribution without extending it into a generic
simulator-certification claim.

## B. A basis-risk score is not a welfare certificate

Maier–Scherer's published basis-risk construction uses asymmetric squared
errors and conditional expectiles. Their April 2026 follow-up explicitly
optimizes the weighting using utility and premium principles. Avanzi et al.
separately compare budget-feasible contracts under a mean–variance objective.
These distinctions already rule out broad novelty for merely separating the
criteria. [Basis-risk paper](https://link.springer.com/article/10.1007/s13385-026-00447-w),
[utility-weighting paper, equations 6–9](https://arxiv.org/html/2604.21372v1),
[budget comparison, equations 23–24](https://onlinelibrary.wiley.com/doi/10.1111/jori.70070).

Define a hypothetical three-state contract, with no data estimated:

| Probability | Trigger I | Actual loss S | Payment |
| --- | --- | --- | --- |
| 1/2 | 0 | 0 | 0 |
| 1/4 | 1 | 1 | k |
| 1/4 | 1 | 3 | k |

Payment kI is permitted to exceed loss in a triggered state, as in the
declared parametric design. There are no fixed fees, timing frictions or
behavioral responses. Premium is pi(k)=1.1*E[kI]=11k/20. The common
premium budget is 8/5, so 0<=k<=32/11. Equal budget does **not** mean
equal premium spent.

For a fixed underpayment weight tau=.9, define the normalized score

\[
R_{.9}(k)=\mathbb E[.9(S-kI)_+^2+.1(kI-S)_+^2].
\]

For 1<=k<=3 this is

\[
R_{.9}(k)=\tfrac14[.1(k-1)^2+.9(3-k)^2].
\]

It has its feasible global minimum at k_R=14/5. On k<1 the score
decreases towards this interval; the budget bound lies below 3. The
normalization uses the expectile level tau, not the original paper's
unsquared asymmetry parameter.

Let final wealth W=w-S+kI-pi(k), and explicitly choose the mean–variance
criterion V(k)=E[W]-Var(W). This is the declared objective, not an assertion
of equivalence to every concave expected-utility preference. Direct moments give

\[
\mathbb E[W]=w-1-k/20,\qquad
\operatorname{Var}(W)=3/2-k+k^2/4,
\]
\[
V(k)=w-5/2+19k/20-k^2/4.
\]

Its unique feasible maximum is k_V=19/10. Exact comparison:

| Payout | Premium | Asymmetric score | Residual variance | Welfare |
| --- | --- | --- | --- | --- |
| k_V=1.9 | 1.045 | .2925 | .5025 | w-1.5975 |
| k_R=2.8 | 1.54 | .09 | .66 | w-1.8 |

Moving to the score-optimal contract lowers the score by .2025 but lowers
welfare by .2025 as well. Both contracts satisfy the same budget and improve
on no insurance, whose welfare is w-2.5. This is not a premium-matched
comparison and does not compare against an optimal indemnity contract.

For contrast, under a fixed loss law and fixed expected payout, the
identity E[(S-P)^2]=Var(S-P)+(E[S-P])^2 shows that unweighted squared
error and residual variance have the same ordering. If premiums are equal,
this also orders the chosen mean–variance objective. Likewise, expanding a
feasible contract class while preserving the objective and all constraints
cannot lower its optimized value: the old contract remains available.
Our score-selected example contradicts neither statement.

**Close the score-to-welfare certificate and its proposed novelty.** A
budget cap appended to a familiar objective mismatch is insufficient for a
new contribution. The cited utility paper already treats the substantive
weight/premium problem. No claim about general expected utility, demand,
solvency, actual insurance welfare or every possible index refinement follows.

## Disposition and next update

Counts: **2 raw / 2 F1 / 0 F2 / 0 F3 / 0 cards**. Five distinct retained
primary works, with selected substantive definitions/model sections inspected.
Gorka v2 and v3 are one work; the screen uses v3. No full proof audit,
prospective probability, data asset, solver, simulation or implementation.
Other indexed weather, emissions and insurance intake remained unformulated.

Retain the two exact diagnostics with their positive boundaries. Reopening
either closed formulation requires a specific result or lawful control asset
that removes its blocker and the applicable validated trigger. Further
eligible measurement intake should state the complete reference decision
rule and end-use loss before comparing methods. A physical observation or
named index alone does not establish the required measurement truth.
No new experiment, outcome access, compute or publication is authorized.
