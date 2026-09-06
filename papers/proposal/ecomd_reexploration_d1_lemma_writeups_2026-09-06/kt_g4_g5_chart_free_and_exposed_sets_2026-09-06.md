# KT-G4 (chart-free restatement, prongs a–c) and KT-G5 (exposed-set characterization)

D-1 lemma writeup, 2026-09-06. Screening-legal deliverable under
`pi_reexploration_d1_authorization_20260906` (theorem/schema work only; no GPU, no engine
execution, no data access, no new literature fetch). Companion to
`ecomd_reexploration_theory_appendix_2026-09-06.md` (Part I P0–P9, Part II M1 contract),
`ecomd_reexploration_d1_killer_tests_and_ops_2026-09-06.md` §A (KT-G4, KT-G5),
`ecomd_reexploration_experiment_plan_2026-09-06.md` (§2 OOD axes, §3 theory deliverables,
§12 risk register). Citations are drawn exclusively from
`ecomd_reexploration_d2_evidence_map_2026-09-06.md`.

**Attacks discharged.**

- **KT-G4**: "P8's generic-rank dimension statement is chart-dependent (a reparameterization
  changes ranks); the dichotomy could be a coordinate artifact."
- **KT-G5**: "The exposure results are contrived-D: you cherry-picked deployment maps that
  expose."

**Status summary (honest).** KT-G4 prongs (a) and (b): **proven**. KT-G4 prong (c):
**proven_with_conditions** (naturality of the floor is unconditional; exposed-set invariance
carries an explicit D-equivariance hypothesis; the exact closed-form constant is
reference-measure-relative, tied to the preregistered box reference, not chart-relative).
KT-G4 prong (d) (positive dimensionality in θ-charts) is **conceded as chart-dependent** with
DPIOT (2022) as owner of that residue — per the KT-G4 spec. KT-G5: **proven_with_conditions**
(exhaustive characterization within the engine-native grammar and the linear consumer class;
interior-regime and clock hypotheses stated per statement; deployments outside the grammar are
out of scope by preregistration — that scoping is itself the answer to the contrived-D attack).

---

## 0. Shared formalism (consistent with theory appendix Part II §0 / Part I §1)

**Flow space and M1 contract.** One-step clearing instance at the touched price level ℓ: n
resting orders with quantities `q ∈ Z_{≥0}^n` (linear relaxation `R_{≥0}^n` for the theorems;
integrality a lattice remark, as in the appendix), arrival clocks, actor map; incoming
marketable quantity Q with `0 < V* < R*` on the interior regime (`V* = Q − S_<` residual demand,
`R* = Σ_{i∈P} q_i` pool total, m\* = |P| ≥ 2). Raw flow `z = (q, clocks, actor map) ∈ Z`, an
open subset of a finite-dimensional vector space in the linear relaxation. General linear
parameterization `(Q,q) = Bz` pulls fibers back through ker B (appendix P0); every dimension
below gains nullity(B). This writeup works in quantity space (B = I) except where noted.

**Recorded map and grammar.** `T_{k,F}: Z → Y` maps a flow to its rung-g tape under kernel k
and recorded-field contract F (the D1_01-frozen `F_exec`: execution payloads +
`allocation_draw` when present + pre/post BBO prices; prices only, no depths). Y is a finite
alphabet per round (finitely many execution payloads and draw payloads; the tape of one round
is a finite string), hence a standard Borel space with countably generated, point-separating
σ-algebra. The law-level object for stochastic kernels is the measure-valued map
`L_{k,g}: q ↦ P(·|q)` into the simplex over the count/sequence alphabet (also standard Borel).

**Fibers.** Realized-tape fiber `F_τ = {z' : T_{k,F}(z') = τ}`; law-level fiber
`F_{k,g}(z0) = {z : L_{k,g}(z) = L_{k,g}(z0)}`. Recorded σ-algebra `G_{k,g} := σ(T_{k,g}) ⊆ B(Z)`
(and its law-level twin `σ(L_{k,g})`).

**Charts.** A *chart change* is a C¹ diffeomorphism `φ: Z' → Z` (z = φ(ζ)), i.e. a
re-description of the same flow space. A *fiber-preserving diffeomorphism* is a C¹
diffeomorphism `ψ: Z → Z` with `T∘ψ = T` (it maps every fiber into — hence onto — itself).
Charts are harmless re-descriptions; fiber-preserving ψ move the physical instance within a
fiber. KT-G4's job is to show the identification statements transport under charts; KT-G5/T3's
substance is that the named objects do **not** stay constant along fiber-preserving ψ (that is
exposure). Confusing the two is precisely the "coordinate artifact" attack.

**Engine grounding (verified, read-only).**
- `scripts/lab_asset/matching.py:285–296` — the taker fill loop; `fill = min(remaining,
  maker_qty)` iff FIFO, else `fill = 1` (one execution record per drawn unit under
  `random_unit_within_price`).
- `matching.py:585–604` — `_select_maker`: FIFO returns `queue[0]` (arrival-ordered head, no
  draw payload); otherwise `eligible_units = sum(quantity for _, _, quantity in queue)` — the
  **whole remaining level total** — and `selected_unit = rng.randrange(eligible_units)` with a
  cumulative walk over per-order remaining quantities: the draw is uniform over remaining
  units, P(order i) = q_i^rem/S, S = level remaining. This is the sequential
  without-replacement / PPS-to-remaining semantics of thesis v2 and appendix P0/P2.
- `matching.py:606–625` — `_apply_maker_fill` mutates the level queue in place (decrement or
  pop; empty level deleted), so the book persists across rounds within a session (multi-round
  deployments read a mutated state).
- `matching.py:311` — execution payloads carry `clocks = request.clocks`, the **aggressor's**
  clocks (maker clocks are not on the execution record; they live on the maker's
  `order_accepted` event, which `F_exec` excludes).
- Frozen fixtures (`experiments/lab_asset_a2/a2_exit_20260905/`, read-only): `fixture_fifo/
  tape.jsonl` seq 7 — one record, `quantity: 2`, `maker_remaining: 2`, no `allocation_draw`;
  `fixture_random_unit_within_price/tape.jsonl` seq 7–8 — `quantity: 1` each, draws
  `{'eligible_units': 4, 'selected_unit': 2}` then `{'eligible_units': 3, 'selected_unit': 0}`:
  the denominator decrements by exactly the drawn unit, confirming
  draws-without-replacement-to-remaining and the per-draw recording of the level total.

