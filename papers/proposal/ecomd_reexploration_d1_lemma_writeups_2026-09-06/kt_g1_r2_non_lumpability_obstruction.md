---
item: KT-G1 R2 — non-lumpability obstruction lemma
date: 2026-09-06
stage: D-1 theorem work under pi_reexploration_d1_authorization_20260906 (theorem/literature/schema only; no GPU, no engine execution, no data, no mutation of a2_exit_20260905)
status_summary: >-
  R2 is PROVEN as a four-part package: Lemma R2-A (mechanism-level point-mass vs
  multi-hypergeometric separation, TV >= 1 - max_x p_x with exact engine-native constants),
  Lemma R2-B (M1+ non-lumpability of the aggregate chain, uniform in the responsive policy
  class), Proposition R2-C (the honest M0 concession: lumpability holds exactly on the
  resource-slack / no-self-crossing stratum — and fails off it already at M0 through the
  identity-dependent validation channel, which strengthens rather than weakens the
  obstruction), Corollary R2-D (training-signal obstruction: no aggregate-tape-measurable
  predictor of the forward law, minimax TV >= (1/2)(1 - max_x p_x)). One asymptotic
  sharpness remark is PARTIAL (exact for balanced pools via the Binomial limit; no general
  log-concavity citation is used, per D-2 citation discipline).
companion_docs:
  - papers/proposal/ecomd_reexploration_theory_appendix_2026-09-06.md (Part I Sec 1 M1 contract; P0-P9; Part II Sec 0)
  - papers/proposal/ecomd_reexploration_experiment_plan_2026-09-06.md (Sec 3 planned attack; Sec 12 risk register row "KT-G1 R2 failure")
  - papers/proposal/ecomd_reexploration_d1_killer_tests_and_ops_2026-09-06.md (Sec 2 KT-G1 R1/R2/R3 split)
  - papers/proposal/ecomd_reexploration_d2_evidence_map_2026-09-06.md (only citation source)
---

# KT-G1 R2: the non-lumpability obstruction lemma

## 0. What R2 must prove, and what it must not

KT-G1 splits the sufficiency-reduction attack into R1 (static toric concession — already
conceded into T1 scope), R2 (dynamic sufficiency failure — this document), R3
(aggregate+random collapse = marginalization — labeled the trivial data-processing direction).
The referee attack R2 answers is: *"sufficiency theorems equate fibers across all downstream
uses under the model; your aggregate-tape fiber is just a coarsening, so everything true at the
per-unit rung has an aggregate-shadow corollary."* R2 is the statement that this reduction
**fails for the engine's own forward law** once flows are M1+.

Two candidate readings had to be separated before stating anything, because the weak one is
true almost trivially and carries no sufficiency content:

- **Weak reading (full-state forward laws differ).** For aggregate-indistinguishable states
  s ≡_A s', the *full-state* one-step forward laws differ — under **every** flow process,
  including M0 exogenous ones, because the random_unit attribution (which maker order took
  which unit) differs in law. True, but useless: nobody claimed the identity layer of the
  state was recoverable; a sufficiency reduction for the aggregate tape does not need the
  full state to be predictable, only the aggregate-observable process.
- **Strong reading (aggregate forward laws differ — non-lumpability).** There exist
  s ≡_A s' and an admissible flow process under which the law of the **aggregate-observable
  process itself** (the aggregate state chain / per-price prints) differs between the two
  starting states. This is the obstruction that matters: it says the coarsening is not closed
  under the dynamics, i.e., the aggregate statistic is not sufficient for the forward law of
  the very process it records.

R2 is proven here in the strong reading, with the quantifier class of flow processes made
explicit (Section 1.4), and the honest boundary (Proposition R2-C) proven in the other
direction: for M0 flows on the resource-slack stratum the aggregate chain **is** lumpable —
the sufficiency reduction genuinely goes through there. The lemma is therefore a sharp
triple-interaction statement — kernel x granularity x policy-feedback — not a blanket
non-sufficiency claim.

## 1. Formal setup (engine-grounded, appendix-consistent)

### 1.1 State, aggregate statistic, kernel

Consistent with the theory appendix Part II Section 0 and the M1 contract of Part I Section 1:

- **Full state** s = (bids, asks, cash, inventory, counters, order_meta, order_status,
  order_parent, latency_choices, used_client_ids, rng_state, sequence, clocks). The books are
  **order-level queues**: `bids/asks: dict[int, list[(order_id, actor, remaining_quantity)]]`
  (`scripts/lab_asset/matching.py:46-47`, `scripts/lab_asset/schema.py:242-243`).
- **Aggregate statistic** A(s) := (per-price level sums on each side, total cash, total
  inventory, last_match_ts) — literally `aggregate_state_hash`
  (`scripts/lab_asset/schema.py:299-325`): `levels = [[price, sum(qty …)] …]`
  (line 314-315), `"total_cash": sum(cash.values())` (line 321),
  `"total_inventory": sum(inventory.values())` (line 322). A sums out order identity, actor
  attribution, queue order, **and** the actor-level distribution of cash/inventory (only
  totals survive). This is the *strongest* aggregate observer in the engine; non-lumpability
  against A implies non-lumpability against every coarser aggregate (per-price prints
  {(p, V_p)} at the `agg` rung included, since those are functions of the level sums and
  request sizes). The full-state hash additionally binds FIFO order and rng_state
  (`schema.py:239-296`), which A discards.
