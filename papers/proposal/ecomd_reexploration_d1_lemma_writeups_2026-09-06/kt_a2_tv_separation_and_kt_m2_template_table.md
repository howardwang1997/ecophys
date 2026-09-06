---
note: >-
  D-1 theory deliverable (2026-09-06), item KT-A2 stage-1 + KT-M2, produced under
  pi_reexploration_d1_authorization_20260906 ([NOW] theorem/schema work only). Statuses are
  per-statement and honest; engine-semantics claims carry file/line citations to the frozen
  read-only bundle experiments/lab_asset_a2/a2_exit_20260905/ (manifest fea8b136...9581c, never
  mutated) and to scripts/lab_asset/. Stage-2 empirical items (identical-input replay, single-maker
  negative control run) remain run-gated [AUTH] per
  papers/proposal/ecomd_reexploration_d1_killer_tests_and_ops_2026-09-06.md section 3.
---

# KT-A2 Stage-1 TV separation lemma + KT-M2 template-expressibility table

Companion formalism: `ecomd_reexploration_theory_appendix_2026-09-06.md` Part I Section 0 / Part I
Section 1 (M1 contract) and Part II Section 0 (F_exec). Citation discipline: every external-work
claim below is a restatement of a row of `ecomd_reexploration_d2_evidence_map_2026-09-06.md`
(GAMMA table section 1.2, ALPHA table section 2.2, ALPHA panel ruling section 2.3) or of the
killer-tests document; no new literature is cited as fact.

---

# Part I — KT-A2 stage-1: TV separation of the through-M corpus law from the kernel-blind corpus law

## 0. The attack being answered

KT-A2 (killer-tests doc, section A section 2): "re-plugging an engine" is an attack on the
**manipulation** — the claim that swapping the allocation kernel is engineering plumbing, not a
law-changing scientific manipulation. The stage-1 answer is a paper lemma: at the level of the
**training-corpus law** (before any model is trained), the two arms of the frozen DGP generate
total-variation-separated corpus distributions, with an explicit constant, and the separation
collapses exactly on the strata the stage-2 negative controls name. Stage 2 (identical-input
replay through the recorded request subsequence, and the single-maker negative control run)
verifies the same statement in the running engine and stays [AUTH].

## 1. Engine semantics used (each verified in the frozen bundle or engine code)

- **E1 (determinism surface).** The engine is deterministic given (prestate, request stream): its
  only randomness source is `random.Random(prestate.seed)` (`scripts/lab_asset/matching.py:44`),
  and the only consumption of that generator in the entire engine is
  `self.rng.randrange(eligible_units)` inside `_select_maker` (`matching.py:593`); the FIFO branch
  of `_select_maker` returns a `None` draw and consumes no randomness (`matching.py:589-590`).
  The RNG state is sealed inside `state_hash` (`matching.py:122`; schema_spec.json
  `notes.hashes`). Consequently: **the FIFO arm's full tape is a deterministic function of
  (prestate, requests)**, and the random-unit arm's tape is a deterministic function of
  (prestate, requests, draw sequence).
- **E2 (draw law).** In the random-unit branch, `eligible_units` is the sum of remaining
  quantities over the level's queue in arrival order (`matching.py:592`), `selected_unit` is
  uniform on `{0,...,eligible_units-1}`, and the maker is resolved by a cumulative walk over the
  queue in arrival order (`matching.py:594-603`). Since units are blocked by queue position,
  `P(next draw = order i | current remaining counts) = q_i^rem / R^rem` with `R^rem` the level's
  remaining quantity: sequential uniform-without-replacement over resting units (probability
  proportional to remaining quantity). This is the semantics the theory appendix P0 already
  binds ("sequential PPS-to-remaining = uniform-over-remaining-units").
- **E3 (fill size and record granularity).** FIFO fill = `min(remaining, maker_qty)` — one
  execution record per (incoming order, maker) pair with multi-unit `quantity`
  (`matching.py:292-296`); random-unit fill = 1 unit — one execution record per drawn unit
  (`matching.py:295`). Visible in the frozen fixtures: `fixture_fifo/tape.jsonl` sequence 7 has
  one execution with `quantity: 2, maker_remaining: 2`;
  `fixture_random_unit_within_price/tape.jsonl` sequences 7-8 have two executions with
  `quantity: 1` each, `maker_remaining` 3 then 2.
- **E4 (allocation_draw presence).** `allocation_draw` is appended to the execution payload iff
  the resolved draw is non-None, i.e. iff the kernel is `random_unit_within_price`
  (`matching.py:344-345`). In the frozen bundle, `allocation_draw` occurs only in
  `fixture_random_unit_within_price/tape.jsonl` (2 records) and never in `fixture_fifo/tape.jsonl`
  (consistent with the killer-tests doc section 1 grounding fact).
- **E5 (queue-rank invariance).** Fills update the maker tuple in place; queue order (arrival
  rank) is preserved after partial fills (`matching.py:618-622`). Hence the FIFO
  counterfactual allocation on the same book is well-defined while the round is in progress.
- **E6 (the frozen bundle instantiates the single-maker stratum).** Event 7 in both fixtures
  trades against a single maker order `O00000003` (quantity 4 resting at ask 101; both arms share
  `pre_aggregate_state_hash da930600...` at sequence 6). There is **no multi-order rationed level
  anywhere in the 21/22-record frozen tapes** — this is exactly the D1_03 fixture-enrichment gap
  ("Current 21-22-event fixtures cannot measure O-C, O-D or the S1a random-unit gates",
  killer-tests section 1 and experiment plan section 2; the present lemma adds: nor the KT-A2
  stage-2 multi-maker cells).