---

## 1. KT-G4(a) — sigma-algebra prong

**Attack being discharged.** "Dimension/identification statements are properties of the
coordinate expression of the recorded statistic."

### Proposition A (recorded information is a σ-algebra; identification content transports)

Let `T: Z → Y` be the recorded map of any cell (k, g, F), Y standard Borel, `G = σ(T)`.

**(A1) Transport identity.** For every C¹ diffeomorphism `φ: Z' → Z`,
`σ(T∘φ) = φ^{-1}(σ(T))`. Consequently, for any `h: Z → R`: h is G-measurable **iff**
`h∘φ` is `σ(T∘φ)`-measurable.

**(A2) Atoms are fibers.** The atoms of G are exactly the realized-tape fibers:
`atom_G(z) = {z' : T(z') = T(z)}`. Hence "the tape point-identifies a functional h" (h
constant on fibers) **is equivalent to** "h is G-measurable" — a statement about the pair
(h, G), no coordinates involved. Fiber dimension at z is the dimension of the atom, a
diffeomorphism-invariant of the pair (Z, G).

**(A3) Equivalence with the P8 coordinate statement.** On the interior regime, for the
statistic S (deterministic cells) or the pmw-vector map `q ↦ P(·|q)` (stochastic cells):
(i) `rank D(S∘φ)_ζ = rank DS_{φ(ζ)}` for every C¹ diffeomorphism φ, by the chain rule
(`D(S∘φ) = DS·Dφ`, Dφ invertible ⇒ rank preserved). (ii) The P8 local fiber dimension
`dim F = d − rank D(S∘f_θ)` at regular points is therefore invariant under C¹-diffeomorphic
reparameterization of the flow coordinates and of the ambient statistic; the constant-rank
theorem's local dimension is transported by φ. (iii) The law-level identification content of
P2/P4 — point identification of q_P for (random_unit, po/pu) at V\* ≥ 2, scale-ray fiber at
V\* = 1, dimension grid of P4 — is a statement about `σ(L_{k,g})` (via A2 applied to the
measure-valued recorded map) and transports identically.

**(A4) General B.** With `(Q,q) = Bz`, `σ(T∘B) = B^{-1}(σ(T))` for linear injective B; fibers
gain ker B in dimension (appendix P0) — again a σ-algebra transport, not a coordinate accident.

*Proof.* **(A1)** For any map φ and family 𝒜 of subsets of Z, `σ({φ^{-1}A : A ∈ 𝒜}) =
φ^{-1}(σ(𝒜))`, because φ^{-1} commutes with complements and arbitrary unions; apply with 𝒜 =
σ(T). The measurability equivalence is then immediate: (h∘φ) is σ(T∘φ)-measurable iff h is
σ(T)-measurable by (A1) and the definition of preimage measurability. **(A2)** ⊆: T is
constant on atoms of σ(T) (T is G-measurable and singletons of Y generate... precisely: for
z, z' with T(z) = T(z'), every G-set {T ∈ A} contains both or neither, so z' lies in every
G-set containing z). ⊇: Y standard Borel has a countable point-separating generator (E_n);
the atom of z is `∩_n {T ∈ E_n}^{±(z)}` = T^{-1}(T(z)) because the generator separates the
point T(z) from every other value: ∩{E ∋ T(z)} over the generator = {T(z)}. Tape alphabets are
finite per round, so this is explicit. "h constant on fibers ⇒ h G-measurable": h factors
through T via a map on the image; the factor is Borel on the image of a standard Borel space
under a Borel map (Lusin–Novikov/universability of standard Borel images — for countable
alphabets this is elementary: the factor is defined on the countable set of realized tapes).
**(A3)(i)** chain rule and rank inequalities: rank(DS·Dφ) ≤ rank DS with equality when Dφ is
onto (invertible); symmetric for φ^{-1}. (ii) At a regular point the fiber of S∘φ through ζ
is `φ^{-1}(fiber of S through φ(ζ))` (set-theoretic identity), and a C¹ diffeomorphism maps
C¹ submanifolds to C¹ submanifolds of the same dimension. (iii) The measure-valued map
L takes values in the simplex over a finite alphabet (po: count vectors; pu: sequences) —
standard Borel; A2/A3 apply verbatim with T replaced by L. ∎