- **Kernel** k = `random_unit_within_price` unless stated. Draw semantics
  (`matching.py:585-604`): at price p, `eligible_units = sum(q_i)` over the resting queue,
  `selected_unit = rng.randrange(eligible_units)`, and the selected maker is the order whose
  cumulative quantity interval contains the drawn unit. Each execution removes exactly one
  unit (`fill = 1` for the random arm, `matching.py:292-296`), so a residual demand V* at the
  marginal price is a sequence of V* draws, each uniform over the R* − t remaining units:
  **P(step-t hit on order i) = (q_i − c_i^{(t)})/(R* − t)** with c_i^{(t)} the hits so far.
  Frozen-fixture confirmation: `fixture_random_unit_within_price/tape.jsonl` seq 7–8 record
  `eligible_units` 4 then 3 for a V* = 2 walk against a single resting order of quantity 4
  (seq 5, order O00000003 at 101) with `quantity: 1` per execution and `maker_remaining`
  3 then 2.
- **One clearing round** (M1 contract): incoming order of size Q; better levels clear fully;
  marginal level p* with pool P, pool size R* = Σ_{i∈P} q_i, residual demand V* = Q − S_< ∈
  [0, R*]; interior regime 0 < V* < R*. Under both arms the aggregate level evolution of a
  round is the same: the marginal level total decreases by exactly V*
  (`matching.py:285-346` loop; `_apply_maker_fill` `matching.py:606-625` removes exactly the
  fill and deletes the price when the queue empties) and settlement transfers cash/inventory
  between actors with **totals conserved** (`_settle`, `matching.py:640-644`).

### 1.2 Recorded rung and forward law

The `agg` rung of the appendix ladder records, per round, the per-price prints {(p, V_p)} and
BBO prices; ambient request events are outside `F_exec` (frozen corpus contract, decision
D1_01). For the lemma I use the **strongest aggregate observer**: the full sequence of
aggregate states A(s_t) at request boundaries plus per-price prints. Beating the strongest
observer beats both rungs. The **forward law** of the process under flow π from state s is
the law of the trajectory (A(s_1), A(s_2), …) together with the prints (and, for the
full-state variant, of (s_1, s_2, …)).

### 1.3 Incoming-flow process classes (the policy ladder, thesis v2)

Following `papers/proposal/ecomd_random_unit_priority_thesis_v2_2026-08-27.md` (lines 70-71):

- **M0 (aggregate-lumpable):** each actor's request at each boundary is a measurable function
  of the *anonymous* aggregate history (level sums, public information releases, own
  exogenous signals) plus exogenous policy randomness; **allocation identity never feeds
  back**.
- **M1+ (identity/resource-responsive):** requests may additionally depend on the actor's own
  realized fills, inventory, cash, induced values — i.e., on the identity-level components of
  the actor's own state. (M2 feedback-adaptive and M3 rule-aware are subsets of M1+ for the
  purposes of this lemma; R2 needs only the M1 channel.)

Formal responsive class used in Lemma R2-B (minimal, and shown necessary in Section 5):