- **E7 (the two arms' prestates differ only by the kernel).** `fixture_fifo/prestate.json` and
  `fixture_random_unit_within_price/prestate.json` share seed 20260905, actors, initial book
  (`IB1`, ask 103, qty 4), bands, cash, inventory, induced schedules; they differ in
  `allocation_rule` and `session_id`. Swapping only `allocation_rule` at fixed everything-else is
  the replay contract's native operation (schema_spec.json `notes.replay`: "re-execute the
  request events from the prestate; the regenerated tape must equal the recorded tape
  record-by-record including every state hash").

## 2. Setup: corpus laws on the frozen DGPs

**DGP instance.** A frozen triple `D = (pi, rho)`: prestate `pi` and request subsequence `rho`
(the replay-contract inputs). The engine seed is a load-bearing DGP coordinate: under the corpus
contract the training corpus of a through-M arm is generated by running the engine on `D` with
seed `s`; the **corpus law** `Lam_k^G(D)` is the law of the projected tape when `s` is drawn from
the frozen seed population (`data_seed` namespace, contract C1), where `G` is the tape
projection (grammar) and `k in {fifo, ru}` the allocation rule (`ru = random_unit_within_price`).

**Projections (grammar ladder).**

- `G_agg`: aggregate prints only — level quantities/totals (the `aggregate_state_hash` view;
  anonymous level quantities, schema_spec.json `notes.hashes`).
- `F_exec` (PI-frozen D1_01): execution sub-payloads (execution id, aggressor/maker actors and
  order ids, price, quantity, maker_remaining, clocks, round), `allocation_draw` when present,
  and pre/post best bid/ask prices (prices only).
- `Pi_att` (**key-equalized attribution projection**): strip `allocation_draw`; aggregate the
  per-unit execution records of one incoming order's clearing round by maker into the per-maker
  fill-count vector `c = (c_1,...,c_m)` at the touched level (both arms are mapped onto the same
  statistic; this removes the two trivially arm-dependent payload features — draw presence (E4)
  and record granularity (E3)). `Pi_att` is a coarsening of `F_exec`, which is a coarsening of
  the full grammar.

**One clearing round (M1 contract, theory appendix Part I Section 1).** The incoming size walks
the book by price priority; the marginal level `p*` has pool `P` with quantity vector
`q = (q_1..q_m)`, `R* = sum q_i`, residual demand `V* in [1, R*]` (interior `1 <= V* <= R*-1`
is the strict-partial-fill regime; `V* = R*` is exhaustion). The **attribution** of the round is
the fill-count vector `c`, `sum c_i = V*`. Under FIFO it is the prefix allocation
`c^F = c^F(q, V*)` (deterministic; E3, E5). Under `ru` it is random (E2).

**Assumption (A3') (engine draw-law realization).** Under the frozen seed population, the
engine's `randrange` calls realize the idealized draw law of E2 (iid uniform stream consumed by
the without-replacement mechanism). The engine is deterministic given the seed (E1), so this is
an assumption about the seed-to-draw map. It is exactly what the post-freeze S3
without-replacement discriminator and the 27 conformance tests + replay validator pin down, and
its failure is the STOP-class "engine-law mismatch" risk (experiment plan section 12, row 1).
Every statement below is labeled with whether it needs (A3').

## 3. Lemma A (layer 0 — aggregate anonymity: the honest collapse toward plumbing)

**Statement.** `Lam_fifo^{G_agg}(D) = Lam_ru^{G_agg}(D)` for every DGP instance `D`; in
particular `TV(Lam_fifo^{G_agg}, Lam_ru^{G_agg}) = 0`.

**Proof.** The aggregate projection records level quantities and totals, which are functions of
the book's evolution; the kernel allocates within the marginal pool only and conserves units and
cash at every fill (`matching.py:627-655`), so the anonymous level quantities are unaffected by
which order inside the level was drawn. Formally this is P3 of the theory appendix (kernel
anonymity at the aggregate rung), here read at corpus level: both corpus laws are the point mass
of the same deterministic aggregate tape (E1). No (A3') needed. ∎

**Concession recorded.** At aggregate granularity the swap **is** plumbing — this layer is where
the attack is right, and the lemma pair says so on paper.

## 4. Lemma B (layer 1 — full-grammar separation: TV = 1)

**Statement.** Fix a DGP instance `D` whose request stream triggers at least one execution.
Let `A` be the event "the projected tape contains at least one execution record carrying an
`allocation_draw` key". Then `P_{Lam_ru}(A) = 1` and `P_{Lam_fifo}(A) = 0`, hence
`TV(Lam_fifo^{G}, Lam_ru^{G}) = 1` for any grammar `G` that preserves record payload keys
(in particular `G = F_exec`).

**Proof.** By E2/E3, under `ru` every executed unit produces exactly one execution record and
every such record carries a non-None draw, so `A` occurs as soon as any execution occurs (E4).
By E4 the FIFO arm never emits the key. TV dominates the indicator-event discrepancy:
`TV >= |P_ru(A) - P_fifo(A)| = 1`. No (A3') needed (only draw *presence*, not draw law). ∎

This is the trivial layer and is labeled as such (the R3 discipline: no referee may inflate it
into the lead claim). The scientific content is whether separation survives key equalization.

## 5. Lemma C (layer 2 — the load-bearing lemma: separation survives key equalization on multi-order pools)

Throughout, fix the **first contested round** of `D` (the first incoming marketable order after
the prestate; its marginal pool `q`, `R*`, `V*` are deterministic given `(pi, rho)` by E1).

**Statement.**

**(i) FIFO corpus law is a point.** `Lam_fifo^{Pi_att} = delta_{c^F}`. (E1, E3, E5; no A3'.)

**(ii) Random-unit attribution law (under A3').** `Lam_ru^{Pi_att} = MVHG(q, V*)`, the
multivariate hypergeometric law `Q(c) = prod_i C(q_i, c_i) / C(R*, V*)` on
`{c : sum c_i = V*, 0 <= c_i <= q_i}`.

**(iii) Exact separation identity (kernel-law-general).** For the engine's actual attribution
law `nu` (whatever the draw mechanism realizes; `nu = MVHG(q, V*)` under A3'),
`TV(Lam_fifo^{Pi_att}, Lam_ru^{Pi_att}) = TV(delta_{c^F}, nu) = 1 - nu({c^F})`.
Under A3': `TV = 1 - prod_i C(q_i, c^F_i) / C(R*, V*)`.

**(iv) Explicit constants (under A3').**
- (a) *Exact:* as in (iii).
- (b) *Second-atom bound:* `TV >= max_{c' != mode} Q(c')`, in particular
  `TV >= Q(V* e_j) = C(q_j, V*)/C(R*, V*)` for any pool order `j` with `q_j >= V*` whose
  full-depletion allocation differs from the mode. (Elementary: the two largest atoms sum to at
  most 1.)
- (c) *Contested-regime rate (Lemma D below):* let
  `sigma_j^2 = V* (q_j/R*) (1 - q_j/R*) (R*-V*)/(R*-1)` (the variance of the marginal
  `c_j ~ Hyperg(R*, q_j, V*)`) and `sigma* = max_j sigma_j`. If `sigma* >= 2` then
  `TV >= 1 - 2/sigma*`. In the contested regime — some order `j` with
  `q_j/R* in [theta_0, 1-theta_0]` and `V*/R* in [v_0, 1-v_0]`, `theta_0, v_0 > 0` —
  `sigma_j^2 = V* theta_j (1-theta_j) (R*-V*)/(R*-1) >= V* theta_0 (1-theta_0) v_0 . R*/(R*-1)
  >= V* theta_0 (1-theta_0) v_0` (since `R* - V* >= v_0 R*` and `R*/(R*-1) >= 1`), so
  `TV >= 1 - 2/sqrt(theta_0 (1-theta_0) v_0) . 1/sqrt(V*)` — precisely the
  "TV >= 1 - C/sqrt(k)" form recorded in the killer-tests doc, with `k = V*` the draw count and
  `C = 2/sqrt(theta_0 (1-theta_0) v_0)` an explicit regime constant.

**(v) Strict-positivity dichotomy (no A3' beyond non-degeneracy).** For any attribution law `nu`
that is not a point mass at `c^F`, `TV = 1 - nu({c^F}) > 0`. Under A3' the dichotomy is exact:
`Q(c^F) = 1` **iff** `m = 1` (single-order pool) **or** `V* = R*` (exhaustion round, where
`c = q` surely under both kernels) — hence on multi-order pools with `1 <= V* <= R*-1` the
key-equalized separation is **strictly positive** for every pool vector `q`. In the partial-fill
case where FIFO leaves at least one pool order untouched (`c^F_i = 0, q_i >= 1` for some `i`),
the explicit floor `TV >= sum_{i: c^F_i = 0} q_i / R*` holds (the event "first draw hits an
order FIFO would not touch" already escapes the FIFO corpus).

**Proofs.**

(i) E1 + E3 + E5: with no RNG consumption in the FIFO branch, the tape is a deterministic
function of `(pi, rho)`; its `Pi_att` projection is the fixed vector `c^F(q, V*)` (prefix fill).

(ii) Couple the draw mechanism to a uniformly random permutation of the `R*` resting units: by
E2, step `t` picks order `i` with probability `(q_i - c_i^{(t)})/(R* - t)`, which equals the
conditional probability that position `t` of a uniform random permutation of the `R*` units
(blocked by queue position, `selected_unit` a uniform unit label) lands in order `i`'s block
given first-`t` counts `c^{(t)}` (induction on `t`; each step reveals one uniformly chosen
remaining unit). The first `V*` positions of a uniform permutation have per-block counts
distributed `MVHG(q, V*)` (classical multivariate hypergeometric composition law; folklore, as
already scoped in the theory appendix Part I section 3 item 2 — no novelty claimed). The
`Pi_att` projection discards order and unit labels, leaving exactly the count vector.

(iii) For distributions `P = delta_{c^F}` and any `nu`: `sum_x min(P(x), nu(x)) = nu({c^F})`,
and `TV = 1 - sum_x min`. (Two lines; the identity holds for whatever `nu` the engine actually
realizes — the separation statement is thus robust to draw-law misspecification, with the
constant law-specific.)

(iv)(b) The mode atom and any other atom sum to at most 1, so `1 - max_c Q(c) >= Q(c')` for
every non-mode `c'`. (iv)(c) is Lemma D applied to
`max_c Q(c) <= max_x P(c_j = x)` (marginalization decreases atoms), with `j = argmax sigma_j`.

(v) Under A3': `Q(c) < 1` for every single atom iff the support of `Q` has at least two points,
which happens iff `m >= 2` and `1 <= V* <= R*-1` (if `m = 1` the support is `{(V*)}`; if
`V* = R*` it is `{q}`; if `V* = 0` there is no round; conversely with `m >= 2` and
`1 <= V* <= R*-1`, both `c = V* e_1`-type and a shifted allocation carry positive mass). The
floor: `{first draw = i}` has `ru`-probability `q_i/R*` (E2) and forces `c_i >= 1`, while
`c^F_i = 0`; hence `nu({c^F}) <= 1 - sum_{i: c^F_i = 0} q_i/R*`. ∎

**Corpus-level extension (contraction).** For the full-corpus laws on any grammar `G` coarser
than the full tape (in particular `F_exec`):
`TV(Lam_fifo^G, Lam_ru^G) >= 1 - P_{Lam_ru}(corpus^{Pi_att} = c^F on the first contested round)
>= 1 - Q(c^F)`, because `TV` contracts under the Markov kernel "project the corpus to the
first-round attribution", and the event {first-round attribution = `c^F`} contains the event
{entire corpus equals the FIFO-consistent corpus}. So the single-round constant lower-bounds the
corpus separation. (Only the first contested round is used: later-round pools are themselves
draw-dependent under `ru` — the forward non-lumpability phenomenon of KT-G1 R2 — and are not
needed here.)

## 6. Lemma D (hypergeometric mode-atom bound; self-contained, explicit constant)

**Statement.** Let `X ~ Hyperg(N, K, n)` (population `N`, `K` successes, `n` draws without
replacement), `theta = K/N`, variance
`sigma^2 = n theta (1-theta) (N-n)/(N-1) >= 4`. Then
`max_x P(X = x) <= e^{1/3} sqrt(2/pi) (1 - 1/sigma^2)^{-2} sigma^{-1} <= 2/sigma`.

**Proof.** Standard explicit Stirling bounds
`ln m! in [m ln m - m + (1/2)ln(2 pi m), m ln m - m + (1/2)ln(2 pi m) + 1/(12m)]` give, for
`p(x) = C(K,x) C(N-K, n-x)/C(N,n)`:

```
p(x) <= e^{eps} * (2 pi)^{-1/2} * sqrt( N n (N-n) K (N-K) / (N x (K-x) (n-x) (N-K-n+x)) )
        * exp( K h(x/K) + (N-K) h((n-x)/(N-K)) - N h(n/N) ),
```

with `h` the natural binary entropy, `eps = 1/(12K) + 1/(12(N-K)) + 1/(12n) + 1/(12(N-n)) <= 1/3`
on the interior support (degenerate edges have `sigma = 0`, excluded).

*Entropy part.* By concavity of `h` (mixture inequality with weight `a = K/N`,
`p_1 = x/K`, `p_2 = (n-x)/(N-K)`, `a p_1 + (1-a) p_2 = n/N`):
`K h(x/K) + (N-K) h((n-x)/(N-K)) - N h(n/N) <= 0`, so the exponential factor is `<= 1`.

*Mode location.* The forward ratio
`r(x) = p(x+1)/p(x) = (K-x)(n-x) / ((x+1)(N-K-n+x+1))` is strictly decreasing in `x` on the
support (each factor monotone), so `p` is unimodal with mode `m*` the least `x` with
`r(x) <= 1`; solving the quadratic `r(x) = 1` gives `|m* - mu| <= 1` with `mu = n theta`
(the mode lies next to the mean).

*Prefactor at the mean.* Each of the four denominators at `x = mu` satisfies
`mu = nK/N >= sigma^2` (since `(1-theta)(N-n)/(N-1) <= 1`),
`K - mu = K(N-n)/N >= sigma^2` (since `sigma^2 <= theta(N-n) n(1-theta)/(N-1) <= theta(N-n)` for
`n(1-theta) <= N-1` on the interior), `n - mu = n(1-theta) >= sigma^2`, and
`N-K-n+mu = (N-K)(N-n)/N >= sigma^2` (since `nK/(N^2(N-1)) <= 1`). Substituting `x = mu` the
prefactor collapses: `x(K-x)(n-x)(N-K-n+x) = K^2 (N-K)^2 n^2 (N-n)^2 / N^4`, so

```
prefactor(mu) = (2 pi)^{-1/2} N^{3/2} / sqrt(K (N-K) n (N-n)) = (2 pi)^{-1/2} sqrt(N/(N-1)) / sigma
             <= (2 pi)^{-1/2} sqrt(2) / sigma   (N >= 2).
```

*Window degradation.* At `x = m*`, each denominator is at least its value at `mu` minus 1, hence
at least `sigma^2 - 1 >= (3/4) sigma^2` for `sigma >= 2`; the four-term square-root ratio
contributes at most `(1 - 1/sigma^2)^{-2} <= 16/9`.

Combining: `p(m*) <= e^{1/3} (2 pi)^{-1/2} sqrt(2) (16/9) sigma^{-1} <= 2/sigma`. (Numerical
spot-checks: `Hyperg(140,50,60)` mode atom 0.1399 with `sigma = 2.816` — `sigma * atom = 0.394`;
`Hyperg(301,150,150)` atom 0.0916, `sigma * atom = 0.398`; the bound `2/sigma` holds with wide
slack, as expected since the true asymptotic constant is `1/sqrt(2 pi) ~ 0.40`.) ∎

**Corollary (contested-regime C/sqrt(k)).** If some pool order has `q_j/R* in [theta_0, 1-theta_0]`
and `V*/R* >= v_0`, then `sigma_j >= sqrt(V* theta_0 (1-theta_0) v_0 * (R*-V*)/(R*-1))`... more
cleanly: `sigma_j^2 = V* theta_j (1-theta_j) (1 - V*/R*) R*/(R*-1) >= V* theta_0 (1-theta_0) v_0'
` with `v_0' = (1-V*/R*) R*/(R*-1) > 0` a pool constant, so
`TV >= 1 - 2/(sqrt{V* theta_0 (1-theta_0) v_0'}) = 1 - C/sqrt(V*)`, `k = V*` the draw count.
This is a **regime** statement, not a uniform one — see the hostile check (adversarial pools).

## 7. Worked examples (numbers exact; computed with integer arithmetic)

**Example 1 — the S3 frozen family pool (theory appendix Part I section 5 scaffold).**
`q = (5,4,3,2)`, `R* = 14`, `V* in {1,2,4,6}` (FIFO prefix sums (5,9,12,14)):

| V* | c^F | Q(c^F) = prod C(q_i,c^F_i)/C(14,V*) | TV = 1 - Q(c^F) |
|---|---|---|---|
| 1 | (1,0,0,0) | 5/14 = 0.3571 | **0.6429** |
| 2 | (2,0,0,0) | C(5,2)/C(14,2) = 10/91 = 0.1099 | **0.8901** |
| 4 | (4,0,0,0) | C(5,4)/C(14,4) = 5/1001 = 0.0050 | **0.9950** |
| 6 | (5,1,0,0) | C(5,5)C(4,1)/C(14,6) = 4/3003 = 0.00133 | **0.9987** |

The analytic bound (iv)(c) is vacuous here (`sigma* < 1`; the pools are too small for the
Gaussian regime) while the exact constants are large — the exact formula carries small pools,
Lemma D certifies large ones.

**Example 2 — scaled contested pool.** `q = (50,40,30,20)`, `R* = 140`, `V* = 60`:
`c^F = (50,10,0,0)`, `Q(c^F) = C(50,50)C(40,10)/C(140,60) = 3.75e-32`, so
`TV >= 1 - 3.75e-32` exactly; the Lemma D route gives `sigma* = 2.816` and
`TV >= 1 - 2/2.816 = 0.290` — constant-explicit and conservative.

**Example 3 — two-order pools (smallest non-trivial case).** `q = (7,3), V* = 3`:
`TV = 1 - C(7,3)/C(10,3) = 0.7083`; `q = (8,8), V* = 4`: `TV = 1 - C(8,4)/C(16,4) = 0.9615`;
top atoms 0.5250/0.2917 and 0.4308/0.2462/0.2462 respectively.

**Example 4 — the frozen bundle (negative-control instantiation).** In both frozen fixtures the
only touched level (event 7) has a single maker (`O00000003`, qty 4): `m = 1`, so by Lemma C(v)
the `Pi_att` separation is exactly **0** — the frozen tapes realize the collapse stratum. The
divergence visible in the frozen data (one record of quantity 2 vs two records of quantity 1,
plus draw payloads) is Lemma B's grammar-level separation, not the attribution-level content.
The positive branch of Lemma C is instantiated by the D1_03-enriched fixtures (multi-order
rationed levels), and by the S3 scaffold pools above; both are preregisterable before any run.

## 8. The "through-M vs raw corpus" reading (what the orchestrator's phrase means, precisely)

Under the M0/M1-lumpable DGP freeze (contract C2(a): primary-truth DGP policies never depend on
allocation identity, so executed request streams are kernel-invariant), the **raw corpus** (the
request stream `rho` itself) has the **same law in both arms** — the raw arm is kernel-blind by
construction. The lemmas then say:

- the through-M corpus law at the full `F_exec` grammar differs from the raw-corpus-pushforward
  by TV = 1 (Lemma B);
- after key equalization, the through-M corpus under `fifo` **is** a deterministic function of
  the raw corpus (replay determinism, E1/E7), while under `ru` it escapes the raw-consistent
  corpus with probability `1 - Q(c^F)` on multi-order pools and never escapes on single-order
  pools (Lemma C);
- at aggregate granularity the through-M corpus degenerates back to a raw-flow function (Lemma A).

So "the through-M corpus law and the raw corpus law are TV-separated by an explicit constant on
the frozen DGPs" is exactly Lemma B/C(v) with the collapse strata named — the separation is a
property of the recording mechanism, is absent from the raw corpus, and is attributable to
priority because it vanishes precisely where priority cannot bind (single-maker, exhaustion).
That vanishing is what the stage-2 single-maker negative control verifies in the running engine.

## 9. Per-statement status

| Statement | Status | Condition |
|---|---|---|
| Lemma A (aggregate anonymity, TV = 0) | proven | none |
| Lemma B (full-grammar TV = 1) | proven | request stream triggers >= 1 execution |
| Lemma C(i) FIFO point mass | proven | none (E1 determinism) |
| Lemma C(ii) MVHG attribution law | proven_with_conditions | (A3') engine draw-law realization |
| Lemma C(iii) exact identity `TV = 1 - nu({c^F})` | proven | none (kernel-law-general) |
| Lemma C(iv) constants (exact, second-atom, 2/sigma, C/sqrt(V*)) | proven_with_conditions | (A3'); Lemma D needs `sigma* >= 2` |
| Lemma C(v) strict-positivity dichotomy | proven | (A3') for the iff; robust version for any non-degenerate `nu` |
| Lemma D (hypergeometric mode-atom bound) | proven | self-contained; `sigma >= 2` |
| Corpus-level contraction | proven | first contested round multi-order |
| KT-M2 table (Part II) | proven | every cell a restatement of a D-2 map row |

## 10. Hostile check (attacking my own proof the way the D-1 red team would)

**H1 — the weakest step is (A3').** The entire quantitative layer (MVHG constants) leans on the
engine's `randrange` realizing the uniform law under seed randomization; the frozen fixtures
contain exactly two draws (both hitting the single maker, necessarily) and have zero statistical
power to test this. *Stress:* suppose the engine's draw were biased. Then `nu` is not MVHG and
every constant changes. *Why the lemma survives:* Lemma C(iii) is kernel-law-general —
`TV = 1 - nu({c^F})` for whatever law the engine actually realizes, and the qualitative
dichotomy (v) only needs "`nu` is not a point mass at `c^F`", which fails only if the "random"
kernel deterministically reproduces FIFO allocation on a multi-order pool — a gross engine-law
mismatch already covered by the STOP rule (experiment plan section 12 row 1) and falsified
by S3's V*=2 rank-jump discriminator. The honest residual: pre-freeze, the MVHG constants are
conditional statements about the recorded kernel semantics, not measured facts about the running
engine. The prereg must say so.

**H2 — "you chose the projection `Pi_att` to make the lemma true."** The actual `F_exec` corpus
keeps per-unit records with `maker_remaining` chains and execution-id ordering, so even with
`allocation_draw` stripped, record counts and orderings differ and TV = 1 trivially — the
equalized layer is doing more work than the statement admits. *Response:* this is exactly why
Lemma B is labeled the trivial layer and Lemma C is stated on the **deepest** equalization
(both draw annotation and record granularity removed). Any coarser-than-`Pi_att` projection that
still separates is a fortiori covered; `Pi_att` is chosen to be the *most favorable to the
attack*, and separation still survives there. Note also that keeping fill order (inter-maker
execution ordering) can only increase TV (more coordinates on which the laws differ); the
marginalization lower bound is safe in every direction.

**H3 — "the explicit constant is regime-dependent; `1 - C/sqrt(k)` oversells."** Correct as
attacked: `q = (R*-1, 1), V* = 1` gives `Q(c^F) = (R*-1)/R*` and `TV = 1/R* -> 0`. There is no
uniform-in-pool constant. *Response:* the statement actually proven is (a) the exact pool-level
constant `1 - Q(c^F)` (computable and preregisterable per fixture), (b) strict positivity on all
multi-order interior pools, and (c) the `C/sqrt(V*)` rate **in the contested regime** (bounded
fractional orders, bounded `V*/R*`), which is the regime the S3/D1_03 fixtures preregister. The
killer-tests doc's "TV >= 1 - C/sqrt(k)" is honored as a regime corollary, not a uniform bound;
the writeup for D-1 wording must not drop the regime qualifier.

**H4 — "the frozen bundle proves nothing positive."** True and stated (Example 4): the frozen
21/22-event fixtures contain only single-maker touched levels, so they instantiate the collapse
stratum, not the separation stratum. The lemma's positive branch is grounded in engine *code*
semantics (E2, `matching.py:585-604`) and instantiated by the preregistered S3 scaffold pools
and the D1_03-enriched fixtures, both of which exist before any GPU run. The prereg must scope
the claim to "the frozen engine semantics and the enriched-fixture family", never to the
21/22-event bundle.

**H5 — "corpus-level contraction hides multi-round coupling."** The contraction argument uses
only the first contested round and event containment; later-round pool composition under `ru` is
draw-dependent (forward non-lumpability), but none of that is needed for the lower bound. The
upper direction (TV could be even larger) is irrelevant to the lemma. No gap found.

**H6 — "deterministic-kernel collapse is misstated."** `pro_rata` is not an engine kernel
(schema_spec.json `allocation_rules` = {fifo, random_unit_within_price}); all pro-rata statements
are taxonomy-level (theory appendix Part II section 0 marks it "not in this engine"). For
deterministic kernel *pairs*, corpus laws are point masses and TV in {0,1}, equal to 0 exactly
when the two kernels induce identical recorded corpora (single-order pools, exhaustion,
proportion-aligned pools) — the same strata as Lemma C(v). No claim is made beyond this.

**H7 — hostile reading of the raw-corpus formulation.** "Under M0/M1-lumpability the raw corpus
is kernel-invariant; so 'through-M vs raw separation' is just 'recording adds the draw'." This
is Lemma B and is conceded as trivial. The non-trivial content is that the separation survives
the removal of every arm-identifying payload feature (Lemma C) and collapses exactly where
priority cannot bind (Lemma C(v)) — which is what makes the stage-2 single-maker control a
*control* rather than a corroboration.

**Verdict after self-attack:** the lemma stands with two conditions that must be carried into
D-1 wording: (A3') for the MVHG constants (machine-checked post-freeze by S3/conformance), and
the contested-regime qualifier for the `C/sqrt(k)` form. Neither weakens the qualitative claim,
which is kernel-law-general.

---

# Part II — KT-M2: template-expressibility table for the prereg

## 0. The parent template (as adjudicated; no new claims)

Duruisseaux et al. 2024 (ICML AI4Sci WS; D-2 map section 2.3 panel ruling, verbatim evidence):
four arms on an FNO surrogate for PDE operator learning (Kolmogorov flow Re = 500/5000) —
baseline `G`; `G` trained with the projection; and the locked-checkpoint inference-only surgery
cell ("B+Projection: The original surrogate model G is trained for N epochs in a purely
data-driven way, and its output is projected using pr_C at inference time"); the layer is
continuous Fourier/Leray projection; the estimand is constraint-satisfaction / L2 fidelity with
5 seeds. Ruling: external genre parent, must be cited; "first train x inference constraint
crossing" phrasing permanently falsified; novelty scoped to (i) market-native
combinatorial/integer clearing layer M and (ii) the SESOI-graded path-dependence attribution
estimand.

## 1. Rows = template-inexpressible features of the merged design

- **R1. Competing-mechanism swap at fixed truth reference.** `allocation_rule` exchange
  (fifo -> random_unit) inside one engine, DGP truth tapes unchanged (contract C4 kernel-swap
  axis; C2 item 6: "truth reference stays the original FIFO tape"). The parent template has
  exactly one mechanism (a projection of the *same* physics); it has no slot for exchanging one
  clearing mechanism for a *different* one at fixed truth.
- **R2. Kernel x enforcement interaction measured on OOD axes.** The train x infer enforcement
  factorial crossed with population-2N / tick-2Delta / truncation stress axes as *confirmatory*
  interaction estimands (contract C3 `J`, C4 axes, C9 families). Killer-tests KT-M2: "no OOD
  factor in the template".
- **R3. Fiber-resampling control.** Dual-hash-validated without-replacement interleaving
  regeneration holding the aggregate tape fixed (D1_02 instrument; acceptance = identical
  `aggregate_state_hash` sequence with differing `state_hash`). Requires a stochastic kernel
  whose draws admit within-fiber regeneration; the template's layer is deterministic
  projection.
- **R4. Dual-lineage architecture-transfer gate (contract C9).** Two independent simulator
  lineages (L1 ecomd_v2, L2 fact-surrogate) through the same 8-cell grid with a preregistered
  `>= 8/16 material` gate and boundary reporting (never pooled, never hidden). The template is
  single-architecture, 5 seeds.
- **R5. Preregistered point-null / exact-zero pattern cells.** O-B `swap->fifo` point null
  (exactly blind, equivalence-tested against SESOI); O-D price-notional exact-zero preregistered
  null on ru splits; KT-A1 P1/P2/P3 attribution patterns explicitly inexpressible as scalar
  comparisons (killer-tests KT-A1). The template's estimand (constraint satisfaction / L2
  fidelity vs baseline) has no point-null, equivalence-test, or pattern-class slot.

**Deliberate exclusion (honesty item).** Plain "surgery cells on locked checkpoints with zero
optimizer steps" is **not** an inexpressible row: the panel's verbatim evidence assigns the
locked-checkpoint inference-only surgery cell to the parent template. The inexpressible part of
our surgery cells is the *mechanism-identity crossing* (swapping the clearing kernel, not a
projection of the same physics), which is row R1. Listing plain surgery cells as inexpressible
would be a false claim against the adjudicated record; the prereg table must show the surgery
template as parent-owned with R1 as the delta.

## 2. Table (cells: OWNS / DNO = does-not-own; one-line reason, each a restatement of a D-2 map row)

| Inexpressible feature | Duruisseaux 2024 | Solver-in-the-Loop 2020 | GradABM (Chopra 2023) | Dyer et al. ICAIF 2023 | Gen-DFL 2025 | MarS 2024 | M3 2026 | KineticSim 2026 / matching-ABM 2021 |
|---|---|---|---|---|---|---|---|---|
| **R1 competing-mechanism swap at fixed truth** | DNO — layer is continuous Fourier/Leray projection of the same physics; no second mechanism exists to swap (map 2.3 panel) | DNO — training-face only; inference always through solver, never swapped (map 2.2) | DNO — epi feasibility; no clearing layer/cube (map 2.2) | DNO — feasibility anchor; M never an experimental factor (map 2.2) | DNO — no mechanism layer; decision-robustness estimand (map 2.2) | DNO — production raw-train/through-M-infer cell; never crossed (map 2.3) | DNO — engine never off, no FIFO to swap (map 2.3) | DNO — M as fixed infrastructure, nothing trained/swapped (map 2.3) |
| **R2 kernel x enforcement on OOD axes** | DNO — no OOD factor in the template; constraint/L2 estimand, 5 seeds (map 2.3 panel; KT-M2) | DNO — single face, no factorial (map 2.2) | DNO — no cube (map 2.2) | DNO — M never a factor (map 2.2) | DNO — no enforcement axis (map 2.2) | DNO — single production cell, no axes (map 2.3) | DNO — anchor mismatch documented; engine never removed (map 2.2) | DNO — no trained model to cross (map 2.2 KineticSim "nothing trained"; ABM-2021 fixed M) |
| **R3 fiber-resampling control (dual-hash regeneration)** | DNO — deterministic projection layer; no draws to regenerate (map 2.3 panel) | DNO — no stochastic kernel (map 2.2) | DNO — no kernel/fiber object (map 2.2) | DNO — no kernel/fiber object (map 2.2) | DNO — no kernel/fiber object (map 2.2) | DNO — pre-mechanism likelihood, engine downstream; no draw-level control (map 2.2) | DNO — order-level likelihood; no mechanism in loss, no fiber (map 2.2) | DNO — M is infrastructure; KineticSim's bitwise-identical books support swap *well-definedness* only (map 2.5) |
| **R4 dual-lineage transfer gate (C9)** | DNO — single FNO lineage, 5 seeds (map 2.3 panel) | DNO — single lineage (map 2.2) | DNO — single lineage (map 2.2) | DNO — single model (map 2.2) | DNO — no lineage axis (map 2.2) | DNO — single system (map 2.2) | DNO — single foundation model (map 2.2) | DNO — nothing trained (map 2.2/2.3) |
| **R5 point-null / exact-zero pattern cells** | DNO — estimand is constraint-satisfaction/L2 fidelity; no point-null or pattern slot (map 2.3 panel) | DNO — solver-fidelity comparisons (map 2.2) | DNO — feasibility, no null machinery (map 2.2) | DNO — feasibility anchor (map 2.2) | DNO — decision-robustness estimand (map 2.2) | DNO — production objectives, no preregistered nulls (map 2.2) | DNO — likelihood anchor, no equivalence tests (map 2.2) | DNO — no estimand machinery at all (map 2.2) |

What the template **does** own (recorded, never claimed by us): the four-arm train x infer
constraint-enforcement factorial including the locked-checkpoint inference-only surgery cell
(Duruisseaux 2024, map 2.3); the training face (Solver-in-the-Loop 2020); the production
(raw-train, through-M-infer) default cell (MarS 2024; Nagy 2023; MarketGPT 2024; TABL-ABM 2025;
TradeFM 2026 — map 2.3 cleared-but-instructive list); M-infrastructure prior art (matching-engine
ABM 2021; KineticSim 2026). Paper D remains the internal parent for the cube and the statistical
contract (map section 3), cited, never double-counted.

## 3. Confirmation vehicles and discharge linkage (preregistered)

Each inexpressible row is confirmed by a named post-D0 measurement; per the killer-tests KT-M2
specification, **one confirmation discharges KT-A1 or KT-A3 or KT-M1 simultaneously** (the tests
are correlated by design; the forecast must not multiply them independently):

| Row | Post-D0 confirmation vehicle | Discharges |
|---|---|---|
| R1 | KT-A2 stage-2 identical-input replay (same prestate + request subsequence, only `allocation_rule` swapped; Lemma C constant `1 - Q(c^F)` preregistered per fixture) + KT-A3 swap contrast on locked checkpoints | KT-A2, KT-A3 |
| R2 | Mandatory-family interaction `J` on OOD axes at h in {1,4,16,31} (contract C9; EP1 primary cell B1 kernel-swap h16) | KT-A1 (P2 pure-interaction pattern), KT-A3 |
| R3 | KT-A3 resample arm (swap > delta AND resample < delta/10, dual-hash acceptance) + KT-M1 deployment experiment | KT-A3, KT-M1 |
| R4 | C9 transfer gate on block B3 (both outcomes reported; failure = boundary) | KT-A5 |
| R5 | O-B swap->fifo point null (equivalence-tested) and O-D exact-zero null cell; KT-A1 P1/P2/P3 frozen decision rule | KT-A1, KT-A3 |

## 4. Hostile check on the table

**H1 — "every cell says DNO; the table is vacuous."** The table's function is the KT-M2
discharge: a *written, line-by-line checkable* record that no adjudicated parent expresses any of
the five feature classes, so the prereg can cite it when the "domain transplant of a workshop
ablation" attack lands (map 2.6). Vacuity would require at least one OWNS cell in the five rows;
there is none, and the parent-owned elements are explicitly listed in section 2's ownership
paragraph (four-arm template, surgery cell, training face, production cell, M-infrastructure) —
the table is not claiming the parents did nothing.

**H2 — "the table smuggles unverified claims about the parents."** Each cell's reason quotes or
paraphrases a specific map row (sections 2.2, 2.3, 2.5); the OOD-factor absence is stated by the
KT-M2 spec itself; the "no FIFO to swap" for M3 is the panel's verbatim ruling. No cell rests on
my own reading of any external paper. Any D-1 reviewer can audit the table against the map
without opening an external document.

**H3 — "R4/R5 are additions beyond the KT-M2 minimum, chosen to be easy."** True that the
minimum was R1-R3; R4 (C9 gate) and R5 (point-null cells) were identified from the plan/contract
as the two further template-inexpressible classes. They are also the two rows a hostile referee
is most likely to test (transfer-is-folklore attack, map 2.5; attribution-reduces-to-superiority
attack, KT-A1) — including them is defensive, not padding. The candidate row the orchestrator
suggested — plain surgery cells — was **excluded** as parent-owned (section 1's honesty item),
which is the opposite of choosing easy rows.

---

## 5. Consequences for D-1 wording (inputs to the prereg text)

1. **The kernel-swap axis is a law-changing manipulation, not re-plumbing**, with a
   preregistered per-fixture constant: cite Lemma C(iii)/(iv)(a) `TV = 1 - prod_i C(q_i, c^F_i)/C(R*, V*)`
   on the first contested round of each enriched fixture; state Lemma A (aggregate TV = 0) in the
   same sentence so the concession is on paper.
2. **The F_exec freeze (D1_01) is what makes the lemma non-trivial**: under the full grammar the
   separation is trivial (Lemma B), at aggregate granularity it vanishes (Lemma A); F_exec with
   key equalization is where the science lives. This is the corpus-contract analogue of the T1
   granularity dichotomy and should be phrased as such.
3. **Single-maker and exhaustion strata must be preregistered as negative-control strata**,
   excluded from separation claims (mirrors P4(iii)); the frozen bundle instantiates them (E6).
4. **Scope sentence required**: the positive branch is a statement about the frozen engine
   semantics (`matching.py:585-604`) and the enriched-fixture/S3-scaffold family, not about the
   21/22-event bundle; the MVHG constants are conditional on (A3') until S3/conformance
   machine-check it post-freeze.
5. **Never phrase the cube as "first train x inference constraint crossing"** (map condition);
   phrase R1 as "competing-mechanism exchange at fixed truth reference — template-inexpressible",
   with the surgery template itself attributed to the parent.

*Grounding files (absolute):*
`/Users/howardwang/Desktop/playground/ecophys/experiments/lab_asset_a2/a2_exit_20260905/{schema_spec.json, fixture_fifo/tape.jsonl, fixture_fifo/prestate.json, fixture_random_unit_within_price/tape.jsonl, fixture_random_unit_within_price/prestate.json}`
(read-only, unmutated); `/Users/howardwang/Desktop/playground/ecophys/scripts/lab_asset/matching.py`;
companion docs `papers/proposal/ecomd_reexploration_{theory_appendix,d1_killer_tests_and_ops,contract_v1,experiment_plan,d2_evidence_map}_2026-09-06.md`.
