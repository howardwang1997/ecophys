---
note: >-
  Verbatim output of a planning-workflow agent (2026-09-06), grounded in the frozen lab-asset-v3
  artifacts and the D-2 evidence map. Theorem status: propositions/proofs below are D-1 working
  material, NOT claimed results of the paper. Companion to
  ecomd_reexploration_experiment_plan_2026-09-06.md.
---

# Statistical contract v1 (candidate, D-1 working material): Paper D → ALPHA market cube port

# Statistical Contract Port: Paper D → ALPHA Market Cube (FROZEN CONTRACT v1 candidate)

Grounding read (all paths absolute):
- `/Users/howardwang/Desktop/playground/ecophys/papers/paper_d_constraints/main.tex` (contract source, lines 286–345, 431–441), `/Users/howardwang/Desktop/playground/ecophys/papers/paper_d_constraints/SUBMISSION_EXECUTION_PLAN_20260902.md`, `/Users/howardwang/Desktop/playground/ecophys/papers/paper_d_constraints/SUBMISSION_CHECKLIST.md`
- `/Users/howardwang/Desktop/playground/ecophys/experiments/lab_asset_a2/a2_exit_20260905/schema_spec.json` + `bundle_manifest.json` (lab-asset-v3; engine RNG state is inside `state_hash`; `allocation_draw` is a per-unit execution payload field; replay must equal the tape record-by-record)
- `/Users/howardwang/Desktop/playground/ecophys/papers/proposal/ecomd_random_unit_priority_thesis_v2_2026-08-27.md` (M0–M3 ladder; draws without replacement, probability proportional to remaining quantity)
- `/Users/howardwang/Desktop/playground/ecophys/ecomd/eval/synthetic_dgps.py`, `/Users/howardwang/Desktop/playground/ecophys/ecomd/training/fact_surrogates.py`

---

## Part 1 — Element-by-element port audit (Task 1)

