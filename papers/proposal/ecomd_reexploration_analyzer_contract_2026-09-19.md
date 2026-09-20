# EcoMD Re-Exploration — Analyzer Contract

**File** (freeze-list path): `papers/proposal/ecomd_reexploration_analyzer_contract_2026-09-19.md`
**Status**: DRAFT v0.3 — adversarial-audit findings incorporated (audit run 2026-09-19: 22 agents, 12 confirmed findings fixed; provenance labels, O-test count column, Stage-2 bootstrap-seed coverage, h = 64 descriptive stream, 15-seed halt translation, audit-publication story, and citation prefixes corrected). Verifier pass complete 2026-09-19: PASS-with-notes; 3 residual defects (one citation mis-attribution, one header overstatement, three bare § refs) fixed. **All 16 Part 10 flags PI-ratified at their defaults 2026-09-19** (decision `pi_analyzer_contract_flags_ratification_20260919`; "整体批，授权"); no flag remains open. NOT FROZEN. This file enters the prereg v2 §1.3(2) freeze list (per-file sha256 plus one commit-level hash over the ordered file list, lexicographic by path) at the D0 outcome-blind freeze on **2026-09-21** (Annex B(j); amended pre-hash from 2026-10-09 on 2026-09-21 by PI decision `pi_campaign_advance_20260921`, Annex C item C-13; originally 2026-09-19 per C-12).
**Authoring window**: pre-D0, Mac-legal document work (OPS Part A §3 "writing all empirical protocols into frozen macros"; D0 calendar items 8–10, authorized under the D1 blanket/build scope).
**Authority**: none. This contract authorizes no run, no analysis execution, no data access. Analyzer execution requires the D0 outcome-blind freeze plus explicit PI authorization (CV1 governance; OPS Part A §3; MENU compute gate). After the freeze this file is immutable; any change is a new frozen, hash-recorded amendment (C13/C15), and any breach is STOP-class, no repair (PR §1.3, §8.3).

## Source documents

| Tag | Document | Role here |
|---|---|---|
| PR | `papers/proposal/ecomd_reexploration_prereg_v2_2026-09-06.md` | Governing statistical preregistration (C1–C16, G1–G12, §3.4 counts, §4.1 staging, §4.4 machinery, §5 estimators, Annex B, Annex C supersessions) |
| CV1 | `papers/proposal/ecomd_reexploration_contract_v1_2026-09-06.md` | Amended statistical contract (C-clause originals; Part 2c families; Part 3 surgery; Part 4 firewalls) |
| OPS | `papers/proposal/ecomd_reexploration_d1_killer_tests_and_ops_2026-09-06.md` | Ops plan (session table, budgets, verifier machinery, halt rules); superseded in part by PR (Annex C) |
| MENU | `papers/proposal/ecomd_reexploration_estimator_menu_2026-09-06.md` | Through-M estimator menu (KT-A4 audit; fixture gate; instability criteria) |
| SIMCON | `papers/proposal/ecomd_reexploration_simulator_contracts_2026-09-06.md` | Engine/schema facts (event grammar, hashes, seeding, build register E-1..E-5, L1/L2 items) |
| CAL | `papers/proposal/ecomd_reexploration_d0_calendar_proposal_2026-09-08.md` | D0 readiness items 8–10; build workflow (draft → adversarial audit vs prereg v2 → verifier) |

Known supersessions applied throughout (Annex C): OPS seed namespaces 1000–1029/2000–2014 → 11000–11029/12000–12029 (C-2); OPS "Holm across the 8 mandatory cells" → 16-cell mandatory family per block (C-3); OPS (data, init, train) triplet → C1 RNG tree checked by G2 stream hashes; OPS t4 wording → the v2 mechanical trainability threshold with the C9 gate excluded; MENU "K = 8" → K = 16 (C-1); OPS underscore classification labels → Annex B(g) macro names; CV1 C14 printed 122,880/240/480 → PR §3.4 restatement 299,520/450/420 (C16 item (15)); OPS full-grid 480 trainings → two-stage §3.4 enumeration.

## 0. Provenance discipline

Every substantive statement in Parts 1–9 carries one of:

- **[pin]** — verbatim or direct import from a frozen source, cited by tag and clause/line.
- **(derived)** — operationalization forced by frozen text, with the forcing stated. Derivations add no threshold, count, or statistical rule absent from the sources.
- **(FLAG-n)** — not pinned in any frozen source. A proposed default was stated for PI ratification at the pre-freeze review; **all 16 flags were ratified at their defaults on 2026-09-19** (decision `pi_analyzer_contract_flags_ratification_20260919`, recorded under `research/discovery/decisions/`); Part 10 records them. No flag remains open; any post-hash change to a ratified default is a new frozen, hash-recorded amendment (Part 11).

---

## 1. Scope

**Deliverable** [pin, CAL item 8; PR §1.3(2)]: the freeze-list analyzer-contract file containing (i) the one-shot G1–G12 execution order, (ii) the input record schema, (iii) the bootstrap mechanics, (iv) the macro emission — plus the OPS Pre-D0 row deliverable "analyzer macros + dummies".

**In scope**: the four confirmatory one-shot analyzers (Part 2); the A10 audit analysis unit (Part 2.2); gates G1–G12 operationalization (Part 4); the input record schema (Part 5); estimands and statistics (Part 6); bootstrap mechanics (Part 7); macro emission (Part 8); dummies and pre-freeze validation (Part 9).

**Out of scope** (each item is executed or governed elsewhere; the analyzer program never executes them):

- Cleanup scripts and the D0-S1 node-cleanup session — CAL item 9, disjoint from item 8; no cleanup logic here, no analyzer logic there [pin, OPS §3 item 1; CAL item 9].
- The S3/EP3 exact FIM rank-grid machine-check — a separate one-shot CPU-exact instrument (PR §4.3 EP3; PR §2.5 (A3′)), seeds 20260974–20260976 (Annex B(c)); its engine-law-mismatch outcomes are STOP-class (PR §8.3) but it is not one of the four analyzers and not gated by G1–G12.
- Stage-2 H5 items (identical-input replay through the recorded request subsequence with only `allocation_rule` swapped; the single-maker negative-control run) — run-gated [AUTH], outside the four analyzers [pin, PR §2.5].
- The reflexive deployment cell — C12 firewalls; schedulable only after all four analyzers' analysis-JSON hashes publish (Part 3.1).
- T4 drift telemetry — exploratory register only (EP5; Annex B(d) subsets).
- All training, corpus generation, evaluation, and surgery execution — ops-plan territory; this contract consumes their records only.

**Compute placement** [pin, PI activation rule 2026-09-19]: every execution associated with this contract — gate runs, analyzer runs, dummy validation, replay re-execution — happens on the remote V100 nodes over ssh. Nothing of any size, including CPU smokes and dry-runs, runs on the MacBook; the Mac carries document authoring, governance, and git only. This supersedes the OPS "Mac, legal now" smoke/dry-run classifications for anything that executes code [pin, OPS Pre-D0 row, as amended by the activation rule]. The analyzers themselves are CPU-only, overlapped with the GPU streams, budget 12 V100-h campaign-total (8 Stage-1 / 4 Stage-2) for ~1,000 estimands [pin, OPS §2, §3 budget rows].

---

## 2. The one-shot analyzers

### 2.1 The four-analyzer enumeration (derived; FLAG-3)

Frozen facts: exactly **four** confirmatory one-shot analyzers exist, and the reflexive cell is schedulable only after all four have run and their analysis-JSON hashes are published [pin, C12; PR §4.6]. No package document enumerates the four by name (checked: PR v1/v2, CV1, OPS, MENU, SIMCON, CAL).

This contract pins the four as **one analyzer per block**:

| Analyzer | Block | Lineage × DGP | Stage / session | Seeds | Confirmatory status |
|---|---|---|---|---|---|
| `A_B1` | B1 (primary) | L1 × lab-asset-v3 | Stage 1, D0-S4 | 11000–11029 | confirmatory |
| `A_B3` | B3 | L2 × lab-asset-v3 | Stage 1, D0-S4 | 12000–12029 | confirmatory |
| `A_B2` | B2 | L1 × synthetic variant A | Stage 2, D0-S5 | 11000–11014 | descriptive robustness (C16(13)) |
| `A_B4` | B4 | L2 × synthetic, both variants (A and B) | Stage 2, D0-S5 | 12000–12014 | descriptive robustness (C16(13)) |