> **Class Π_resp (single-actor own-fill-responsive, non-cancelling).** π ∈ Π_resp if, at the
> constructed node (a completed rationed round at p* with pool actors' fill counts c_i), one
> designated responsive actor r ∈ P submits exactly one follow-up request whose submitted
> quantity is g(c_r) for a measurable g that is **injective on the support of the spread
> fill-count law**, the request is **resource-slack** (no cash/inventory/induced-capacity
> constraint binds in any fiber member — cf. `matching.py:683-710`) and **non-self-crossing**
> (it does not cross a level containing r's own resting order — cf. `_would_self_trade`,
> `matching.py:715-721`); all other actors are inert at that node.

Two engine-native instantiations used below: (i) **marketable sell of own fill count into the
opposite side** (g(c) = c, no self-trade possible since the actor owns no resting order on
that side, aggregate effect = a print of volume g(c) and a level-total change of −g(c));
(ii) **cancel of own remaining order** (quantity a − c, injective in c; boundary caveat when
c = a, the order is already filled and the cancel is rejected — Section 6.3).

### 1.4 Definition (lumpability / dynamic sufficiency) and the quantifier order

> **Definition.** The aggregate statistic A is **sufficient for the forward law over flow
> class Π** if for every π ∈ Π and every pair s, s' with A(s) = A(s'), the laws of the
> aggregate-observable process coincide: Law_π(A-process | s) = Law_π(A-process | s').
> (Equivalent lumpability phrasing: the aggregate chain is closed — its transition kernel is
> a well-defined function of the aggregate state.) R2 asserts **failure** of sufficiency over
> M1+ classes; R2-C asserts **success** over M0 on the slack stratum.

**Quantifier order chosen (and why).** The proven statement is:

  ∃ a fixed pair (s_pm, s_sp), A(s_pm) = A(s_sp), such that ∀ π ∈ Π_resp:
  TV( K_π(· | s_pm), K_π(· | s_sp) ) ≥ 1 − max_x p_x ≥ explicit constant,

where K_π(· | s) is the one-step aggregate-transition kernel at the constructed node. This is
the strong order (fixed witness pair, separation **uniform** over the admissible class — the
bound does not depend on g except through injectivity). The universally-quantified-over-all-M1+
version is false and is not claimed: Section 5 exhibits an M1 policy (all pool actors
buy-back-own-fills on the same side) whose aggregate one-step separation vanishes by
conservation — the obstruction is exactly coextensive with the active, non-cancelling
feedback channel, which is the content, not a defect (Section 8, hostile check item 2).

## 2. Lemma R2-A (mechanism-level separation; policy-free) — PROVEN

**Statement.** Fix the interior regime 0 < V* < R* at the marginal level p*, pool composition
q = (q_1, …, q_m), m ≥ 2, q_i ≥ 1. Let Split(q) denote the law of the per-order fill-count
vector c under the random_unit kernel. Then:

(i) **(Engine draw law = MVHG.)** Split(q) is the multivariate hypergeometric law
P(c) = ∏_i C(q_i, c_i) / C(R*, V*), and the per-step law is
P(step t hits i) = (q_i − c_i^{(t)})/(R* − t).

(ii) **(Point-mass vs spread separation.)** Let q° be any composition whose induced split law
is a point mass δ_{x°} — either a **single-order pool** (q° = (R*), x° = (V*), any kernel) or
any composition under a **deterministic kernel** (fifo at fixed q; x° = the prefix-fill
split). Then for every such pair, with p := Split(q) the spread law,

  TV( δ_{x°}, p ) = 1 − p(x°) ≥ 1 − max_x p(x).

(iii) **(Explicit constants, engine-native pools.)** For the two-order balanced pool
q = (m, m) and V* ∈ {1, 2}: 1 − max_x p(x) = 1/2 (V* = 1, p = (1/2, 1/2)) and
1 − max_x p(x) = 1/3 (V* = 2, m = 2, p = (1/6, 2/3, 1/6); increasing to 1/2 as m → ∞). For
the S3 frozen scaffold pool q_P = (5, 4, 3, 2), R* = 14, with point-mass x° = (V*, 0, 0, 0)
(the single-order fiber member): TV = 1 − P(c_1 = V*) equals 9/14, 81/91, 996/1001, 1 for
V* = 1, 2, 4, 6 respectively (at V* = 6 the supports are disjoint: q_1 = 5 < 6). Universal
lower bounds 1 − max_x p(x) for the same pool: 0.357, 0.505, 0.580, 0.580.

(iv) **(Large-pool sharpening, balanced family.)** For q = (m, m), fixed V* = v and m → ∞,
Split((m, m)) → Binomial(v, 1/2) pointwise, so 1 − max_x p(x) → 1 − C(v, ⌊v/2⌋)/2^v
(= 1/2, 5/8, 11/16 for v = 2, 4, 6); the adversarial lower bound improves toward 1 as v
grows.

**Proof.** (i) Induction on draw steps using the engine rule. After t draws the state of the
pool is a uniformly chosen (R* − t)-subset of the R* units remaining invariant: the engine
draws `selected_unit` uniform on `randrange(eligible_units)` and the cumulative-interval walk
(`matching.py:592-603`) makes each *unit* of each order equally likely, i.e., the t-th draw is
uniform on the remaining units, which is exactly negative-hypergeometric sampling without
replacement. Aggregating units to orders gives P(c) = ∏_i C(q_i, c_i)/C(R*, V*) (classical
identity; one-line verification: the probability of any particular interleaving ω with counts
c is ∏_i (q_i)_{c_i}/(R*)_{V*} — the appendix P0/P2 computation — and the number of
interleavings with counts c is V!/∏_i c_i!, so P(c) = [∏_i (q_i)_{c_i}/∏_i c_i!] /
[(R*)_{V*}/V*] = ∏_i C(q_i, c_i)/C(R*, V*)). The frozen fixture instantiates the denominators:
eligible_units 4 then 3 for R* = 4, V* = 2 (`tape.jsonl` seq 7, 8). Direct sequential check for
q = (2, 2), V* = 2: P(c_1 = 2) = (2/4)(1/3) = 1/6; P(c_1 = 1) = (2/4)(2/3) + (2/4)(2/3) =
2/3; P(c_1 = 0) = (2/4)(1/3) = 1/6 — matching ∏C/C = (1, 4, 1)/6.

(ii) For any point x° in the support, TV(δ_{x°}, p) = ½(|1 − p(x°)| + Σ_{x ≠ x°} p(x)) =
½((1 − p(x°)) + (1 − p(x°))) = 1 − p(x°) ≥ 1 − max_x p(x), since p(x°) ≤ max_x p(x). A
single-order pool forces x° = (V*) under any kernel because every unit drawn belongs to the
only order; a deterministic kernel forces its unique split.

(iii) Exact rational arithmetic on the formula of (i) (verified by direct enumeration in a
CPU-only check, no engine execution). E.g. V* = 2, q = (2, 2): p = (1/6, 4/6, 1/6) by (i);
point-mass coincidence probability p(x°) with x° = (2, 0) or (0, 2) is 1/6, so
TV = 5/6 while the adversarial bound 1 − max p = 1/3.

(iv) P_m(c) = C(m, c)C(m, v − c)/C(2m, v) → C(v, c) 2^{−v} since
C(m, c)/C(2m, v) · C(m, v−c) = [∏ ratios] and each fixed-order ratio → (1/2)^{...}; more
explicitly, for fixed c and v, C(m, c)C(m, v−c)/C(2m, v) =
[ (m)_c (m)_{v−c} / (c!(v−c)!) ] / [ (2m)_v / v! ] and (m)_k/(2m)_k → 2^{−k} termwise, giving
v!/(c!(v−c)!) · 2^{−v} = C(v, c) 2^{−v}. The mode of Bin(v, 1/2) is ⌊v/2⌋ with mass
C(v, ⌊v/2⌋)/2^v. ∎

**Status.** PROVEN. Part (iv) is labeled PARTIAL as a *general* sharpness statement: it is
exact for balanced two-order pools; for general compositions I provide only the universal
bound of (ii) with the computed pool-specific constants, and I deliberately do not invoke a
log-concave maximal-atom inequality to get 1 − O(R*^{−1/2}) for all compositions, because no
such result is in the adjudicated D-2 map (see Section 7 / new references).

**Remark (unification with the KT-A2 kernel-separation shape).** Lemma R2-A(ii) does not care
where the point mass comes from: concentrated composition under random_unit, or deterministic
kernel (fifo) at a fixed spread composition. The KT-A2 lemma (FIFO point mass vs random_unit
MVHG at the *same* composition) is the second source of δ_{x°}; R2 uses the first source
(point mass *within* the random_unit kernel across aggregate-identical states), because R2's
claim is about a single fixed kernel. Same bound, different witness — worth one sentence in
the paper to preempt "you proved the KT-A2 lemma twice."

## 3. Lemma R2-B (M1+ non-lumpability of the aggregate chain) — PROVEN

**Statement.** Fix the engine, kernel random_unit, actors {A, B, C} plus sufficient
resource slack, price bands containing 99 ≤ 101 ≤ 103, and the book

  s_pm : asks[101] = [(O1, A, 4)], bids[99] = [(O0, E, 8)]  ("point-mass" member)
  s_sp : asks[101] = [(O1, A, 2), (O2, B, 2)], bids[99] = [(O0, E, 8)]  ("spread" member)

with identical actor-total cash and inventory (no trades yet; resting orders reserve nothing
from the cash/inventory *maps*, which are mutated only at settlement,
`matching.py:640-644`). Then A(s_pm) = A(s_sp) (level sums [[101, 4]] on the ask side,
[[99, 8]] on the bid side, identical totals, identical clock). Let the incoming flow be: C
submits a marketable buy of quantity 2 at price 101 (the frozen fixture's event shape:
actor c, side B, price 101, quantity 2), followed by the responsive action of Π_resp with
responsive actor r = A and g = id (A submits, iff c_A ≥ 1, a marketable sell of quantity
c_A at price 99). Then the one-step aggregate-transition kernels at the post-round boundary
satisfy, uniformly over every π ∈ Π_resp and every injective g,

  TV( K_π(· | s_pm), K_π(· | s_sp) ) = 1 − P_{s_sp}(c_A = g-matched value) ≥ 5/6
  (for g = id: 1 − P(c_A = 2) = 5/6),

where the aggregate observation is the next aggregate state and print (bid level at 99 and
the print volume there). Moreover the same separation is visible in the frozen corpus
contract F_exec (an execution record with quantity c_A at price 99), and in the
level-total-only observer (bid level 8 − c_A ∈ {8, 7, 6}).

**Proof.**

Step 1 (aggregate indistinguishability through round 1). Under both members, C's buy
executes exactly V* = 2 units at 101 (the while-loop `matching.py:285` runs twice for the
random arm; two execution records, `quantity: 1` each — fixture seq 7-8 shape). The ask
level total at 101 becomes 2 in both; the print (101, 2) is issued in both; settlement
conserves total cash and inventory (`matching.py:640-644`); the bid level is untouched; the
number of execution records (2) is aggregate-invariant under random_unit because it equals
V*. The actor attribution differs (s_pm: A sells 2, deterministic — single order forces
x° = 2; s_sp: (c_A, c_B) ~ (1/6, 4/6, 1/6) on {(2,0),(1,1),(0,2)} by R2-A with q = (2, 2),
V* = 2 — sequential law (2/4)(1/3) etc. verified in R2-A(i)) but attribution is not an
aggregate observable. Hence the aggregate state sequence and print sequence agree through
the end of round 1, a.s., under both members.

Step 2 (the responsive action is valid in both members and is an injective function of the
attribution). A's own fill count c_A ∈ {0, 1, 2} is a function of A's own state (inventory
and cash changed by c_A units at settlement; own order remaining 4 − c_A resp. 2 − c_A),
so g(c_A) = c_A is M1-admissible (thesis-v2 ladder line 71: "actions may depend on current
inventory, cash and induced value"). The marketable sell at 99 crosses only the bid side,
where A owns no resting order, so `_would_self_trade` (`matching.py:715-721`) does not fire;
resource slack holds by assumption (Π_resp); quantity c_A ≥ 1 when submitted, so
`NEGATIVE_OR_ZERO_QUANTITY` does not fire. In s_sp the same holds branchwise. The map
c ↦ (next aggregate observation) is: print (99, c) and bid level 8 − c — injective in c.

Step 3 (pushforward and TV). Under s_pm, c_A = 2 a.s., so the next aggregate observation is
the point mass δ_{(print (99,2), level 6)}. Under s_sp it is the pushforward of
c_A ~ {1/6, 4/6, 1/6} through the injective map of Step 2 (on {0, 1, 2}; c_A = 0 ⇒ no
submission ⇒ observation "no event, level 8"). Injectivity makes the pushforward TV equal to
the TV of the count laws against the point mass (data-processing holds with equality for
injective maps on the relevant support). By R2-A(ii): TV = 1 − P_{s_sp}(c_A = 2) = 5/6 ≥
1 − max_x p(x) = 1/3. Uniformity over π ∈ Π_resp: the value 1 − P_{s_sp}(c_A = 2) depends
only on the engine's draw law at (q, V*) and on injectivity of g, not on any other feature
of π. ∎

**Status.** PROVEN. Conditions, all explicit and all necessary-or-scoped: interior regime
(0 < V* < R*; exhaustion in Section 6.2), m ≥ 2 pool in the spread member (Section 6.5),
single responsive actor with injective non-cancelling response (necessity: Section 5),
resource slack and no self-crossing at the node (failure of these strengthens the
obstruction: Section 4, Remark).

**Corollary (full-state version, for completeness).** The same pair separates the *full-state*
one-step forward laws by TV ≥ 5/6 (attribution itself: δ_{(A:2)} vs the spread law have
disjoint-or-smaller overlap 1/6). This is the weak reading of Section 0 — true, and now
seen to be implied by the strong one.

**Corollary R2-D (training-signal obstruction) — PROVEN.** Let Ķ(· | h) be any predictor of
the next-observation law that is measurable in the aggregate tape history h (in particular:
any simulator trained by any loss functional of the aggregate tape distribution, by the
appendix Lemma 0 byte-identity argument applied at the agg rung). Then at the constructed
node, with K_1, K_2 the two true one-step kernels of Lemma R2-B,

  sup_{s ∈ {s_pm, s_sp}} TV( Ķ(· | h_A), K_s(·) ) ≥ ½ · TV(K_1, K_2) ≥ ½ (1 − max_x p_x)
  ( = 5/12 on the (2,2), V* = 2 pool ),

so no aggregate-tape training signal can constrain the forward law on the M1+ stratum: the
predictive law of the aggregate process is not a function of the aggregate history.
*Proof.* For any Ķ, TV(Ķ, K_1) + TV(Ķ, K_2) ≥ TV(K_1, K_2) by the triangle inequality for
total variation (elementary: Σ_x |Ķ(x) − K_1(x)| + Σ_x |Ķ(x) − K_2(x)| ≥ Σ_x |K_1(x) −
K_2(x)| pointwise via the triangle inequality on each term; halve both sides), so at least
one of the two errors is ≥ ½·TV(K_1, K_2); the bound then follows from R2-B. ∎ (The
two-point minimax step is proved inline; no external two-point lemma is cited, per D-2
citation discipline.)

## 4. Proposition R2-C (the M0 concession — and its sharp boundary) — PROVEN

**Statement (lumpability on the slack stratum).** Let π be an M0 flow process (Section 1.3)
and assume the **resource-slack / no-self-cross condition**: every request issued by π at
every reached aggregate state a is accepted in *every* fiber member s ∈ A^{−1}(a) (i.e., no
cash, inventory, induced-capacity, or self-trade constraint binds in any member; this is the
schema's own condition — `schema.py:307-311`: "Under an exogenous, resource-slack request
tape, this hash is equal after each completed request even when identity allocations
differ"). Then the aggregate state sequence is a measurable function of (A(s_0), the request
sequence, policy randomness): in particular Law_π(A-process | s) = Law_π(A-process | s')
for all s ≡_A s'. The aggregate statistic is sufficient for the aggregate forward law over
M0-slack flows: **the sufficiency reduction goes through, exactly as KT-G1 conceded.**

**Proof.** Induction over requests. Fix a reached pair s ≡_A s' and an issued request
(side, price, quantity). By the slack condition it is accepted in both (validation
`matching.py:671-721` depends on the identity layer only through `_reserved_cash` /
`_reserved_inventory` / `_reserved_bid_units` — per-actor sums over the actor's *own*
resting orders, `matching.py:831-853` — and through `_would_self_trade`; none bind). The
execution walk is then determined in aggregate: each crossed level's cumulative supply is its
level total (a function of A), so the sequence of crossed levels, the executed volume V_p at
each fully-cleared level, and the marginal residual V* = Q − S_< are functions of (A,
request); each execution removes exactly its fill from the level total and the level is
deleted at total zero (`matching.py:606-625`), identically under both arms; settlement
conserves total cash and total inventory (`matching.py:640-644`). Cancellations and
replacements of *own* orders by M0 actors: an M0 actor's decision to cancel is
aggregate-measurable, and the cancelled volume is the actor's own remaining quantity — an
identity-level number whose *aggregate* effect (level-total decrement) is the random
identity split, so here the induction needs one more care: an aggregate-measurable *cancel
of a specific order* is not an M0-well-defined action, because order ids are not
aggregate-observable. The clean statement is therefore for request streams whose grammar is
(side, price, quantity) submissions only; order-id-addressed actions (cancel/replace) are
not M0-admissible unless keyed to aggregate-observable labels, in which case the same
argument runs and the level decrement equals the keyed label's aggregate content. With that
grammar clause, A(s_{t+1}) = Φ(A(s_t), request) for a deterministic measurable Φ, which
implies identical aggregate-process laws from all fiber members. ∎

**Remark (off the slack stratum, the obstruction holds already at M0).** If the slack
condition fails, lumpability fails even for M0 flows, through the engine's own
identity-dependent validation: take asks[101] = [(O1, A, 2)] vs [(O1, B, 2)] (identical
aggregate level total 2; the *owner* of the best ask differs) and the M0-aggregate-measurable
request "A submits a marketable buy at 101." In the first member this is rejected
(`SELF_TRADE_PREVENTED`, `matching.py:715-721`: A's own ask is crossed), aggregate state
unchanged; in the second it executes V* units and moves level totals. The aggregate one-step
laws differ by TV = 1 (deterministic divergence). The same works with
`INSUFFICIENT_CASH`/`INSUFFICIENT_INVENTORY` via the per-actor reserve sums
(`matching.py:831-853`). So the true boundary of the sufficiency reduction is not the M0/M1
policy ladder alone but "no identity-dependent channel is active," of which policy feedback
(M1) and validation feedback (self-trade, reserves) are the two engine-native instances.
This *strengthens* R2 (non-lumpability is harder to escape than the M1 concession suggests)
and must be stated honestly in T1's wording: the M0 concession is a stratum statement, not a
class statement.

**Status.** PROVEN (with the request-grammar clause on order-id-addressed actions stated
above).

## 5. Sharpness: the class assumption in R2-B is necessary — PROVEN (counterexample)

If *every* pool actor responds with exact buy-back-own-fills on the same side (g_i(c_i) =
c_i for all i ∈ P) within one aggregate window, the total response volume is
Σ_i c_i = V* in every fiber member (counts sum to V* deterministically), the level totals
reconcile, and the aggregate one-step separation at that node is TV = 0. With per-event
print granularity the print *sequence* still separates (single print (V*) vs the sequence
((c_i)_i), TV = 1 − C(q_r, V*)/C(R*, V*) — 5/6 on the (2,2), V* = 2 pool), but under a
window-pooled aggregate observer the one-step separation genuinely vanishes. Hence: no
injective-own-count response ⇒ no uniform separation; the obstruction is exactly coextensive
with Π_resp-style active feedback. R2 is stated as the triple interaction
(kernel x granularity x policy feedback), matching the KT-G1 verdict line, and this
counterexample is what forbids the stronger (all-M1+) claim.

## 6. Scope check — the lemma is stated only as widely as proven

**6.1 Linear case / fixed regime (P9).** The construction fixes the marginal level p* = 101
by crossing (better levels empty), so the clearing price is endogenous-but-shared: both
members sit in the *same* linear region of the P9 piecewise structure, away from tie walls
(V* = 2 < R* = 4 is a strict partial fill; no prefix-sum coincidence). The lemma holds on
the interior of any fixed combinatorial regime with m ≥ 2 pool orders in the spread member
and any point-mass member. At tie walls (V* exactly a prefix sum) the analysis of the
specific stratum applies unchanged (the round is still a strict partial fill of the pool
whenever 0 < V* < R*); the stratification by the price-jump flag (appendix P4iii) is
preregisterable and covers the glueing. Endogenous prices do not weaken the construction
because both fiber members share the aggregate book, hence the same crossing logic.

**6.2 Exhaustion boundary V* = R*.** The single-round attribution becomes deterministic in
*every* member (all pool orders fully fill), so Lemma R2-A's random separation degenerates.
Non-lumpability survives deterministically through the same M1 channel with a
fresh-order response: at exhaustion A's fill count is 4 under s_pm-type members and 2 under
s_sp-type members (both deterministic), so a responsive resting submission of quantity
g(c_A) at an untouched price (e.g., 105; no self-trade, slack) yields next aggregate level
totals g(4) vs g(2): TV = 1. Statement for the exhaustion stratum is this deterministic
version; it is part of the lemma package but must be labeled a different mechanism
(identity-forced counts, not draw randomness).

**6.3 V* = 1.** R2-A(iii): spread law (1/2, 1/2) on {0, 1}, universal bound 1 − max = 1/2,
construction TV = 1 − P(c_A = 1) = 1/2 for g = id. Separation persists at half strength;
consistent with (and independent of) the appendix's static statement that V* = 1 degrades
*static per-order identification* to proportions (P2iii) — R2 is about the forward law, not
static identification, and does not degrade to zero at V* = 1.

**6.4 Boundary caveat of the cancel-response variant.** If the responsive action is "cancel
own remaining order," the branch c_A = q_A (own order exhausted) degenerates to a rejected
cancel (`ALREADY_FILLED`, `matching.py:734-735`) rather than a zero-quantity cancel; the
map c ↦ next level total c remains correct on all branches, but the *event type* differs
across branches. The marketable-sell variant of R2-B has no degenerate branch and is the
one used in the proof; recorded here so the paper never relies on the cancel variant
without the branch note.

**6.5 Single-order pools (m = 1).** No spread member exists at a single-order level
(the only fiber directions are level totals and deeper levels, whose non-lumpability at M0
is false by R2-C and at M1 follows from R2-B applied at whichever level has m ≥ 2). R2
needs at least one touched level with a multi-order pool across the fiber — which is
exactly the D1_03 fixture-enrichment gap: the frozen 21–22-event fixtures contain **no
multi-order rationed level** (the random-unit fixture's pool at 101 is the single order
O00000003(b, 4), seq 5-8), so the empirical arm of this lemma (S1a-type pairs) is
unmeasurable until the enrichment lands.

**6.6 What is NOT claimed.** No claim for M0 flows off the slack stratum being *lumpable*
(false, Section 4 Remark); no claim for all M1+ policies (false, Section 5); no
multi-step/asymptotic identification claim (the appendix's P7 conjecture boundary is
respected: here only one-step separation, hence by existence of a separating node the
finite-horizon non-sufficiency, is proven); no claim about the pro_rata kernel (not in this
engine — `AllocationRule` has exactly two members, `schema.py:22-24`); no log-concavity-based
universal 1 − O(R*^{−1/2}) constant for arbitrary compositions (Section 7).

## 7. Parent positioning (adjudicated D-2 map only)

- **Diaconis–Sturmfels 1998 (algebraic algorithms for sampling from conditional
  distributions; map row: adjacent/med).** Static, data-space sufficiency fibers for exact
  tests on a *fixed sample space*. R2 is a *dynamic* sufficiency failure: the aggregate
  statistic fails to support the forward law of a stateful controlled process, and the
  failure is gated by a policy-feedback condition that has no analogue in a fixed-sample
  conditional-inference problem. R1 (the static toric concession) is precisely the part of
  our story that *does* reduce to this row — already conceded into T1 scope.
- **Fibers of multi-way contingency tables (2014; adjacent/med).** Deterministic
  constraint-granularity analog, inference level, no dynamics, no kernel. Same boundary.
- **Discrete Probabilistic Inverse Optimal Transport (ICML 2022; adjacent/high).**
  Inference-level likelihood fiber modulo an OT mechanism, fixed observation, no claim that a
  coarsening fails to be sufficient for a *sequential* law under feedback flows.
- **Perturb-Argmax/Softmax (arXiv:2406.02180; cleared collision/high).** Noise law determines
  the stochastic fiber for the *state-free argmax family*. Our separation is
  state-composition-dependent (hypergeometric over a pool), inside a stateful matching
  engine, and the object is forward-law sufficiency, not static fiber shape.
- **Properties from Mechanisms (ICLR 2022; adjacent/med).** Identification up to shared
  equivariance — static identification result; R2's obstruction lives one level up (the
  recorded statistic does not support prediction), and the M0/M1 boundary has no
  counterpart there.
- **SBI summary-statistic rows (Lack of confidence in ABC 2011; On Consistency of ABC 2015;
  Comparison of Likelihood-Free Methods 2021; MI summary-statistic audit 2023; all
  adjacent/low).** The nearest genre: summaries losing information for *parameter*
  inference. The honest adjacency: insufficiency of a summary for static parameter
  identification is classical; R2's object is insufficiency for the *forward law of the
  observed process itself* under identity-feedback flows — a controlled-process statement
  (the coarsening is not closed under the dynamics), not a static-inference statement. The
  2023 MI audit is the borrowable empirical instrument (measure MI between aggregate tape
  and forward-law-relevant latents).
- **Research Design Meets Market Design (2017; adjacent/low).** Randomness as an instrument
  for identification; does not state tape-granularity sufficiency failure.
- **Bogomolnaia–Moulin 2001 / Stable and Fair Random Allocations 2026 (background /
  adjacent/low).** Own the lottery-vs-fractional allocation mathematics; design-side, no
  recording or training object.
- **Markov lumpability (strong/weak lumpability).** NOT in the adjudicated map. The
  writeup's "closed coarsening / lumped chain" framing is the standard lumpability
  vocabulary; per D-1 citation discipline the primary literature for it is *not cited as
  fact* and is listed in new_references_needing_verification. No proof step depends on any
  lumpability theorem — the lumpability statements here are proved directly from the engine.

## 8. Hostile check (self-attack of the weakest steps)

1. **"The divergence is policy-authored, not engine-authored."** Strongest attack. Response:
  the *channel* is policy (that is the M1+ class, stated in the theorem, and the M0
  concession R2-C shows the engine alone does not separate — that is the content, the triple
  interaction); the *constant* is engine-authored: TV = 1 − P_{q,V*}(c_r = forced value)
  depends only on the engine's draw law (composition x V*), not on g beyond injectivity, and
  the same 5/6 would obtain for any responsive policy. The engine's hypergeometric
  attribution is what makes the response distribution differ; the policy only routes engine
  randomness into aggregate observables. Residual honesty: a referee may still prefer to
  call R2 "a controlled-process non-sufficiency lemma with an engine-native constant" rather
  than an "engine theorem" — the T1 wording should say exactly that.
2. **"Your class Π_resp is hand-picked; Section 5 shows M1 policies with zero separation."**
  Conceded and converted into sharpness: the lemma claims exactly the active-channel class,
  the counterexample is recorded as the necessity direction, and R2-C is the sufficiency
  direction of the boundary. The statement is falsifiable as a *characterization*, which is
  stronger than a blanket existence claim. Weakness retained: Π_resp does not characterize
  *all* separating policies (per-event print granularity separates some conserving policies
  too); the paper must not claim "if and only if."
3. **"The pair s_pm = [A(4)] vs s_sp = [A(2), B(2)] differs in order count, which arrival
  records would reveal."** Under the frozen corpus contract F_exec (D1_01) arrival records
  are excluded; under `aggregate_state_hash` order count is summed out (`schema.py:314-315`).
  If a future corpus contract re-admits arrival records, the *aggregate state* fiber shrinks
  and R2's witness pair must move to compositions not distinguishable by the enriched
  grammar (e.g., same order count, different quantities: [A(3), B(1)] vs [A(1), B(3)] —
  same analysis, TV = 1 − P(c_A = 3·…), strictly positive). The lemma's mechanism survives;
  the witness does not. Flagged for the corpus-contract freeze wording.
4. **"R2-C's grammar clause (cancel/replace not M0-admissible unless aggregate-keyed) is
  doing real work."** True and disclosed in the proof. Without the clause, an "M0" actor
  cancelling an order *it cannot identify* is not a well-defined policy; the honest statement
  is that M0 lumpability is proven for submission-grammar flows and for
  aggregate-keyed cancel grammars, nothing else.
5. **"V* = R* exhaustion uses a different mechanism (deterministic identity-forced counts);
  bundling it into the same lemma is scope inflation."** Labeled separately (Section 6.2) as
  a deterministic corollary with its own mechanism; the random-bound clause and the
  exhaustion clause are never mixed in the paper text.
6. **"Your constants are computed, not closed-form."** The ladder constants are exact
  rationals from the MVHG formula; the asymptotic 1 − O(v^{-1/2}) is proven only for
  balanced pools via the Binomial limit (termwise ratio argument). A general-composition
  universal atom bound would need a log-concavity result outside the D-2 map; deliberately
  not used. A referee supplying one only *improves* our constants, so this is safe exposure.
7. **"Step 2 assumes the responsive actor knows c_A."** The actor knows its own inventory,
  cash, and order remaining — each a deterministic function of own fills — which is the
  thesis-v2 M1 definition verbatim. No knowledge of the *other* side's composition or of the
  draw annotation is assumed. The point-mass member forces c_A = 4 − (own remaining): own
  observation suffices.
8. **"Is s_pm reachable?"** It is a valid prestate (`_validate_prestate` accepts a one-order
  initial book) and the frozen random-unit fixture realizes exactly this shape
  (single resting order of quantity 4 at 101, seq 5). The spread member is the same fixture
  with the level split — the D1_03 enrichment's declared purpose.
9. **"Why does P3 (kernel anonymity at agg) not contradict R2?"** P3 is the one-round,
  policy-free statement: the aggregate print law of a single round is kernel-independent and
  fiber-collapsing. R2 agrees (Step 1: round-1 aggregate observables coincide) and locates
  the failure at the *second* boundary, where identity feedback re-enters through the flow.
  No tension; the two statements compose into the granularity-dichotomy-plus-feedback story.
10. **Weakest step, named.** Step 2's injectivity-plus-slack hypothesis is the load-bearing
  and least "engine-native" element: it is a condition on the *policy class*, verified only
  for the two engine-native instantiations (marketable sell, cancel-with-branch-note). The
  red team should attack there; the defense is that the condition is exactly the operational
  definition of M1 (active own-state feedback), and Section 5 shows removing it kills the
  lemma — so the condition is the theorem's honest boundary, not a hidden assumption.

## 9. Consequence for T1/D-1 wording (feeds the D-1 wording freeze)

1. T1's obstruction lead sentence: "for identity-responsive (M1+) flows the aggregate tape is
   not sufficient for the engine's forward law: aggregate-indistinguishable book
   compositions induce one-step aggregate-transition laws separated by
   TV ≥ 1 − max_x p_x^{MVHG} (explicit constants; 5/6 on the two-unit balanced pool),
   uniformly over responsive policies" — with the M0-slack lumpability concession and the
   validation-channel remark (Section 4) in the same statement block, since the honest
   boundary is "no active identity channel," not "M1 or below."
2. The R1 static toric concession stays as written (Diaconis–Sturmfels / contingency-table
   fibers cited as owners of the static fiber shape); R2 is the dynamic complement; R3 stays
   labeled the trivial data-processing direction.
3. The exhaustion stratum gets its own deterministic clause (never merged with the random
   bound); V* = 1 carries the 1/2 constant.
4. The witness pair requires a multi-order rationed level — restate the D1_03 enrichment
   dependency for any empirical S1a-type realization of this lemma.
5. Risk register: the KT-G1 R2 failure row does **not** fire; no REFRAME needed.

## 10. Engine citations index (all claims above)

- Draw semantics / eligible_units / uniform-over-units: `scripts/lab_asset/matching.py:585-604`;
  per-unit fill for the random arm: `matching.py:292-296` (and `:443-448` for replace path).
- Aggregate level evolution of a round / level deletion: `matching.py:285-346`, `:606-625`.
- Settlement conservation of totals: `matching.py:640-644` (`_settle`).
- Identity-dependent validation (self-trade, per-actor reserves): `matching.py:671-721`,
  `:715-721`, `:831-853`; cancel rejection on filled orders: `matching.py:734-735`.
- Aggregate statistic definition (level sums, total cash/inventory, no order count, no rng):
  `scripts/lab_asset/schema.py:299-325`; M0-lumpability docstring condition:
  `schema.py:307-311`; full-state hash contents: `schema.py:239-296`; two-member
  AllocationRule: `schema.py:22-24`.
- Frozen fixtures (read-only): `experiments/lab_asset_a2/a2_exit_20260905/fixture_random_unit_within_price/`
  — `prestate.json` (actors a-d, bands [90,110], book IB1(d,4)@103), `tape.jsonl` seq 5
  (resting 4 at 101), seq 7-8 (eligible_units 4, 3; quantity 1; maker_remaining 3, 2);
  single-maker pool confirms the D1_03 enrichment gap. Bundle manifest fea8a136…9581c
  untouched (no writes to this directory in this session).
- Policy ladder M0/M1: `papers/proposal/ecomd_random_unit_priority_thesis_v2_2026-08-27.md`
  lines 70-71.
- Exact-rational constant check (CPU-only, no engine execution): /tmp/ktg1/hyp.py —
  two-order (2,2) V*∈{1,2}: 1−max = 1/2, 1/3; S3 pool (5,4,3,2) V*∈{1,2,4,6}:
  TV(point-mass) = 9/14, 81/91, 996/1001, 1; balanced-family 1−max values and Binomial
  limits 1/2, 5/8, 11/16.