| # | Paper D element (verbatim source) | Verdict | Market-native reason |
|---|---|---|---|
| 1 | "Seeds, not trajectories or rollout frames, are the inference units; each bootstrap draw resamples the complete paired … seed vector" | **KEEP principle, AMEND object** | Inference is no longer deterministic given checkpoint: `random_unit` consumes engine RNG at train and inference; the DGP engine itself consumes RNG (bound into `state_hash`). A "seed" must become the **root of a frozen RNG derivation tree** (data/prestate, init, minibatch order, training-kernel stream, K inference-kernel streams). Kernel draws and rollout rounds are explicitly **nested, never inference units** — this must be written down or a reviewer counts 30×8×8 units. |
| 2 | 50,000-draw paired bootstrap; 95% CI for materiality / smaller-statistical, 90% CI inside [−δ,+δ] for practical additivity | **KEEP VERBATIM** (mechanics) | Percentile paired bootstrap on seed indices survives untouched. Only mechanical change: the resampled vector is the **paired eight-cell** seed vector (Paper D cube resampled the four-cell trained vector + derived cells; here all 8 cells exist per seed). |
| 3 | SESOI δ = 0.1·Ȳ_R0 (reference cell mean) | **KEEP form, AMEND reference, ADD guard** | R00 must be pinned to one output coordinate (freeze: increment coordinate — the market analog of Paper D's residual reference); the endpoint aggregates ≥2 conserving channels (units, cash ticks) at different scales so a frozen DGP-native channel scaling is required; integer-lattice errors make the **single-record** metric discrete but the **per-seed aggregate** continuous, so 0.1·mean survives — except when Ȳ_R00 ≈ 0, which needs a frozen degeneracy rule (Clause C6). |
| 4 | Ordered classification {material non-additivity / smaller statistical non-additivity / practical additivity / unresolved} | **KEEP VERBATIM** | ALPHA cube is factorially isomorphic to the Paper D cube (coordinate × training enforcement × inference enforcement; J = D00 − D10 − D01 + D11). No change. Add one new label value, "unresolved (reference-degenerate)", which is a *sub*-label of unresolved and confers no positive claim. |
| 5 | Secondary interaction sign-flip tests, Holm-corrected across the mandatory cells; cannot override the primary | **KEEP mechanism, AMEND family definition** | Paper D's "12 mandatory cells" (3 resolutions × 4 horizons) does not exist here. The mandatory family must be re-derived exactly (Clause C9): **16 = 4 evaluation axes × 4 horizons per preregistered block, 4 blocks**, Holm within block. Without this clause the family is undefined and multiplicity control is decorative. |
| 6 | One-shot analyzers; "no grid, seed, threshold, or outcome definition may change" | **KEEP VERBATIM + extend scope** | The one-shot rule must additionally cover the frozen draw count K, the kernel-stream derivation, the fixture-generation procedure, and the axis generators. Any gate failure = analyzer abort with no partial metrics. |
| 7 | Analyzer gates: record coverage, run-ID uniqueness, source/config hashes, seed pairing, parameter parity, finite metrics, checkpoint binding, target invariant, horizon-one projection identity | **KEEP + market-native extensions** | Each gate has a market analog (Clause C13/G-list): the horizon-one **clearing identity** (through-M on the DGP's realized request stream must reproduce the DGP tape byte-exactly via the lab-asset replay validator) replaces the horizon-one projection identity; exact integer conservation on through-M cells; `allocation_rule` binding; zero-optimizer-step attestation for surgery cells. |
| 8 | Frozen macros: all tables/macros generated from hashed analysis JSON | **KEEP VERBATIM** | Add the amendment ledger (Clause C16) as a generated macro so the paper cannot silently drop a deviation. |

**Verdict summary: nothing is "cannot apply."** The two elements that look dead on arrival (SESOI on integer channels; seed-as-unit under stochastic M) are salvageable by amendment, and the amendments are themselves the scientific content (T1 granularity, T3 exposure).

---

## Part 2 — The four hard problems (Task 2)

### 2a. M is stochastic under `random_unit`: paired-seed and tape-likelihood protocol

Randomness inventory per seed: (i) DGP sampling (prestate, agent population, request stream), (ii) training (init tensor, minibatch order — already paired by Paper D discipline), (iii) **training-time kernel draws** (through-M arms), (iv) **inference-time kernel draws**, (v) neural decode. The frozen resolution is a **two-level hybrid — request-level CRN + draw-level averaging**:

1. **Request-level common random numbers (exact).** All eight cells within a seed, and all axes that do not change the DGP, see byte-identical request streams, prestates, and init/minibatch state. This is only possible because the primary-truth DGP is constrained to the **M0/M1-lumpable policy class** (thesis v2 ladder: actions depend only on anonymous book state, inventory, cash, induced value — never on allocation identity). Under M0/M1 the executed request stream is invariant to the allocation kernel, so CRN is exact, not approximate. **This is a DGP design constraint that must be frozen at D0**; it is the single load-bearing assumption of the whole pairing contract. M2 (feedback-adaptive) settings are reflexive/exploratory only (Part 4).
2. **Kernel-draw CRN + K-draw averaging.** Each seed spawns K = 8 inference-kernel streams (`spawn(seed_root, "kernel", k)`, k = 1…8, counter-based/SeedSequence derivation frozen by library+version pin). The **same K streams are replayed for every cell that consumes draws, within a seed**, across all axes. Per-seed cell value = mean over K draws. Deterministic-kernel cells (fifo, pro_rata) execute the identical evaluation 8 times; the 8 records must be **byte-identical** — this converts the wasted compute into an inference-determinism gate (G8). Neural decode is frozen deterministic (no sampling heads at eval).
3. **Training-time kernel stream**: one seed-spawned stream, replayed across all through-M arms within the seed (arms share minibatch order, so draw alignment is exact). Through-M training under integer/combinatorial M uses the preregistered surrogate family (Onoda et al. ICLR 2026; surrogate-loss DFL 2025) — the surrogate choice is frozen at D0, not tuned on outcomes.
4. **Bootstrap resamples seeds, never draws.** The K-draw mean is the per-seed estimand (kernel expectation inside the seed average); draw-level Monte Carlo error O(σ_kernel/√8) enters seed variance and is therefore covered conservatively by the seed-level percentile bootstrap. Variance identity for the paired contrast: Var(D̂) = Var_seed(μ_D) + E[σ²_D]/K, and CRN makes σ²_D small precisely where the arms share draws — the variance-reduction premise of the paired bootstrap is preserved, which is what justifies inheriting 50,000 draws and 30 seeds verbatim.
5. **Tape-level pairing: NO for confirmatory inference, YES for mechanism diagnostics.** Conditioning the cube on a single realized tape would change the estimand to a tape-conditional quantity and conflate draw noise with fiber structure. But for the **T1/T3-facing diagnostics** the per-unit `allocation_draw` field supports a frozen **tape-likelihood diagnostic**: the likelihood of the realized per-unit tape under each candidate within-fiber flow (probability proportional to remaining quantity, draws without replacement), reported as a one-shot descriptive profile (secondary, no Holm, no confirmatory status). This is exactly the evidence that T2's "divergence is mechanism-attributable" needs (vanishes when M_k removed), and it is kept out of the cube's confirmatory machinery.
6. **Kernel-swap axis (T3 bridge)**: DGP truth tapes are generated under FIFO; through-M inference cells are deployed under `random_unit` (K = 8 draws); the truth reference stays the original FIFO tape. The reverse swap and `pro_rata` swaps are exploratory.

K is frozen at 8 now; a **DGP-only, zero-GPU, engine-only variance preflight** (no model training, no model metrics) may be PI-authorized before D0 to move K within {4, 8, 16}; after D0, K is immutable (one-shot).

### 2b. SESOI on integer/lattice conserving channels — frozen definition

The per-event conserving-channel errors are integer (units, cash ticks), but the per-seed endpoint is an aggregate and therefore real-valued; 0.1·mean is not automatically degenerate. The failure modes are (i) scale incommensurability across channels and (ii) Ȳ_R00 ≈ 0 (then δ → 0 and every nonzero interval is "material" — the classification silently degrades into a significance test). Frozen definition (Clause C5–C6):

- **Endpoint.** Y(seed, cell, axis, horizon) = RMS over rollout rounds and conserving channels of the **channel-scaled** error: Y = sqrt( mean_ch mean_t ( (x̂_ch,t − x_ch,t) / s_ch )² ), where x̂ is the simulator's rolled-out conserving channel and x the DGP truth channel; s_ch = frozen DGP-native per-event innovation std for channel ch (volume in units; cash in ticks), computed **from the DGP generator alone** (analytic values or a hash-sealed DGP-only sample generated by the frozen fixture procedure) — never from any model output, never from a pilot that saw model metrics.
- **SESOI.** Per stratum s = (lineage, DGP, axis, horizon): δ_s = 0.1 · Ȳ_R00(s), where R00(s) = the (increment, raw-train, raw-infer) cell evaluated **in the same stratum**. This preserves the Paper D semantics ("10% of what the unconstrained pipeline typically errs in this regime") and keeps δ axis-proportional — OOD axes get proportionally larger thresholds, exactly as Paper D's coarser resolutions did.
- **Reference-degeneracy guard.** If Ȳ_R00(s) < 1.0 scaled unit (one average per-event DGP innovation std), the stratum is auto-classified **"unresolved (reference-degenerate)"** and reported with no positive label — never rescoped to another endpoint, never dropped. The primary stratum additionally has three preregistered fallback strata (Clause C9) in case the primary is degenerate; if all four are degenerate, the SESOI machinery is inoperative (see diesIf).
- **No clamping, no repair.** Raw arms are never clamped onto the lattice (Paper D precedent: clamping is an unregistered nonlinear intervention); through-M cells' conservation violation must be **exactly zero** (integer-exact) — but note the endpoint is conserving-channel **rollout error against DGP truth**, which is NOT structurally zero for through-M cells (book-state divergence propagates through M). This is what makes the estimand path-dependence attribution rather than constrained-is-better superiority.
- **Why not switch to an absolute-unit δ:** the aggregated metric is continuous, the relative interpretation survives the lattice, and changing δ's form would break verbatim inheritance and invite the "δ was retuned" attack. Keep 0.1; add the floor; disclose in the amendment ledger.

### 2c. Holm family definition — mandatory cells vs exploratory periphery, EXACTLY

The 8 cube cells are the **factorial structure, not the multiplicity contexts** (in Paper D the 12 mandatory cells were resolution × horizon evaluation contexts, each carrying one interaction test computed from the full cube). Port:

- **Preregistered blocks** (4): B1 = (L1 EcoMD v2 × lab-asset-v3) — **primary block**; B2 = (L1 × synthetic_dgps); B3 = (L2 fact-surrogate × lab-asset-v3); B4 = (L2 × synthetic). Synthetic DGPs enter as exogenous driver processes feeding the **same frozen request generator**, so all endpoint definitions are unchanged across blocks (one endpoint definition everywhere).
- **Mandatory family per block (16)**: evaluation axes {ID, agent-population ×2, tick ×2 coarser, kernel-swap FIFO→random_unit} × horizons {1, 4, 16, 31} rollout rounds. Each cell carries the three-way interaction J computed from all 8 cube cells at that context, with δ_s from Clause C6.
- **Primary cell**: B1, kernel-swap axis, horizon 16. Single prespecified primary; its ordered classification is not Holm-adjusted and not overridable by secondaries (verbatim Paper D). Horizons 1 and 4 exist because Paper D's mechanism finding ("absent at one step, appears by horizon four") is expected to repeat; horizon 31 is the stress context.
- **Holm families**: sign-flip tests on the 16 mandatory interaction cells, **Holm within each block** (4 families of 16). Mirrors Paper D's per-design separate freezing (Advection / SWE / U-Net each had their own gate).
- **Axis-contrast secondaries (preregistered, separate family)**: per block, the three differences (J_OOD-axis − J_ID) at horizon 16 — the T3 "market-native generalization absent in PDEs" estimands — Holm-corrected as a 3-test family per block.
- **Architecture-transfer gate (preregistered)**: block B3 passes transfer iff primary J material AND ≥ 8/16 mandatory cells material (Paper D U-Net gate was ≥ 6/12 — same fraction). A failed gate is reported as an architecture boundary (U-Net lesson), never hidden, never re-gated.
- **Exploratory periphery (no confirmatory status, mandatory "exploratory" label, excluded from abstract, no Holm, no SESOI claims)**: per-cell simple effects beyond the interaction; endpoint class flips enumeration; reflexive cell (Part 4); tape-likelihood diagnostics; SGD within-fiber drift measurements (T4 is conjecture-only — cite Soudry 2017 + "The Loss Does Not See the Basis but Adam Does" 2026); reverse/pro-rata kernel swaps; M2 adaptive DGP runs; any post-transfer-gate lineage follow-up.
- **Reporting-all rule** (ALPHA novelty condition): every cell, axis, horizon, block, class flip, and null appears in the generated tables — reporting is unconditional; confirmatory *status* is the thing the family definition controls.

### 2d. OOD-axis contrasts and class flips as preregistered findings vs multiplicity

- Axis **main contexts** (the 4 axes) enter the confirmatory machinery only through the 16-cell mandatory family (interaction J per axis × horizon) and the 3-test axis-contrast family at h = 16. Nothing else about the axes is tested.
- **Class flips** (ordered classification differing between blocks, lineages, or axes — e.g., B1 material, B3 practical additivity) are **preregistered descriptive findings, not tested hypotheses**: they are deterministic readouts of the frozen classification machinery applied to preregistered strata, so they carry no additional p-values and no multiplicity debt. They may be narrated ("the interaction fails to transfer to L2 at the tick-shift axis") but cannot be claimed as positive discoveries; the only preregistered lineage-level *decision* is the transfer gate. This is the same device Paper D used for the U-Net boundary.
- The axis generators themselves are frozen procedures (Clause C4): population axis regenerates prestates at 2N with induced capacities rescaled per the lab-asset-v3 schema (`induced_*_capacity_exceeded` rejection semantics preserved); tick axis regenerates with tick 2Δ and the frozen price-band scaling rule; kernel-swap axis regenerates nothing (truth tapes unchanged; only deployment kernel changes). All fixture tapes hashed at D0.

---

## Part 3 — Zero-training surgery cells (Task 3)

The 4 surgery cells = each trained (coordinate, training-enforcement) arm evaluated at the **other** inference enforcement, on the same locked checkpoint, **zero optimizer steps** — the market analog of Paper D's "changing only the compatible forward map at evaluation."

- **Checkpoint lock.** All 240 trained checkpoints (4 arms × 30 seeds × 2 lineages) SHA-256 hash-locked the moment the last training record lands and before any metric is read; the lock manifest is an analyzer input. Surgery records must reference the parent checkpoint hash; **parameter parity**: surgery-cell parameters byte-identical to the parent trained cell (Paper D gate, verbatim port).
- **No training randomness.** Verified by attestation: optimizer-step counter equals training-final (no further steps), no optimizer state in the eval config, and byte-identical re-execution of a frozen 5% sample of records (G9).
- **Inference randomness contract for surgery arms = identical to trained-cell inference** (this is the whole point: the only difference between a trained cell and its surgery partner is the forward map). Deterministic neural decode; the same K = 8 seed-spawned kernel streams replayed (streams are properties of the **seed**, not the arm, so surgery cells inherit identical draws); per-seed value = K-draw mean. Through-M surgery cells consume the draws; raw surgery cells ignore them but still record n_draws = 8 (uniform record schema).
- **Record-coverage arithmetic (frozen).** Per block: 30 seeds × 8 cells × 4 axes × 4 horizons × 8 draws = **30,720 records**; 4 blocks = **122,880 confirmatory evaluation records**, plus 240 training records (one per training) and 4 × 30 × 4 = 480 horizon-one clearing-identity probe records. Reflexive/exploratory records live in a separate namespace and are not counted here. Any count mismatch = analyzer abort.

---

## Part 4 — Reflexive cell firewall (Task 4)

Reflexive deployment cell = simulator vs a simple adapting execution policy (sim-in-loop), exploratory only. Five frozen firewalls:

1. **Namespace separation.** Reflexive records carry `exploratory=true, reflexive=true`, separate run-ID prefix, separate output directory; the confirmatory analyzers' input globs exclude the namespace by construction; the frozen macro tables have no reflexive slot.
2. **Temporal separation.** Reflexive execution is scheduled only **after** all four confirmatory one-shot analyzers have run and their analysis-JSON hashes are published — eliminating any channel by which reflexive observations could motivate "rechecking" or rederiving a confirmatory cell.
3. **Statistical separation.** No ordered classification, no SESOI, no sign-flip tests, no Holm, no CIs presented as inference; descriptive summaries only, with the mandatory label "exploratory, excluded from confirmatory inference"; may appear only in a marked exploratory subsection citing TRADES 2025 and DEX closed-loop 2026 for the paired-seed descriptive discipline it does follow.
4. **No gate inputs.** Reflexive metrics never feed any gate, threshold, or claim; a reflexive crash does not affect confirmatory record-coverage gates (its own coverage is reported as-is).
5. **No retro-hypotheses.** Any reflexive observation that suggests a hypothesis must be written as future work and is barred from being tested on the existing records in this paper.

---

## Part 5 — FROZEN CONTRACT v1 (D0-adoptable verbatim)

### Definitions

**Seed** = the root of a frozen RNG derivation tree spawning named substreams: `data` (prestate + request stream), `init`, `minibatch`, `train_kernel`, `kernel:1..K`. **Cell** = a (coordinate, training-enforcement, inference-enforcement) triple. **Stratum** = (block, axis, horizon). **Arms within a seed share** the `data`, `init`, `minibatch`, and `train_kernel` streams; cells within a seed share the `kernel:1..K` streams.

---

**C1 — Units and pairing.** The inference unit is the seed. Kernel draws, rollout rounds, and tapes are nested within seeds and are never inference units. Each bootstrap draw resamples the complete paired **eight-cell** seed vector. n = 30 seeds per block, fresh never-reused ranges: B1/B2 seeds 11000–11029; B3/B4 seeds 12000–12029. Arms within a seed share sampled trajectories (request streams and prestates), minibatch order, and initial parameter tensors (Paper D discipline, verbatim).

**C2 — Randomness contract.** (a) Primary-truth DGP policies are frozen in the M0/M1-lumpable class (actions depend only on anonymous book state, own inventory, cash, induced values — never on allocation identity), so executed request streams are kernel-invariant and request-level CRN is exact. (b) K = 8 inference-kernel draws per seed per cell, derived `spawn(seed, "kernel", k)`, replayed identically across cells within a seed; per-seed cell value = K-draw mean. (c) Deterministic-kernel cells execute 8 identical evaluations; byte-identity is gate G8. (d) Neural decode is deterministic at eval; no sampling heads. (e) A DGP-only, zero-GPU variance preflight may adjust K within {4, 8, 16} before D0 with PI authorization; after D0, K is immutable.

**C3 — Cube structure and estimands.** Trained arms: (c, t), c ∈ {absolute next state, increment}, t ∈ {raw, through-M}; each evaluated at inference e ∈ {raw, through-M} → 8 cells Y_{c,t,e}. D_{te} = Ȳ_absolute,te − Ȳ_increment,te; T_0 = D_00 − D_10; T_1 = D_01 − D_11; E_0 = D_00 − D_01; E_1 = D_10 − D_11; **J = D_00 − D_10 − D_01 + D_11**; φ_train = (T_0 + T_1)/2, φ_infer = (E_0 + E_1)/2, φ_train + φ_infer = D_00 − D_11. Sign convention: positive J means the absolute-minus-increment coordinate contrast grows with joint through-M enforcement. M = the exact combinatorial clearing layer (volume and cash conservation, unit integrality, tick lattice, priority kernel ∈ {fifo, pro_rata, random_unit}); through-M training uses the preregistered surrogate family frozen at D0. **No confirmatory test compares through-M vs raw for superiority; the estimand is path-dependence attribution.**

**C4 — Blocks, axes, horizons, fixture generators.** Blocks B1–B4 as in Part 2c. Axes: ID; agent-population ×2 (prestates regenerated at 2N, induced capacities rescaled per lab-asset-v3 schema); tick ×2 coarser (tick 2Δ, frozen band-scaling rule); kernel-swap (DGP truth under FIFO; through-M inference under random_unit; truth reference unchanged). Horizons: {1, 4, 16, 31} autoregressive clearing rounds. All DGP fixtures are produced by the frozen fixture-generation procedure from seed roots; every prestate and tape SHA-256 is bound at D0 (existing lab-asset-v3 bundle manifest `fea8a136…9581c` is the schema anchor; new per-seed fixtures extend, never modify, schema `lab-asset-v3`).

**C5 — Endpoints.** Primary endpoint: conserving-channel rollout error against DGP truth, Y = sqrt(mean_ch mean_t ((x̂_ch,t − x_ch,t)/s_ch)²), channels = {volume units, cash ticks}, s_ch frozen DGP-native per-event innovation std from the generator alone. Through-M cells' conservation violation must be exactly zero (integer-exact); raw cells are never clamped or repaired. Book-state and price-path errors are preregistered secondary endpoints, reported descriptively, outside all Holm families.

**C6 — SESOI.** Per stratum s: δ_s = 0.1 · Ȳ_R00(s), R00(s) = (increment, raw-train, raw-infer) cell in stratum s. Guard: if Ȳ_R00(s) < 1.0 scaled unit → stratum is "unresolved (reference-degenerate)", no positive label, reported, never dropped, never rescoped. Primary fallback strata (in order): B1 kernel-swap h31, B1 tick-shift h16, B1 population h16.

**C7 — Ordered classification (Paper D verbatim).** *Material non-additivity* if the 95% paired-bootstrap interval for the estimand lies wholly above +δ_s or below −δ_s; *smaller statistical non-additivity* if that interval excludes zero but the first rule fails; *practical additivity* if the 90% interval lies wholly inside [−δ_s, +δ_s]; *unresolved* otherwise (with the reference-degenerate sub-label per C6). Both interaction and additivity are falsifiable; an interval spanning zero and a SESOI boundary receives no positive label.

**C8 — Bootstrap (Paper D verbatim mechanics).** 50,000 draws, percentile intervals, seed-level resampling of the complete paired eight-cell vector; draws are averaged within seed and never resampled.

**C9 — Primary and multiplicity.** Primary cell: B1, kernel-swap, horizon 16. Holm families: sign-flip tests on the 16 mandatory interaction cells per block, Holm within block; secondaries cannot override the primary classification. Axis-contrast family: per block, three (J_axis − J_ID) at horizon 16, Holm within the triple. Architecture-transfer gate: B3 passes iff primary J material AND ≥ 8/16 mandatory cells material; failure reported as boundary.

**C10 — Class flips and reporting-all.** All cells, axes, horizons, blocks, flips and nulls are reported unconditionally; class flips are preregistered descriptive findings carrying no p-values and no confirmatory status; the transfer gate is the only preregistered lineage-level decision.

**C11 — Zero-training surgery cells.** Derived from hash-locked checkpoints; zero optimizer steps; parameter parity byte-identical to parent; inference randomness identical to C2 (shared seed-owned kernel streams). Lock order: last training record → hash lock → metric unlock.

**C12 — Reflexive firewall.** The five firewalls of Part 4, verbatim.

**C13 — One-shot analyzers and gates.** Each analyzer runs once, on complete records, after gates G1–G12 pass, in order; any failure aborts with no partial metrics; no rerun without a new frozen, hash-recorded amendment.

**C14 — Record-coverage contract.** Exactly: 240 training records; 122,880 confirmatory evaluation records (30 × 8 × 4 × 4 × 8 per block × 4 blocks); 480 horizon-one clearing-identity probes; reflexive records uncounted here (separate namespace).

**C15 — Frozen macros.** All tables and macros generated from the hashed analysis JSON; macros include draw count K, fixture-manifest hashes, and the amendment ledger.

**C16 — Amendment ledger (generated, non-omissible).** Every deviation from Paper D appears in the generated ledger: (1) seed = RNG-tree root (stochastic M); (2) eight-cell resampling vector; (3) R00 coordinate pinned to increment; (4) channel-scaled multi-channel endpoint; (5) reference-degeneracy guard; (6) Holm families 4 × 16 (Paper D: 1 × 12); (7) axis-contrast family (new, market-native); (8) K-draw CRN protocol; (9) transfer-gate fraction 8/16 = 6/12 preserved; (10) clearing-identity gate replaces projection-identity gate.

### One-shot analyzer gate list

- **G1 Record coverage**: exact counts per C14, per cell/axis/horizon/draw; no extras, no missing.
- **G2 Run-ID uniqueness and seed pairing**: each seed's 8 cells share `data`/`init`/`minibatch`/`train_kernel` stream hashes and config hashes.
- **G3 Source/config binding**: DGP fixture manifest hashes (including lab-asset-v3 anchor `fea8a136…9581c`), `schema_version == "lab-asset-v3"`, git SHA, `config.yaml` hash, seed ranges per C1.
- **G4 Checkpoint binding**: 240 checkpoint SHA-256 vs lock manifest; surgery records reference parent hash.
- **G5 Parameter parity + zero-step attestation**: surgery parameters byte-identical to parent; optimizer-step count = training-final.
- **G6 Horizon-one clearing identity**: through-M on the DGP's realized request stream reproduces the DGP tape byte-exactly (lab-asset replay validator, record-by-record including every `state_hash`).
- **G7 Conservation exactness**: through-M inference cells have exactly zero volume/cash conservation violation at every step (integer-exact); no clamping anywhere.
- **G8 Deterministic-kernel draw identity**: fifo/pro_rata cells' 8 draw-records byte-identical.
- **G9 Determinism replay**: frozen 5% seeded sample of records re-executed byte-identically.
- **G10 Field validity**: finite metrics; `pre/post_best_bid/ask` present; `allocation_rule` matches the cell/axis spec; `n_draws == 8`.
- **G11 Namespace hygiene**: no exploratory/reflexive namespace records in any confirmatory input.
- **G12 Macro binding**: analyzer emits macros exactly once from the analysis JSON; hashes published.

### Compute arithmetic check

Trainings: 4 arms × 30 seeds × 2 lineages = 240 — exactly Paper D's 240 (Advection 120 + SWE 120), which fit ≈ 2 weeks on 2 × V100; the ≈ ×2 ceiling (≈ 4 weeks) covers through-M surrogate overhead. Evaluation: 122,880 records × ≤ 31 clearing rounds each — integer engine + single forward pass per round, negligible vs training. Hard operational prerequisite: both V100 disks (98% / 96% full) must be cleaned before any run. Mac/`ecophys` for editing and CPU smoke of the analyzer gates only.

### Residual notes for the paper text

- The dedicated gauge-conflation remark (V4): the contract's surgery cells are the empirical exhibit — members indistinguishable to the training loss (within-fiber) yet distinguished by the deployment maps (kernel swap, truncation) — position against Quotient-Space Diffusion Models (ICLR 2026), Neural Mechanics (ICLR 2020).
- T2 consumer-variance lower bound: the axis-contrast family (C9) is the confirmatory quantitative home; the tape-likelihood diagnostic (2a.5) supplies mechanism attribution (divergence vanishes when M_k removed).
- T4 stays conjecture-only; any within-fiber drift measurement lives in the exploratory periphery with its citation pair (Soudry 2017; "The Loss Does Not See the Basis but Adam Does", 2026).
- Governance: this contract authorizes nothing. It is preregistration-ready text for D0; execution requires D0 outcome-blind freeze plus explicit PI authorization.
