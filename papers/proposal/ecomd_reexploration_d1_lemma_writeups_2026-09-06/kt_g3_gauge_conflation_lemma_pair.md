---
note: >-
  KT-G3 deliverable (D-1 wave, 2026-09-06). Lemma pair upgrading the V4 gauge-conflation remark
  from prose to proven statements, in the formalism of
  papers/proposal/ecomd_reexploration_theory_appendix_2026-09-06.md Part II (Sections 0-4).
  Screening-legal: theorem/schema work only; no GPU, no engine execution, no data access, no
  network. Frozen bundle experiments/lab_asset_a2/a2_exit_20260905/ was read, never mutated.
  External citations are ONLY adjudicated names from
  papers/proposal/ecomd_reexploration_d2_evidence_map_2026-09-06.md (Section 1.2 table).
status: Lemma A proven_with_conditions; Lemma B proven (given the frozen Theorem 1 package); soft-quotient extension proven; V4 remark rewritten.
---

# KT-G3 — The gauge-conflation lemma pair (Lemma A / Lemma B)

**Attack being discharged (killer-tests doc, section A, KT-G3 / D-2 veto family V4):**
"the mechanism fiber is just a gauge symmetry; the fix is quotienting the hypothesis space, as in
quotient-space generative modeling."

**What is proven here.**

- **Lemma A (not function-preserving).** No quotient of raw-flow space is simultaneously
  corpus-compatible, nontrivial on the mechanism fiber, and preserving of the named consumer
  family. A gauge symmetry lives in the kernel of *every* deployment map including the identity;
  the mechanism fiber provably does not.
- **Lemma B (no quotient repair / quotient injury).** Every quotient-confined (and every soft /
  randomized-quotient) predictor is fiber-constant (in distribution) and therefore has best-case
  consumer error exactly equal to the Theorem 1 information floor: the floor is information-
  theoretic, not representational — quotienting cannot reduce it, and the quotient hypothesis
  class already contains the attaining predictor, so the repair buys nothing while deleting the
  coordinates the deployment maps read.

Both lemmas are engine-grounded in the frozen lab-asset-v3 artifacts and `scripts/lab_asset/`
code; every engine-semantics claim below carries a file/line citation.

---

## 0. Setup (measure-theoretic; extends theory appendix Part II Section 0, notation unchanged)

**Spaces.** One instrument, tick lattice fixed. For the one-step contract (Part II Section 0): raw
flow `z = (q, t, α)` with submitted quantities `q ∈ Z_{≥0}^{1+n}` (linear relaxation `R_{≥0}`;
integrality a lattice remark, matching Part II), arrival clocks `t = (t_1, …, t_n)` with
`t_1 < … < t_n` **strictly ordered** (M1 scaffold), and actor map `α` (order ownership). Write
`Z_qt = R_{≥0}^{1+n} × {t : t_1 < … < t_n}` for the *consumer-relevant coordinates*: by assumption
A3 of Part II, every named consumer is a finite linear functional of `(q, t)`; `α` never enters a
named consumer. `Z_qt` is a Borel subset of `R^{2n+1}`, hence standard Borel; multi-round corpora
live in countable products of such spaces (standard Borel; the lemmas are applied per corpus
fibre, i.e. conditional on the full tape `τ`).

**Recorded map / corpus.** `T := T_{k,F_exec} : Z → Y` maps a raw flow to the through-M training
corpus under corpus contract `F_exec` (PI decision `D1_01`): **execution-event payloads only** —
the `execution` sub-payload, `allocation_draw` when present, and `pre/post_best_bid/ask` prices —
per `schema_spec.json` `payload_fields.execution = [execution, aggressor_role, maker_role,
allocation_draw?, pre_best_bid, pre_best_ask, post_best_bid, post_best_ask]`. Two load-bearing
exclusions, both verified against the frozen artifacts:

1. **The integrity hashes are not corpus fields.** `pre/post_state_hash` and
   `pre/post_aggregate_state_hash` sit at the *tape envelope* level (siblings of `event_type` /
   `payload` in `tape.jsonl`), not inside any `payload_fields` list (`schema_spec.json`
   `payload_fields`, all event types). `F_exec` is a payload projection, so `T(z) = T(z')` does
   *not* imply `state_hash(z) = state_hash(z')` — this is exactly S1a gate G2 (state-hash chains
   differ on constructed fiber pairs). If a referee reads the hashes into the corpus, every fiber
   is a point and T1–T3 are vacuous; the frozen corpus contract forbids this (wording condition,
   Section 6).
2. **`order_accepted` (with `resting_quantity`) is excluded**, so declared quantities of resting
   orders and the aggressor's unexecuted remainder are corpus-invisible
   (`schema_spec.json` `payload_fields.order_accepted`; Part II Section 0 already records this).

`Y` is countable (finite payload grammar, bounded corpus length per contract), so `T` is
measurable iff each `T^{-1}(y)` is Borel — true because on each fixed combinatorial regime the
recorded constraints are piecewise-linear/rational in `(q, t)` (T1 propositions P0, P9).

**Engine facts used (all verified).**

- (E1) *Random arm draw semantics.* `_select_maker` computes
  `eligible_units = sum(quantity for _, _, quantity in queue)` — the total remaining quantity at
  the marginal price, *before* the draw — and `selected_unit = rng.randrange(eligible_units)`,
  uniform over remaining units; the recorded `allocation_draw = {price, eligible_units,
  selected_unit, maker_order_id}` (`scripts/lab_asset/matching.py:585-604`). Fixture:
  `fixture_random_unit_within_price/tape.jsonl` seq 7–8, `eligible_units` 4 then 3,
  `maker_remaining` 3 then 2.