Derivation: (i) the campaign's confirmatory record workload decomposes into exactly four block-level streams (PR §3.4 per-block table; B4's two DGP variants per D1_05 are one block with two sub-blocks) — any roster that omits B2/B4 fails the count, since no frozen source assigns those records to any other analyzer; (ii) C16(13) keeps Stage-2 analyzers inside the one-shot/C13/G-gate discipline — mandatory-family tests "executed and reported", Holm p-values "computed for completeness and labeled non-confirmatory" — so "the four confirmatory one-shot analyzers" names the C13 analyzer program as a whole (the counterpart of the exploratory/reflexive namespace), not a claim that Stage-2 cells carry confirmatory status; (iii) the A10 audit and the truncation analyses are not block-analyzer candidates: the truncation contrasts are secondary families emitted inside their block analyzers (C16(14)), and the audit is a separately published one-shot robustness unit outside all Holm families (Part 2.2), not a block-level record stream. The campaign therefore publishes **five** analysis-JSON hashes — the four block analyzers plus the audit unit — and C12's "all four … analysis-JSON hashes published" is satisfied by the four block-analyzer hashes among them.

`A_B4` covers both variant sub-blocks (B4-variantA and B4-variantB) in one one-shot run: one analyzer, two record sub-streams, one analysis JSON [derived from D1_05 + PR §3.4].

### 2.2 The A10 audit analysis unit (derived; FLAG-3)