**Prong (d) concession (required by KT-G4 spec).** Positive dimensionality of fibers **in
θ-space** under a general neural parameterization z = f_θ(ζ) *is* chart-dependent: if Df_θ is
rank-deficient at ζ (non-immersive), ζ-space fibers are strictly larger than the pulled-back
z-space fibers. The chart-free statement is the flow-space (z) fiber content of A2/A3; the
parameter-space positive-dimension residue is owned by DPIOT (Discrete Probabilistic Inverse
Optimal Transport, ICML 2022; D-2 map: "owns bare positive-dimensional likelihood fiber modulo
OT") and Perturb-Argmax/Softmax (arXiv:2406.02180; cleared analog owning "noise law determines
the stochastic fiber" for the argmax family). T1 wording must keep the dichotomy on flow-space
fibers and cite both, per the D-2 conditions 1–2.

---

## 2. KT-G4(b) — likelihood-ratio prong

**Attack being discharged.** "The V\* = 2 rank jump of S3/EP3 could be an artifact of the
R⁹ chart; a reparameterization might move or remove it."

The count law families (V\* draws at the touched level, counts c with `Σc_i = V*`, pool
`q_P`, `R* = Σq_i`):

- **MVHG** (engine semantics, without replacement to remaining):
  `P(c|q) = Π_i C(q_i, c_i) / C(R*, V*)`.
- **Multinomial** (with-replacement / proportional-to-initial falsifier):
  `P(c|q) = (V*!/Π_i c_i!) Π_i π_i^{c_i}`, `π_i = q_i/R*`.

**Likelihood equivalence.** For a family {P_θ} on a fixed outcome space, write `θ ~ θ'` iff
`P_θ = P_{θ'}` as measures (equivalently the likelihood-ratio process ≡ 1 on the support).
The identified functionals are exactly those constant on ~-classes. This relation is a
property of the family of measures — no parameterization appears in its definition.

### Proposition B (the scale-identification jump is a property of the count-law family)

**(B1) MN never identifies scale, at any V\* ≥ 1.** For every V\* ≥ 1, `P_MN(·|q)` depends on
q only through π = q/R\*: if π(q) = π(q') then `P_MN(·|q) = P_MN(·|q')`. Hence the ~-classes
of MN (on pools with common support) are exactly the scale rays {λ q : λ > 0}, and every
identified functional factors through π. In particular no integer-valued or
scale-sensitive functional of q_P (e.g. q_i itself) is identified, at any V\*.

**(B2) MVHG identifies scale exactly when V\* ≥ 2.** Define the law-functionals
`ρ_i(L) := E_L[c_i]/V*` and `γ_i(L) := E_L[c_i(c_i−1)]/(V*(V*−1))` — Borel functions of the
count law L on the finite count alphabet. On the MVHG model (m\* ≥ 2, interior
`0 < V* < R*`, R\* ≥ 3 so V\* ≥ 2 is feasible):
- `ρ_i = q_i/R*`, `γ_i = q_i(q_i−1)/(R*(R*−1))` (exchangeability: each draw position is
  marginally uniform over pool units; ordered pairs of distinct draws likewise — the count
  marginal of the uniform-permutation sequence law, appendix P2i);
- the closed form `q_i = (1 − γ_i/ρ_i)/(1 − γ_i/ρ_i²)` holds on the model image (algebra:
  γ_i/ρ_i = (q_i−1)/(R*−1), γ_i/ρ_i² = R\*(q_i−1)/(q_i(R\*−1)); then
  `1−γ_i/ρ_i = (R*−q_i)/(R*−1)` and `1−γ_i/ρ_i² = (R*−q_i)/(q_i(R*−1))`, whose ratio is
  exactly q_i; edge q_i = 1 gives γ_i = 0 and the formula returns 1; q_i = R\* is excluded by
  m\* ≥ 2 with positive quantities).
Hence at V\* ≥ 2 the ~-classes of MVHG on pool coordinates are **points**; at V\* = 1 the law
is categorical `P(c = e_i|q) = q_i/R*`, a function of π alone, so the ~-classes are the scale
rays. The identified σ-algebra therefore strictly increases from V\* = 1 to V\* = 2:
**the jump**.

**(B3) The jump transports through every smooth reparameterization.** Let `θ ↦ q(θ)` be any
C¹ map into pool space (a reparameterized family). The transported families satisfy
`P^{MN}_θ = P^{MN}_{θ'}` whenever π(q(θ)) = π(q(θ')), **for every V\* ≥ 1 simultaneously**;
and at V\* ≥ 2, `P^{MVHG}_θ = P^{MVHG}_{θ'}` iff q(θ) = q(θ') (given common support), so any
two parameter points with equal proportions but different scale are separated exactly when
V\* ≥ 2. Consequently: (i) no C¹ reparameterization creates a scale-identification jump for
MN at any V\* — equality of laws is preserved by transport, and scale-ray twins have equal
laws at *every* V\*; (ii) the MVHG jump survives every C¹ reparameterization that separates
scale at fixed proportions (in particular every C¹ diffeomorphism of pool space); under a
non-injective reparameterization the jump can only persist or shrink by merging θ-points —
it can never appear for MN nor invert direction.

**(B4) Rank form (S3/EP3).** At any parameter point that is an immersion for the chart in
use, the FIM rank equals the dimension of the identified tangent subspace, i.e.
`rank J = d − dim(tangent fiber)`; by (A3)(i) this is diffeomorphism-invariant. The
preregistered S3 ladder — (ru, po) rank 6 at V\* = 1 (proportions 3 + better 2 + Q 1) rising
to 7 at V\* ∈ {2,4,6} (pool scale identified) — is therefore not a coordinate artifact; the
multinomial falsifier stays at rank 6 at every V\* by (B1)/(B3)(i). *Condition:* the rank
statement assumes the immersion hypothesis (Dq full rank at the point, τ = 1e-8 spectral
floor); the identification statement (fiber dimension on pool coordinates) is unconditional.

*Proof.* (B1) is immediate from the pmf expression. (B2): the moment identities are
classical MVHG moments obtained here from the uniform-permutation lift (each of the V\*
sequential draws is exchangeable, and P(specific ordered pair of distinct draws both hit
units of order i) = q_i(q_i−1)/(R\*(R\*−1)); summing over the C(V\*,2) ordered pairs gives
E[c_i(c_i−1)] = V\*(V\*−1)·q_i(q_i−1)/(R\*(R\*−1))); the closed-form algebra is displayed
above; V\* = 1 categorical case is direct. Identified-functionals-are-exactly-~-invariants:
a functional is a function of the law iff it is constant on equal-law points, i.e. constant
on ~-classes; and at V\* ≥ 2 every q_i is a function of the law (the closed form exhibits
the Borel right inverse), so ~ refines to points on pool coordinates. (B3): transport of
equal laws is equality of composed laws; the dichotomy of ~-classes transfers to preimages;
the "never invert" clause holds because preimage of a partition cannot split blocks (it can
only merge). (B4): FIM rank = rank of the Jacobian of θ ↦ (pmf vector) at nondegenerate
points; equals dimension of the image tangent = d − tangent-fiber dimension at regular
points; invariant by (A3). ∎

**Remark (what the prong does and does not claim).** (B) does not claim novelty for the
hypergeometric identifiability algebra (classical/folklore, conceded in the appendix
reduction check §3.2); the prong's role is defensive: the V\* = 2 discriminator is a property
of the pair of measure families, so no reparameterization — in particular no adversarial
"chart" a referee might substitute for the R⁹ coordinates — can move it. The falsification
tie to the engine stands: S3's "no jump ⇒ engine law is not draws-without-replacement"
(rule §12 STOP, engine-law mismatch) is a statement about the engine's law family, chart-free
by (B3).

---

## 3. KT-G4(c) — consumer prong

**Attack being discharged.** "Theorem 1's floor constant and Theorem 3's exposed sets are
chart artifacts of the linear-consumer coordinates."

Consumers are **named market-native functionals of the deployed record**:
`C_risk(z) = Σ_i p_i q_i`, `C_lat^W(z) = Σ_i p_i 1{clock_i ≤ W} q_i`, and allocation
consumers `C_w(allocation record) = Σ_j w_j c_j` (linear in fill counts). Deployment maps D
are **named semantic operations on the flow** (kernel swap, truncation window, readout; §4).
Both classes are defined on Z (or on the deployed record) compositionally — a chart is only
used to *evaluate* them.

### Proposition C (floor and exposed sets under diffeomorphisms)

Let `T` be the recorded map of the training cell, `G = σ(T)`, and
`floor_μ(C | τ) := inf{ E_μ[(C − Ĉ)² | τ] : Ĉ is G-measurable } = Var_μ(C | G)` (Theorem 1:
the conditional variance around fiber-constant predictors; tightness by the fiber-mean
estimator — appendix Part II §1).

**(C1) Floor naturality — any chart, any diffeomorphism.** For every C¹ diffeomorphism
`φ: Z' → Z`: `floor_{φ_*μ}(C∘φ | σ(T∘φ)) = floor_μ(C | σ(T))`, where φ\*μ is the pushforward
measure. In particular, for a **fiber-preserving** diffeomorphism ψ (T∘ψ = T):
`floor_{ψ_*μ}(C∘ψ^{-1} | G) = floor_μ(C | G)` — the floor of the transported consumer at the
transported reference equals the original floor, *exactly*.

**(C2) Zero structure is chart-free.** `floor(C|τ) = 0` ⟺ C is G-measurable (C constant on
fibers). By (A1) this transports; by (A2) it is equivalently "C is constant on the fiber."
For linear consumers `C_v(z) = v^T z` and the two engine cells: (i) fifo/F_exec — the fiber
is `{z : z_{U^c} = z̄_{U^c}, z_U ≥ 0 free}` (recession orthant U = never-executed + hidden
depth; appendix Part II §0 table), so `floor = 0 ⟺ v_U = 0 ⟺ v ⊥ span(U)`;
(ii) ru per-unit/F_exec — the touched-level fiber directions are the split kernel
`K_ℓ = {u : Σ_{i∈neverdrawn(ℓ)} u_i = 0}` (`eligible_units` is a summation functional; its
kernel is exactly the split subspace), so `floor = 0 ⟺ Proj_{K} v = 0`, i.e. v is
level-constant on never-drawn orders. The exact-zero predictions of Theorem 1(e) (price-notional
consumer on ru splits: v_i ≡ p_ℓ on the level ⇒ v|_K = 0) are therefore σ-algebra facts and
transport under every chart change and every fiber-preserving diffeomorphism.

**(C3) Projection structure.** In the preregistered box reference (uniform on the truncated
fiber), `floor = (R²/12)‖Proj_{L}v‖²` with `L = span U` (orthant cell) resp. the split kernel
K (ru cell) — i.e. the floor is the squared norm of the projection of v onto the fiber's free
(lineality) subspace **L = ker dT_z̄ ∩ (quantity span)**, a geometric object defined by the
recorded map's differential, evaluated in the engine's native unit-tick metric. Under a chart
change φ the consumer transports to `C∘φ` and the constant transforms by the change-of-variables of (C1); under a fiber-preserving ψ the *value* is invariant with the pushed
reference (C1). The closed form `R²‖v_U‖²/12` is the evaluation of the chart-free quantity
`Var_μ(C|σ(T))` in the preregistered uniform-box chart — the reference measure is a declared
contract item (frozen at D0; Gaussian references give the same scaling, appendix Remark R3),
not a hidden coordinate choice.

**(C4) Exposed-set naturality.** Define `Exp(D, C, z̄) := {u ∈ T_{z̄}F : t ↦ (C∘D)(z̄+tu) is
non-constant on [0,R]}` (appendix Part II §3; randomized-D version via positive
first-order exposure variance). Let φ be a chart change that **transports D's semantic
coordinates** (`D∘φ = φ_out∘D` for the induced map φ_out on deployed records — true for every
map in the grammar of §4 when φ is applied to the flow coordinates the map reads). Then
`Exp(D, C∘φ, φ(z̄)) = dφ_{z̄}(Exp(D, C, z̄))`: exposed-set membership, sign (zero vs nonzero),
and the partition {exposed, blind} are chart-free; magnitudes transform by the Jacobian.
For **fiber-preserving** ψ the transported set stays inside the same fiber.

**(C5) What is deliberately NOT invariant.** For a fiber-preserving ψ that *warps ambiguous
coordinates*, the kernel-swap deployment is **not** ψ-equivariant (`D_swap∘ψ ≠ ψ_out∘D_swap`):
the swap reads the very coordinates the tape does not record (P3.2). Consequently
`Exp(D_swap, C)` is *not* constant along fiber warping — and that non-constancy **is**
Theorem 3 (fiber members are deployment-distinguishable). Prong (c) separates the harmless
chart-dependence (removed by C1–C4) from the substantive fiber-variation (the science).

*Proof.* (C1): For G-measurable Ĉ', `Ĉ'∘φ` is σ(T∘φ)-measurable and conversely every
σ(T∘φ)-measurable predictor has this form (A1); and `E_{φ_*μ}[(C∘φ − Ĉ'∘φ)² 1_{T∘φ ∈ A}] =
E_μ[(C − Ĉ')² 1_{T ∈ A}]` by the change-of-variables identity
`E_{φ_*μ}[h∘φ] = E_μ[h]` applied to h = (C−Ĉ')²1_{T∈A} (note `(T∘φ)∘φ^{-1} = T` under the
substitution). The infima therefore coincide; the conditional-variance identity is Theorem
1(b). For fiber-preserving ψ: σ(T∘ψ) = σ(T) = G, and the consumer C∘ψ^{-1} with measure ψ\*μ
is the instance of the same computation. (C2): zero floor ⟺ some G-measurable predictor
equals C μ-a.s. (the fiber mean) ⟺ C G-measurable; (A1)/(A2) transport it; the two cell
computations are the fiber shapes of the Part II §0 table, engine-grounded: `eligible_units`
records the level total (matching.py:592), whose kernel on never-drawn coordinates is the
split subspace; drawn orders are pinned by `maker_remaining`. (C3): the box-reference
variance of a linear functional is (R²/12)‖v‖² on independent uniform coordinates (Theorem
1(a)); identifying the free subspace with ker dT ∩ quantity span is (A3) plus the explicit
recorded statistics of P0–P2. (C4): `d/dt (C∘φ∘D)(φ(z̄)+t·dφ u)`: since
`(C∘φ∘D)∘φ^{-1}`-compatibility gives `φ∘D = D∘φ_out`... with `D∘φ = φ_out∘D`,
`(C∘φ)(D(φ(z̄+tu))) = C(φ_out(D(z̄+tu)))`, and non-constancy in t of `C(φ_out(D(z̄+tu)))` is
equivalent to that of `(C∘φ_out)(D(z̄+tu))` because φ_out is a diffeomorphism on records
(composition with a diffeomorphism preserves non-constancy); the right side is the exposure
of the transported consumer `C∘φ_out` at z̄ in direction u. (C5): P3.2's derivatives
`dp_j/dq_i ≠ 0` (matching.py:592–603) exhibit the failure of equivariance concretely. ∎

**Honest conditions.** (i) C1–C3 are unconditional for the named consumers; (ii) C4 requires
the transport compatibility `D∘φ = φ_out∘D`, satisfied by the grammar maps when φ moves only
coordinates the map does not read, or moves them together with the map's output — for
kernel swap, φ must preserve book quantities (the swap reads them), which is exactly why
fiber-warping ψ fall outside C4 (C5); (iii) the closed-form constant is relative to the
preregistered reference measure (declared), not chart-free in the absolute sense — the
chart-free object is `Var_μ(C|σ(T))`.

---

## 4. KT-G5 — deployment grammar and consumer classes (definitions fixed first)

**Attack being discharged.** "For any loss-invariant fiber you can contrive a separating map;
the exposure results are contrived-D."

### 4.1 The preregistered grammar 𝒢 (nothing post hoc)

𝒢 := the deployment maps generated by:

- `D_read` — **record readout** (consumer sees only the deployed tape). Null control:
  every `C∘D_read` is σ(T)-measurable, so `Exp = ∅` for every consumer.
- `D_raw` — **raw-flow readout** (consumer sees the true submitted flow; the risk-manager
  baseline of P3.1). Maximal control: `Exp(D_raw, C_v) = {u ∈ U : v^Tu ≠ 0}` = all of U for
  any consumer with v_U ≢ 0.
- `D_swap→ru`, `D_swap→fifo` — kernel swap: replay the recorded request stream from the same
  prestate with `allocation_rule` swapped (the replay contract's native operation; the two
  frozen fixtures are literal same-prestate dual-arm instances).
- `D_trunc^W` — truncation window W: the deployed environment retains only units/messages
  with clock ≤ W (out-of-window resting orders are removed from the deployed book before
  replay).
- `D_h` — horizon extension to h clearing rounds (h ∈ {1,4,16,31} of contract C4; the book
  mutates across rounds per matching.py:606–625).
- finite **compositions** of the above.

Every generator is a semantic operation on the flow, preregistered in the experiment plan
§2 (OOD axes: kswap, trunc_lag/trunc_cap, horizons) and contract C4 — the grammar predates
any exposure computation, which is the first half of the answer to contrived-D (§7).

**Nomenclature reconciliation (D-1 wording item).** The killer-test doc's
"exposed(D_id) = ∅" and the appendix P3.1 "Exp(id, C_risk) = span⁺(U)" use two different
"identity" maps. This writeup splits them into `D_read` (Exp = ∅ — the killer doc's null) and
`D_raw` (Exp = U — P3.1's baseline). Both are in the grammar as the bracketing null controls.
T1/T3 wording at D-1 must use these two names.

**Consumer classes.** Linear raw-flow consumers `C_v(z) = v^T z` (risk notional, latency
notional: v = p ⊙ 1{clock ≤ W}); allocation consumers `C_w(a) = Σ_j w_j c_j` on the deployed
fill counts (linear in counts). Exposure is evaluated on the deployed record
(`C∘D`, Theorem 3 definition); for randomized D (ru draws) the deterministic channels
(eligible_units fields) and the probability channels (draw pmf, expected counts) are
reported separately below.

**Ambiguous sets by training cell** (from the Part II §0 table, engine-grounded):

- **fifo/F_exec cell**: `U_fifo` = never-executed orders at any level + the threshold order's
  hidden depth (q_{j*} − c_{j*}); fiber = translate of `R_{≥0}^{|U|}`.
- **ru per-unit/F_exec cell**: at each touched level, split directions among never-drawn
  orders `K_ℓ = {u : Σ_{i∈neverdrawn(ℓ)} u_i = 0}` (aggregate pinned by `eligible_units`,
  drawn orders pinned by `maker_remaining`) ⊕ never-executed orders at untouched levels
  (orthant).
- **ru aggregate cell**: kernel anonymization (P3) — the fiber contains the fifo-shaped
  orthant; nothing is swap-exposed at this rung beyond the aggregate-recorded directions.

Throughout: interior regime `0 < V* < R*` (exhaustion rounds stratified per P4(iii)); when a
statement needs a clock configuration it is stated as a hypothesis.

### 4.2 Theorem T-1 (one-step exposed-set table — exact, with sign and magnitude)

For each (deployment, cell, consumer class), the exposed set, its sign structure, and its
magnitude order in the injected scale δ (u = δe_i or split δ(e_a − e_b), t ∈ [0,R]):

**(1) D_read: `Exp = ∅` for every consumer.** `C∘D_read` is tape-measurable (Lemma 0
discipline); constant on fibers. Probability-1 detection: none. (Null control.)

**(2) D_raw: `Exp(D_raw, C_v) = {u ∈ U : v^Tu ≠ 0}`** — the full ambiguous set with nonzero
consumer loading. Sign: sign(v^Tu); magnitude Θ(δ) exactly (|v^Tu| linear); detection
probability 1 under μ_R when v_U ≢ 0. (Maximal control; P3.1.)

**(3) D_swap→fifo on the fifo cell: `Exp = ∅` exactly, for all t ≥ 0 — not merely
first-order.** Every direction in `U_fifo` is fifo-silent: appended units on never-executed
orders never reach the queue head (`_select_maker` returns `queue[0]`, matching.py:589–590);
hidden depth at the threshold order j\* cannot change j\*'s fill because the fill is
demand-capped (`fill = min(remaining, maker_qty)`, matching.py:292–296: with incoming
remaining R = V\* − prefix < q_{j*} + t, the fill stays R); never-executed orders at other
levels are untouched by price priority. Hence the deployed fifo tape is *identical* along the
whole ray: `T_fifo(z̄ + tu) = T_fifo(z̄)` for all t ≥ 0, including on the integer lattice (no
tie or crossing events arise: prefix sums at or before the threshold are unchanged; the
exhaustion/tie wall is excluded by the interior regime). Every consumer of the deployed
record is therefore fiber-constant. *This is the exact-blindness half of the swap asymmetry
(O-B point null).*

**(4) D_swap→fifo on the ru cell (split directions): threshold exposure on the arrival
prefix, exact blindness beyond it.** Deploying fifo on the same book, let `F_f` be the fifo
filled set (earliest arrival orders up to cumulative V\*; j\*_fifo the threshold order).
(i) Splits `u = e_a − e_b` between never-drawn orders **both beyond the fifo threshold**
(arrival after j\*_fifo): blind — prefix sums at or before the threshold are unchanged and
neither order is reached. (ii) Splits with an endpoint a ∈ F_f: the deployed fifo fill of a
is `min(R_a, q_a + t·s)` (R_a = demand reaching a); moving quantity *out of* a changes
allocations iff `q_a − δ < R_a`, i.e. iff δ exceeds a's slack `h_a := R_a − (fill of a)`:
magnitude `Θ((δ − h_a)^+)` — an integer-lattice **jump** after a dead zone, sign: a loses,
later orders gain. Note `F_f`, `R_a`, `h_a` depend on never-drawn quantities and are
**instance-level** (not tape-computable in the ru cell; computable from the fixture/prestate
— honest limitation, flagged for O-B's cell assignment: the swap→fifo equivalence test
belongs to the fifo-trained cell where U_fifo is exactly blind by (3)).

**(5) D_swap→ru: all touched-level magnitude directions exposed at Θ(δ/S), sign-definite.**
For u = δe_i on a never-drawn order at a touched level (S = level remaining = the recorded
`eligible_units`): `dp_j/dq_i = −q_j/S² < 0` (j ≠ i), `dp_i/dq_i = (S−q_i)/S² > 0` (strict
while ≥ 2 orders remain at the level, which holds since never-drawn others have positive
remaining). Deterministic channel: the deployed draw records' `eligible_units` field reads
`S + δ` — an exact integer displacement, visible with probability 1 in a single deployed
draw (matching.py:592 computes S as the full queue sum before the RNG call).
Probability channel: expected counts `E[c_j] = V*·p_j` move at `Θ(δ/S)` with the signs above
(sign-definite per direction; consumer contrast sign = sign(w^T dp)). Deeper levels
(untouched in round 1): **silent one-step** under both kernels (price priority) — exposed
only through horizon extension (T-3). At the agg rung: no swap exposure at all (P3 kernel
anonymization — the swap-exposed directions do not exist in the aggregate record).

**(6) D_trunc^W: masking — exposure = id-exposure ∩ window.**
`Exp(D_trunc^W, C_v) = {u ∈ U : supp(u) ⊆ in-window orders, v^Tu ≠ 0}`; out-of-window
directions are dropped from the deployed flow before any consumer reads them. Magnitude on
surviving directions: unchanged (Θ(δ), linear); on dropped directions: exactly 0. Floor
localization: `Var = R²‖v_{U∩W}‖²/12` (orthant) and `(R²/3)p_ℓ²(m_in·m_out/m)` (splits) —
monotone nondecreasing in W, zero when no never-drawn order straddles the latency boundary
(P3.3; O-C). Truncation alone never creates exposure — it is a projection on the flow.

*Proof of (3)–(6).* (3) and (4) are prefix-sum algebra over the arrival-ordered queue with
the engine fill rules cited; the demand-cap argument is displayed in (3); (4)(ii) follows
from `min(R_a, q_a − δ)` vs `R_a`. (5) differentiates the uniform-over-remaining-units draw
pmf p_j = q_j^rem/S (matching.py:592–603) and uses `E[c_j] = V* p̄_j` with the sequential
martingale structure; the eligible_units channel is the literal field value. (6) is the
definition of the masking map. ∎

**Asymmetry corollary (O-B).** Allocation-level divergence: `swap→ru` is Θ(δ/S) > 0
(deterministic eligible_units channel Θ(δ), probability-1 visible) while `swap→fifo` is
exactly 0 on the fifo cell (T-1(3)) — strict, preregistrable, per-level weights 1/S
computable from fixtures (not from the deployed fifo tape, which does not record S — honest
anchoring note).

### 4.3 Theorem T-2 (compositions: no-creation, destruction asymmetry, postponed creation)

**(T-2a) Functorial no-creation (one-step grammar).** Let `D = D_n∘…∘D_1` with each D_k a
one-step grammar map, and let u ∈ T_zF. If for every k the stage-k input is u-invariant
(`D_1(z+tu) = D_1(z)`, and inductively `D_k(…D_1(z+tu)…) = D_k(…D_1(z)…)`) — equivalently u
is blind for every factor at its stage — then the composition is u-blind and
`u ∉ Exp(D, C)` for every consumer C. Consequently, within the one-step grammar **no
composition exposes a direction that every factor is blind to**: exposure of a composition
implies some stage read the direction, and the only one-step readers are the two channels of
T-1(5)–(6) (the level-total denominator `eligible_units`; the window mask on clocks).

*Proof.* Induction on n: output-invariance of D_1 gives identical inputs to D_2; hypothesis
at each stage gives identical outputs; the consumer composes through identical records. The
"only readers" clause is the exhaustive input-sensitivity list of the generators: swap→ru
reads level totals and queue composition at touched levels; swap→fifo reads the arrival
prefix up to the demand threshold; truncation reads clocks; D_read/D_raw are bracketing
controls. ∎ *(This lemma is elementary by design — its content is the exhaustive
input-sensitivity table, i.e. that the grammar has exactly two one-step exposure channels.)*

**(T-2b) Order-asymmetry / destruction theorem (P3.4 elevated).** Fix the ru-relevant
configuration: order i at the touched level, never drawn, `clock_i > W` (out-of-window
maker); aggressor order in-window (`clock ≤ W`; feasible — clocks are per-request metadata,
matching.py:311 puts the aggressor's clocks on the execution records, and `F_exec` carries no
maker clocks). Let u = δe_i. Then:

- `Exp(D_swap→ru ∘ D_trunc^W, ·)` **excludes** u: truncation deletes order i before the swap
  replays, so the deployed flows are literally equal —
  `D_trunc^W(z+tu) = D_trunc^W(z)` ⇒ `P[(A∘T_W)(z+tu) ≠ (A∘T_W)(z)] = 0`. **Composition
  destroys exposure** that the swap factor alone has (T-1(5)).
- `Exp(D_trunc^W ∘ D_swap→ru, ·)` **contains** u, with probability 1 and deterministically:
  the swap replays on the full book, whose level total is `S + δ` — every deployed draw
  record of that level carries `eligible_units = S + δ ≠ S` (matching.py:592 sums the whole
  queue, *level-total, not window-total*) — and the deployed execution records carry the
  in-window aggressor clocks and so survive the outer truncation. Hence
  `P[(T_W∘A)(z+tu) ≠ (T_W∘A)(z)] = 1`. **Composition preserves exposure through the
  denominator channel even when the exposing order itself is out-of-window.**

Therefore `Exp(D_trunc^W ∘ D_swap→ru) ⊋ Exp(D_swap→ru ∘ D_trunc^W)` strictly (the difference
is exactly the set of out-of-window magnitude directions at touched levels):
**deployment order is decision-relevant**, and the strongest form of the O-C/O-B prediction
here is the deterministic eligible_units displacement, not the O(δ/S) probability shift.

**(T-2c) Postponed creation (two-step; the P7 channel inside the grammar).** Let u = δe_i on
order i at a level ℓ′ strictly deeper than round-1's marginal level, and consider the
horizon-extended swap deployment `D_swap→ru ∘ D_2` (clear round 1, mutate the book, clear a
round-2 incoming order that reaches ℓ′). Every one-step factor is u-blind: round-1 swap
never touches ℓ′ (price priority under both kernels), round-1 truncation with
W ≥ round-1 clocks does not read ℓ′'s quantities, and D_read is blind by T-1(1). Yet on the
event `E_{ℓ'}` that ℓ′ is the marginal level in round 2 (positive probability under any
nondegenerate flow — P7's hypothesis; in the engine, levels persist in the book across
rounds and `_select_maker` at ℓ′ sums ℓ′'s whole queue), the round-2 draw records read
`S' + δ ≠ S'` with probability 1, and round-2 draw probabilities move at Θ(δ/S′). Hence
`u ∈ Exp(D_swap→ru ∘ D_2) \ (∪ one-step factor exposures)`: **exposure created by
postponement**, absent in every factor. Conversely, composing truncation *before* round 2
with `clock_i > W` destroys it again (T-2b mechanism).

*Proof.* T-2b: displayed — equality/inequality of deployed records is deterministic through
the eligible_units field (computed before the RNG call, matching.py:592–593); survival of the
execution records under the outer truncation is the aggressor-clock condition. T-2c: P7's
strict-shrinkage mechanism instantiated: the book-update map (fills decrement; untouched
levels persist — matching.py:606–625) makes ℓ′'s quantity a round-2 input exactly on
`E_{ℓ'}`; T-1(5) then applies verbatim at ℓ′. ∎

**(T-2d) Growth classes for the floor under compositions.** Theorem 1's floor localizes
along the exposed directions only: for a composition D, replace U by
`U_D := U ∩ (directions the deployed record reads)` — orthant case `R²‖v_{U_D}‖²/12`, split
case `(R²/3)Σ_{ℓ}(v_i − v̄_ℓ)²` over the levels/orders the deployed record still reads. T-2a
gives `U_{D'∘D} ⊆ U_D ∪ U_{D'}`(stage-wise); T-2b gives the two strict-inclusion patterns;
T-2c gives the strictly-larger `U` of horizon extension. Every quantity involved
(never-drawn sets, eligible_units levels, clock straddling) is tape- or fixture-computable
per the S1a pair grammar (splits preserve eligible_units sequences and all execution
payloads — verified against the fixture draw records).

### 4.4 Answer to the contrived-D attack (scope statement)

1. **The grammar is preregistered** (plan §2 OOD axes + horizons; contract C4), fixed
   before any exposure computation; nothing in §4.2–4.3 was selected after seeing exposure
   structure.
2. **The characterization is exhaustive within the grammar** for the linear consumer
   classes: T-1 enumerates every generator's exposed set with sign and magnitude; T-2a
   (functoriality) closes compositions under "no new channels"; T-2b/c identify the only two
   mechanisms by which composition changes exposure at all (the level-total denominator
   channel and the marginality/horizon channel). There is no residue of unexplained exposure
   inside 𝒢.
3. **Two bracketing null controls** (D_read: Exp = ∅; D_raw: Exp = U) show the nontrivial
   maps sit strictly between the extremes, with the swap pair itself asymmetric
   (exactly-blind vs Θ(δ/S) + deterministic eligible_units displacement) — a contrived-D
   construction would not produce an exact point-null.
4. **Out of scope, honestly:** pro-rata swaps, reverse swap, population/tick axes, adaptive
   or reflexive deployments, nonlinear consumers, and exhaustion/tie boundary strata are
   outside this characterization (the first three are exploratory per plan §2; the boundary
   strata are stratified per P4(iii)). Deployments outside 𝒢 can behave differently; the
   theorem says nothing about them, and the paper must state the grammar's boundary in the
   same sentence as any exposure claim.

---

## 5. Hostile check (self-attack of the weakest steps)

1. **"A1/A2 is textbook measure theory dressed as a prong."** Conceded in part: the
   transport identity and atoms-are-fibers are standard. The prong's value is defensive
   scoping — it fixes *which* object T1's dichotomy lives on (the recorded σ-algebra /
   likelihood-equivalence classes), which is exactly what the attack denied had been done.
   No novelty claim is attached to A1–A2.
2. **Strongest remaining hit on prong (b):** (B4)'s rank invariance needs the immersion
   hypothesis; a referee can exhibit a degenerate parameterization (θ encodes (π, scale)
   with scale pinned) where the FIM rank is 6 for MVHG too. The defense is the explicit
   condition-split: the *identification* statement (B1–B3: fiber dimension on pool
   coordinates, likelihood-equivalence classes) is unconditional and chart-free; only the
   FIM *rank encoding* is immersion-conditional. S3's preregistered ladder is evaluated at
   an immersion point (B = I in R⁹), so the condition holds there; the writeup must keep
   the split visible or the referee wins the rank version.
3. **Strongest remaining hit on prong (c):** C4's equivariance hypothesis
   (`D∘φ = φ_out∘D`) is doing real work, and for fiber-warping ψ the swap fails it — by
   design (C5). A hostile reader can say prong (c) is then "naturality where trivial,
   non-invariance where it matters." The honest answer: that is precisely the intended
   trichotomy (chart re-description harmless; reference measure declared; fiber variation =
   the science), but the writeup must not oversell C1–C4 as new mathematics — they are
   scoping lemmas, and the exact-constant content is contract-relative. If D-1 wording
   claims more, prong (c) is attackable.
4. **Strongest remaining hit on KT-G5:** T-1(4) (swap→fifo on the ru cell) depends on
   instance quantities (F_f, R_a, h_a) that the ru tape does not record — the
   characterization of that cell is instance-level, not tape-computable. This is disclosed
   and the O-B equivalence cell is assigned to the fifo-trained arm (where T-1(3) is exact),
   but a referee may still call the ru-cell row "characterization by cases." Second hit:
   T-2a is a tautology (induction on output-invariance); its content is entirely the
   input-sensitivity table — if that table had a gap (some generator reading a coordinate I
   missed), no-creation would be false. Mitigation: the generator list is short and each
   map's reads were verified against matching.py line-by-line (cited); the risk is
   mis-specification of a *future* enriched grammar (fixture enrichment D1_03 adds orders,
   not new map semantics — but any new deployment map must be added to the grammar's
   preregistration before exposure claims extend to it).
5. **Clock-feasibility of T-2b:** the out-of-window-maker / in-window-aggressor
   configuration is legal in the schema (clocks are per-request metadata) but *does not
   occur in the current 21–22-event frozen fixtures*; the deterministic eligible_units
   displacement prediction is therefore testable only after the D1_03 fixture enrichment
   (clock-straddling never-drawn orders — exactly the enrichment the plan already mandates).
   If enrichment is not authorized, T-2b's empirical arm (O-C) degrades to the
   monotonicity-only form of P3.3.
6. **Boundary strata:** all statements are interior-regime; exhaustion rounds (V\* = R\*)
   and tie walls (V\* on a prefix sum) are stratified away per P4(iii)/P9. A referee pushing
   the boundary sees different (mostly trivial or discontinuous) exposure behavior —
   conceded, stratified, preregisterable from price-only quotes.
7. **Interaction with KT-G1's toric concession:** the static per-unit equivalence class is a
   Diaconis–Sturmfels toric fiber (uniform interleavings). Nothing here contradicts that:
   KT-G4/G5 characterize identification content and deployment exposure, not static fiber
   novelty; the DS/contingency-table citations of the appendix reduction check remain
   mandatory, and DPIOT remains the owner of the parameter-space residue (prong d).

**Reframe recommendation (keyed to plan §12).** None of the results here is refuted, so no
REFRAME fires. Conditions to carry into D-1 wording: (i) prong-(d) concession sentence with
DPIOT/Perturb-Argmax citations in T1; (ii) the D_read/D_raw nomenclature split replacing the
inconsistent `D_id` usage; (iii) the exposed-set characterization must always be stated with
its grammar scope clause (§4.4 item 4); (iv) the eligible_units deterministic displacement
promoted to the strongest O-B/O-C prediction (it is probability-1 visible, integer-exact,
and fixture-testable post-enrichment). If the red team at D-1 still judges prong (c)
insufficient, the fallback is risk-register row "KT-G2 separation-lemma failure" wording
(T2 repositioned as risk characterization) — prong (c)'s naturality lemmas survive that
reframe intact, since they make no novelty claim.

## 6. Statement-level status

| Statement | Status | One-line reason |
|---|---|---|
| KT-G4(a) Prop A (σ-algebra transport; atoms=fibers; rank equivalence) | proven | elementary but complete; conditions: standard-Borel tape (holds), interior regime |
| KT-G4(b) Prop B (MN never jumps / MVHG jumps at V\*≥2; transport through any smooth reparam) | proven | family-level unconditional; FIM-rank form conditional on immersion (stated) |
| KT-G4(c) Prop C (floor naturality; zero-structure chart-free; exposed-set naturality) | proven_with_conditions | naturality unconditional; C4 needs D-transport compatibility; constant is reference-measure-relative |
| KT-G4(d) positive-dimensionality in θ-charts | conceded (chart-dependent, by design) | DPIOT owns the residue; T1 wording carries the concession |
| KT-G5 T-1 (one-step exposed-set table) | proven | engine-grounded prefix/pmf algebra; ru-cell swap→fifo row instance-level (disclosed) |
| KT-G5 T-2a (functorial no-creation) | proven | induction; content = exhaustive input-sensitivity table |
| KT-G5 T-2b (order asymmetry / destruction) | proven | deterministic eligible_units channel; needs the clock configuration (legal, not in current fixtures) |
| KT-G5 T-2c (postponed creation via horizon) | proven_with_conditions | on the P7 event E_{ℓ'} (positive probability under nondegenerate flow); two-round book persistence engine-grounded |
| KT-G5 T-2d (floor localization under compositions) | proven | direct from Theorem 1 + T-2a–c |

**Grounding files (absolute).**
/Users/howardwang/Desktop/playground/ecophys/scripts/lab_asset/matching.py (lines 285–296,
311, 585–604, 606–625); /Users/howardwang/Desktop/playground/ecophys/scripts/lab_asset/schema.py
(TapeRecord hash fields); /Users/howardwang/Desktop/playground/ecophys/experiments/lab_asset_a2/a2_exit_20260905/
(both fixtures' tape.jsonl — read-only, untouched); grounding docs listed in the header.
