---
note: >-
  D-1 theorem deliverable (KT-G2), produced 2026-09-06 under PI decision
  pi_reexploration_d1_authorization_20260906 (theorem/literature/schema work only; no GPU, no
  engine execution, no data access, no new literature). Companion to
  ecomd_reexploration_theory_appendix_2026-09-06.md Part II (Theorem 1 / attack in its section 6)
  and ecomd_reexploration_d1_killer_tests_and_ops_2026-09-06.md Part A section 2 (KT-G2).
  Status: D-1 working material, not a claimed result of the paper. Theorem 1 is used as proven in
  the theory appendix; the lemmas below inherit its status until D0 freeze.
---

# KT-G2 — Separation lemma: no kernel-blind bound tracks Theorem 1's floor

## 0. The attack being armored against (verbatim, theory appendix Part II section 6)

> "Theorem 1(b) is the law of total variance / Rao–Blackwell applied to a non-injective recording:
> for any `Z` and any consumer not co-measurable with the recording, the conditional variance
> floors every recorded-measurable predictor; Le Cam two-point arguments, censored-regression
> (Tobit) and missing-data bounds give the same. DPIOT (ICML 2022) already owns positive-dimensional
> fibers for learned simulators. The market mechanism only supplies a censoring pattern; T2 is an
> immediate consequence of fiber geometry plus classical estimation theory."

The existence-level content of this attack is **already conceded** (D-2 scoping; appendix section 6,
"Conceded"). Theorem 1 as proven gives the *exact* minimax value — `R^2 ||v_U||^2 / 12` (orthant/box
case) and `(R^2/3) * sum_{i in neverdrawn(l)} (v_i - v_bar_l)^2` (split case) — exact, tight,
tape-computable. So the live question KT-G2 must answer is not "can generic methods produce *some*
bound" but:

> **Can a kernel-independent, mechanism-independent method — one that knows only fiber-geometry
> data (box radius `R`, the consumer's coordinate norm `||v||`, dimension, or any coarsening-free
> functional of kernel-blind data) — reproduce or track these exact values across the kernel x
> granularity grid?**

The answer proven below is **no**, in a precise and (for the zero-floor cell) convention-free sense:
any kernel-blind bound that is a *valid* floor uniformly over the priority-kernel family is forced
to zero on data where the true kernel-specific floors are strictly positive and mutually separated
by factors of 3 to infinity. Conversely the naive generic bound `R||v||/sqrt(12)` (Lipschitz norm x
box geometry — the bound the attack claims "gives the same") is exact on fifo orthant cells and
**false as a certified lower bound** on random-unit split cells, where it exceeds the exact floor
by an infinite factor. There is no third option.

## 1. Setup (notation fixed to the theory appendix Part II section 0; engine-grounded)

**Engine semantics used (all statically verified; no engine was run):**

- **fifo kernel**: `_select_maker` returns `queue[0]` (front of the price-level queue) with no draw
  payload — `scripts/lab_asset/matching.py:585-590`; the fill is
  `fill = min(remaining, maker_qty)` — `matching.py:292-296` — so the fifo arm emits **one execution
  record per maker per incoming order** (`fixture_fifo/tape.jsonl` sequence 7: `quantity: 2`,
  `maker_remaining: 2`, no `allocation_draw`).
- **random_unit kernel**: `eligible_units = sum(quantity for _, _, quantity in queue)` over the
  remaining resting units at the price, `selected_unit = rng.randrange(eligible_units)` — a single
  draw uniform over all remaining units at the level (equivalently PPS-to-remaining-quantity);
  `fill = 1` unit per record — `matching.py:592-603, 295`. The draw payload
  `{price, eligible_units, selected_unit, maker_order_id}` is attached iff this rule is active —
  `matching.py:344-345` (`fixture_random_unit_within_price/tape.jsonl` sequences 7–8:
  `eligible_units: 4 -> 3`, `maker_remaining: 3 -> 2`, `quantity: 1` each).