The KT-A4 two-estimator audit analysis is a **separate one-shot unit executed in the D0-S4 session immediately after `A_B1`/`A_B3`**, not one of the four. Grounds: MENU classifies the ST-vs-PAM comparison as "a preregistered robustness gate on the cube, not a confirmatory superiority test", outside all Holm families; PR §3.4 gives the audit its own records (7,680) and checkpoints (30, inside the G4 total of 450); PR §5.4 binds it under the same one-shot rules (C13, C11, C14, Annex B(a)). It is executed under the same gate pass as the D0-S4 session (its records and checkpoints are inside that session's G1/G4 scope), and it **publishes its own analysis JSON and hash** under G12/C13 like every one-shot analyzer; C12's four-hash condition is satisfied by the four block-analyzer hashes (Part 2.1), of which the audit hash is a fifth, not one.

### 2.3 Execution order

- **D0-S4** (2026-10-07/08 at D0 = 2026-09-21): gates G1→G12 in order, scoped per Part 4.1 → `A_B1` → `A_B3` → A10-audit → Stage-2 go/no-go via t1–t4 (mechanical only) [pin, OPS D0-S4 row; C13; PR §4.1].
- **D0-S5** (if triggered): gates G1→G12 scoped to the Stage-2 record set → `A_B2` → `A_B4` [pin, OPS D0-S5; derived scoping per Part 4.1].
- **D0-S6**: campaign-total reconciliation against the full PR §3.4 table (Part 4.1).

`A_B1` runs first because the primary cell and all three fallback strata are B1 cells [pin, C6/C9]. No analyzer output feeds the Stage-2 go/no-go [pin, PR §4.1: mechanical triggers only]; the order among analyzers carries no statistical meaning — each is one-shot on complete records.

### 2.4 Cancellation edge (FLAG-5)

If Stage 2 is cancelled (t1–t4 failure or the shrink ladder), `A_B2`/`A_B4` never execute, so "all four … analysis-JSON hashes published" (C12) is unsatisfiable as written: every resolution deviates from the frozen sentence on some conjunct, and the deviations are stated symmetrically; the PI ratified the stub-JSON default 2026-09-19 (Part 10).

Proposed default: on cancellation, emit `A_B2`/`A_B4` **not-run stub analysis-JSONs** (every cell `class_not_run` per C10) with published hashes, preserving the four-hash publication literally. Recorded deviation: a stub stretches C12's "have run" (the two analyzers never ran) and C15's "generated from the hashed analysis JSON" is vacuous for content-less stubs.

Alternative (requires a new frozen, hash-recorded amendment; not a default): discharge the C12 temporal condition by publication of (i) the `A_B1`, `A_B3`, and A10-audit analysis-JSON hashes and (ii) the frozen mechanical cancellation decision record standing in for the two missing analyzer hashes. Recorded deviation: this replaces two of the four analyzer hashes with a non-analyzer record, waiving both conjuncts of the frozen unlock condition. Rationale either way: cancellation is itself a frozen mechanical outcome (never outcome-triggered, PR §4.1), and with no B2/B4 cells in existence the firewall's purpose — no reflexive observation can motivate rechecking or rederiving a confirmatory cell [pin, CV1 Part 4 firewall 2] — is fully served.

### 2.5 What the analyzers never consume

Reflexive records (namespace-separated, uncounted, C12/G11); T4 telemetry (EP5); exploratory periphery items (reverse kernel swap; M2 adaptive DGP runs; per-cell simple effects beyond the interaction; class-flip enumeration as findings) [pin, CV1 Part 2c]; pro_rata executions (not an engine kernel; any record showing pro_rata execution is rejected, C3/D1_14).

---

## 3. Execution semantics (C13)

- **C13 verbatim** [pin]: "Each analyzer runs once, on complete records, after gates G1–G12 pass, in order; any failure aborts with no partial metrics; no rerun without a new frozen, hash-recorded amendment."
- **One-shot scope extension** [pin, PR §3.3 tail]: the frozen draw count K, kernel-stream derivation, fixture-generation procedure, axis generators, and estimators are inside the one-shot discipline — any post-D0 change is a frozen, hash-recorded amendment or nothing.
- **Complete-records precondition** [pin, OPS §3 item 5]: analyzer execution happens only after both training workers complete, under `outcome_access: metric_values_printed_or_inspected: false`; no early analysis. The first-record gate (10 records / 5 seeds / both enforcement mechanisms, D0-S3 day 2–3) validates the Part 5 schema on live records before the campaign proceeds.
- **Abort semantics**: any gate failure or analyzer failure aborts with **no partial metrics emitted**; macro emission (G12) has no path that fires on a partial run. Post-freeze, any analyzer rerun without a PI deviation memo is STOP, NO REPAIR [pin, PR §1.3; PR §8.3].
- **Halt rule, paired-seed loss** [pin, OPS §4; PR §8.3]: per-run loss of a seed removes that seed-index from the paired bootstrap for **all arms of that seed-index** (pairing preserved); more than 3/30 seeds lost on any mandatory cell → stop, PI decision; never silent seed substitution. **15-seed translation (FLAG-16)**: the frozen threshold is worded against 30-seed cells only; for the Stage-2 15-seed mandatory blocks (and any 12-seed shrink variant) the contract's proposed default is the proportional reading — halt at > 10% of the cell's seeds lost (≥ 2 of 15; ≥ 2 of 12) — matching PR §8.3's proportional "> 15% nonfinite" phrasing style and erring toward earlier halt; the literal reading (> 3 seeds regardless of cell size) is recorded as the closed alternative. PI-ratified 2026-09-19 (Part 10 row 16).
- **Estimator fixture competence gate**: `tests/test_through_m_estimators.py` (20/20 at D-1, read-only, 7 manifest files sha256 re-verified, nothing written) must pass immediately before G1 at every analyzer session, on the executing node, as an external pre-gate (derived placement; FLAG-14). Both estimators failing it at any point → cube collapses to surgery-only (C11 zero-training surgery cells on raw-trained checkpoints) and the campaign STOPs pending PI decision; no post-D0 repair, λ/σ re-tuning, or estimator substitution without a new frozen, hash-recorded amendment [pin, MENU; STOP-class per PR §8.3].

### 3.1 Session timing under the amended freeze

D0 = **2026-09-21** [pin, Annex B(j), C-13]. Only day-offsets are operative [pin, CAL §3]; dates below are computed from D0 for convenience: D0-S4 = days 16–17 = 2026-10-07/08; t2 deadline "Stage 1 complete by D0+26d" = 2026-10-17; 4-week hard ceiling = 2026-10-19 (reserved for the shrink ladder, not slippage); D0-S5 = days 17–28; D0-S6 = days 28–29.

**Reflexive scheduling supersession (FLAG-4)**: the OPS session table's "reflexive cell days 14–16" slot (inside D0-S3) is stale under every reading of C12 — reflexive execution is schedulable only after all four analyzers have run and their hashes published, which happens at the earliest at the end of D0-S5. C12 (prereg v2, later and more specific) governs. Consequence recorded: the ~6 V100-h reflexive line moves out of the D0-S3 window in burn accounting; the reflexive cell (10 seeds 11000–11009 / 12000–12009, cells {R00, R11}, D1, both lineages) is scheduled after the four-hash publication event.

**Stage-2 go/no-go inputs** [pin, PR §4.1, verbatim semantics]: (t1) cumulative burn < 1,150 V100-h; (t2) Stage 1 complete by D0+26d; (t3) L1 convergence-failure rate ≤ 15% (quality gate, not performance); (t4) ≥ 28/30 L2 seeds reach finite training loss under the day-5 thresholds on D1. The C9 architecture-transfer-gate result is NOT an input to any Stage-2 decision; any outcome-triggered launch downgrades the D2 block to exploratory or forbids it (PR §8.3). Shrink ladder: slip > 5 d → variant A only at 12 seeds; slip > D0+26 d or burn > 1,150 V100-h → cancel Stage 2 [pin, CAL §3 tail].

---

## 4. Gates G1–G12

### 4.0 Verbatim gate list (v2 amended text) [pin, PR §3.3]

- **G1 Record coverage**: exact counts per the ratified C14 (Section 3.4 table), per cell/axis/horizon/draw; no extras, no missing.
- **G2 Run-ID uniqueness and seed pairing — with namespace-disjointness sub-check** (folded in at v2, panel R3-8; NOT a new gate): each seed's 8 cells share data/init/minibatch/train_kernel stream hashes and config hashes; AND every preregistered instrument/instrument-analysis namespace is disjoint from every training namespace and from every other: S3 robustness seeds (Annex B(c)), enrichment master 20260972, resampler namespace 20260973, K-preflight 31000–31099, bootstrap seeds (Annex B(a)), and training namespaces 11000–11029 / 12000–12029.
- **G3 Source/config binding**: DGP fixture manifest hashes (incl. lab-asset-v3 anchor `fea8a136b0c3e19a00bddcb131a1540ca40fda6c1576dbc949001dbf76a9581c`, the canonical value; Annex C typo inventory governs audit reconciliation), schema_version == "lab-asset-v3", git SHA, config.yaml hash, seed ranges per C1.
- **G4 Checkpoint binding** (amended at v2, panel R2-1): **450** checkpoint sha256 vs lock manifest (240 Stage-1 mandatory + 180 Stage-2 + 30 audit-cell; Section 3.4); surgery records reference parent hash.
- **G5 Parameter parity + zero-step attestation**: surgery parameters byte-identical to parent; optimizer-step count = training-final.
- **G6 Horizon-one clearing identity**: through-M on the DGP's realized request stream reproduces the DGP tape byte-exactly (lab-asset replay validator, record-by-record including every state_hash).
- **G7 Conservation exactness**: through-M inference cells exactly zero volume/cash conservation violation at every step (integer-exact); no clamping anywhere.
- **G8 Deterministic-kernel draw identity**: fifo cells' K = 16 draw-records byte-identical; raw-inference kswap-stratum duplicates byte-identical to their ID-stratum evaluations (C4(iii)).
- **G9 Determinism replay**: frozen 5% seeded sample of records re-executed byte-identically. Selection rule pinned at v2 (Annex B(b)): deterministic stride — sort all record keys lexicographically within each record class, select every 20th record starting at index 0 (exactly 5%), no RNG.
- **G10 Field validity**: finite metrics; pre/post_best_bid/ask present; allocation_rule matches the cell/axis spec per the pinned kernel-swap stratum definition (C4(i)–(iii), including allocation_rule = fifo on raw-inference duplicates); n_draws == 16.
- **G11 Namespace hygiene**: no exploratory/reflexive namespace records in any confirmatory input.
- **G12 Macro binding**: analyzer emits macros exactly once from the analysis JSON; hashes published.

Gate failure at any point aborts the session with no partial metrics (C13). All gate code executes on the nodes (Part 1).

### 4.1 G1 operationalization — per-session scoping (derived; FLAG-6) and the count tables

The two-stage design (C16(13)) forces per-session gate scoping: at D0-S4 the Stage-2 records do not exist, so G1/G4 cannot be evaluated against campaign totals there. Scoping rule (derived; FLAG-6): each analyzer session evaluates G1/G4/G6 against its own record sub-tables; the campaign-total table is reconciled at D0-S6 (freeze audit). G1's population is exactly the count tables of this Part; the h = 64 descriptive stream (PR C4: "h = 64 recorded descriptively only"; PR §4.2) is outside that population by C4's own "descriptively only" restriction — h = 64 records are neither counted nor gate-rejected, are excluded from all confirmatory machinery and from the 299,520 total, and are reported per C10 (derived handling). Counting granularity is per cell/axis/horizon/draw; any count mismatch = analyzer abort [pin, CV1 Part 3].

**Mandatory-axes evaluation records** (per seed-block unit = 8 cells × 4 axes × 4 horizons × 16 draws = 2,048) [pin, PR §3.4]:

| Block | Lineage × DGP | Seeds | Records | Session |
|---|---|---|---|---|
| B1 | L1 × lab-asset | 30 | 30 × 2,048 = **61,440** | D0-S4 |
| B3 | L2 × lab-asset | 30 | 30 × 2,048 = **61,440** | D0-S4 |
| B2 | L1 × variant A | 15 | 15 × 2,048 = **30,720** | D0-S5 |
| B4-variantA | L2 × variant A | 15 | 15 × 2,048 = **30,720** | D0-S5 |
| B4-variantB | L2 × variant B | 15 | 15 × 2,048 = **30,720** | D0-S5 |

Stage 1 subtotal 122,880; Stage 2 subtotal 92,160 (panel R2-1 adjudication); mandatory-axes campaign total **215,040**. The full 4-block 30-seed grid (245,760) is not the authorized design.

**Truncation deployment passes** (ID axis, all 8 cells, all 4 horizons, K = 16 per condition; L1 blocks both conditions, L2 blocks trunc_lag only — C16(14)) [pin, PR §3.4]:

| Block | Conditions × seeds × 8 × 4 × 16 | Records | Session |
|---|---|---|---|
| B1 | 2 × 30 × 8 × 4 × 16 | **30,720** | D0-S4 |
| B3 | 1 × 30 × 8 × 4 × 16 | **15,360** | D0-S4 |
| B2 | 2 × 15 × 8 × 4 × 16 | **15,360** | D0-S5 |
| B4-variantA | 1 × 15 × 8 × 4 × 16 | **7,680** | D0-S5 |
| B4-variantB | 1 × 15 × 8 × 4 × 16 | **7,680** | D0-S5 |

Campaign total **76,800**.

**Audit cell A10** [pin, PR §3.4]: +30 trainings (D1 block, L1 lineage, 30 paired seeds 11000–11029; reuses B1's D1/L1 fixture streams — same data/init/train seeds, only the estimator differs; no new probes, no new fixtures); evaluation records = 1 cell × 30 seeds × 4 axes × 4 horizons × 16 = **7,680**. Session D0-S4.

**Campaign totals (D0-S6 reconciliation target)** [pin, PR §3.4]: 215,040 + 76,800 + 7,680 = **299,520** confirmatory evaluation records; **450** trainings/checkpoints = 240 (Stage 1: 4 arms × 30 seeds × 2 lineages) + 180 (Stage 2: 120 variant-A both lineages + 60 variant-B L2-only) + 30 (audit A10); **420** horizon-one probes = 120 (B1) + 120 (B3) + 60 (B2) + 60 (B4-A) + 60 (B4-B), per block-lineage × DGP-variant unit at 4 axes, K-independent. Reflexive namespace excluded by construction, uncounted (C12).

Per-session G1/G4/G6 scope: **D0-S4** = 122,880 mandatory + 46,080 truncation + 7,680 audit evaluation records; 270 checkpoints (240 + 30); 240 probes (B1 + B3). **D0-S5** = 92,160 mandatory + 30,720 truncation; 180 checkpoints; 180 probes. (derived arithmetic from the tables above.)

### 4.2 G2 operationalization

- Run-ID uniqueness (derived discharge of G2's title clause; the frozen gate text names the check but defines no field or criterion): every record carries `run_id` (Part 5.2) and G2 asserts run-ID uniqueness over the session input set — a duplicate `run_id` with divergent content is an abort. Redundant by design with G1's exact counts and record_key uniqueness, which already abort on any duplicate or missing record at (block, record_class, condition, axis, horizon, cell, seed, draw) granularity; the explicit assertion exists so the gate's title clause has an implementation path in the schema.
- Pairing check per seed: the 8 cells share `data`/`init`/`minibatch`/`train_kernel` stream hashes and config hashes [pin]. Definitions per CV1 C1: seed = root of the frozen RNG tree; **cell** = (coordinate, training-enforcement, inference-enforcement) triple; arms within a seed share `data`, `init`, `minibatch`, `train_kernel`; cells within a seed share `kernel:1..K`.
- Namespace disjointness set (pairwise, verbatim constants) [pin, Annex B(a)/(c), PR §7.4, G2]: training 11000–11029 (B1/B2) and 12000–12029 (B3/B4); Stage-2 subsets 11000–11014 / 12000–12014; reflexive/telemetry subsets 11000–11009 / 12000–12009; S3 robustness arms 20260974, 20260975, 20260976; enrichment master 20260972; resampler 20260973; K-preflight 31000–31099 (masters 31000–31031); bootstrap seeds as derived per Annex B(a) (mod-2^63 values — not disjoint from the integer namespaces by construction, only with overwhelming probability, so the G2 sub-check asserts actual disjointness against every named namespace; seeds recorded in the analyzer manifest).
- Rank-seed collision sub-check (derived; adopted from SIMCON §6 flag 5): existing `rank_seed = seed + rank*10000` and `auxiliary +5,000,000` (`train_distributed.py:722-727`) must not collide with any named substream or namespace above; the seed/stream manifest (E-5) records the full derivation.

### 4.3 G3 operationalization

Binding fields on every record (Part 5.2): DGP fixture manifest hash, schema_version == "lab-asset-v3" (the backward-compatible lab-asset-v3.1 enrichment extension, Annex B(e)-adjacent PR §7.2, is accepted for enriched-fixture inputs — arrival_clocks as pre-session prestate metadata, deliberately excluded from prestate_hash), git SHA, config.yaml hash, seed ranges per C1. The frozen A-2 exit bundle is read-only and never mutated; enriched-fixture manifests extend it and are separately hashed (parent lineage anchor `fea8a136…9581c`; `schema_spec.json` sha256 `c2341ce73f8c32d1b395fad81f0bd4c68a3ac0de0e235ea4d638acc48c24346a`) [pin, SIMCON; PR §7.2]. Per-event payload field lists are bound by hash reference to `schema_spec.json` (`payload_fields`), never restated here [pin, SIMCON §1].

### 4.4 G4 operationalization

450 checkpoint sha256 values against the lock manifest, decomposed 240 + 180 + 30, scoped per session (Part 4.1). The lock manifest is itself an analyzer input [pin, CV1 Part 3]. Lock order: last training record → hash lock → metric unlock [pin, C11]. Every surgery record references its parent checkpoint hash [pin, G4]. Checkpoint payload carries (or is sidecar-bound to) `n_draws`, `allocation_rule`, seed, and corpus-manifest binding so G4/G10 are self-contained [pin, SIMCON L1-5]; the G4 hook is `training_log.json` `checkpoint_sha256` [pin, SIMCON §2.5/§3.5].

### 4.5 G5 operationalization

Surgery parameters byte-identical to parent; optimizer-step count = training-final (zero new steps) [pin]. Surgery cells read only final optimizer-stripped CPU-offloaded lock checkpoints [pin, OPS §3 item 4].

### 4.6 G6 operationalization

420 horizon-one probes campaign-total, K-independent, scoped per session (240 / 180; Part 4.1). Validation instrument: `lab_asset.replay.replay` — record-by-record comparison of sequence, event type, all four hashes (`pre/post_state_hash`, `pre/post_aggregate_state_hash`), and byte-level `record_to_json` equality, including every `state_hash` [pin, SIMCON §1; G6].

### 4.7 G7 operationalization

Every through-M inference record: exactly zero volume- and cash-conservation violation at every step, integer-exact; no clamping anywhere in any cell [pin]. The record schema carries per-step conservation-violation counters for through-M cells (Part 5.2).

### 4.8 G8 operationalization

(i) fifo cells' K = 16 draw-records byte-identical [pin]. (ii) Raw-inference cells ((·, raw-train, raw-infer) and (·, through-M-train, raw-infer)) have no deployment kernel; their kswap-stratum evaluations are **byte-identical duplicates** of their ID-stratum evaluations, recorded separately for record-coverage symmetry with `allocation_rule` pinned to the training-time kernel field (`fifo`) and n_draws == 16; the analyzer checks duplicate byte-identity, and a mismatch is a G8/G10 failure [pin, C4(iii)]. R00(s) is numerically identical across the ID and kswap strata by construction, so δ_s at kswap is anchored to ID-scale R00 [pin, C4(iv)].

### 4.9 G9 operationalization — record classes and the stride

Selection rule verbatim [pin, Annex B(b)]: lexicographic sort of record keys within each record class; every 20th record from index 0; exactly 5%; no RNG. Re-execution happens on the nodes; output is byte-compared.

**Record-class taxonomy** (derived; FLAG-7). Classes are chosen so "exactly 5%" is well-defined (each class size divisible by 20):

| Class | Contents | Size | 5% sample |
|---|---|---|---|
| RC1-mandatory-B1 / -B3 / -B2 / -B4A / -B4B | mandatory-axes evaluation records, per block sub-table | 61,440 / 61,440 / 30,720 / 30,720 / 30,720 | 3,072 / 3,072 / 1,536 / 1,536 / 1,536 |
| RC2-truncation-B1 / -B3 / -B2 / -B4A / -B4B | truncation deployment-pass records, per block | 30,720 / 15,360 / 15,360 / 7,680 / 7,680 | 1,536 / 768 / 768 / 384 / 384 |
| RC3-audit | audit-cell evaluation records | 7,680 | 384 |
| RC4-probes | horizon-one clearing-identity probe records | 420 | 21 |

Training records are **not** a G9 class: 450 is not divisible by 20, so "exactly 5%" is undefined for it, and trainings are already hash-covered by G4 rather than re-executed (derived; FLAG-7).

**Record key** (derived; FLAG-7): `record_key` = dot-joined string with pinned field order `(block_id, record_class, condition, axis, horizon, cell_id, seed, draw_index)`, numerics zero-padded (seed 5 digits, horizon 2, draw 2); the lexicographic sort is byte-wise over this string. Annex B(b) pins the stride, not the key serialization; this contract supplies it.

**L1-4 precondition** [pin, SIMCON §2.4]: G8/G9 byte-identity for L1 rests on the L1-4 generator-threading change (threading the rollout `generator` into `TypedRelationalPotential._sample_edges`) having landed pre-freeze with its own test. The freeze session records the L1-4 status in the freeze record; if L1-4 did not land, cross-node replay rests on an uncontracted global-RNG assumption and G9 for L1 is flagged accordingly in the analyzer manifest (FLAG-12).

### 4.10 G10 operationalization

Field validity per record: finite metrics; `pre/post_best_bid/ask` present; `allocation_rule` matches the cell/axis spec per C4(i)–(iii) including `allocation_rule = fifo` on raw-inference duplicates; `n_draws == 16` [pin]. Uniform-schema rule: raw cells record the draws they ignore, with n_draws == 16 [pin, CV1 Part 3, as amended by the K = 16 supersession].

### 4.11 G11 operationalization

No exploratory or reflexive namespace record in any confirmatory input [pin]. Input globs exclude the reflexive namespace by construction; reflexive records carry `exploratory=true, reflexive=true` and a separate run-ID prefix [pin, CV1 Part 4 firewall 1]. A reflexive crash never blocks a confirmatory analyzer [pin, OPS §4].

### 4.12 G12 operationalization

Macros emitted exactly once, generated from the hashed analysis JSON, hashes published (Part 8; FLAG-11 for the channel).

---

## 5. Input record schema

### 5.1 Record classes and their provenance

The schema below is the same schema the D0-S3 first-record gate checks [pin, OPS §3 item 5]. It covers: mandatory-axes evaluation records (RC1), truncation deployment-pass records (RC2), audit-cell evaluation records (RC3), horizon-one probe records (RC4), training/manifest records (450, G4-bound, not G9-strided), surgery records (inside the 8-cell grid; see 5.5), and the h = 64 descriptive-only stream (PR C4/§4.2; see 5.2 — outside all confirmatory counting and not a G9 class).

### 5.2 Common envelope (every record)

| Field | Content | Gate |
|---|---|---|
| `record_key` | Part 4.9 serialization | G9 |
| `record_class` | RC1/RC2/RC3/RC4/training/descriptive-h64 | G1, G9 |
| `run_id` | run identifier; asserted unique over the session input set (Part 4.2) | G2 |
| `block_id` | B1 / B3 / B2 / B4_variantA / B4_variantB | G1 |
| `lineage`, `dgp_variant` | L1/L2; lab-asset-v3 / synthetic-A / synthetic-B | G1, G3 |
| `seed` | integer in the block's C1 namespace | G2 |
| `cell_id` | (coordinate c, training enforcement t, inference enforcement e) triple per CV1 C1 | G1, G10 |
| `axis` | ID / population(2N) / tick(2Δ) / kernel-swap | G1, G10 |
| `horizon` | {1, 4, 16, 31} confirmatory; 64 descriptive-only (PR C4 "recorded descriptively only" — outside all G1/G8/G10 confirmatory counting and all Holm families, reported per C10) | G1 |
| `draw_index` | k ∈ 1..16 (present on all eval records, including raw cells that ignore draws) | G8, G10 |
| `condition` | ID / trunc_lag / trunc_cap | G1 |
| `config_sha256`, `git_sha` | run binding | G2, G3 |
| `fixture_manifest_sha256` | DGP fixture manifest hash (frozen bundle or enrichment manifest) | G3 |
| `schema_version` | "lab-asset-v3" (v3.1 enrichment extension accepted for enriched inputs) | G3 |
| `stream_hashes` | data / init / minibatch / train_kernel (shared per seed across arms) | G2 |
| `checkpoint_lock_sha256` | parent lock hash (surgery/cross cells and training records) | G4, G5 |
| `allocation_rule` | fifo / random_unit_within_price; fifo on raw-inference duplicates per C4(iii) | G10 |
| `n_draws` | 16 on every eval record | G8, G10 |
| `metrics` | finite endpoint/statistic values | G10 |
| `pre/post_best_bid`, `pre/post_best_ask` | BBO fields | G10 |
| `conservation_violation_steps` | per-step volume/cash counters (through-M inference cells; all zero) | G7 |
| `pre/post_state_hash`, `pre/post_aggregate_state_hash` | the four record hashes | G6, G9 |
| `estimator_id`, `estimator_seed_provenance` | A10 records only (see 5.4) | G2/G3 |

Payload-level fields are bound by hash reference to `schema_spec.json` `payload_fields` (14 event types) and are never restated here [pin, SIMCON §1].

### 5.3 Evaluation-record payload specifics

- F_exec projection (draw-consuming analyses) [pin, D1_01/SIMCON]: execution payloads + `allocation_draw` + pre/post BBO only; request-side events and `order_accepted.resting_quantity` excluded.
- Allocation-draw fields on the random-unit arm: `{price, eligible_units, selected_unit, maker_order_id}` [pin, SIMCON §1].
- Execution-payload fields used by forward-exactness validation: maker id, quantity, maker_remaining [pin, MENU fixture rows 2–3].
- Conserving-channel truth series for endpoint Y: extracted from engine state via `regenerate()` (cash/inventory are engine state, not tape payload fields) [pin, SIMCON §1; build item E-4]. Channels are the two aggregate per-clearing-round totals {executed volume units, executed cash ticks} [pin, C5 v2 pin].

### 5.4 Audit-cell records (RC3)

A10 = the increment-coordinate, through-M-train, raw-infer cell (`Y_increment,through-M,raw`), D1 lab-asset-v3 block, L1 lineage, 30 paired seeds 11000–11029, sharing data/init/train seeds and the training-time kernel stream with the ST run of the same cell — estimator identity is the only manipulated factor [pin, MENU; PR §5.4]. RC3 records carry `estimator_id ∈ {straight_through, perturb_and_map}` and the RNG-tree seed provenance (never the module default 20260906, which is fixture/replay-only) [pin, MENU].

### 5.5 Surgery records (derived placement; FLAG-8)

The 8-cell grid per (seed, axis, horizon) consists of 4 native cells (t = e) and 4 cross-enforcement cells (t ≠ e). The cross cells are the C11 zero-training surgery cells: inference-only deployment of a hash-locked parent checkpoint under the other enforcement map, zero optimizer steps, parameters byte-identical to parent, inheriting the seed-owned kernel streams [pin, C11; CV1 Part 3]. They are counted inside the RC1/RC2 enumeration (no separate PR §3.4 row exists for them) and are the P3-hysteresis instrument's inputs (Part 6.9). FLAG-8 records this placement for PI confirmation, since OPS separately says "4 surgery cells per trained checkpoint (inference-only)" without a PR §3.4 count row.

### 5.6 L2 condition set

PR §3.4 governs: all blocks carry the same 4 mandatory axes; L2 blocks carry trunc_lag only (no trunc_cap) per C16(14). The OPS Stage-1 line "all 8 eval conditions on L1, 6 on L2 (drop trunc_cap, pop_4x on L2)" predates v2 and is superseded in part: the trunc_cap L2 de-scope survives (C16(14)); the pop_4x L2 drop has no counterpart in the v2 uniform 4-axis enumeration and does not apply (derived supersession; FLAG-13).

---

## 6. Estimands and statistics

### 6.1 Cube and estimands [pin, C3]

Trained arms (c, t), c ∈ {absolute next state, increment}, t ∈ {raw, through-M}; each evaluated at e ∈ {raw, through-M} → 8 cells. D_{te} = Ȳ_absolute,te − Ȳ_increment,te; J = D_00 − D_10 − D_01 + D_11; T_0 = D_00 − D_10, T_1 = D_01 − D_11 (training-enforcement contrasts at inference enforcement raw / through-M); E_0 = D_00 − D_01, E_1 = D_10 − D_11 (inference-enforcement contrasts at training enforcement raw / through-M); φ_train = (T_0 + T_1)/2; φ_infer = (E_0 + E_1)/2; φ_train + φ_infer = D_00 − D_11. Subscript order in D_{te} is (training, inference). Positive J = the absolute-minus-increment contrast grows with joint through-M enforcement.

Engine kernels are exactly {fifo, random_unit_within_price}; pro_rata is not an engine kernel and never executes in any cell (S3 exact-arithmetic only, D1_14). No confirmatory test compares through-M vs raw for superiority; the estimand is path-dependence attribution.

### 6.2 Endpoint [pin, C5]

Y = sqrt(mean_ch mean_t ((x̂_ch,t − x_ch,t)/s_ch)²), channels pinned to exactly two aggregate engine-level conserving channels per clearing round: {total executed volume units, total executed cash ticks}; no per-actor or per-side series. s_ch: frozen DGP-native per-event innovation std, computed from the hash-sealed DGP-only sample branch only (Annex B(e); D0-hash-committed generator sample; never simulator output, never the paired corpus). Through-M cells' conservation violation must be exactly zero (integer-exact, G7); raw cells are never clamped or repaired. Book-state and price-path errors are preregistered secondary endpoints, reported descriptively, outside all Holm families.

### 6.3 SESOI [pin, C6]

Per stratum s: δ_s = 0.1 · Ȳ_R00(s), R00(s) = the (increment, raw-train, raw-infer) cell in the same stratum. Guard: Ȳ_R00(s) < 1.0 scaled unit → "unresolved (reference-degenerate)", no positive label, reported, never dropped, never rescoped. Primary fallback strata in order: B1 kernel-swap h31; B1 tick-shift h16; B1 population h16. Reference degeneracy in all four strata is a STOP (PR §8.3; no post-hoc metric substitution).

### 6.4 Ordered classification [pin, C7; Annex B(g)]

Material non-additivity: 95% paired-bootstrap interval wholly above +δ_s or below −δ_s. Smaller statistical non-additivity: interval excludes zero but the first rule fails. Practical additivity: 90% interval wholly inside [−δ_s, +δ_s]. Unresolved: otherwise (with the reference-degenerate sub-label per C6 and the draw-noise-dominated sub-label per PR §4.4). An interval spanning zero and a SESOI boundary receives no positive label. Label → macro mapping is exactly Annex B(g) (Part 8.2).

### 6.5 Multiplicity and the transfer gate [pin, C9; C16(13)/(14)/(16)]

- Primary cell: B1, kernel-swap axis, horizon 16; single prespecified; not Holm-adjusted; not overridable by secondaries.
- Holm families: sign-flip tests on the 16 mandatory interaction cells (4 axes × 4 horizons) per block, Holm within each block. Family instantiation across the five record sub-blocks: B1 and B3 confirmatory; B2, B4-variantA, B4-variantB computed for completeness and labeled non-confirmatory (C16(13)). Whether B4's two variants form one 32-cell family or two 16-cell families is FLAG-9; proposed default: one 16-cell family per variant sub-block (5 families of 16 total; the "4 families of 16" phrasing predates the D1_05 variant split; reporting-only, since no confirmatory claim attaches to Stage 2).
- Axis-contrast secondary family: per block, the three (J_axis − J_ID) at horizon 16, Holm within the triple.
- Truncation secondary family (C16(14)): per L1 block a two-test family {J_trunclag,h16 − J_ID,h16; J_trunccap,h16 − J_ID,h16}, one-sided in the O-C direction (divergence nondecreasing in truncation), Holm within the pair; per L2 block a one-test family {J_trunclag,h16 − J_ID,h16}.
- Architecture-transfer gate: B3 passes iff B3's own primary-analogue cell (kernel-swap, h16, block B3) is material AND ≥ 8/16 mandatory cells of block B3 are material (Paper D 6/12 fraction preserved). The gate consumes the **UNADJUSTED C7 ordered-classification labels** by frozen design ("material" = the C7 95%-interval rule, not a Holm-adjusted p-value); Holm-adjusted sign-flip results feed exactly the two named paper sentences ("interaction present under multiplicity control in k of 16 cells per block" and the axis-contrast family sentence) and nothing else [pin, PR §4.4 multiplicity mapping]. Denominator under degeneracy: remains 16; degenerate cells count as not-material; never renormalized; a gate failure can never be attributed to or excused by degeneracy. Failure is reported as an architecture boundary, never hidden, never re-gated. The h = 1 strata are pre-flagged as the degeneracy-risk strata.
- Failed-gate scoping [pin, SIMCON §6]: on a failed L2 transfer gate, all confirmatory statements come from B1 only; B3 is reported per C10 with no confirmatory status; no pooled or cross-lineage estimate is computed or shown anywhere, including the abstract.

### 6.6 Seed-mean level and the draw-noise guard [pin, PR §4.4]

All allocation-level confirmatory quantities (O-B arms, KT-A3 resample arm, KT-M1) are computed and reported at seed-mean level: per-seed value = K-draw mean (16 draws); interval = seed-level 95% paired bootstrap over seeds. Mechanical draw-noise guard: for every O-test or KT contrast whose decision margin is an allocation-level margin, if the margin is smaller than 10× the preflight-derived draw-noise scale for that statistic class (bootstrap upper CI of the within-seed draw-std of the K-draw mean, matched units; for the allocation class the K-preflight's alloc_proprata_dev_mean gives within-seed variance W = 0.0141, i.e. draw-std of the K = 16 mean ≈ √(W/16) ≈ 0.030 in native units), the test auto-labels "unresolved (draw-noise-dominated)" → `class_unresolved_draw_noise_dominated`; it can never fire a confirmatory claim. `alloc_proprata_dev_mean` remains draw-dominated at every authorized K (ratio 0.1958, CI [0.1182, 0.4703] at K = 16) and carries its explicit draw-noise caveat in all reporting [pin, C2(b)].

### 6.7 O-tests (EP2) [pin, PR §4.4 table; Count column restored verbatim; the source's family-status content is condensed into the trailing paragraph]

| Test | Statistic | Units | Prediction | Procedure / margin | Population (PR §4.4 count) |
|---|---|---|---|---|---|
| O-A attribution floor | consumer RMSE(through-M-trained, raw-infer) − R‖v_U‖/√12 | consumer notional units (v^T z); floor tape-computable | RMSE ≥ floor; float tolerance 1e-9 relative on the integer-exact floor | per cell: seed-level 95% bootstrap interval; confirmed iff lower bound ≥ floor − tol; paper sentence limited to "floor attained in k of n cells (full table)" | per block: fiber-exposed consumer cells (locked checkpoints) |
| O-B swap→ru | allocation-consumer divergence under D_swap→ru | fill-count units (any nonzero ≥ 1 fill) | Θ(δ/S) > 0, per-level weights 1/S | seed-mean divergence, 95% seed-level interval; confirmed iff lower bound > 10× draw-noise scale | per block, per locked checkpoint |
| O-B swap→fifo (point null) | divergence under D_swap→fifo | fill-count units, integer-exact | exact zero (Theorem T-1: Exp = ∅; any nonzero falsifies) | integer-exact deterministic subcheck, all seeds all K draws; confirmed iff every divergence is exactly 0; NO statistical equivalence margin | per block, per locked checkpoint |
| O-C truncation monotonicity | divergence increments vs window W | (R²/12)Δ‖v_{U∩W}‖² (orthant); (R²/3)p²Δ(m_in·m_out/m) (split) | increments match precomputed curves; monotone nondecreasing in W; zero at no-straddling | deterministic curve comparison per fixture (integer-exact curve constants; seed-mean measured increments with intervals; subcheck = zero at no-straddling windows) | per L1/L2 block × windows |
| O-D granularity fingerprint | magnitude-consumer floor collapse; exact-zero cell | consumer units | price-notional on ru splits floor ≡ 0 (preregistered null); latency consumer retains split floor | integer-exact zero subcheck for the null cell; interval comparison for the retained floor | per fixture family |
| O-E controls | training-enforcement interaction, tape-measurable consumers | δ_s units (endpoint Y) | zero interaction | ordered classification vs δ_s per C7 (same machinery as mandatory cells); descriptive control, no claim attaches | per block |

Deterministic subchecks (eligible_units displacement under swap→ru; O-B swap→fifo null; O-C no-straddling zeros) are integer-exact engine-semantics checks, reported as pass/fail tables with no p-values [pin, PR §4.4]. All O-tests sit outside all Holm families, each with the frozen justification (deterministic tape-computable prediction constants; exhaustive pass/fail, no selective claiming). The J-level truncation contrasts are separate and INSIDE the C16(14) Holm family — the analyzer keeps the two levels distinct [pin]. O-test populations are unrestricted "per block" in PR §4.4 (no stage restriction), so bootstrap seeds are derived for all five block_ids (Part 7.3); Stage-2 results carry the C16(13) non-confirmatory labeling.

### 6.8 KT-A3 and KT-M1 [pin, PR §4.4]

KT-A3: swap arm = seed-mean endpoint divergence under D_swap (channel-scaled RMS units of Y, matched to δ_s of the stratum); resample arm = seed-mean endpoint divergence under within-fiber allocation regeneration. Fires iff swap > δ_s AND resample < δ_s/10, both at seed-mean with 95% seed-level bootstrap intervals, subject to the draw-noise guard on the δ_s/10 margin. KT-M1 (gauge-twin): the fiber-resampler regeneration divergence at seed-mean level against the same guard. Resampler acceptance semantics per PR §7.1 (identical aggregate_state_hash sequence AND differing state_hash chain); resampler namespace 20260973; deterministic kernels and single-order pools correctly admit no accepted resample (the KT-A3 control) [pin, PR §7.1]. Both outside all Holm families. The frozen text assigns no per-block count to either test; the block assignment of their bootstrap seeds is a contract default inside FLAG-2 (Part 7.3).

### 6.9 KT-A1 patterns [pin, Annex B(h)]

P1 = opposing-sign training/inference enforcement credits (T-contrast and E-contrast signs oppose). P2 = pure interaction (J material with both main-effect contrasts non-material). P3 = surgery hysteresis on locked checkpoints (surgery cells diverge across deployment maps while parents are training-loss-identical). Kill pattern: |I| ≤ δ/2 everywhere, no sign opposition, surgery antisymmetric → ALPHA is an ablation (REFRAME, PR §8.3).

### 6.10 A10 audit statistics [pin, MENU; PR §5.4–5.5]

After the audit retrain, recompute the C3 attribution estimands on the audited stratum (D-contrasts involving the retrained cell, J, φ_train, φ_infer) with the same frozen analyzer macros. Instability criteria (mechanical): (1) sign-pattern instability — any preregistered contrast flips sign across the Holm-corrected significance bands between ST-trained and PAM-trained versions (within-band sign differences reported but not firing); or (2) ordered-classification instability — the C7 classification of any affected cell or contrast changes class across the SESOI band. The comparison is outside all Holm families (preregistered robustness gate, not estimator superiority). Outcomes: audit stable → primary ST cube reported as preregistered, audit enters as a one-table control with both estimators' values; audit fires → estimator-conditional reporting (both estimators side by side, no pooled or ST-only claim) for every estimand touching the retrained coordinate, entered in the deviations ledger, R-family raw-train cells unaffected; both estimators fail the fixture gate → surgery-only collapse + STOP (Part 3).

### 6.11 Reporting-all and discharge [pin, C10; PR §6.5]

Every cell, axis, horizon, block, class flip, and null is reported unconditionally; unrun cells surface as "not run" / "unresolved" (`class_not_run`), never dropped; class flips are preregistered descriptive findings with no p-values; the transfer gate is the only preregistered lineage-level decision. One confirmation discharges KT-A1/A3/M1 simultaneously (correlated by design; forecasts must not multiply them independently) [pin, C10; PR §6.5].

---

## 7. Bootstrap mechanics

### 7.1 C8 verbatim [pin]

50,000 draws, percentile intervals, seed-level resampling of the complete paired eight-cell vector; draws are averaged within seed and never resampled.

### 7.2 Bootstrap RNG seed derivation [pin, Annex B(a); byte rule FLAG-1]

Per (block, family): bootstrap seed = int(sha256(preimage), 16) mod 2^63, where the preimage is built from the frozen strings "ecomd_reexploration_v2_bootstrap", block_id, family_id. Deterministic from frozen strings; independent of all training seeds; recorded in the analyzer manifest.

**Byte rule (FLAG-1)**: PR prints the concatenation operator inconsistently — ASCII `||` at C8 (line 656) vs U+2016 `‖` at Annex B(a) (line 1434) — and the two encodings produce different seeds. This contract pins: the operator is metalanguage; the preimage is the **UTF-8 encoding of the three strings concatenated with no separator bytes** (`"ecomd_reexploration_v2_bootstrap" + block_id + family_id`). This is the standard reading of concatenation notation and adds no data bytes; PI-ratified 2026-09-19 (Part 10 row 1) — this reading now fixes every bootstrap seed.

### 7.3 block_id / family_id string table (FLAG-2)

| block_id | Used by |
|---|---|
| `B1` | mandatory16, axis_contrast, truncation, estimands, primary, O_A…O_E, KT_A3, KT_M1, audit |
| `B3` | mandatory16, axis_contrast, truncation, estimands, O_A…O_E, KT_A3, KT_M1 |
| `B2` | mandatory16, axis_contrast, truncation, estimands, O_A…O_E |
| `B4_variantA` | mandatory16, axis_contrast, truncation, estimands, O_A…O_E |
| `B4_variantB` | mandatory16, axis_contrast, truncation, estimands, O_A…O_E |

| family_id | Family | Members |
|---|---|---|
| `mandatory16` | sign-flip Holm family | 16 mandatory interaction cells of the block |
| `axis_contrast` | axis-contrast secondary family | 3 tests (J_axis − J_ID) at h16 |
| `truncation` | C16(14) family | 2 tests (L1 blocks) / 1 test (L2 blocks) |
| `estimands` | C8 percentile-interval machinery for the C3 estimands | D_te contrasts, T_0/T_1, E_0/E_1, φ_train, φ_infer, and the C7 classification intervals of the block's mandatory cells and O-E controls; the A10 audit reuses these macros on the audited stratum (MENU §5 instability criteria: "with the same frozen analyzer macros"; audit counts per PR §5.4) |
| `primary` | primary cell CI (not Holm-adjusted, but needs a seed) | B1 kswap h16 |
| `audit` | A10 ST-vs-PAM comparison | A10 stratum (under block_id B1) |
| `O_A` … `O_E` | O-test bootstrap seeds | per §6.7, on **all five** block_ids — PR §4.4's counts are "per block" with no stage restriction; Stage-2 results carry C16(13) non-confirmatory labeling |
| `KT_A3`, `KT_M1` | killer-test contrasts | per §6.8 — default block assignment B1 + B3 (contract default, inside FLAG-2: the frozen text assigns no per-block count) |

These strings appear nowhere in the frozen sources (Annex B(a) presumes them); they are contract-authored conventions (FLAG-2), PI-ratified 2026-09-19 together with the all-blocks O-test seed coverage and the KT_A3/KT_M1 block assignment. Bootstrap seeds for every (block_id, family_id) pair are derived once, recorded in the analyzer manifest, and checked by the G2 disjointness sub-check.

### 7.4 Paired-vector mechanics

Each bootstrap draw resamples the complete paired eight-cell seed vector [pin, C1]; draws are averaged within seed first and never resampled [pin, C8]. Lost seeds are removed at the seed-index level for all arms of that index; the Part 3 halt rule applies.

### 7.5 Statistical-engine pins (FLAG-10)

The frozen sources pin the seed derivation but not the resampling generator or the sign-flip enumeration. Proposed defaults: (i) bootstrap resampling via `numpy.random.default_rng(seed)` (PCG64) with the Annex B(a) seed; (ii) sign-flip tests enumerated completely when 2^n ≤ 2^24 (covers Stage-2 n = 15 → 32,768 flips), otherwise a seeded random flip subset of 10^7 draws using the same (block_id, family_id) seed with suffix `_signflip`. Alternatives recorded and closed; the PI ratified the defaults 2026-09-19 (Part 10 row 10).

---

## 8. Macro emission

### 8.1 Exactly once [pin, G12; C15]

Each analyzer emits its macros exactly once, generated from the hashed analysis JSON. There is no re-emission path; a macro-emission failure aborts (no partial metrics).

### 8.2 Label → macro mapping [pin, Annex B(g)]

"material non-additivity" → `class_material_nonadditivity`; "smaller statistical non-additivity" → `class_smaller_stat_nonadditivity`; "practical additivity" → `class_practical_additivity`; "unresolved" → `class_unresolved`; "unresolved (reference-degenerate)" → `class_unresolved_ref_degenerate`; "unresolved (draw-noise-dominated)" → `class_unresolved_draw_noise_dominated`; "not run" → `class_not_run`. No other classification macro names are emitted (the OPS underscore label set is superseded).

### 8.3 Non-omissible macro contents [pin, C15]

Every macro file includes: K (= 16); the fixture-manifest hashes (frozen-bundle anchor, schema_spec.json hash, enrichment manifest); and the amendment ledger — items (1)–(16): (1) seed = RNG-tree root; (2) eight-cell resampling vector; (3) R00 pinned to increment; (4) channel-scaled multi-channel endpoint; (5) reference-degeneracy guard; (6) Holm families 4 × 16 (frozen ledger text retained verbatim; instantiated as 5 families of 16 under the FLAG-9 B4 variant split — §6.5); (7) axis-contrast family; (8) K-draw CRN protocol; (9) transfer-gate fraction 8/16 = 6/12; (10) clearing-identity gate replaces projection-identity gate; (11) K = 16 (K-preflight `none_in_set`, results sha256 `f61e410cd59c37b5624504a3cdf057c701b4b682067f948d2f8528ace018c2d4`, PI "用需要算力多的那个"); (12) kernel set {fifo, random_unit_within_price}, pro_rata demoted to S3 exact-arithmetic; (13) two-stage execution; (14) truncation secondary family with corrected membership; (15) C14 restatement under K = 16; (16) C9 transfer-gate primary reference = B3's own primary-analogue cell.

### 8.4 Macro set inventory

Per mandatory cell (all 16 × 5 sub-blocks): classification macro, estimand value + interval, Holm p-value (with confirmatory/non-confirmatory labeling per stage). **C3 estimand macros** (family `estimands`, Part 7.3): value + C8 percentile interval + C7 classification for D_te, T_0/T_1, E_0/E_1, φ_train, φ_infer per block/stratum — the same frozen macros the A10 audit reuses (§6.10). Primary cell macro (unadjusted). Transfer-gate macro (B3: pass/boundary, denominator 16, degeneracy labels alongside). Truncation-family macros. Axis-contrast-family macros. O-A…O-E result macros (pass/fail tables for deterministic subchecks). Secondary-endpoint descriptive macros (book-state and price-path errors; C5/§6.2). KT-A1 P1/P2/P3 pattern macros + kill-pattern status. KT-A3/KT-M1 macros with guard labels. A10 audit macros (both estimators' values; downgrade status). Class-flip tables. Not-run coverage (`class_not_run`). The `alloc_proprata_dev_mean` draw-noise caveat statement. All cells, axes, both lineages, flips and nulls — unconditionally (C10).

### 8.5 Publication channel (FLAG-11)

Proposed: each analyzer's `analysis.json`, macro files, and analyzer manifest (bootstrap seeds, gate receipts, session metadata) upload to `r2://ecophys/alpha_cube_d0_20260921/analysis/<analyzer_id>/`, followed by a git commit of the macro tables and a session-log entry with the R2 etags — mirroring the PR §1.3 freeze recording order (git commit → R2 immutable object → session log). The published analysis-JSON hashes are the C12 unlock event for the reflexive cell. PR pins "hashes published" but not the channel; the PI ratified the proposed channel 2026-09-19 (Part 10 row 11).

---

## 9. Dummies and pre-freeze validation (contract-authored scope; FLAG-15)

The OPS Pre-D0 row requires "analyzer macros + dummies"; no frozen document defines the dummy scope. This contract defines it:

1. **Schema-conformance dummies**: synthetic minimal records per record class (RC1–RC4 + training envelope), validating every Part 5 field, every G-check's positive path, and the record_key serialization.
2. **Planted-fault negative controls**: one planted fault per gate G1–G12 (wrong count, broken pairing, hash mismatch, missing parent reference, nonzero conservation, non-identical duplicates, field violation, reflexive contamination, double-emission attempt). Each fault must FAIL its gate and abort with no partial metrics — a gate that passes on its planted fault is a validation failure.
3. **Macro-emission dry run**: a synthetic analysis JSON driving emission of all seven class macros, `class_not_run` paths, the non-omissible contents (K, fixture hashes, ledger (1)–(16)), and the Holm labeling per stage.
4. **Annex B(a) seed self-derivation**: recompute every (block_id, family_id) seed from the string table under the FLAG-1 byte rule; record in a dummy manifest.
5. **G9 stride self-check**: each Part 4.9 class at known counts → exactly 5%, every 20th from index 0, no RNG.
6. **Bootstrap determinism check**: same seed → identical percentile intervals, twice.

Execution: all dummy validation runs on the remote nodes (PI activation rule; supersedes any OPS Mac-legal smoke classification). Dummies never touch confirmatory records (none exist pre-D0), never write the Part 8.5 publication channel, and live under a `dummies/` namespace with receipts hashed into the D0 archive alongside this contract.

---

## 10. PI-ratified items (all 16 flags approved at their proposed defaults, 2026-09-19 — decision `pi_analyzer_contract_flags_ratification_20260919`)

The "Proposed default" column below is the ratified resolution of each item. The "Alternative" and "If unresolved at freeze" columns are closed as live options and retained as the recorded stakes; after the D0 hash, switching to any alternative requires a new frozen, hash-recorded amendment (Part 11).

| Flag | Item | Proposed default | Alternative | If unresolved at freeze |
|---|---|---|---|---|
| 1 | Annex B(a) preimage bytes (`‖` vs `||` inconsistency) | UTF-8 plain concatenation, no separator | ASCII `\|\|` literal between strings | Bootstrap seeds are ambiguous → blocker |
| 2 | block_id / family_id string table (7.3) — three elements: the strings; O-test seeds on all five blocks (PR §4.4 counts are stage-unrestricted); KT_A3/KT_M1 block assignment (default B1 + B3) | As tabled (incl. `estimands` family, `B4_variantA`/`B4_variantB`, O_A…O_E on all blocks) | Any PI-amended strings / scope (Stage-1-only O-tests would supersede PR §4.4's per-block counts and must be recorded as such) | Seed derivation not reproducible → blocker |
| 3 | Four-analyzer enumeration + A10 as separate unit (2.1–2.2) | Per-block quartet; A10 outside the count | PI-specified alternative roster | C12's "four" has no referent → blocker |
| 4 | Reflexive "days 14–16" OPS slot vs C12 firewall | C12 governs; reflexive after four-hash publication | — (supersession recorded either way) | Scheduling contradiction at D0-S3 |
| 5 | Stage-2-cancellation discharge of "all four hashes" (2.4) | B2/B4 not-run stub JSONs with published hashes (stretches C12's "have run") | Cancellation record + Stage-1 hashes standing in (requires a frozen amendment; replaces two analyzer hashes) | Reflexive cell unschedulable after cancellation |
| 6 | Per-session G1/G4/G6 scoping (4.1) | Session sub-tables; D0-S6 campaign reconciliation | Single campaign-total gate run only at D0-S6 | G1 unpassable at D0-S4 → program stalls |
| 7 | G9 record-class taxonomy; trainings excluded; record_key serialization (4.9) | RC1–RC4 as tabled; 450 % 20 ≠ 0 → trainings out; dot-joined key | PI-specified classes/keys | Stride not implementable |
| 8 | Surgery records inside the 8-cell grid as the t ≠ e cells (5.5) | Yes; no separate PR §3.4 row | Separate surgery record class + count row | G1 counting basis for surgery cells |
| 9 | B4 family split under D1_05 (6.5) | One 16-cell family per variant sub-block (5 families total) | One 32-cell B4 family | Holm bookkeeping for Stage-2 completeness only |
| 10 | Statistical-engine pins: bootstrap generator; sign-flip enumeration (7.5) | `default_rng` PCG64; complete enumeration ≤ 2^24 else 10^7 seeded subset | PI-specified engine | Intervals not reproducible → blocker |
| 11 | G12/C12 hash-publication channel (8.5) | R2 `alpha_cube_d0_20260921/analysis/` + git + session log | PI-specified channel | "Published" undefined |
| 12 | L1-4 generator-threading status recorded at freeze (4.9) | Record status in freeze record; flag L1 G9 if not landed | — | L1 replay rests on uncontracted global-RNG assumption |
| 13 | OPS "8/6 conditions" line vs PR §3.4 (5.6) | trunc_cap L2 de-scope only; pop_4x drop does not apply | PI-specified reading | Axis-condition set ambiguous for L2 |
| 14 | Fixture-gate placement (3) | External pre-gate, re-run at each session start on the node | Inside G1 | Gate-order ambiguity |
| 15 | Dummy scope definition (9) | Items 1–6 as written | PI-specified additions/cuts | Pre-D0 row deliverable undefined |
| 16 | Halt-rule threshold for 15-seed Stage-2 blocks (and 12-seed shrink variant) — frozen text words it as 3/30 only (Part 3) | Proportional: halt at > 10% of the cell's seeds (≥ 2 of 15; ≥ 2 of 12) | Literal count: > 3 seeds regardless of cell size | Undefined STOP-class decision at D0-S5 in the 2–3-loss band |

Related supersessions recorded (no PI action required): OPS label list → Annex B(g) (C-3); MENU K = 8 → K = 16 (C-1); OPS seed namespaces (C-2); OPS t4 wording; CV1 122,880/240/480 (C16(15)); OPS reflexive burn line moves with FLAG-4.

---

## 11. Amendment and failure policy

Post-freeze, this contract is immutable. PROHIBITED after freeze [pin, PR §1.3]: any new confirmatory proposition; any endpoint, estimator, threshold, cell, seed, axis, horizon, family, schema, or record-count definition change; any analyzer rerun; any outcome-dependent analysis of any kind. Any breach is STOP-class, no repair (PR §8.3; the full 22-item risk register incorporated by reference without exception). Any deviation requires a new frozen, hash-recorded amendment (PI deviation memo) — the only legal rerun path.
