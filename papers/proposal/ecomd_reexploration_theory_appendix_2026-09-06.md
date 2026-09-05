---
note: >-
  Verbatim output of a planning-workflow agent (2026-09-06), grounded in the frozen lab-asset-v3
  artifacts and the D-2 evidence map. Theorem status: propositions/proofs below are D-1 working
  material, NOT claimed results of the paper. Companion to
  ecomd_reexploration_experiment_plan_2026-09-06.md.
---

# Theory appendix (D-1 working material): T1 and T2/T3 packages

## Part I — T1 theorem package

# T1 Theorem Package: One-Step Uniform-Price Clearing Fibers (GAMMA lead)

Screening-legal work: literature/schema/theorem only. No GPU, no simulation execution, no data access. All semantics grounded in-repo:
`papers/proposal/ecomd_random_unit_priority_thesis_v2_2026-08-27.md`, `experiments/lab_asset_a2/a2_exit_20260905/schema_spec.json`, both fixtures (`fixture_fifo/tape.jsonl`, `fixture_random_unit_within_price/tape.jsonl`), `fixture_*/prestate.json`.

## 0. Grounding facts verified from the repo (these constrain the model)

1. **Draw semantics** (thesis v2, "Exact treatment"): random arm draws **uniformly without replacement from all remaining resting units at that price**; an order with quantity q has draw probability proportional to its remaining q; the semantic draw is recorded. Schema name: `random_unit_within_price`. Price priority is arm-invariant; the kernel acts **within the marginal price's pool**. This is exactly sequential PPS-to-remaining = uniform-over-remaining-units, so allocations are multivariate hypergeometric over orders (fact used in P2).
2. **Tape grammar** (fixtures): random arm emits **one execution record per incoming unit**, each with `execution` (execution_id, aggressor actor/order, `maker_actor`, `maker_order_id`, `maker_remaining` after the fill, price, quantity=1) plus `allocation_draw` = {`eligible_units` (pool size at the price before the draw), `maker_order_id`, `selected_unit`}. FIFO arm emits **one record per maker per incoming order** (`quantity: 2` in one record, no draw payload). Pre/post best bid/ask fields are **prices only** (no sizes). Arrival records (`order_accepted`) carry `resting_quantity` — an ambient enrichment handled in P5, not in the core rungs.
3. **Post-trade best price reveals the exhaustion event**: after a strict partial fill the best ask stays at the pool price; after pool exhaustion it jumps. Price-only quotes therefore stratify rounds by exhaustion at every rung (used in P4's caveat and the S3 design).

## 1. Model contract M1 (Task 1)

**Scaffold (fixed, observed structurally).** One instrument; tick lattice fixed. Ask side has n resting orders; order i has price pi, arrival rank tau_i within its price, quantity q_i in N (units). Which orders exist at which prices/ranks is fixed; the **latent is the quantity vector and incoming size**, linearly parameterized: (Q, q) = B z, B in R^{(1+n) x d} full column rank (base case B = I, z = (Q, q) in R^{1+n}; general B pulls every fiber back through ker B, adding nullity(B) to every dimension below).

**One clearing round.** Incoming buy of integer size Q walks the book by price priority: every level with cumulative supply below Q clears fully; the **marginal level p\*** has pool P = {orders at p\*}, pool size R\* = sum_{i in P} q_i, and residual demand V\* = Q - S_< in [0, R\*], where S_< is supply at strictly better levels. Levels deeper than p\* (set D) are untouched. Interior regime: 0 < V\* < R\* (strict partial fill at the margin); V\* = R\* is the exhaustion boundary (P4).

**Kernels.** k allocates V\* within P:
- `fifo`: prefix fill by arrival rank; let j\* = index of the (partially) filled pool order given V\*.
- `pro_rata`: c_i = V\* q_i / R\* (continuum; unit-lattice rounding in Remark R3).
- `random_unit` (= `random_unit_within_price`): V\* sequential draws, each uniform over the R\* - t remaining pool units; P(order i at step t) = (q_i - c_i^{(t)})/(R\* - t).

**Tape rungs g** (the ladder coarsens ONLY the execution/allocation record; ambient fields — pre/post best prices — held fixed across rungs, so the ladder is a pure recording treatment):
- `agg`: aggregate prints, one per price: {(p, V_p)}; at p\*, V\* — a kernel-independent statistic.
- `po` (per-order): one fill record per filled order: (order id, price, c_i). Zero-fill orders emit nothing.
- `pu` (per-unit): one record per drawn unit in draw order (aggressor unit, maker order id), optionally with engine annotations (eligible_units, maker_remaining, selected_unit) — the annotated variant is analyzed in P5.

**Fiber (identification object).** L_{k,g}(z) = law of the rung-g tape of the round under kernel k (deterministic kernels give point masses). F_{k,g}(z0) = {z in interior regime : L_{k,g}(z) = L_{k,g}(z0)}. **Training-loss bridge (T2 "exactly zero")**: any training loss of the form E_{y~L(z)}[l(y; theta)] is constant on fibers by definition; the scientific content is that the fibers are positive-dimensional in specific directions and that deployment maps vary along them (P6). Distinguish throughout: **law-level fibers** (what a training distribution identifies) vs **realized-tape fibers** (what one round's record identifies; P5).

## 2. Propositions (Task 2)

### P0 (Regime lemma — recorded statistics are linear / rational-homogeneous / hypergeometric)
On the interior of a fixed combinatorial regime (fixed marginal level, fixed V\* in (0, R\*), fixed j\*), in the base parameterization: the `fifo` recorded statistics are affine-linear in (Q, q); the `pro_rata` recorded fill vector is homogeneous of degree 1 and degree-0 in q up to scale (q -> q/R\* proportions); the `random_unit` count law is multivariate hypergeometric and the sequence law is its uniform-permutation lift. Proof: on the interior, min/prefix operations are linear; pro-rata is a ratio of linear forms; sequential uniform-without-replacement over units aggregated by order has P(c) = prod_i C(q_i, c_i)/C(R\*, V\*) and P(omega) = prod_i (q_i)_{c_i}/(R\*)_{V\*} (falling factorials), since a draw of order i at step t has probability (q_i - c_i^{(t)})/(R\* - t), the same as revealing a uniformly chosen remaining unit. Consequence: general-B fibers are preimages under B of the quantity-space fibers below; all dimensions gain nullity(B).

### P1 (Deterministic kernels: fiber = recorded-map preimage + uncleared-excess directions; never a point)
**Statement.** For k in {fifo, pro_rata}, on the interior regime, in quantity space (d = 1 + b + m\* + |D|, with b = fully-cleared better-priced orders, m\* = |P|):
(i) `agg` (both kernels): the recorded statistics are the better-level sums S_p and V\*; all kernel-independent. dim F = sum_{p<p\*}(m_p - 1) + m\* + |D| (within-better-level splits, whole pool, deeper levels all free; Q pinned via V\* + S_<).
(ii) `fifo, po`: recorded linear map L pins every fully-filled order individually and one linear combination at the marginal order (c_{j\*} = V\* - sum_{i<j\*} q_i); free directions = the marginal order's **hidden depth** (q_{j\*} - c_{j\*} > 0), the m\* - j\* pool orders beyond j\*, and D. **dim F = 1 + (m\* - j\*) + |D|**. The fiber is exactly {z : L(Bz) = L(Bz0)} — the preimage of the recorded linear map on the cleared portion — plus all uncleared-excess directions; the recorded map has trivial kernel on the binding-side coordinates it touches.
(iii) `pro_rata, po`: c determines pool proportions and V\* determines nothing about pool scale; the pool fiber is the **scale ray** {lambda q_P : lambda >= V\*/R\*} (check: q' = lambda q_P gives c' = c for every lambda). **dim F = 1 + |D|**. Note: the pro-rata fiber is a multiplicative ray, **not** an affine fiber of any linear statistic — relevant to the reduction check. Note also fifo and pro-rata fibers are **incomparable** (prefix+combination vs proportions), so the two deterministic sub-cells must both appear in the grid.
(iv) `pu` = `po` for deterministic kernels: the unit-to-order sequence is a deterministic function of the fill vector (fixtures confirm: FIFO emits one multi-unit record; a per-unit relabeling adds no information).
(v) **No deterministic (k, g) identifies z**: every cell has dim >= 1 (hidden depth / scale ray / deeper directions); in the exhaustion boundary V\* = R\* the pool is fully recorded at `po`/`pu` for every kernel (dim = |D| + incoming-excess ray), so the dichotomy content lives on strict partial fills (P4).
Proof sketches: (i)-(ii) explicit rank count of L on the interior; (iii) homogeneity computation above; (iv) determinism; (v) the exhibited free directions never enter any recorded statistic.

### P2 (random_unit + per-unit tape: likelihood-equivalence class; strict shrinkage; surviving symmetries)
**(i) Law.** P(omega | q_P) = prod_i (q_i)_{c_i(omega)} / (R\*)_{V\*}; counts c ~ MV-Hypergeometric(q_P, V\*); sequence given counts is uniform over orderings (hence ancillary).
**(ii) Saturation (P2b).** The factorization P(omega|q) = P(c|q) x (uniform ordering given c) makes the count vector c **sufficient** for q from the per-unit tape, and the count marginal recovers the per-order law, so **F_{ru,po} = F_{ru,pu}** exactly. The granularity ladder has exactly two informative rungs: {agg} vs {po, pu}.
**(iii) Identification (the sharpened core).** Let rho_i = P(first draw = order i) = q_i/R\*, gamma_i = P(first two draws both order i) = q_i(q_i - 1)/(R\*(R\*-1)). Then, for V\* >= 2 and m\* >= 2,
**q_i = (1 - gamma_i/rho_i) / (1 - gamma_i/rho_i^2)** —
a closed-form identification (algebra: gamma/rho = (q_i-1)/(R\*-1), gamma/rho^2 = R\*(q_i-1)/(q_i(R\*-1)); numerator and denominator both reduce so the ratio is exactly q_i; the q_i = 1 edge gives gamma_i = 0 and the formula returns 1). Hence the law-level fiber on pool coordinates is a **point** for V\* >= 2. For **V\* = 1** (single-unit fills, unannotated rung) the law is categorical with P(c = e_i) = q_i/R\*: scale-invariant, so the pool fiber is the **scale ray** {lambda q_P} — proportions identified, scale not. Per-order-rung injectivity at V\* >= 2 also follows from adjacent-count ratios: P(c)/P(c + e_k - e_l) with c_k = 0, c_l = 1 gives q_k/q_l (proportions), and the ratio at c_k = 2 gives (q_k - 1)/(2 q_l) (one absolute value propagates through the proportions); degenerate witnesses fall back to support maxima (q_i < V\* read off max c_i).
**(iv) Strict shrinkage.** On pool coordinates: {q_P} (V\* >= 2) is strictly inside F_{fifo,po} (free hidden depth and beyond-j\* directions, dim 1 + m\* - j\*) and incomparable-with-but-strictly-smaller-than F_{pr,po}'s ray (a point is strictly smaller than a ray; note the two deterministic kernels' fibers are mutually incomparable, so "strictly shrinks" is stated per deterministic kernel as a dimension drop to zero on pool coordinates).
**(v) Surviving symmetries — why it is never a point on full z.** (a) Deeper levels D: never traded, free in every cell (dim |D|). (b) Under quantity aggregation (the T1 setting: agent-level flow behind order-level queue entries), all within-order co-ownership splits are exchangeable-agent directions invisible to every rung: dim sum_i (A_i - 1). (c) At the **realized-tape** level (P5), never-drawn pool orders are identified only through the pool-size residual, so their splits survive (dim = #never-drawn - 1 whenever >= 2 pool orders go undrawn). (d) General B adds ker B. The modeling contract: z is the flow-level vector (includes deeper levels and per-agent splits), so dim F_{ru,pu} >= 1 always; the **honest scoped claim** is point identification on executed-pool coordinates only. If a reviewer's model takes z = pool quantities alone with no aggregation, the fiber IS a point at V\* >= 2 — the paper must not overclaim "never a point" without the aggregation structure in the model.

### P3 (random_unit + aggregate tape: collapse; kernel anonymity)
At `agg` the recorded statistics (level prints; V\* at p\*) are deterministic functions of (Q, q) and are **kernel-independent**: the kernel only permutes allocation within the pool, and the aggregate print records only V\*. Hence L_{ru,agg}(z) = delta_{(p\*, V\*)} = L_{k,agg}(z) for every kernel k, and **F_{ru,agg} = F_{k,agg}**: the draw marginalizes out — indeed the entire kernel anonymizes at aggregate granularity. This is stronger than "randomness marginalizes": it is a cross-kernel statement (see reduction check), and it holds for deterministic kernel pairs too.

### P4 (Granularity dichotomy — summary grid; interaction; boundary stratification)
Pool-coordinate fiber dimensions (quantity space; deeper/aggregation directions free everywhere):

| k \ g | agg | po | pu |
|---|---|---|---|
| fifo | m\* | 1 + (m\* - j\*) | = po |
| pro_rata | m\* | 1 (scale ray) | = po |
| random_unit | m\* | 0 (V\*>=2); 1 (V\*=1) | = po |

(i) Neither factor alone identifies: kernel randomness alone (agg rung) collapses to the deterministic fiber (P3); granularity alone (deterministic kernels, any rung) leaves dim >= 1 (P1v). (ii) The unique identifying cell is (random_unit, po-or-finer) with V\* >= 2 — an interaction of kernel randomness and tape granularity, exactly the T1 lead. (iii) **Boundary caveat**: on exhaustion rounds (V\* = R\*) every kernel identifies the pool at po/pu (trivial cell); the dichotomy is a statement about **strict partial-fill rounds**; the price-only post-quote reveals the stratum at every rung, so stratification is preregisterable and costless. (iv) Q >= 2 caveat: single-unit fills (V\* = 1) degrade identification to proportions (P2iii); the engine's eligible_units annotation repairs it (P5a).

### P5 (Engine-grammar enrichment corollary — lab-asset-v3)
(a) Adding `eligible_units` (pool size R\* at each draw) to the per-unit record adds the statistic R\*: the V\* = 1 scale ray collapses to a point for all V\* >= 1. `maker_remaining` and `selected_unit` are functions of (q, c-path) and of uniform within-order unit labels respectively — the latter are the literal exchangeable-unit symmetries and carry no quantity information. Law-level fibers are otherwise unchanged. (b) Realized-tape inference: each drawn order's quantity is read off pathwise; never-drawn pool orders are pinned only in aggregate (their sum = R\* minus drawn quantities), so **within-pool splits among never-drawn orders are the surviving realized-tape symmetry**. (c) Ambient arrival records (`order_accepted` with `resting_quantity`) would observe declared quantities directly; under that full grammar the fiber migrates to hidden-vs-declared quantity and co-ownership directions — the same aggregation symmetries one level down. The core theorems are stated for the clearing-record rungs with the scaffold conditioned; the paper must say which grammar each claim uses.

### P6 (Exposure — T3 hook, one-step law-level table)
For deployment map D and training cell (k, g), the exposed set is E_D = {v in T_z F_{k,g} : d/dt|_0 L_{D(k,g)}(z + t v) != 0}, i.e., tangent directions silent to training but detected by deployment. **Kernel swap** fifo -> random_unit at po exposes the hidden-depth and beyond-j\* directions (dim 1 + m\* - j\*); random_unit -> fifo exposes **nothing** (the ru fiber is a pool point; remaining free directions — deeper levels — are silent under both kernels): an asymmetric, market-native exposure structure. At agg, no swap exposes anything (P3). **Message-tail truncation** at pu coarsens to a po-equivalent record, so by data processing it exposes nothing at law level; the nontrivial truncation exposure is **stateful** (consumer-context truncation meeting deeper-book state) and is delegated to the two-step lemma below. **Identity** is the null control (exposure 0 by construction; T2's mechanism-attributability check — divergence vanishes when M_k is removed — uses it). This one-step table is the clean formal core behind T3; the PDE-absent, market-native part is precisely the kernel-swap column.

### P7 (Two-step lemma — provable within timeline; stated for the paper)
Let the book update deterministically (fills decrement, uncleared rests) and let F^{(2)} be the fiber of the two-round tape law. On the event that a deeper level becomes marginal at t = 2 (positive probability under any nondegenerate flow process), its quantity enters round-2 statistics, so dim F^{(2)} < dim F^{(1)} strictly; the intersection-stable core across T rounds is: never-marginal levels + within-order co-ownership splits + (at agg) within-level splits. Asymptotic (T -> infinity) identification of everything but the aggregation core is a **conjecture** (linked to T4, exploratory only). Two-step proof by explicit composition of the P0–P2 statistics through the book-update map; this is the provable backbone for the truncation-exposure claim in P6.

### P8 (Nonlinear parameterization — provable generic-rank version)
For z = f_theta(zeta) smooth (neural flow parameterization), for a.e. theta and any regular tape value, dim F^{nl}_{k,g} = d_zeta - rank D(S_{k,g} o f_theta) locally (constant-rank theorem; S the statistic or likelihood functional of P0–P2). Corollary: the P4 grid separation persists generically whenever Df_theta is full-rank on pool coordinates (the ru cell still point-identifies q_P, deterministic cells still rank-deficient). Global fiber geometry (curved, possibly disconnected fibers) is out of reach and is not claimed.

### P9 (Endogenous price — piecewise structure, provable)
With the clearing price determined by crossing, the global recorded statistic is piecewise linear/rational with finitely many regions indexed by (marginal level, exhaustion flag, j\*); the global fiber is a finite union of region fibers (dimension = max), glued along tie walls (V\* lands exactly on a pool prefix sum), where fibers can jump. Theorems are stated on interiors; boundary strata are handled by the P4(iii) stratification. A semi-algebraic description of the glueing is provable but laborious; only the stratification lemma goes in the paper.

### R1–R3 remarks
R1: pro_rata on the unit lattice with deterministic rounding: the pool fiber is a finite union of lattice cells approximating the scale ray; the dimension statement survives. R2: two-sided books are symmetric (bid side mirrors). R3: the gauge-symmetry pre-emption (V4): these fibers are **not** function-preserving gauges — members are training-loss-equivalent yet deployment-distinguishable (P6) — to be positioned against Quotient-Space Diffusion (ICLR 2026), Neural Mechanics (ICLR 2020), internal gauge symmetries; T4 (SGD fiber selection) stays conjecture-only, citing Soudry 2017 and "The Loss Does Not See the Basis but Adam Does" (2026).

## 3. Hostile reduction check (Task 3) — feeds D-1

**Verdict: the deterministic branch reduces; the random branch does not.**
1. **Deterministic cells (P1): YES — plain admission.** In the linear case L_{k,g} is a linear statistic and F = {z : L(Bz) = L(Bz0)} intersected with the regime polyhedron — exactly the Diaconis–Sturmfels (1998) / fibers-of-contingency-tables (2014) shape of "integer points with a fixed linear sufficient statistic", and rung refinement monotonicity (agg -> po -> pu shrinks) is a bare data-processing corollary. The P1 shrinkage content is demoted to a sufficiency corollary; the paper cites both works as owners of the fiber shape (consistent with the scoped-novelty list: no claim for bare positive-dimensional fibers; DPIOT ICML 2022, Perturb-Argmax/Softmax 2406.02180 as argmax-family analogs). **What survives deterministically**: (a) the market-native dimension formulas — which specific coordinates stay free (marginal hidden depth 1 + (m\* - j\*), deeper |D|) are functions of the clearing combinatorics, not generic; (b) the pro-rata pool fiber is a multiplicative ray, the fiber of the proportion statistic q -> q/R\*, **not** an affine DS fiber of any linear statistic; (c) kernel anonymity at agg (P3) is cross-kernel, outside DPI (which is fixed-kernel, coarser-rung).
2. **Random cells (P2/P3): NO reduction found.** DPI cannot deliver (a) the cross-kernel equality F_{ru,agg} = F_{k,agg}, nor (b) the point-vs-positive-dimension separation between kernels at the po rung. The (ru, po) fiber is the likelihood-equivalence class of a hypergeometric law — not a fiber of a linear statistic — and the identifying argument (first-draw ratios + two-draw concentration, closed form in P2iii) has no Diaconis–Sturmfels analog. **Honest scoping**: the mathematical core (multivariate hypergeometric composition identifiability) is classical/folklore and must be cited as such; the contribution is the mechanism-x-recording interaction taxonomy (P4 grid), the market-native dimension formulas, and the exposure asymmetry (P6), not the hypergeometric lemma.
3. **Consequence for T1's wording (condition adjustment for D-1)**: T1 must lead with the interaction grid + dimension formulas + partial-fill stratification; "finer tape shrinks fibers" must appear only as a sufficiency corollary with DS/contingency-table citations. This is a killer-test result to log, not a failure: it kills only the deterministic-shrinkage sub-claim as a novelty carrier.

## 4. Open beyond the linear parameterization (Task 4)

**Provable within the timeline (paper scope):** P8 (generic-rank local dimension for nonlinear f_theta, dichotomy persistence under submersive pool coordinates); P9 (piecewise/glued fibers under endogenous prices, stratification lemma); P7 (two-step strict fiber shrinkage, deeper-direction exposure under truncation/eligibility renewal); R1 (lattice rounding); the exhaustion-boundary stratum.
**Open, explicitly not claimed:** global nonlinear fiber geometry; asymptotic multi-step identification of everything but the aggregation core (conjecture, T4-adjacent, exploratory measurement only); state-dependence with latent/hidden book state and between-round cancellations (only coarse bounds available); strategic/endogenous flow (z responding to the tape — out of scope; the ALPHA reflexive deployment cell stays exploratory, TRADES 2025 / DEX closed-loop 2026 citations as planned); T4 SGD fiber selection (conjecture only).

## 5. S3 signature experiment — Fisher-information rank on Z by kernel x granularity (Task 5)

**Role:** GAMMA killer test 1 (theorem-compatible falsification) plus the without-replacement discriminator (killer test 2, adjacent). CPU-exact; runs only post-D0 freeze with PI authorization; currently spec-only.

**Frozen family.** Scaffold: one better level with 1 order (q1), a second better level with 1 order (q2), marginal pool P with m\* = 4 orders, base q_P = (5,4,3,2), two deeper orders (q7, q8); z = (Q, q) in R^9, B = I; robustness arm: z = z0 + G theta with G orthogonal, 3 preregistered seeds. V\*-ladder {1, 2, 4, 6} via Q in {6,7,9,11} (S_< = 5, R\* = 14). FIFO j\*(V\*) schedule from prefix sums (5,9,12,14): j\* = 1,1,1,2.

**Cells.** 3 kernels x 3 rungs x 4 V\* values, plus the annotated-pu variant for random_unit (eligible_units on): 40 exact FIM computations. Tape alphabets: agg = 1; po <= C(9,3) = 84 count vectors; pu <= 4^6 = 4096 sequences (random arm), single tape (deterministic arms). Exact pmf by enumeration; FIM J(theta; k,g) = sum_y p theta(y) grad log p grad log p^T by autodiff of the exact log-pmf (CPU seconds; no GPU, no data, no market simulation — this is exact-law arithmetic on the frozen formula, cross-checkable against the lab-asset-v3 engine post-freeze, which the 27 conformance tests already bind to manifest fea8a136...9581c).

**Statistic and decision rule.** Eigenvalues of J; rank r̂ = #{i : lambda_i > tau lambda_1}, tau = 1e-8 frozen; spectral-gap certificate on an 11-point grid (+-10% on each free coordinate); one-shot analyzer, enumeration-coverage record (mass = 1 by construction; report alphabet sizes), checkpoint-lock, no reruns.

**Preregistered predictions (from P1–P4; rank in R^9):**
- (k, agg), all k, all V\*: **rank 3** (q1, q2, Q). Kernel-independence signature (P3).
- (fifo, po): **3, 3, 3, 4** across the V\*-ladder (rank = 2 + j\*(V\*); j\*-schedule above). Dimension-formula signature (P1ii).
- (pro_rata, po): **6** for all V\* >= 1 (2 better + 3 proportions + 1 scale... correction: 2 better + 3 proportions + V\*(Q) = 6; pool scale free). Ray signature (P1iii).
- (ru, po): **6, 7, 7, 7** (V\* = 1: proportions only; V\* >= 2: pool point + Q + better). The **V\* = 2 rank jump is the without-replacement discriminator**: under with-replacement / proportional-to-initial draws the count law is multinomial, proportions-only at every V\*, so the jump never happens.
- (ru, pu) = (ru, po) at every V\*; (k, pu) = (k, po) for all k (saturation signature, P1iv + P2b).
- Annotated (ru, pu) at V\* = 1: **7** (eligible_units supplies R\*). P5a signature.
- Zero rank contribution of deeper coordinates (q7, q8) in every cell; zero rank on co-ownership directions if the co-ownership arm is enabled.

**Falsification map.** rank(ru, po) = 6 at V\* = 6 kills P2(iii) (scale unidentified: engine law is not draws-without-replacement-to-remaining — e.g., multinomial); rank(agg) kernel-dependent kills P3; rank(ru, pu) != rank(ru, po) kills P2b (sequencing informative: non-exchangeable draws, e.g., biased selected_unit); rank(fifo, po) off the 3/3/3/4 ladder kills P1ii or signals grammar leakage (diagnosed by which coordinates gain rank); rank jump at the wrong V\* kills the j\*-schedule or the exhaustion stratification.

**Tie-ins.** (a) S3's certified null-space bases are exactly the fiber tangent frames T2's bounded quantitative consumer-variance lower bounds need (leading version: Var_nu[C] >= sigma_min(J_C|_{T_zF})^2 x Var_nu(fiber coordinate) under a reference measure nu on a bounded fiber section — full constants in the paper; the unbounded version is demoted as attackable). (b) The exhaustion stratum (price-jump flag) is a preregistered conditioning variable; boundary/tie rounds are excluded from the interior-regime rank tests and reported separately. (c) Sampled arm (n = 1e5 exact-engine draws, seeded) is pipeline validation only, excluded from confirmatory inference per the statistical contract (50,000-draw paired bootstrap is reserved for ALPHA cells; S3 is deterministic-exact).

## 6. Conditions to carry into D-1 / D-3 wording

1. T1 lead = P4 interaction grid + market-native dimension formulas + exposure asymmetry (P6); deterministic shrinkage demoted to sufficiency corollary with DS/contingency-table citations.
2. New quantifier conditions in T1's statement: strict-partial-fill rounds (0 < V\* < R\*), V\* >= 2 for unannotated point identification (V\* >= 1 with eligible_units), law-level vs realized-tape fibers distinguished, "never a point" scoped to flow-level z with aggregation structure.
3. The exhaustion and V\*-ladder stratifications are preregisterable from price-only quotes and draw counts respectively — no extra recording needed; feed both to the ALPHA design (kernel-swap OOD axis intersects the exposed sets of P6).

Grounding files (absolute): /Users/howardwang/Desktop/playground/ecophys/papers/proposal/ecomd_random_unit_priority_thesis_v2_2026-08-27.md; /Users/howardwang/Desktop/playground/ecophys/experiments/lab_asset_a2/a2_exit_20260905/schema_spec.json; .../fixture_fifo/tape.jsonl; .../fixture_random_unit_within_price/tape.jsonl; .../fixture_random_unit_within_price/prestate.json. Session log should record this derivation under the parent's task #4 (D-2 evidence map + experiment plan docs).

---

## Part II — T2/T3 theorem package

# T2/T3 Theory Package — Merged GAMMA+ALPHA Paper (screening-legal: schema + theorem only; no GPU, no execution)

Grounding: all tape-field claims below were verified against the frozen artifacts at
`/Users/howardwang/Desktop/playground/ecophys/experiments/lab_asset_a2/a2_exit_20260905/`
(`schema_spec.json`, both fixtures' `prestate.json`/`tape.jsonl`; bundle manifest `fea8a136...9581c`)
and the semantics contract `papers/proposal/ecomd_random_unit_priority_thesis_v2_2026-08-27.md`.
No engine was executed; every invariance claim is a static consequence of the recorded payload fields.

---

## 0. Formal setup (engine-grounded, one-step linear case)

**Raw flow.** A one-step clearing instance at a touched price level ℓ: `n` resting orders with submitted quantities `q = (q_1..q_n) ∈ Z_{≥0}^n` (linear relaxation `R_{≥0}` for the theorems; integrality is a lattice remark), arrival clocks `t_1 < … < t_n`, incoming marketable quantity `Q > 0` with `Q < Σq_i` (rationed level; if `Q ≥ Σq_i` the level clears fully and contributes no fiber — stated honestly). Raw flow `z = (q, clocks, actor map)`.

**Mechanism (uniform-price clearing with quantity aggregation; kernel `k`).** Allocation `a = M_k(q)`, `Σ_i a_i = Q`:
- `fifo`: fill earliest units to cumulative threshold; threshold order partially filled.
- `random_unit_within_price` (engine semantics, verified): each executed unit is drawn uniformly without replacement from all remaining resting units at ℓ — equivalent to per-draw probability proportional to remaining order quantity. The engine records per draw: `allocation_draw = {eligible_units, maker_order_id, price, selected_unit}` and per execution `maker_remaining` (schema-verified in both fixtures).
- `pro_rata` (T1 taxonomy / external bridge only; not in this engine): `a_i = q_i Q / Σq_j`.

**Tape granularity `g` and the recorded-field contract `𝔽` (the load-bearing D-1 decision).** The through-M training corpus is a *projection* of the full event grammar. Three variants:
- `𝔽_exec` (**recommended default; used for all theorem instantiations**): execution events (`execution` sub-payload, `allocation_draw` when present) + `pre/post_best_bid/ask` (prices only — no depths).
- `𝔽_exec+orders`: additionally `order_request/order_accepted` (note `order_accepted.resting_quantity` pins every accepted order's quantity).
- `𝔽_full`: the entire arm-invariant grammar.
Under `𝔽_full` the fiber is a point (requests *are* the raw flow) and T1–T3 are vacuous; under `𝔽_exec+orders` the fiber collapses to within-order-timing ambiguity. **Everything below assumes `𝔽_exec`; Section 7 flags this as the contract item D-1 must freeze.** Within `𝔽_exec`, the schema gives, per touched level with ≥1 draw (random arm): the draw sequence, the drawn order ids, `maker_remaining` (pins each drawn order's quantity exactly), and `eligible_units` per draw (pins the *aggregate* remaining quantity at the level, hence the aggregate of never-drawn orders). The fifo arm records no `eligible_units`; only executed orders' `maker_remaining` is pinned. Untouched levels: only best-price quotes — no depth at all.

**Fiber.** `F_τ = {z' : T_{k,𝔽}(z') = τ}` with `T_{k,𝔽}` the recorded map. Structure (engine-level, from the field list above; consistent with T1's audited taxonomy, not re-derived):

| kernel × granularity | ambiguous set `U(τ)` | fiber shape at `z̄` |
|---|---|---|
| fifo, `𝔽_exec` | never-executed orders (any level) + residuals of partially executed orders beyond their last pinned `maker_remaining` | translate of orthant `R_{≥0}^{|U|}` (recession cone) |
| pro_rata, aggregate | scale ray on the rationed side | `{c·a : c ≥ 1}` (T1) |
| random_unit + per-unit tape, `𝔽_exec` | at each touched level: **split directions** among never-drawn orders `{u : Σ_{i∈neverdrawn(ℓ)} u_i = 0}` (aggregate pinned by `eligible_units`; drawn orders pinned individually) + never-executed orders at untouched levels (free orthant) | lower-dimensional subspace (lineality) at touched levels ⊕ orthant at untouched levels — *strictly smaller, never a point whenever ≥2 never-drawn orders share a level or any level is untouched* |
| random_unit + aggregate tape | randomness marginalizes out; contains the fifo-shaped orthant (support-union) | ⊇ fifo fiber |

This refines T1's "never to a point (exchangeable-agent symmetries)" with an **engine-native mechanism: `eligible_units` is an aggregate** — per-unit granularity pins level totals and drawn orders but provably cannot pin the never-drawn split, and untouched-level depth is recorded nowhere in `𝔽_exec`. (Consistent with, not contradicting, the audited T1; recommend T1 owner adopt this as the engine-grounded realization of the exchangeable symmetry.)

**Assumptions.** (A1) one-step linear clearing as above; (A2) `𝔽 = 𝔽_exec`; (A3) consumers below are finite linear functionals of the raw flow; (A4) training procedures are deterministic functions of corpus + seed draws (paired-seed discipline); (A5) integer lattice respected by constructions (all injected quantities integer units).

**Lemma 0 (training-signal identity — "zero training-loss difference, exactly").** If `T_{k,𝔽}(z) = T_{k,𝔽}(z')` then the through-M training corpora are byte-identical; hence any training map `A` (deterministic, or stochastic under paired seeds) yields identical parameters `θ̂ = A(τ, ω_train)`, and every consumer of the trained simulator, `Ĉ = C ∘ sim(θ̂)`, is τ-measurable, i.e. **constant on the fiber**. (Proof: identity of input bytes; measurability by composition. This formalizes "exactly zero": not `ΔL = 0` but *literally the same learning problem*.)

**Consumers (named, market-native).**
- `C_risk(z) = Σ_i p_i q_i` — raw-flow portfolio notional (submitted/queue exposure; a risk manager's object, not the tape's cleared volume).
- `C_lat^W(z) = Σ_i p_i 1{clock_i ≤ W} q_i` — latency-window notional (what a truncating deployment or a Δt-latency policy acts on).
- Distillation student — treated via Proposition 1b (information propagation, no functional form needed).

**Reference measure.** `μ_R` = product uniform on the fiber truncated to a box of radius `R` in the ambiguous coordinates: orthant case `q_i ~ Unif[a_i, a_i+R]` (lower bound `a_i` = recorded allocation/pinned residual); split case `u = P_K ε`, `ε_i ~ Unif[−R, R]` i.i.d., `P_K = I − (1/m)11^T` the projection onto the never-drawn split kernel of a level with `m` never-drawn orders. `R` = admissible excess scale (energy-bounded adversary); Gaussian references give the same scaling (Remark R3).

---

## 1. THEOREM 1 (T2 lead: bounded quantitative consumer-variance floor)

**Theorem 1.** Fix tape `τ` with nonempty ambiguous set `U(τ)` under `(k, g, 𝔽)`, reference `μ_R` on the box-truncated fiber, and consumer `C(z) = v^T z` with `v_U ≢ 0` on the ambiguous coordinates. Then:

**(a) Exact variance.** `Var_{μ_R}(C | τ) = (R²/12)‖v_U‖²` (orthant/box case; independent box coordinates, `Var Unif[a,a+R] = R²/12`). Split case per touched level: `Var = (R²/3)·Σ_{i∈neverdrawn(ℓ)}(v_i − v̄_ℓ)²` with `v̄_ℓ` the level mean (`ε`-variance `R²/3` pushed through `P_K`).

**(b) Estimation floor (impossibility).** For **any** τ-measurable estimator `Ĉ` — in particular any through-M-trained simulator consumer, by Lemma 0 —
`E_{μ_R}[(C − Ĉ)² | τ] ≥ Var_{μ_R}(C | τ)`, equality iff `Ĉ = E[C | τ]` μ-a.s. (Proof: `E(X−c)² = Var X + (EX − c)² ≥ Var X`, applied conditionally; `Ĉ` is fiber-constant.)

**(c) Tightness.** The fiber-center estimator `Ĉ* = E[C|τ]` attains the bound, so `inf_{Ĉ τ-meas.} E[(C−Ĉ)²|τ] = R²‖v_U‖²/12` **exactly** — the floor is the exact minimax value over tape-information-constrained estimators, not merely valid.

**(d) Growth rate.** Floor RMSE `= R‖v_U‖/√12 ≈ 0.289·R·‖v_U‖` — **Θ(R)** in scale, **Θ(R²)** in variance; per-direction contributions `v_i²R²/12` are tape-computable (which orders never executed / were never drawn is decided by the tape itself).

**(e) Granularity trace (quantitative T1 dichotomy).** Under fifo (`𝔽_exec`), `U` = full never-executed orthant → floor grows Θ(R²) in variance. Under random_unit + per-unit tape, magnitude ambiguity at touched levels is annihilated (`eligible_units` pins aggregates, `maker_remaining` pins drawn orders); the surviving floor is the split term `(R²/3)Σ(v_i − v̄_ℓ)²`. Consequences, both exact: (i) for the **price-notional** consumer `v_i ≡ p_ℓ` on never-drawn orders at a level, the split floor is **identically zero** — the per-unit tape fully protects magnitude-level consumers at touched levels; (ii) for the **latency consumer** `v_i = p_ℓ 1{clock_i ≤ W}`, the split floor is `(R²/3)·p_ℓ²·(m_in·m_out/m)` where `m_in/m_out` count never-drawn orders inside/outside the latency window — **positive exactly when a touched level's never-drawn orders straddle the latency boundary**. So the kernel×granularity interaction of T1 appears in T2 as a change of *growth class* (Θ(R²) → Θ(R²) restricted to time-split directions, with exact zeros on magnitude consumers), and T3's truncation map is precisely the detector of what granularity cannot remove.

*Proof sketch.* (a) independence + projection identities; (b) conditional variance decomposition around a fiber-constant predictor; (c) explicit estimator; (e) `eligible_units` is a summation functional — its kernel is the split subspace; `P_K v` kills constant-`v` vectors and retains clock-indicator vectors with the stated norm. Engine-level verification of the field claims: static inspection of `execution`/`allocation_draw` payload fields (done above); dynamic confirmation is the post-freeze S1a gate.

**Proposition 1b (distillation no-recovery; floor propagation).** Let the teacher be any through-M-trained simulator and the student any measurable function of the teacher's outputs (any capacity, any data the teacher saw). Then the student inherits τ-measurability and obeys the same floor (b). A student can beat the floor only by consuming raw-flow information (raw arms). *Corollary for the cube:* the raw-vs-through-M **student** gap is bounded below by the floor minus the raw arm's estimation error — a paired-seed estimable contrast. (One-line proof: composition of measurable maps; the floor depends only on the σ-algebra, not the estimator class.)

**Positioning.** Paper D's rank-one projection gauge is the `|U| = 1` special case of Theorem 1 (cite as design parent). External analogs to cite as delimited, not competing: DPIOT (ICML 2022) owns bare positive-dimensional fibers; Perturb-Argmax/Softmax (arXiv 2406.02180) is the argmax-family analog; censored/truncated regression (Tobit lineage) owns one-sided threshold censoring with *exogenous* thresholds — see §6 for why the mechanism-endogenous censoring here is not that.

---

## 2. COROLLARY 2 (T2 unbounded version — deliberately subordinate)

**Corollary 2.** Under fifo/`𝔽_exec` (or pro_rata aggregate, or ru+aggregate), every `u ∈ R_{≥0}^{U(τ)}` is a **recession direction**: `T(z̄ + t·u) = τ` for all `t ≥ 0` (units added behind the threshold / never executed / scale ray are unrecorded), while `|C(z̄ + t·u) − C(z̄)| = t·|v^T u| → ∞`. By Lemma 0 the training-loss difference is **exactly zero for all t** (identical corpora), and the divergence is mechanism-attributable (Proposition 3.5): remove `M_k` (raw-arm information) and the fiber is a point, so the divergence vanishes. The bounded lead preempts the "unbounded merely because the diameter is unbounded" attack: Theorem 1 already forces positive, exact-constant error on the *truncated* fiber, and Corollary 2 only adds that the truncation is an artifact of the reference measure, not of the mechanism.

---

## 3. THEOREM 3 (T3: deployment-detectable fiber part)

**Exposure definition.** Direction `u ∈ U(τ)` is **D-detectable** at `(τ, z̄)` for consumer `C` if `C ∘ D` is non-constant along `{z̄ + t u : t ∈ [0,R]}` (deterministic D) — equivalently in the linear case `∇_u(C∘D) ≠ 0`; for randomized D, first-order stochastic exposure `Var_ω[Gateaux perturbation] > 0`. `Exp(D, C) ⊆ U(τ)` is the exposed set.

**P3.1 (identity deployment).** `D_id` exposes all of `U(τ)`: `Exp(id, C_risk) = span⁺(U)`. Detection probability 1 under `μ_R` whenever `v_U ≢ 0`. (Baseline; immediate.)

**P3.2 (kernel swap — the asymmetry proposition).**
(i) *Swap → random_unit is first-order exposing.* For `u = δ e_i` on a never-drawn order at a touched level, the next draw probabilities `p_j = q_j^{rem}/S` (S = level remaining, recorded via `eligible_units`) satisfy `dp_j/dq_i = −q_j/S²` (`j ≠ i`), `dp_i/dq_i = 1/S − q_i/S²` — every allocation probability moves at order `δ/S`. Hence `Exp(swap→ru, allocation consumers) ⊇ U(τ) \ {0}` with first-order magnitude `O(δ/S)`.
(ii) *Swap → fifo is exactly blind (not merely small).* FIFO's filled set is the earliest `min(Q, depth)` units; quantities appended to orders whose queue position lies entirely behind the threshold never enter that set, so `M_fifo(z̄ + t·u) = M_fifo(z̄)` **exactly, for all t ≥ 0** — including on the integer lattice (units are appended behind the threshold; no tie/crossing events arise for these directions). Hence `Exp(swap→fifo, allocation consumers) = ∅`.
(iii) *Ordering corollary.* Allocation-level divergence: `swap→ru` is `Θ(R/S)` while `swap→fifo` is exactly 0 — a strict, preregistrable asymmetry with per-level weights `1/S` computable from fixtures. (Under ru + per-unit tape, the magnitude directions are already pinned, so the *remaining* exposure of swap→ru is the split kernel — the swap detector and the truncation detector see the same residual directions.)

**P3.3 (latency/message truncation).** `D_trunc^W` keeps events with `clock ≤ W`. Then `Exp(D_trunc^W, C) = U(τ) ∩ W` (directions whose orders arrive inside the retained window); the floor localizes: orthant case `Var = R²‖v_{U∩W}‖²/12`; split case per level `(R²/3)p_ℓ²(m_in·m_out/m)` — monotone nondecreasing in `W`, zero when no straddling. **Market-native content:** the exposure set is indexed by *arrival clocks*; PDE conservation layers (internal Paper D lineage) have no submission-time coordinates, hence no truncation-exposure axis at all — this is the generalization absent in PDEs claimed in T3.

**P3.4 (non-commutativity remark).** `D_trunc^W ∘ D_swap≠ru` and `D_swap≠ru ∘ D_trunc^W` differ by out-of-window excess entering draw denominators (`S` is level-total, not window-total). One-line proof from the `p_j` formula; worth a remark because it shows deployment-order is itself decision-relevant.

**Proposition 3.5 (mechanism-attributability, formal).** For consumer `C` and deployment `D`, define the attribution contrast
`Attr(C, D) := Var_μ(C∘D | T_{k,𝔽}) − Var_μ(C∘D | z)`,
conditioning on the through-M vs raw training information respectively. `M_k` is **attributable** for `(C, D)` iff `Attr > 0` (note `Var(·|z) = 0` always). Estimand-level version (what S2 measures with paired seeds): `Δ̂ = E|Ĉ_M − C∘D|² − E|Ĉ_raw − C∘D|² ≥ floor(C,D) − (raw-arm estimation error)`, identified by the cube's training-enforcement axis at fixed DGP and seeds. **Criterion (preregistrable):** attribution is confirmed iff (i) through-M consumer divergence ≥ the tape-computable floor (one-sided), (ii) raw-arm divergence ≤ preregistered noise ceiling ("divergence vanishes when `M_k` is removed"), and (iii) the training×inference interaction is ≈ 0 for tape-measurable control consumers. This is exactly the cube's 2×2 — the experimental section is the attribution instrument for the theorem.

---

## 4. Three-way formal distinction (with separating observables)

**(a) Mechanism-induced fiber divergence (ours).** Two raw flows with `T(z) = T(z')` induce *identical corpora* (Lemma 0) — not merely equal losses — and diverge only through consumers reading ambiguous coordinates. *Separating observable:* **constructed exact-tape pairs** (S1a): byte-identical through-M corpora with `ΔC > 0` growing linearly in injected `R`, plus raw-arm collapse (attribution criterion (ii)). Tape-level fit plays no role: the tape can be fit perfectly and the divergence persists.

**(b) Representational failure (Do LLMs Understand LOB Dynamics, 2026 shape).** The hypothesis class fails to fit the *observed* distribution. *Separating observable:* positive within-cell validation loss **on the tape itself**, correlated with the downstream error. Under (a) the tape-level fit is perfect (identical data) while deployment error persists — the dissociation (tape-fit error vs deployment divergence) is the diagnostic; in the cube it is measured per cell by pairing tape-level validation loss with consumer divergence.

**(c) Design-induced operator set-identification (Counterfactual Operator Relevance, 2025 shape).** The ambiguity is created by the *choice of deployment operator/estimand*; the data may pin everything. *Separating observable:* divergence changes under **redesign of D at fixed information**, but not under information change at fixed D; the mirror image of (a), which is killed only by **information change** (M removal) at fixed D. The cube realizes the dissociation as its two axes: inference enforcement = D redesign lever; training enforcement = information lever; architecture transfer = capacity lever. Each failure mode has exactly one rescue lever, and the three levers are the cube's axes.

**Required V4 remark (draft).** *The mechanism fiber is not a gauge symmetry.* Gauge-equivalent configurations are physically identical — every observable agrees, and quotienting the hypothesis space is the correct response (Quotient-Space Diffusion Models, ICLR 2026; Neural Mechanics, ICLR 2020; internal gauge symmetries in learned dynamics). Fiber members are physically **different** market states (different submitted flows, different consumers `C_risk`, different outcomes under `D_swap` and `D_trunc` by Theorem 3) that are **informationally** identical to the training loss — the equivalence is a property of the recording mechanism, not a symmetry of the model. The correct response is therefore exposure characterization (T3), not quotienting; a quotient repair deletes physically real states and cannot reduce the floor of Theorem 1(b), which is information-theoretic.

---

## 5. S1/S2 signature experiments (theorem-compatible falsification designs)

**S1a — constructed fiber pairs (confirmatory; engine-legal pair grammar, schema-static now, engine-confirmed post-freeze).** For each fixture tape with a rationed level: fifo arm — inject integer excess `δ ∈ {0, R/2, R}` onto never-executed orders (any level); random arm — move integer quantity between never-drawn orders at a touched level (splits preserve `eligible_units`, maker ids, and all execution payloads). Acceptance gates: (G1) through-M corpora (`𝔽_exec`) byte-identical; (G2) full `state_hash` chains **differ** (pairs are genuinely distinct raw states); (G3) `|C(z)−C(z')|` matches the predicted linear/exact-split values of Theorem 1(a,e). Predicted from T1/T3: linear growth `δ‖v_U‖` (fifo), split floor `(R²/3)Σ(v_i−v̄)²` (ru), exact zero for price-notional on ru splits. Kill: any G1 failure falsifies the structure lemma in the engine (see diesIf). Note: the current 21–22-event fixtures contain **no multi-order rationed level** — a schema-compatible fixture enrichment (multi-order touched levels with clock-straddling never-drawn orders) is a hard D-1 prerequisite, else S1a/O-C/O-D are unmeasurable.

**S1b — cross-seed gauge wander (exploratory only; T4-adjacent).** K paired seeds of a through-M arm on one corpus; report between-seed spread of implied raw-flow consumer statistics. No theorem claim (Soudry 2017; The Loss Does Not See the Basis but Adam Does, 2026 — cite as conjecture). The floor constrains error-vs-truth, not seed spread; reported, never claimed.

**S2 — surgery cells on locked checkpoints (confirmatory; predicted orderings).** Statistical contract inherited verbatim (seed = inference unit; 50,000-draw paired bootstrap; SESOI δ = 0.1 × mean of R00; ordered classification; Holm across mandatory cells; one-shot frozen analyzers). Predicted orderings:
- **O-A (attribution, from Thm 1b + Prop 3.5):** `consumer RMSE(through-M-trained, raw-infer) ≥ R‖v_U‖/√12` per cell, floor precomputed from fixture tapes; `RMSE(raw-trained, raw-infer)` at noise ceiling; positive interaction for fiber-exposed consumers.
- **O-B (swap asymmetry, from P3.2):** allocation-level divergence `swap→ru = Θ(R/S) > 0` vs `swap→fifo = 0` (point null, equivalence-tested against SESOI margin). Strict ordering, per-level weights `1/S` preregistered.
- **O-C (truncation monotonicity, from P3.3):** divergence increments match the precomputed curve `Δfloor(W) = (R²/12)Δ‖v_{U∩W}‖²` (orthant arms) and `(R²/3)p²Δ(m_in·m_out/m)` (split arms); monotone in `W`.
- **O-D (granularity fingerprint, from Thm 1e):** per-unit-tape arm shows magnitude-consumer floor collapse (predicted **exact zero** for price-notional at touched levels — preregistered null cell) while the latency consumer retains the split floor; aggregate-tape variant restores Θ(R²).
- **O-E (controls):** tape-measurable consumers (e.g., cleared-volume prediction) show no training-enforcement interaction; reflexive deployment cell exploratory only (TRADES 2025; DEX closed-loop 2026 discipline), excluded from confirmatory inference.
All cells, axes, both lineages reported, including class flips and nulls; architecture-transfer gate preregistered (failed transfer reported as boundary).

---

## 6. Hostile triviality check (strongest attack, honest)

**Attack.** "Theorem 1(b) is the law of total variance / Rao–Blackwell applied to a non-injective recording: for any `Z` and any consumer not co-measurable with the recording, the conditional variance floors every recorded-measurable predictor; Le Cam two-point arguments, censored-regression (Tobit) and missing-data bounds give the same. DPIOT (ICML 2022) already owns positive-dimensional fibers for learned simulators. The market mechanism only supplies a censoring pattern; T2 is an immediate consequence of fiber geometry plus classical estimation theory."

**What defeats it, and what does not (honest).**
- **Conceded:** existence-level content is generic — already conceded at D-2 by scoping (no claim for bare positive-dimensional fibers). If a referee reduces the claim to "non-injectivity ⇒ positive conditional variance", we lose that fight and must not fight it.
- **Defense 1 — tape-computable constant:** the floor `R‖v_U‖/√12` has `U` **computable from the public tape alone** (never-executed / never-drawn sets are decided by recorded events), converting a generic impossibility into an operational risk bound a practitioner can evaluate from data in hand. Generic non-injectivity supplies no constant and no computability.
- **Defense 2 — mechanism-endogenous, kernel-dependent censoring:** `U(τ)` is not a fixed missingness pattern. It is *determined by the clearing outcome itself* (which side is rationed, where the threshold falls, which orders never draw), and it **changes with the priority kernel at fixed data**: orthant (fifo) vs scale ray (pro_rata) vs split kernel with exact zeros (ru per-unit, Theorem 1e). A Tobit/exogenous-censoring parent cannot predict the kernel×granularity interaction; Theorem 1e and P3.2 do, with falsifiable orderings (O-B, O-D). The science is the interaction; the floor is the instrument that sees it.
- **Defense 3 — tightness and exact-zero point predictions:** the bound is attained (fiber-mean estimator), so it characterizes the exact information-constrained minimax value, and it yields exact-zero predictions (ru splits × price-notional; swap→fifo) — falsifiable point nulls, not one-sided hedges.
- **Residual risk:** if reviewers judge Defenses 1–3 "engineering of a classical bound", T2 must be positioned as a *risk characterization of tape-trained market simulators with mechanism-endogenous constants* — the paper's theorem weight then rests on T1 (taxonomy + dichotomy) with T2 as its quantitative instrument and the cube as evidence. Do not sell T2 as a new estimation theorem. The unbounded corollary is never to be led with.

**Contribution to the D-1 hostile-T0 forecast (input to the forecaster, not the forecast):** the differentiated, parent-problem-resistant content is (i) endogenous censoring geometry keyed to the priority kernel, (ii) the tape-computable floor with tightness, (iii) exact-zero/null predictions, (iv) clock-indexed truncation exposure with no PDE analog. None of these reduce to censored regression (exogenous threshold), DPIOT (bare fiber dimension), or perturb-argmax (argmax family) — this is the material the T0 case should be built from.

---

## 7. D-1 freeze handoff (what must be pinned; what was not assumed)

1. **Simulator contract decision:** through-M corpus = `𝔽_exec` (execution payloads + allocation draws + pre/post BBO prices). Under `𝔽_full` or `𝔽_exec+orders` (resting_quantity pins quantities) the theorems hold as stated but the fibers shrink toward points and the floors collapse — the paper's claims would need restatement. This is the single highest-leverage contract item.
2. **Fixture enrichment required:** multi-order rationed touched levels with clock-straddling never-drawn orders (schema-compatible additions to the frozen bundle; no physics change).
3. **Engine pair grammar for S1a:** fifo = orthant injections on never-executed orders; ru = integer splits across never-drawn orders at touched levels. Both are exactly the directions the recorded fields cannot see (statically verified).
4. T1's per-unit fiber statement can be strengthened engine-natively (aggregate `eligible_units` ⇒ split-kernel realization of the exchangeable symmetry); flag to T1 owner for adoption at D-1 wording freeze.
5. Not assumed: no multi-step composition, no strategic agent response (reflexive cell excluded), no nonlinearity of `M` beyond the stated piecewise structure, no SGD-interior selection (T4 stays conjecture).