- **Dual-hash contract**: `state_hash` binds the full book *with order identities in FIFO order*,
  order metadata/status/parentage, counters, and the engine RNG state — `scripts/lab_asset/schema.py:239-296`
  (levels as `[[oid, actor, qty], ...]`, line 263-267; `rng_state`, line 294). `aggregate_state_hash`
  binds **anonymous level quantities only** (`levels = [[price, sum(qty ...)], ...]`, lines 314-315)
  plus cash, inventory, `last_match_ts` — `schema.py:299-317`. The engine's own docstring (lines
  307-312) states the invariance used in Lemma G2-1 verbatim: "Under an exogenous, resource-slack
  request tape, this hash is equal after each completed request even when identity allocations
  differ."
- **Corpus contract**: `F_exec` = execution payloads + `allocation_draw` when present + pre/post
  BBO *prices* (frozen by PI decision D1_01). The hash fields are record-level audit metadata and
  are **not** part of the through-M training corpus; this distinction is load-bearing in the
  hostile check (H2).
- **Schema-level kernel fingerprint** (Lemma G2-4): `session_start` carries `allocation_rule`
  verbatim (`a2_exit_20260905/schema_spec.json`, `payload_fields.session_start`, lines 179-185);
  `allocation_draw?` is optional in the `execution` payload (ibid., lines 76-84) and occurs in the
  frozen fixtures only in the random-unit arm.

**Formal objects (theory appendix Part II section 0, taken as given):** one rationed level `l` at
price `p` with `n` resting orders (scaffold fixed: ids, arrival ranks, clocks); latent quantity
vector `q`; incoming size `V* in (0, R*)`, `R* = sum q_i`; tape `tau` under `(k, g, F_exec)`;
fiber `F_tau = {z' : T_{k,F}(z') = tau}`; reference measure `mu_R` (orthant case
`q_i ~ Unif[a_i, a_i + R]` independent on the never-executed coordinates; split case
`u = P_K eps`, `eps_i ~ Unif[-R, R]` i.i.d., `P_K = I - (1/m)11^T` on the `m` never-drawn orders of
the level); consumers `C(z) = v^T z` linear. Theorem 1 (a),(c) give the exact minimax floors

- `floor_fifo(tau, v, R) = (R^2/12) * ||v_U||^2`  (U = never-executed + hidden-residual coordinates),
- `floor_ru(tau, v, R) = (R^2/3) * sum_{i in ND(l)} (v_i - v_bar_l)^2`
  (ND(l) = never-drawn orders at the level; Theorem 1e(i): identically zero for the price-notional
  consumer `v_i = p` on `l`; Theorem 1e(ii): `(R^2/3) p^2 (m_in * m_out / m)` for the latency
  consumer `v_i = p * 1{clock_i <= W}`).

Both reference conventions use the same adversary budget symbol `R` = per-coordinate deviation
bound (`q_i - a_i in [0, R]` one-sided; `eps_i in [-R, R]` two-sided). Hostile check H5 analyzes
what changes under the alternative "width" convention.

## 2. Definitions — what "kernel-independent" means (the load-bearing formalization)

**Definition 1 (kernel-swap group).** Fix a prestate `P` and an exogenous request stream `s`
(resource-slack: no request is rejected for capacity reasons under either rule). The engine's
replay contract natively supports swapping only `allocation_rule` on identical `(P, s)` (killer-test
doc section 1, KT-A2 note). Write `tau_k(P, s)` for the resulting tape under rule `k`. A datum or
functional is **kernel-blind** (swap-invariant) if its value on `tau_k(P, s)` is the same for all
`k in {fifo, random_unit_within_price}` and all `(P, s)`.

This is the minimal formalization of "mechanism-independent method": a method that does not know
which kernel generated the recording must return the same answer on recordings that differ *only*
by the kernel. Anything weaker (a method allowed to read kernel-revealing fields) is not
mechanism-independent in the attack's own sense; anything stronger is not needed.