- (E2) *FIFO semantics.* maker = `queue[0]`, no draw payload (`matching.py:589-590`); fill =
  `min(remaining, maker_qty)` in **one** record (`matching.py:292-296`); random arm fills
  `quantity: 1` per record per drawn unit (`matching.py:295`). Fixture:
  `fixture_fifo/tape.jsonl` seq 7: one execution, `quantity: 2`, `maker_remaining: 2`, no
  `allocation_draw`.
- (E3) *Executed orders are pinned.* every execution records
  `maker_remaining = maker_qty − fill` (`matching.py:298, 310`), so any order that appears in the
  corpus has its quantity pinned by (cumulative fills + last `maker_remaining`), both arms.
- (E4) *Unrecorded magnitudes.* resting orders never executed in the corpus never appear in any
  `F_exec` field (only best **prices**, not depths); the aggressor's post-crossing remainder
  rests unrecorded (`matching.py:356-357`; its quantity lives only in
  `order_accepted.resting_quantity`, excluded by contract). Fixture instance: prestate
  `initial_book` order `IB1` (actor `d`, price 103, quantity 4, side S,
  `fixture_random_unit_within_price/prestate.json`) is a deeper level never touched; after the
  trades at 101 the recorded `post_best_ask` is still 101, so `IB1`'s depth appears nowhere in
  `F_exec`.
- (E5) *Clocks.* execution payloads carry the aggressor's request clocks only
  (`matching.py:311`, `clocks=request.clocks`); maker arrival clocks appear in no `F_exec` field.
  Accepted orders have quantity ≥ 1 (`negative_or_zero_quantity` rejection —
  `matching.py:671-714` `_validate_order`; fixture `fixture_fifo/tape.jsonl` seq 16–17), and
  prices are positive integers inside `price_bands` (prestate `price_bands: [90, 110]`).

**Fiber.** `F_τ = {z' ∈ Z : T(z') = T(z)}`, `T(z) = τ` (Part II Section 0). Its consumer-relevant
ambiguous coordinates, from (E3)–(E5), in the three direction classes used below:

- `U_mag(τ)`: **magnitude directions** — quantities of never-executed resting orders (any level,
  including untouched deeper levels and same-side orders), plus unrecorded residuals of partially
  executed orders (the incoming order's remainder). These are the Corollary 2 recession
  directions: `T(z̄ + t·u) = τ` for all `t ≥ 0`, `u ∈ R_{≥0}^{U_mag}`.
- `K_split(τ)`: **never-drawn split directions** (random arm, touched levels) —
  `u` supported on the never-drawn orders `ND(ℓ)` of a touched level `ℓ` with
  `Σ_{i∈ND(ℓ)} u_i = 0`; the `eligible_units` chain (E1) pins the level aggregate, `maker_remaining`
  (E3) pins drawn orders, never-drawn order ids never appear in any draw payload.
- `U_clk(τ)`: **clock directions** — perturbations of arrival clocks of orders whose clocks are
  corpus-invisible (E5), preserving the strict order (order-preserving under FIFO, since the queue
  is arrival-ordered; irrelevant under the random arm, which reads quantities only, (E1)).

A fourth residue — **ownership relabeling** of never-executed orders (the actor map `α` on
`U_mag ∪ K_split` members) — is fiber-internal but invisible to every named consumer by
construction (A3). It is conceded as a genuine gauge core in Section 3.4; it is the engine-native
realization of T1's aggregation directions (T1 P2(v)).

**Named consumer family (preregistered in Part II Sections 0–3; not reverse-engineered here).**

- `C_risk(z) = Σ_i p_i q_i` (raw-flow portfolio notional);
- `C_lat^W(z) = Σ_i p_i 1{t_i ≤ W} q_i`, `W > 0` (latency-window notional; equals
  `C_risk ∘ D_trunc^W` — the truncation-composed consumer of Theorem 3, P3.3);
- swap consumers: `A^{→ru}_i(z) = q_i^{rem}/S_ℓ` — the next-draw probability of order `i` at
  level `ℓ` under the kernel-swap deployment (`q_i^{rem}` remaining quantity of `i`, `S_ℓ` level
  remaining = the recorded `eligible_units` denominator; engine formula (E1),
  `matching.py:592-597`), and `A^{→fifo}(z)` = the prefix allocation vector (E2).

`C_named := {C_risk} ∪ {C_lat^W : W > 0} ∪ {A^{→ru}_i} ∪ {A^{→fifo}}`. These are exactly the
consumers named in the frozen T2/T3 package (Theorem 1 consumers; Theorem 3 deployment
compositions P3.1–P3.3).

**Quotients (measurability made precise).** A *(deterministic) quotient* is a surjection
`Q : Z → X` onto a set `X` carrying the **final σ-algebra**
`B_X := {A ⊆ X : Q^{-1}(A) ∈ B_Z}`. This is the maximally permissive measurable structure the
repair could ask for: with `B_X` final, a set-theoretic factorization of a measurable map through
`Q` is automatically measurable (if `f = f̃ ∘ Q` then
`Q^{-1}(f̃^{-1}(B)) = f^{-1}(B) ∈ B_Z`, so `f̃^{-1}(B) ∈ B_X`), and any strictly smaller
σ-algebra on `X` only makes factorizations harder. Proving impossibility under the final
σ-algebra therefore proves it under every choice. (Whether `X` is standard Borel is irrelevant —
we allow arbitrary `X` and prove non-existence; `X` need not be smooth here because `T` is
countable-valued and the arguments are set-theoretic once factorization is fixed.)

- **(i) Corpus-compatibility:** the corpus is `Q`-measurable iff `T` factors through `Q`:
  `∃ τ̃ : X → Y`, `T = τ̃ ∘ Q`; equivalently `T` is constant on `Q`-fibers
  (`Q(z) = Q(z') ⟹ T(z) = T(z')`). Note this makes `σ(T) ⊆ σ(Q)`.
- **(ii) Nontriviality on the fiber (the repair's defining property):** `Q` is *fiber-nontrivial*
  iff `∃ z ≠ z'` with `T(z) = T(z')` and `Q(z) = Q(z')` — the quotient identifies at least two
  members of at least one mechanism fiber. The **canonical repair** — collapse each fiber to a
  point, `Q_*(z) = Q_*(z') ⟺ T(z) = T(z')`; e.g. a canonical-interleaving representative map —
  is fiber-nontrivial whenever some fiber has ≥ 2 members.
- **(iii) Consumer preservation:** `C` factors through `Q` iff `∃ C̃ : X → R`, `C = C̃ ∘ Q`
  (equivalently `C` constant on `Q`-fibers).

*Why nontriviality must be hypothesized rather than derived.* The naive route "any `Q` with (i)
must identify fiber members" is **false**: `Q = id` is corpus-compatible and consumer-preserving
and identifies nothing. The correct statement — and all the gauge attack needs or proposes — is
that a *repair* is by definition fiber-nontrivial (its purpose is to collapse the training
equivalence), and *that* already collides with (iii). Lemma A is therefore stated with
nontriviality as a hypothesis; this is a strengthening of the honest quantifier structure, not a
weakening of the lemma.

---

## 1. LEMMA A (the mechanism fiber is not function-preserving)

### Lemma A (no fiber-nontrivial corpus-compatible quotient preserves the named consumers)

Let `k ∈ {fifo, random_unit_within_price}`, `F = F_exec`, and fix a tape `τ` whose fiber
`F_τ` contains two members differing in `(q, t)`-coordinates. Then:

**(A.0) Contrast with a gauge.** If `Q` is corpus-compatible and fiber-nontrivial, and the
identified pair `z, z'` (with `T(z) = T(z')`, `Q(z) = Q(z')`) differs in `(q, t)`, then some
named consumer `C ∈ C_named` has `C(z) ≠ C(z')`, hence `C` does **not** factor through `Q`.
In particular a function-preserving gauge — an equivalence in whose orbits *every* deployment
map, including the identity, is constant — must satisfy (iii) for `D_id`-composed consumers;
the mechanism fiber fails this already for the undeployed consumer `C_risk` (part A.1).

**(A.1) Quantity directions — a two-consumer dichotomy (`C_risk`, else `C_lat^W`).** Let the
identified pair differ by a nonzero quantity component `u` on free coordinates (never-executed
orders at any level, unrecorded residuals, never-drawn split directions — sign arbitrary;
recession directions are the `u ≥ 0` cone, but identified pairs may differ by any vector that
changes no recorded field). All free quantity coordinates carry positive prices (E5), so `u`
defines a price-weighted total `Σ_i p_i u_i`. Then:

- **Case 1: `Σ_i p_i u_i ≠ 0` (in particular every single-order injection `u = δ e_i`,
  `δ ≠ 0`, `i ∈ U_mag(τ)`):** `C_risk(z̄ + u) − C_risk(z̄) = Σ_i p_i u_i ≠ 0`. This is the
  Corollary 2 route — for the canonical repair `Q_*`, `C_risk` does not factor whenever
  `U_mag(τ) ≠ ∅`. Already the *undeployed* consumer separates: the fiber is not in the kernel
  of the identity deployment `D_id` (P3.1), whereas a gauge symmetry is.
- **Case 2: `Σ_i p_i u_i = 0` but `u ≢ 0` (price-weighted redistributions — e.g. never-drawn
  splits at a touched level, or offsetting injections across never-executed orders at different
  prices):** `C_risk` does not separate (this includes Theorem 1(e)(i)'s exact-zero split floor,
  conceded), but the latency family does. Order the support of `u` by clock
  `t_{i_1} < … < t_{i_m}` (strict, M1 scaffold) and set `S_k = Σ_{j ≤ k} p_{i_j} u_{i_j}`.
  `S_0 = 0` and `S_m = Σ_i p_i u_i = 0`; if all `S_k = 0` then every `p_{i_j} u_{i_j} = 0`, hence
  `u ≡ 0` (prices positive) — contradiction. So some `S_k ≠ 0`, and with `W = t_{i_k}`:
  `C_lat^W(z̄ + u) − C_lat^W(z̄) = Σ_{i} p_i 1{t_i ≤ W} u_i = S_k ≠ 0`.

This dichotomy is complete for all quantity directions: every nonzero quantity difference
between fiber members is separated by `C_risk` or by some `C_lat^W`.

**(A.2) Never-drawn splits — the swap consumer separates clock-free (the KT-G3 two-state
construction).** For `u ∈ K_split(τ)`, `u ≢ 0`, supported on the never-drawn orders `ND(ℓ)` of a
touched level `ℓ` (requires `|ND(ℓ)| ≥ 2`), a *third*, clock-independent separator exists:
`A^{→ru}_i(z̄ + u) − A^{→ru}_i(z̄) = u_i / S_ℓ ≠ 0` for every `i ∈ ND(ℓ)` with `u_i ≠ 0` (the
level total `S_ℓ` is *pinned* by the `eligible_units` chain, (E1), so the next-draw probability
`q_i/S_ℓ` moves one-for-one with `q_i`). In TV terms the next-draw law at `z̄ + u` differs from
that at `z̄` by `TV ≥ max_{i: u_i ≠ 0} |u_i|/S_ℓ` — the two-state construction of KT-G3/P3.2,
and the engine-native reason the fiber is *deployment*-distinguishable, not merely
consumer-distinguishable. This separator is the load-bearing one if any variant grammar admits
tied arrival clocks (see Hostile check item 2).

**(A.3) Clock directions — the latency family separates.** If the identified pair differs by a
nonzero clock perturbation `w` (order-preserving under FIFO so the queue and prefix fills are
unchanged; unconstrained under the random arm), pick `i` with `w_i ≠ 0` and `W` strictly between
`t_i` and `t_i + w_i`; then `C_lat^W(z̄ + w) − C_lat^W(z̄) = p_i q_i (1{t_i + w_i ≤ W} − 1{t_i ≤ W}) ≠ 0`
(`q_i ≥ 1`, (E5)). The truncation deployment `D_trunc^W` likewise changes which orders exist in
the deployed world (P3.3).

**(A.4) Characterization corollary (the sharp "not function-preserving" statement).** Define the
`C_named`-gauge core of the fiber by `z ≈ z'` iff `T(z) = T(z')` and `C(z) = C(z')` for all
`C ∈ C_named`. Then on consumer-relevant coordinates `≈` is the identity: `F_τ` is a
function-preserving gauge for the named family **iff** its `(q, t)`-ambiguous set
(`U_mag ∪ K_split ∪ U_clk` directions) is empty — iff the fiber consists solely of ownership
relabelings. Consequently the canonical repair `Q_*` preserves every named consumer iff every
fiber is a pure relabeling class; under corpus contract `F_exec` this fails for every tape with
any never-executed order, any unrecorded residual, any untouched level, or any touched level
with ≥ 2 never-drawn orders.

*Proof.* All parts are one-line computations on the stated functionals once the fiber-direction
claims are granted; the fiber-direction claims are the frozen package's (Corollary 2's recession
directions; Part II Section 0's fiber table; T1 P1–P2), each engine-verified in Section 0
(E1)–(E5). Given a corpus-compatible fiber-nontrivial `Q` and an identified pair `z ≠ z'` with
`T(z) = T(z')`: their difference lies in the fiber's free directions (recorded-field invariance).
Write the difference as `(u, w)` (quantity, clock). If `u ≠ 0`, the A.1 dichotomy separates
(Case 1: `C_risk`; Case 2: some `C_lat^W`; and where `u` has split support at a touched level,
A.2's swap consumer is an additional clock-free separator). If `u = 0`, then `w ≠ 0` (the pair
differs on `(q, t)` by hypothesis) and A.3 separates. In every case some named consumer is
non-constant on `{z, z'} ⊆` one `Q`-fiber, so that consumer cannot factor through `Q` (a
factoring consumer is constant on `Q`-fibers by construction). A.4: (⇐) if the `(q, t)`-ambiguous
set is empty, any two fiber members agree on `(q, t)` and every named consumer — a functional of
`(q, t)` by A3 — agrees; (⇒) is A.1–A.3. ∎

**Status: proven_with_conditions.** Conditions (all stated above, none hidden): (a) corpus
contract `F_exec` exactly as frozen by `D1_01` — in particular the integrity hashes
(`state_hash` / `aggregate_state_hash`) and `order_accepted` events are *not* corpus fields
(breaking either exclusion collapses fibers toward points and A becomes vacuous-with-truth-value-
trivial rather than false — see the corpus-contract STOP risk, Section 6); (b) the named family
`C_named` as preregistered in Part II — the lemma proves the *engine fact* that each free
direction class is read by at least one preregistered consumer; it does not claim separation for
arbitrary consumers (the ownership residue is conceded, A.4); (c) strict arrival clocks for the
A.2 secondary separator — with the clock-free swap consumer as the primary separator this
condition is removable; (d) per-fiber conditional form (`F_τ` with ≥ 2 `(q, t)`-distinct
members), matching Theorem 1's conditional framing; multi-round corpora shrink fibers (T1 P7)
but the surviving directions (never-marginal levels, splits, aggregation) are exactly the ones
covered.

---

## 2. LEMMA B (no quotient repair; the floor is information-theoretic)

### Lemma B (quotient confinement and exact floor equality, deterministic, loss-side, and soft quotients)

Fix `(k, F_exec)`, a tape `τ` with nonempty consumer-relevant ambiguous set in the direction of
consumer `C = v^T z` (`v_U ≢ 0`), and a reference measure `μ_R` on the fiber (any probability
measure with `C ∈ L²`; the contract instance is the box-uniform of Part II Section 0). Then:

**(B.1) Forced tape-measurability of every through-M predictor.** By Lemma 0 (Part II Section 0),
`T(z) = T(z')` implies byte-identical corpora, hence identical trained parameters
`θ̂ = A(τ, ω_train)` for any training map `A` (deterministic, or stochastic under paired seeds,
assumption A4), and every deployed consumer readout `Ĉ = C ∘ sim(θ̂)` is a measurable function of
`(τ, ω_train, ω_eval)` alone. This holds **for every hypothesis space** — quotient-parametrized
(`h ∘ Q`), loss-side-quotiented, canonicalized, or unconstrained: the pipeline's information
input is the corpus, and no representation surgery adds information. Every through-M predictor
is `σ(T) ∨ σ(ω)`-measurable and therefore fiber-constant.

**(B.2) Confinement and exact floor for quotient classes.** Let `Q` be corpus-compatible and
fiber-nontrivial (including the canonical repair `Q_*`, whose `σ(Q_*) = σ(T)` exactly), and let
`H_Q := {h ∘ Q : h : X → R measurable}` be the quotient-parametrized hypothesis class. Then
`H_Q ⊇ {σ(T)-measurable functions}` (if `g = g̃ ∘ T` then `g = (g̃ ∘ τ̃) ∘ Q ∈ H_Q`, using
corpus-compatibility), while by B.1 the *reachable* set of trained predictors is contained in
the `σ(T)`-measurable functions. Hence:

  `inf over quotient-trained predictors E_{μ_R}[(C − Ĉ)² | τ] = inf over σ(T)-measurable Ĉ E_{μ_R}[(C − Ĉ)² | τ] = Var_{μ_R}(C | τ)`

— the Theorem 1(b) floor, **exactly**, with the same unique a.s. minimizer `Ĉ* = E[C | τ]`
(Theorem 1(c); uniqueness because `E(X − c)² = Var X + (EX − c)²`). The repair can neither beat
the floor (it binds every tape-driven predictor) nor is needed to attain it (the minimizer is
already representable in `H_Q`). The floor's value depends only on `(σ(T), C, μ_R)` — not on the
hypothesis space, optimizer, or encoder: **information-theoretic, not representational.**

**(B.3) Soft / randomized quotients (the extension).** A *stochastic encoder* is a Markov kernel
`K : Z × B_X → [0,1]`; it is *fiber-measurable* iff `K(z, ·) = K̄(T(z), ·)` for some kernel `K̄`
from `Y` to `X`. (Every through-M-trained encoder is fiber-measurable: by Lemma 0 its output law
given `z` is the law of `h(τ, ω_enc)` at `τ = T(z)` — a function of `τ`.) Let the predictor be
`Ĉ = g(x, ω)` with `x ~ K(z, ·)` and `ω` exogenous, `g : X × Ω → R` measurable. Then:
- *(fiber-constancy in distribution)* the conditional law of `(x, ω)` given `z` is
  `K̄(τ, ·) ⊗ P_ω`, a function of `τ` alone; hence `Law(Ĉ | z) = Law(Ĉ | z')` whenever
  `T(z) = T(z')`: a fiber-measurable stochastic encoder is still fiber-constant in distribution.
- *(floor)* `E[(C − Ĉ)² | τ] ≥ Var_{μ_R}(C | τ)`, with equality iff
  `g(x, ω) = E[C | τ]` for `K̄(τ,·) ⊗ P_ω`-a.e. `(x, ω)`.

  *Proof.* Condition on `(τ, x, ω)`: `Ĉ = g(x, ω)` is a constant `c`; under
  `z ~ μ_R(· | τ)`, `E[(C − c)² | τ] = Var(C | τ) + (E[C | τ] − c)²`. Average over
  `(x, ω) ~ K̄(τ,·) ⊗ P_ω` (a law not depending on `z`, which is the entire point) and drop the
  nonnegative second term. Equality forces `(E[C|τ] − g(x,ω))² = 0` a.e. ∎

  Consequently `inf` over all soft-quotient pipelines `= Var_{μ_R}(C | τ)` — the same value as
  the deterministic quotient class and the unrestricted tape-information class: randomization,
  softness, and attention-style fiber-weighting (any `K̄`) buy nothing. For any convex loss the
  same argument gives `E[ℓ(C − Ĉ) | τ] ≥ E_ω[ℓ-conjugate form] ≥ ℓ-driven floor`; the quadratic
  case (the contract's metric) is stated as proven, the convex extension as a remark.

**(B.4) Prior-universality (the floor is not a `μ_R` artifact).** For *every* prior `π` on `Z`
with `C ∈ L²(π)`: `inf over tape-driven Ĉ E_π[(C − Ĉ)²] = E_π[Var_π(C | σ(T))]` — the same law-of-
total-variance argument with `π` in place of `μ_R`. The floor is prior-relative (it is the
practitioner's own residual uncertainty given the recording) but **quotient-invariant**: no
choice of `Q`, `K̄`, or readout changes it. This closes the "your floor is your reference
measure" attack.

**(B.5) Injury: the quotient deletes exactly what the deployments read.** For `D ∈ {D_swap→ru,
D_trunc^W}` and consumer `C` with `Exp(D, C) ≠ ∅` (Theorem 3, P3.2/P3.3): `C ∘ D` is non-constant
on fibers containing exposed directions (A.2/A.3 applied to `C ∘ D ∈ C_named`), so no
corpus-compatible fiber-nontrivial `Q` factors `C ∘ D` (Lemma A): the quotient hypothesis space
cannot even *represent* the deployment-composed prediction map. The best tape-driven
approximation error to the deployed target is exactly `Var_{μ_R}(C ∘ D | τ)` (B.2 with consumer
`C ∘ D`), strictly positive precisely on the exposed sets of Theorem 3. The suppression is
**destructive, not a relocation**: `D_swap→ru` reads never-drawn quantities through
`q_i^{rem}/S_ℓ` (E1) and `D_trunc^W` reads arrival clocks (E5) — the very coordinates the
quotient identifies away.

**Status: proven** (given the frozen package: Lemma 0, Theorem 1(b,c), the Part II Section 0
fiber structure — all engine-grounded as in Section 0 above). B.3 (soft quotients) is proven
here for the first time and is the lemma pair's genuinely new argument. Honest framing: B is a
corollary-grade statement *by design* — its scientific content is the quantifier discipline
(every hypothesis space / optimizer / randomization at once; prior-universality; the
representability failure B.5), not a new estimation theorem; it must be presented as the
no-repair twin of A, never as an independent contribution (mirroring the D-2 condition that T2's
generic estimation content is conceded).

---

## 3. The in-repo gauge-injury precedent (`gauge_enforce`)

The "quotient injury" phrasing is grounded in the repository's own recorded gauge-injury event,
which the killer-tests doc (Section 1) already flags as the strongest internal precedent for
KT-G3:

- **Event.** EcoMD v2.0 enforced an Ilinski-style gauge on the pair representation: with
  `gauge_enforce=True` the pair kernel input is `[Δs_ij, τ_i, τ_j]` (differences only), instead
  of the v0.8-style full `[s_i, s_j, |Δs|, τ_i, τ_j]`
  (`ecomd/models/ecomd_v2.py:240-252, 298-310`). The 2026-04-25 overnight ablation found the
  enforced-gauge architecture locked at 4/11 stylized facts across **33/33 configurations**,
  because agent position `s[0]` carries absolute meaning (it is inventory, not log-price): the
  gauge deleted `|s_i|`-dependent information that volatility clustering requires
  (`logs/2026-04-25.md`, Session 21). Disabling the enforcement (`gauge_enforce=False`) restored
  the vol-clustering facts — v2.1 at 6/11 including `ACF(r²) = +0.109` and
  `corr(V, |r|) = +0.265` — and the default was flipped to `False` with the ablation recorded in
  the code comment (`ecomd/models/ecomd_v2.py:70-78`; top-level config
  `ecomd/models/ecomd.py:446` `v2_gauge_enforce: bool = False`; corroborated in
  `papers/proposal/ecomd_lab_truth_asset_coercive_stationarity_trigger_audit_2026-09-05.md`,
  "`v2_gauge_enforce` is false by default after the old gauge ablation reduced fidelity").

- **Parallel (stated as precedent, not proof).** There, an equivalence (common-shift orbit) was
  imposed on a learned representation; the target function class was not invariant under it; the
  enforcement destroyed function-relevant information and the repair was to *remove* the
  symmetry, not to quotient further. Lemmas A/B give this failure class its measure-theoretic
  form for the mechanism fiber: the fiber is not in the kernel of the deployment maps (A), and
  quotienting it away confines predictors to fiber-constant selections at the unchanged
  information floor (B) — destruction of consumer-relevant state, not relocation of redundancy.
- **Honest disanalogy.** The `gauge_enforce` event was an engineering finding about a
  representational choice inside one lineage (L1); the lemma pair is a statement about the
  recording contract (`F_exec`) and holds for any predictor family. The precedent motivates the
  word "injury"; the lemmas carry the weight.

**Empirical twin (preregistered, post-D0 only):** KT-M1's gauge-repair falsification — the
canonical-interleaving fix fails to restore `D_k` invariance on locked checkpoints — and S1a's
G1/G2 gates (byte-identical `F_exec` corpora with differing `state_hash` chains). If KT-M1 nulls
(all deployment maps < δ/10 on fiber pairs), the *interpretation* of A/B as describing the
trained systems' behavior dies (risk-register REFRAME), while the lemmas themselves — statements
about the recording map and the σ-algebra — stand.

---

## 4. The rewritten V4 remark (final, Lemma A/B-backed; replaces the draft at theory appendix Part II Section 4)

> **V4 (not a gauge; quotienting is not a repair).** *The mechanism fiber is not a gauge
> symmetry, and quotienting the hypothesis space is not a repair.* A gauge symmetry of a
> hypothesis space is a function-preserving equivalence: every observable, loss, and deployment
> map is constant on its orbits, so quotienting is harmless-by-design and removes genuine
> redundancy — the design principle of Quotient-Space Diffusion Models (ICLR 2026) for internal
> SE(3) orbits, and of the conservation-law weight structure in Neural Mechanics (ICLR 2020).
> The through-M mechanism fiber is provably not of this kind. **By Lemma A**, any quotient of
> raw-flow space that (i) keeps the `F_exec` training corpus recoverable (corpus-compatibility)
> and (ii) is nontrivial on the fiber — as any fiber-collapsing repair must be — necessarily
> breaks the factorization of a preregistered consumer: the identity deployment already
> separates fiber members through the risk consumer `C_risk` on every unrecorded magnitude
> direction (the Corollary 2 recession directions); the kernel-swap deployment separates
> never-drawn split directions through the next-draw probabilities `q_i/S` (Theorem 3, P3.2);
> the latency/truncation family separates clock directions (P3.3). The equivalence is a property
> of the recording mechanism, not a symmetry of the market: fiber members are physically
> different states (different submitted flows, different consumers, different outcomes under
> `D_swap` and `D_trunc`) that are informationally identical to the training loss. **By Lemma
> B**, the repair is also vacuous as an error-reduction device: every through-M predictor is
> tape-measurable regardless of hypothesis space (Lemma 0), so its best-case consumer error
> equals the Theorem 1 information floor exactly — for deterministic quotients, loss-side
> quotients, and stochastic/soft encoders alike, a fiber-measurable encoder being fiber-constant
> in distribution; the floor depends only on the recorded σ-algebra, the consumer, and the
> practitioner's prior — not on the representation. Quotienting therefore deletes physically
> market-relevant states without moving the floor: destruction, not relocation (Lemma B.5). The
> internal precedent is EcoMD v2's `gauge_enforce` ablation (2026-04-25): enforcing an invalid
> gauge on the pair representation erased `|s_i|`-dependent information required for volatility
> clustering — 33/33 gauged configurations locked at 4/11 stylized facts, recovered by disabling
> the enforcement — the same failure class in engineering form. What does survive as a genuine
> gauge is exactly the conceded residue: ownership relabeling of never-executed orders (the
> aggregation core of T1-P2(v)); on all consumer-relevant coordinates the fiber is
> function-preserving iff its ambiguous set is empty (Lemma A.4). The correct responses to fiber
> degeneracy are exposure characterization (Theorem 3) and information-side repair (raw-arm
> information, Proposition 1b) — never quotienting; the empirical twin is the KT-M1
> gauge-repair falsification. Within-fiber drift under SGD (T4) is a separate, conjecture-only
> question about optimizer selection among fiber-equivalent parameters and is not claimed
> (Soudry et al. 2017; The Loss Does Not See the Basis but Adam Does, 2026).

---

## 5. Hostile check (self-attack of the weakest steps, D-1 red-team style)

1. **"The consumer family is circular — you named consumers that separate."** The strongest
   attack. Response: `C_named` is exactly the preregistered T2/T3 consumer set (risk notional,
   latency notional, swap allocation, truncation), fixed in the theory appendix before this
   lemma; the lemma's content is the *engine fact* that each corpus-free direction class is read
   by at least one of them — falsifiable by S1a/KT-M1, and if KT-M1 nulls, the interpretation
   for trained systems dies (risk-register REFRAME, honestly inherited). Moreover A.2's primary
   separator (swap consumer) is forced by the engine formula `q_i/S` (`matching.py:592-597`) —
   any deployment that re-clears the level through the random kernel reads split members. The
   residual circularity is quarantined in the conceded relabeling core (A.4) and is stated, not
   hidden. An *actor-level* risk consumer `C^a_risk = Σ_i p_i q_i 1{α(i)=a}` would separate even
   the relabeling residue; it is deliberately not claimed (order-level consumer basis per A3).
2. **"Strict clocks are a modeling convenience."** The A.2 secondary separator uses
   `t_1 < … < t_n`. The primary swap separator does not use clocks at all; if a variant grammar
   admitted equal-clock never-drawn pairs, those pairs remain swap-separated. Clock freedom as a
   fiber direction class (U_clk) is also the one place my statement goes beyond the frozen Part
   II fiber table (which is quantity-focused); it is engine-verified (E5: maker arrival clocks
   appear in no `F_exec` field) but is flagged here and in Section 6 for the T2 owner to absorb.
3. **"Multi-round corpora shrink fibers to nothing."** Fibers shrink by intersection (T1 P7),
   but the surviving directions — never-marginal levels, never-drawn splits at levels never
   again touched, the aggressor residual that never again trades, aggregation — are precisely
   the never-recorded coordinates, all covered. The lemma is per-fiber conditional, matching
   Theorem 1's own conditional form; exhaustion rounds (V* = R*) make fibers trivial and the
   lemma silent there — consistent with the P4(iii) stratification. A worst-case corpus in which
   every level is eventually exhausted pins everything: then A.4's right-hand side is empty and
   the fiber *is* a relabeling gauge — the lemma correctly reports this (it is an iff), and the
   preregistration must scope claims to strata with nonempty ambiguous sets (already the T2
   framing).
4. **"Lemma 0's byte-identity is a house of cards."** If training reads anything beyond the
   corpus (engine access at augmentation time, order-level side channels, or — the dangerous
   one — the integrity hashes), Lemma 0 fails and B.1's forced measurability fails with it. This
   is the KT-G2(ii) static dual-hash loss audit (any loss term reading per-unit/per-maker fields
   or hashes falsifies the premise), plus the corpus-contract freeze (D1_01). The lemma pair
   inherits these as conditions, not assumptions.
5. **"Your floor is your reference measure."** Answered by B.4: the equality holds under every
   prior; the floor is the practitioner's own conditional uncertainty given the recording,
   quotient-invariant. What *is* `μ_R`-dependent is the numeric constant (Theorem 1(a)) — already
   conceded and contract-frozen.
6. **"B is trivial."** Yes — corollary-grade by design, and the D-2 triviality concession
   already accepts that the generic estimation content is not ours. B's non-trivial content is
   the quantifier closure (all hypothesis spaces, optimizers, seeds, stochastic encoders at
   once), B.5's representability failure, and the demonstration that the quotient class
   *contains* the minimizer (so the repair is exactly vacuous, neither harmful to the optimum
   nor helpful). Presented as the twin of A, never as an independent theorem.
7. **"Q = id refutes your route."** The task's original route phrasing ("any Q with (i) must
   identify fiber members") is false as literally stated; I repaired the quantifier structure in
   Section 0 (nontriviality as the repair's defining hypothesis) rather than inheriting the
   error. This is flagged as a wording correction, not a silent weakening — the lemma proves
   exactly what the gauge attack needs refuted: every *repair-shaped* quotient breaks a named
   consumer.
8. **"Soft quotients can hedge."** B.3 shows hedging (randomized output) strictly adds
   `(E[C|τ] − g)²` over the fiber mean; the conditional-law statement is the sharp form — the
   encoder cannot even *distributionally* distinguish fiber members, so no downstream readout
   can. The only escape in B.3 is `g ≡ E[C|τ]`, i.e. collapsing back to the deterministic fiber
   mean — which requires side information (the prior) the corpus does not contain; the floor
   value is τ-measurable but not corpus-computable without `μ_R`. (Stated as a knowledge
   remark; the formal floor statement does not depend on it.)
9. **"Deploy on the simulator's reconstruction, not the true z."** Lemma A's `C ∘ D` is a
   functional of the true raw flow (deployment on the market). If `D` is applied to the
   simulator's *implied* raw flow instead, exposure becomes a property of the trained model —
   that is exactly what KT-M1 measures empirically, and why the lemma pair is paired with it.
   The theorem/empirics split is stated in Section 3.
10. **Non-quadratic losses.** The floor statements are quadratic (the contract's metric); convex
    losses follow by the same conditioning plus Jensen (remark in B.3); non-convex losses are
    out of scope and not claimed.

**Weakest single step:** item 1 + item 4 — the lemma pair is exactly as strong as the frozen
corpus contract (`F_exec` payload projection, hashes and `order_accepted` excluded) and the
preregistered consumer family. Both are frozen decisions (D1_01; Part II), both are auditable
(KT-G2(ii) static audit; schema-verified payload fields), and both are inherited conditions
declared in the statuses.

---

## 6. Conditions carried into D-1 / D-3 wording (for the assembly step)

1. Lemma A/B are cited as: Lemma A = "not function-preserving" (conditions: `F_exec` payload
   projection excluding integrity hashes and `order_accepted`; preregistered `C_named`; per-fiber
   conditional on a `(q,t)`-nontrivial fiber); Lemma B = "no quotient repair / quotient injury"
   (deterministic, loss-side, and soft quotients; prior-universal floor).
2. V4 remark final text = Section 4 above (drop the theory appendix Part II Section 4 draft
   paragraph, keep the three-way distinction (a)/(b)/(c) which is untouched).
3. Add to the T2 package's fiber table (Part II Section 0): clock directions `U_clk` as an
   explicit ambiguous class (engine-verified E5), and the ownership-relabeling residue named as
   the conceded genuine-gauge core (consistent with T1 P2(v)'s aggregation directions).
4. Wordings that must never appear: "the fiber is a gauge symmetry" (false by A), "quotienting
   removes the degeneracy" (vacuous by B.2), "canonical interleaving restores kernel invariance"
   (refuted by A.2 + B.5, empirically by KT-M1).
5. Dependency: if KT-M1 nulls empirically, keep the lemmas (recording-map facts) but the V4
   remark's last empirical sentence must be rewritten as a boundary report (risk-register
   KT-M1 REFRAME row).
6. No external citations beyond the adjudicated D-2 names used here: Quotient-Space Diffusion
   Models (2026, ICLR Oral); Neural Mechanics (2020, ICLR); Soudry et al. (2017); The Loss Does
   Not See the Basis but Adam Does (2026). Everything else cited is in-repo.

---

## 7. Grounding file index (absolute paths)

- Frozen bundle (READ-ONLY, verified not mutated):
  `/Users/howardwang/Desktop/playground/ecophys/experiments/lab_asset_a2/a2_exit_20260905/schema_spec.json`;
  `.../fixture_fifo/{prestate.json,tape.jsonl}`;
  `.../fixture_random_unit_within_price/{prestate.json,tape.jsonl}`.
- Engine: `/Users/howardwang/Desktop/playground/ecophys/scripts/lab_asset/matching.py`
  (lines 248-357 submit/walk; 585-604 `_select_maker`; 606-625 `_apply_maker_fill`).
- Gauge precedent: `/Users/howardwang/Desktop/playground/ecophys/logs/2026-04-25.md` (Session 21);
  `/Users/howardwang/Desktop/playground/ecophys/ecomd/models/ecomd_v2.py` (lines 70-78, 240-252,
  298-310); `/Users/howardwang/Desktop/playground/ecophys/ecomd/models/ecomd.py` (line 446);
  `/Users/howardwang/Desktop/playground/ecophys/papers/proposal/ecomd_lab_truth_asset_coercive_stationarity_trigger_audit_2026-09-05.md`.
- Formalism and consumers:
  `/Users/howardwang/Desktop/playground/ecophys/papers/proposal/ecomd_reexploration_theory_appendix_2026-09-06.md`
  (Part II Sections 0-4: Lemma 0, Theorem 1, Prop 1b, Corollary 2, Theorem 3, V4 draft);
  killer-test spec:
  `/Users/howardwang/Desktop/playground/ecophys/papers/proposal/ecomd_reexploration_d1_killer_tests_and_ops_2026-09-06.md`
  (Section 2 KT-G3, Section 1 grounding);
  `/Users/howardwang/Desktop/playground/ecophys/papers/proposal/ecomd_reexploration_d2_evidence_map_2026-09-06.md`
  (Section 1.2 adjudicated names; Section 1.7 condition 4; Section 1.4 V4);
  `/Users/howardwang/Desktop/playground/ecophys/papers/proposal/ecomd_reexploration_experiment_plan_2026-09-06.md`
  (Sections 3, 6, 12);
  `/Users/howardwang/Desktop/playground/ecophys/research/discovery/decisions/pi_reexploration_d1_authorization_20260906.yaml`
  (D1_01 corpus freeze).