**Definition 2 (uniformly valid and c-informative bounds).** A bound `B >= 0` computed from
kernel-blind data (any of: `(R, ||v||, dim)`, geometry budgets, the aggregate tape, the scaffold —
all swap-invariant) is **uniformly valid** for consumer class `V` if for every cell
`(k, g in {po, pu})`, every `(P, s)`, every realized tape `tau` of that cell and every `v in V`:

  `B(data(P, s, tau), v, R) <= floor_k(tau, v, R)`  (Theorem 1's exact minimax value).

`B` is **c-informative** if additionally `B >= floor_k / c` pointwise on every cell. The attack's
claim ("a generic argument ... gives the same bound") asserts a 1-informative uniformly valid
kernel-blind bound exists.

The two requirements are jointly satisfiable on a family of cells iff
`sup_k floor_k / inf_k floor_k <= c` on every swap-equivalence class of data. The lemmas below
compute these ratios on engine-native instances.

## 3. Lemma G2-1 (aggregate-tape kernel invariance — the engine's own kernel-blind statistic)

**Statement.** Fix `(P, s)` exogenous and resource-slack. The sequence of aggregate states
(anonymous level totals, cash, inventory, `last_match_ts` — exactly the `aggregate_state_hash`
content, `schema.py:299-317`) evaluated **after each completed request** is identical under
`fifo` and `random_unit_within_price`. Consequently every kernel-blind functional — in particular
every `B(R, ||v||, dim)`-type bound, every Lipschitz x diameter budget, and every functional of
the aggregate tape or scaffold — takes equal values on `tau_fifo(P, s)` and `tau_ru(P, s)`.

**Proof.** Process the request stream inductively. Non-execution events (acceptances, cancels,
replaces, rejections) touch the aggregate state through the level totals of resting orders and
identical bookkeeping under both rules; their aggregate updates are rule-independent because they
do not allocate. An execution event at level `l` changes the aggregate state only by: (i) level
total at `l` decreases by the total filled at `l` during the current incoming order's walk, (ii)
cash/inventory transfer `p x fill`, (iii) `last_match_ts`. The total filled at each level is
determined by the incoming demand walking fixed price priorities (`V*` at the rationed level)
independent of how the kernel allocates *within* the level: the kernels differ only in the
maker-identity composition of the fill (front-of-queue vs drawn unit), which the anonymous
aggregate cannot see (`schema.py:314-315` sums `(oid, actor, qty)` triples to a level total).
Since the incoming quantity and the fixed book determine the per-level totals filled under both
rules, the post-request aggregate states coincide; induction over `s` closes the argument. (The
comparison is at completed-request boundaries, not event indices, because the arms emit different
numbers of execution records for the same total fill.) Engine confirmation, frozen bundle: the two
arms' executions at price 101 share `pre_aggregate_state_hash da930600...` and reach the identical
`post_aggregate_state_hash f0862093...` — `fixture_fifo/tape.jsonl` sequence 7 (one record,
quantity 2) equals `fixture_random_unit_within_price/tape.jsonl` sequence 8 (two unit records) —
exactly the completed-request alignment. QED

**Status: proven** (static engine semantics + frozen-fixture hash identity; the engine docstring
`schema.py:307-312` asserts the same property as a design contract). *Condition:* exogenous,
resource-slack request tape (the M0-lumpable DGP class the experiment plan already freezes for the
cube; endogenous request reaction to allocations is out of scope of T2's one-step setting anyway).

## 4. Lemma G2-2 (infinity separation: uniform validity forces zero)

**Statement.** There exist a scaffold with `n >= 2` orders at a rationed level, an incoming order
of size `V* = 1`, the price-notional consumer `C = p * sum_i q_i` on the level coordinates, and any
`R > 0`, such that `tau_fifo(P, s)` and `tau_ru(P, s)` arise from the *same* `(P, s)` and

  `floor_fifo = (n-1) p^2 R^2 / 12 > 0`,   `floor_ru = 0`.

Hence any kernel-blind, uniformly valid bound satisfies `B = 0` on the shared kernel-blind data,
while `sup_k floor_k / inf_k floor_k = infinity`: **no kernel-blind bound is c-informative for any
finite `c`** on this data — against the `(R, ||v||, dim)` class, against Lipschitz x diameter
budgets, and against every swap-invariant functional whatever.

**Proof.** (1) *fifo cell.* With `V* = 1` the front order `O_1` is selected
(`matching.py:589-590`) and filled `min(1, q_1) = 1` (`matching.py:292-296`); the tape records
`maker_remaining = q_1 - 1`, pinning `q_1` exactly. Orders `O_2..O_n` appear in no `F_exec` field:
execution payloads reference executed makers only, and the BBO quotes stay at the pool price on a
strict partial fill (theory appendix Part I section 0.3), revealing no depth. So
`U(tau) = {q_2, ..., q_n}` with the independent box reference `q_i ~ Unif[a_i, a_i + R]`, and
Theorem 1(a) gives `Var_{mu_R}(C | tau) = sum_{i=2}^n p^2 R^2/12 = (n-1)p^2R^2/12`; Theorem 1(c)
makes this the *exact* minimax floor over tape-measurable estimators.

(2) *random-unit cell.* The single draw is uniform over the `R*` eligible units
(`matching.py:592-593`); the tape records `eligible_units = R*` (pinning the level aggregate
`sum_i q_i` for the round) and the drawn order's `maker_remaining` (pinning its quantity). The
fiber on the never-drawn coordinates is the split kernel `{u : sum_{i in ND} u_i = 0}` with
reference `u = P_K eps`. The consumer `C = p * sum q_i` is constant on the fiber (the aggregate is
pinned), so `Var_{mu_R}(C | tau) = 0` and `floor_ru = 0` — Theorem 1e(i)'s exact-zero cell.

(3) *Separation.* Both tapes arise from the same `(P, s)`, so by Lemma G2-1 all kernel-blind data
coincide; a uniformly valid kernel-blind `B` must satisfy `B <= 0` (the ru cell) and `B >= 0`
(floors are variances), forcing `B = 0`; on the fifo cell the truth is `(n-1)p^2R^2/12 > 0`, so
the informativeness ratio `floor / B` is infinite. QED

**Status: proven** (conditional on Theorem 1 as given in the theory appendix; the multi-order
rationed level needed for the split cell is engine-semantic — the frozen 21–22-event fixtures
contain only a single-maker rationed level, so dynamic confirmation waits on the D1_03 enrichment
and the S1a gates; see hostile check H6).

## 5. Lemma G2-3 (same-data >= 2x separation with a non-constant consumer; explicit constants)

The infinity cell uses a constant-on-level consumer; a referee will call that degenerate. This
lemma delivers the plan's factor with the latency consumer, on the *same prestate and request
stream* for both arms.

**Statement.** Same swap setting as G2-2 (`V* = 1`; `m = n - 1` never-touched orders at the level,
identical under both arms — fifo's never-executed set and ru's never-drawn set coincide when the
draw realization is the front order). Consumer `C_lat^W = p * sum_i 1{clock_i <= W} q_i` with
`m_in >= 1` never-touched orders inside and `m_out = m - m_in >= 1` outside the window. Then

  `floor_fifo = (R^2/12) p^2 m_in`,   `floor_ru = (R^2/3) p^2 (m_in m_out / m)`
  (Theorem 1e(ii)), and the ratio is

  `rho = floor_ru / floor_fifo = 4 m_out / m = 4 (1 - m_in/m)`.

(i) If `m_out >= m_in` then `rho >= 2`. (ii) `sup rho = 4` (attained in the limit `m_in = 1`,
`m -> infinity`), so **no kernel-blind uniformly valid bound is c-informative for any `c < 4`**
within the latency family; the constant 4 is sharp for this family. (iii) *Concrete instance* —
`n = 5` orders, window covering exactly `{O_1, O_2}`, `V* = 1`, ru draw realization `O_1` (a
positive-probability tape realization): `floor_fifo = R^2 p^2 / 12` (U = `{O_2..O_5}`,
`v_U = (p,0,0,0)`), `floor_ru = (R^2/3)(3/4)p^2 = R^2 p^2 / 4` (never-drawn `{O_2..O_5}`,
`v = (p,0,0,0)`, `v_bar = p/4`) — **ratio exactly 3** on identical `(P, s, v, R)` and identical
aggregate tape; the ambiguous-set *dimensions* differ by exactly one (4 vs 3), an intrinsic
consequence of the aggregate-pinning hyperplane `eligible_units` adds. (iv) *Plan-wording
corollary (equal second-moment budget).* The KT-G2 spec phrase "equal reference-measure geometry
budget (equal second moment of pairwise separation)" is realized across instances: fifo with
`m_f = 4(m_r - 1)` never-executed coordinates matches the ru split budget, both
`E||Z - Z'||^2 = 2R^2/3 * (m_r - 1)`; with `m_r = 2`, `m_f = 4`, `||v|| = p` on both, the floors
are `R^2 p^2/12` vs `R^2 p^2/6` — **ratio exactly 2** at equal `R`, equal `||v||`, equal budget
(dims 4 vs 1; the swap-pair version (iii) is the stronger same-data statement).

**Proof.** Theorem 1e(ii) supplies both floors. The two-group variance identity gives
`sum_{i in ND}(v_i - v_bar)^2 = p^2 m_in m_out / m` for the indicator-weighted `v`. Then
`rho = [(R^2/3) p^2 m_in m_out/m] / [(R^2/12) p^2 m_in] = 4 m_out/m` (the `R^2/3` vs `R^2/12`
ratio is the reference-width constant; see H5). More generally, for arbitrary `v` on the common
never-touched set with `S = ||v||^2`, `T = sum v_i`: `rho = 4 (1 - T^2/(mS)) in [0, 4)` by
Cauchy–Schwarz, with `rho -> 0` as `v -> constant` (the G2-2 cell) and `rho -> 4` for
single-in-window consumers on large levels. For (iii), direct computation:
`floor_fifo` uses `U = {O_2..O_5}` (`O_1` pinned as the executed front order, its `v`-coordinate
inactive); `floor_ru` uses the same never-touched set as never-drawn (draw realization `O_1`),
`sum(v_i - v_bar)^2 = (p - p/4)^2 + 3 (p/4)^2 = 3p^2/4`. For (iv), pairwise second moments:
fifo `E||Z - Z'||^2 = 2 sum Var = 2 m_f R^2/12`; ru split
`E||u - u'||^2 = 2 tr((R^2/3) P_K) = (2R^2/3)(m_r - 1)`; equality at `m_f = 4(m_r - 1)`. QED

**Status: proven_with_conditions.** Conditions: (a) Theorem 1 as given; (b) the frozen
reference-measure convention of the theory appendix (`eps ~ Unif[-R, R]`, i.e., per-coordinate
deviation bound `|eps_i| <= R`); under the alternative *width*-matched convention the factor
`4 m_out/m` becomes `m_out/m <= 1` — see hostile check H5 for why the infinity separation of G2-2
is unaffected but this lemma's factor is convention-coupled; (c) ru floors are conditional on the
realized tape (never-drawn set depends on the draw); instance (iii) uses realization `O_1`
(probability `q_1/R* > 0`), and every other realization gives `rho in {3, 4}` (never-drawn sets
containing both `O_1, O_2` give `m_in = 2, m_out = 2`, `rho = 4`).

## 6. Lemma G2-4 (grammar–kernel equivalence: resolving "tape-aware but kernel-blind")

The brief flags the dangerous question: Theorem 1e says the tape pins `U(tau)` and hence the
floor — is that kernel-dependent or not? If the *tape* determines the floor, hasn't the attacker
won ("my generic method reads the tape")? Answer: the `F_exec` tape determines the floor **because
and only because its grammar carries a kernel fingerprint**; no kernel-blind coarsening of it
does. There is no circularity — there is a clean dichotomy.

**Statement.** (i) The `F_exec` tape determines the allocation rule: (a)
`session_start.payload.allocation_rule` records it verbatim (`schema_spec.json` lines 179-185;
both frozen fixtures); (b) `allocation_draw` appears in an execution payload iff the rule is
random-unit (`matching.py:344-345`; fixtures: 2 occurrences in the ru tape, 0 in the fifo tape);
(c) absent those fields, the record granularity still separates them (per-unit `quantity = 1`
records vs per-maker `min(remaining, maker_qty)` records; `matching.py:292-296`). (ii) The set of
drawn / executed order ids — hence `U(tau)` and `ND(l)` — is a function of the kernel-revealing
part of the tape only; the aggregate tape is anonymous (`schema.py:314-315`) and cannot recover
it. (iii) Therefore Theorem 1e's tape-computability is a **kernel-aware** computation, and the
separation of G2-2/G2-3 stands: kernel-blind data does not determine the floor within any
constant factor; kernel-aware data (the corpus grammar) determines it exactly. T2's practical
value (Defense 1: a practitioner evaluates the floor from the tape in hand) and T2's theoretical
value (Defense 4, this lemma: that evaluation is irreducibly mechanism-specific) are the two
halves of one statement, not a contradiction.

**Proof.** (i) is the cited static inspection. (ii) Drawn ids occur only inside
`execution`/`allocation_draw` payloads; the aggregate levels are `(price, total)` pairs. (iii) is
G2-2/G2-3 plus (i)-(ii). QED

**Status: proven** (schema-static; no execution needed).

## 7. Hostile check — attacking the lemma the way the D-1 red team would

**H1 — "So the generic method reports 0; you claim victory over a triviality?"** The honest shape
of the result is a dichotomy, and it should be stated as one. Any kernel-blind bound is either
(a) positive somewhere, hence *false as a certified lower bound* on every split cell where the
exact floor is smaller — the naive `R||v||/sqrt(12)` (the bound the attack says "gives the same")
over-predicts the ru split floor by an infinite factor for the price-notional consumer, i.e., it
is not a bound there — or (b) identically zero wherever a zero-floor cell shares its kernel-blind
data, hence uninformative by an infinite factor on the fifo cell of the same data (G2-2). Validity
x informativeness is jointly impossible for any finite factor. That *is* the content: kernel-blind
risk certification is vacuous; to certify a nonzero floor you must consume the kernel's censoring
geometry. *Discharged.*

**H2 — the cleverest generic bound: tape-aware but kernel-blind.** Grant the analyst the full
record chain *including* `post_aggregate_state_hash` values (hence the post-trade level totals by
brute-force dictionary over plausible states — or more fairly, grant the completed-request
aggregate states as data), plus the scaffold, `R`, `v`. Require only swap-invariance. This is the
strongest kernel-blind procedure I can construct, and it *still* fails, in both directions:

(a) *On the fifo cell* the aggregate chain pins the post-trade level total `T = R* - V*`. The
analyst conditions their kernel-blind reference on it and computes a sum-constrained conditional
variance ~ `(R^2/12) sum(v_i - v_bar)^2` (exactly, with a Gaussian reference; up to Irwin–Hall
corrections for the box). But the *true* fifo floor is `(R^2/12) ||v_U||^2`, because the through-M
corpus `F_exec` contains **no** aggregate depth field — the trained simulator cannot condition on
what its corpus omits. For the price-notional consumer the analyst certifies zero risk where the
truth is `(n-1)p^2R^2/12`: wrong (uninformative) by an infinite factor. For general `v` they
understate by `1/(1 - T^2/(mS)) in [1, infinity)`. This is the corpus-visibility mismatch: hash
chains are audit metadata, not training data (D1_01 froze exactly this boundary).

(b) *On the ru split cell* the corpus itself pins the aggregate (`eligible_units`) and the
drawn orders (`maker_remaining`), so aggregate conditioning is *correct* there — but no single
kernel-blind reference width is correct on both cells: width-`R` thinking under-predicts the split
floor by the factor 4 (split deviations are two-sided, `eps in [-R, R]`); width-`2R` thinking
yields `(R^2/3)||v_U||^2 > floor_fifo` on the fifo orthant — **not a valid lower bound** there.
A "mixed" analyst who conditions on the aggregate only when it helps must decide *when the corpus
pins the aggregate* — which is exactly the kernel question (Lemma G2-4). *Discharged* — and it
sharpens the lemma: even hash-augmented kernel-blind procedures fail, in opposite directions on
the two arms of the same `(P, s)`.

**H3 — "Let the bound branch on the reference-measure second moments (the 'geometry budget');
those differ between orthant and split, so I branch and output the exact floor per branch."**
This concedes the attack. The reference measure is a functional of the *fiber*; the fiber is
kernel-determined (same `(P, s)`, different rule, different fiber — G2-1/G2-2 exhibit it). A
procedure that reads "the reference covariance of the cell" reads swap-*variant* data and is
kernel-aware by the back door — it is Theorem 1 with extra steps, not a mechanism-independent
method. The separation lemma is deliberately stated against swap-invariant inputs so that this
move is visible as a scope concession rather than a defeat. *Discharged by scoping.*

**H4 — "Your infinity cell is degenerate (constant-on-level consumer)."** G2-3(iii) gives the
same-data ratio 3 with a non-constant (latency) consumer, and the family sweeps `rho in [0, 4)`,
so no monotone kernel-blind correction exists even within the latency family (the ratio changes
*sign of gap direction* across the family: `rho < 1` when `m_out < m_in/3`). *Discharged.*

**H5 — convention fragility (the weakest step after H6, stated plainly).** The factor `4` in
`rho = 4 m_out / m` is the ratio of reference constants `R^2/3` (split, `eps ~ Unif[-R, R]`,
two-sided deviation budget `|eps_i| <= R`) to `R^2/12` (orthant, `q_i - a_i in [0, R]`, one-sided).
Under a *width*-matched convention (`eps ~ Unif[-R/2, R/2]`), `rho` becomes `m_out/m <= 1`: the ru
floor is then always the *smaller* one and the >= 2x gap of G2-3 inverts — the separation survives
(as `rho in [0,1)`, still kernel-dependent, still zero for constant `v`) but the headline number
"3" does not. The theory appendix froze the deviation-budget reading (both references use
per-coordinate deviation magnitude `<= R`), under which G2-3's constants hold as stated.
Recommendation to the D-1 wording freeze: state both reference conventions explicitly as
per-coordinate deviation bounds so no referee can read the factor 4 as an inconsistency, and lead
the armor with G2-2 (convention-robust: zero stays zero and the fifo floor stays positive under
any positive-width rescaling) with G2-3 as the finite-gap illustration under the frozen
convention. *Concession recorded; lemma survives with labeled conditions.*

**H6 — fixture grounding.** The frozen 21–22-event fixtures contain only a *single-maker* rationed
level (O00000003, quantity 4 at price 101), so the multi-order split cells of G2-2/G2-3 are proven
at the semantics level (code paths cited) and confirmed statically by the draw-field behavior
(`eligible_units 4 -> 3`, `maker_remaining 3 -> 2` across sequences 7–8), not yet dynamically on a
frozen multi-order fixture. This is exactly the D1_03 enrichment + S1a gate dependency already
recorded in the plan. If the enriched engine ever records a field that pins the never-drawn split
(a per-never-drawn-order quantity), G2-2's ru floor would cease to be zero and the separation
would need restating — but that event also falsifies Theorem 1e itself (S1a STOP class), so the
lemma and the theorem stand or fall together. *Dependency flagged, not a weakness of the proof.*

**H7 — "Your definition of 'mechanism-independent' (swap-invariance) is a choice; the attack never
meant that."** This is the genuinely weakest step and I state it without disguise. Any formal
reading of "a generic argument that does not use the mechanism" must at least be invariant under
relabeling the mechanism while holding its inputs fixed; swap-invariance is the minimal such
requirement, and the engine's replay contract makes the swap a native operation (only
`allocation_rule` differs). If the referee instead claims the attacker is *granted the kernel-
dependent fiber and reference measure*, then yes — the floor is a two-line Rao–Blackwell
computation, exactly as Theorem 1 presents it; that existence-level content was conceded at D-2
and is not what T2 claims. The separation lemma is the precise boundary between those two
readings: fiber geometry is not mechanism-independent data. *Defended; the boundary is the
result.*

## 8. Summary table

| Statement | Content | Status |
|---|---|---|
| G2-1 | aggregate tape (engine's own `aggregate_state_hash` content) is swap-invariant; all kernel-blind data coincide on swap pairs | **proven** (code + frozen-fixture hash identity) |
| G2-2 | price-notional cell: `floor_fifo > 0`, `floor_ru = 0` on identical kernel-blind data; validity forces `B = 0`; no finite `c` | **proven** (given Theorem 1) |
| G2-3 | latency cell: same-data ratio `rho = 4 m_out/m in [0,4)`; instance ratio exactly 3; `c < 4` impossible within the family; equal-budget cross-instance ratio exactly 2 | **proven_with_conditions** (frozen reference-width convention; draw-realization conditioning) |
| G2-4 | `F_exec` grammar carries a kernel fingerprint; Theorem 1e's tape-computability is kernel-aware; no conflict with the separation | **proven** (schema-static) |

## 9. Consequences for D-1 wording (T2 armor, risk register)

1. **The KT-G2 REFRAME row does not fire.** The separation is provable; T2 keeps lead status with
   a fourth defense added: *kernel-blind certification is vacuous — any uniformly valid
   kernel-independent floor bound is identically zero on data where kernel-specific floors are
   positive and separated by 3x to infinity; the exact constants are computable only through the
   mechanism's censoring geometry.*
2. Theorem 1e's tape-computability (Defense 1) must be worded as **kernel-aware**: the corpus
   grammar *is* the kernel fingerprint (G2-4). One sentence at the wording freeze prevents a
   referee from manufacturing a circularity out of Defenses 1 and 4.
3. Lead G2-2 (convention-free), illustrate with G2-3 under the frozen reference convention, and
   state both conventions as per-coordinate deviation budgets (H5).
4. The hostile-T0 contribution of KT-G2 (killer-test doc section 5 table, P(kill) = 0.15) can now
   be revised downward at D-1 calibration: the separation-lemma failure mode is closed at theory
   level, with residual probability mass only on the S1a dynamic-confirmation branch (H6), which
   is shared with Theorem 1 itself.

*Grounding files (absolute):* `/Users/howardwang/Desktop/playground/ecophys/scripts/lab_asset/matching.py`
(lines 285-296, 344-345, 585-604); `/Users/howardwang/Desktop/playground/ecophys/scripts/lab_asset/schema.py`
(lines 228-317); `/Users/howardwang/Desktop/playground/ecophys/experiments/lab_asset_a2/a2_exit_20260905/schema_spec.json`
(lines 76-84, 179-185); `.../fixture_fifo/tape.jsonl` (sequence 7); `.../fixture_random_unit_within_price/tape.jsonl`
(sequences 7-8); theory appendix Part II; killer-test doc Part A section 2 (KT-G2); experiment plan
section 12 (KT-G2 REFRAME row — not triggered). No new external references were introduced; all
prior-art anchors invoked (Diaconis–Sturmfels 1998; DPIOT ICML 2022; Perturb-Argmax
arXiv:2406.02180; the Tobit/Le Cam/Rao–Blackwell lineage named inside the attack itself) are
already adjudicated in the D-2 evidence map or quoted verbatim from the theory appendix's hostile
section.
