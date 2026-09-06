---
document: Panel response + disposition record for preregistration v2
repo_path: papers/proposal/ecomd_reexploration_prereg_panel_response_2026-09-06.md
authored: 2026-09-06
panel: adversarial 3-reviewer panel (PI decision D1_08), 2026-09-06
reviewed_artifact: papers/proposal/ecomd_reexploration_prereg_v1_2026-09-06.md
produced_artifact: papers/proposal/ecomd_reexploration_prereg_v2_2026-09-06.md
dispositions: 28 issues — 28 FIXED, 0 REJECTED, 0 DEFERRED
outcome_access_at_authoring: none
---

# Panel Response — Preregistration v1 → v2 (28 issues, all dispositioned)

## 1. The three verdicts

| Reviewer | Role | Verdict | Issues |
|---|---|---|---|
| R1 | reviewer-2 — preregistration-integrity auditor (clinical-trial/OSF model; garden of forking paths) | **major_revision** | 9 (1 blocker, 7 major, 2 minor — v1 Annexes + §3.4/§10.1 self-flags corroborated) |
| R2 | NeurIPS/ICLR-AC-grade statistical methodologist (estimands, SESOI, multiplicity, K-provenance, record arithmetic, one-shot discipline) | **major_revision** | 9 (5 major, 4 minor; independent recomputation of the full record arithmetic) |
| R3 | market-microstructure + scientific-ML domain referee (PRL/ICLR caliber) | **major_revision** | 10 (1 blocker, 4 major, 5 minor; citation-provenance and frozen-archive audit) |

Reviewer-identified strengths recorded by the panel and carried forward: the merge structure
(GAMMA theorems + ALPHA cube) was judged coherent and honestly labeled; the K-preflight and
one-shot analyzer discipline were judged real, not decorative; the v1 draft self-flagged most
of the blocker cluster correctly (v1 §3.4 LOUD FLAG, §10.1, Annex A.1/A.2) — the panel's
rulings converted those self-flags into ratified text. Kill-class risk was judged
concentrated in KT-A1/KT-A4/KT-M2 (0.30 each) exactly as the forecast ledger already records;
no reviewer found an unpriced kill class.

## 2. Cross-reviewer adjudications (explicit, per the revision charter)

- **ADJ-1 (Stage-2 record count: R2 vs R1/R3).** R2's Issue 1 recomputes the Stage-2
  mandatory-axes total as **92,160**; R1-1/R3-1's required fixes carry the stale figure
  61,440 (2 blocks x 30,720). Both blockers are otherwise identical in substance. Ruling:
  **R2's 92,160 is correct.** D1_05 gives B4 two DGP variants (A: both lineages; B: L2-only),
  so Stage 2 = B2 (L1 x varA, 15 seeds) 30,720 + B4-varA 30,720 + B4-varB 30,720 = 92,160;
  v1's own training row (180 = 120 + 60) already counted both variants, making v1 internally
  contradictory. v2 §3.4 adopts 92,160 and records the adjudication. R1-1/R3-1 are dispositioned
  FIXED against the corrected enumeration, not their carried-over figure.
- **ADJ-2 (C14 restatement landing site).** R1-1 demands the restatement land IN THE CONTRACT
  TEXT, not only in prereg §3.4. R3-1 phrases it as "ratify one complete restated C14 into the
  frozen text". Ruling: adopted via the pre-freeze amendment route — the contract is a D-1
  candidate until freeze; v2 §3.1 records restatements (C)–(F) into the contract's amendment
  banner, C16 items (15)–(16) bind them into the non-omissible ledger, and the D0 freeze hash
  chain covers the contract file explicitly (v2 §1.3). This satisfies both reviewers without
  post-freeze edits.
- **ADJ-3 (G4 count).** R2-1 flags G4's "240 checkpoint sha256" as stale against the
  420-training (+30 audit) campaign. R1-1/R3-1 do not contradict; v2 amends G4 to 450 with the
  decomposition.
- **ADJ-4 (who closes the "TO BE PINNED" items).** R1-9 pins the freeze date at panel close;
  R3-1 rules every non-hash "[TO BE PINNED AT D0]" must be pinned at v2. No conflict: v2 pins
  the date (2026-09-19), all counts, all seeds, all procedures; only the freeze timestamp and
  freeze sha256 remain D0-pinned.

## 3. Disposition table (one row per issue; 28 rows)

| ID | Severity | Section (v1) | Issue summary | Disposition | Action taken in v2 (or reason) |
|---|---|---|---|---|---|
| **R1-1** | blocker | 3.4 / C14 / G1 | Contract C14 freezes stale K=8 arithmetic (122,880) while C2/G8/G10 froze K=16; two-stage probe split and truncation/A10 enumerations open; G1 would abort against the campaign's own numbers with no lawful repair | **FIXED** | C14 restated via pre-freeze amendment (§3.1(C), C16 item (15)); §3.4 gives the complete derivation: 215,040 mandatory-axes (Stage 1 122,880; Stage 2 92,160 per ADJ-1) + 76,800 truncation passes + 7,680 audit = **299,520** evaluation records; 450 trainings; 420 probes fully enumerated with condition lists; G1's target is now internally consistent. Adjudication ADJ-1 recorded |
| **R1-2** | major | 1.4 / 3.2 C9 / 10.1 | Transfer-gate "primary J" ambiguous between B1 primary cell (cross-block) and B3's own kernel-swap-h16 analogue; two readings give opposite gate outcomes; prereg-side clarification cannot outrank the ambiguous contract | **FIXED** | C9 amended in the contract text via pre-freeze amendment (§3.1(D)); C16 item (16): gate reference = **B3's own primary-analogue cell (kernel-swap, h16, block B3)**; cross-block reading rejected as outcome-choosable; §3.2 C9 restated |
| **R1-3** | major | 4.1 | Stage-2 trigger named "L2 trainability/transfer gate" imports the outcome-based C9 gate into a "mechanical triggers only" list — a documented post-freeze fork | **FIXED** | Trigger renamed to the mechanical criterion "≥ 28/30 L2 seeds reach finite training loss under the day-5 thresholds on D1" (trigger t4, §4.1); explicit sentence added: the C9 transfer-gate result is NOT an input to any Stage-2 entry/de-scope/cancellation decision; the outcome-trigger protective clause restored to §8.3 |
| **R1-4** | major | 4.2 | Truncation "3 tests/block" family members never defined anywhere (no statistic/direction/threshold); Stage-2 "directional robustness" has no operational rule while C9's families still include B2/B4 | **FIXED** | Family itemized in C16 item (14): per L1 block {J_trunclag,h16 − J_ID,h16; J_trunccap,h16 − J_ID,h16}, one-sided O-C direction, Holm within pair; per L2 block the 1-test family (trunc_lag); recorded reason for the change from "3" (membership never enumerated + L2 trunc_cap de-scope makes uniform 3 impossible). Stage-2 family status pinned in C16 item (13): tests executed and reported, descriptive robustness, no confirmatory claim attaches |
| **R1-5** | major | 10.1 / C16 | Authorized two-stage execution (D1_04) and truncation family (plan ruling 5) absent from the frozen C16 ledger; slots (11)–(12) taken; post-freeze additions prohibited | **FIXED** | C16 items (13)–(14) ratified with full text (§3.2, §10.1); items (15)–(16) added for the C14 restatement and C9 disambiguation; ledger complete against every authorized amendment as of v2 |
| **R1-6** | major | 1.2 / 1.3 / 7.4 | Freeze chain underspecified: hashing agent/procedure/order/recording unstated; hash-locked list omits the contract and theory appendix; four companions print the wrong bundle anchor `fea8b136`, one internally contradictory | **FIXED** | §1.3 freeze mechanics pinned: agent (PI D0 session), exact hash inputs (file list INCLUDING contract + theory appendix), recording order (git commit → R2 immutable object → session log); full 64-hex canonical anchor pinned in §1.1 and §7.4; typo policy = flag-list route (Annex C-4) with the canonical form stated once and the five-line inventory recorded |
| **R1-7** | major | 3.2 / 3.3 / 4.3 / 4.6 | Eight analyst-choosable degrees of freedom remain: bootstrap seed, G9 sample rule, S3 seeds, two 10-seed subsets, s_ch branch, S1a gate naming, label-to-macro binding, KT-A1 rule living only in a level-4 companion | **FIXED** | Consolidated Annex B pinning table (a)–(j): bootstrap seed = sha256 over frozen strings mod 2^63; G9 = deterministic lexicographic stride every 20th; S3 seeds 20260974–76 (reserved-block continuation, PI-ratifiable at v2 review); 10-seed subsets = first 10 per namespace; s_ch = hash-sealed DGP-only sample (single branch); S1a-G1..G3 rename (EP4); label-to-macro mapping table; KT-A1 P1/P2/P3 rule restated inline (Annex B(h)); provenance note distinguishes convention constants from empirical ones |
| **R1-8** | minor | 3.2 C2(e) | Dangling conditional: re-run "before freezing K" implies K adjustable at D0 though D1_11 closed the window; consequence of a re-run undefined | **FIXED** | C2(e) rewritten (§3.2, §3.1(E)): E-2 preflighted pre-D0, result caveat-and-reporting-only; K = 16 immutable regardless; material endpoint-shaped insufficiency = named STOP-class PI decision item, never a K change; M1 own-state ambiguity dissolved empirically (preflight runs on the actual E-2 generator) |
| **R1-9** | minor | 1.2 | Freeze date "[TO BE PINNED AT D0] by the panel" implies a panel act at D0, contradicting the v1 → panel → v2 → freeze order | **FIXED** | Freeze date pinned 2026-09-19 at panel close (§1.2, Annex A.10); "by the panel at D0" phrasing removed; responsible agent and recording location named (§1.3); only freeze hash/timestamp remain D0-pinned |
| **R2-1** | major | 3.4 + G1/G4 | Draft's own "corrected" arithmetic still under-enumerates: Stage-2 row counts B4 as one variant (61,440) while the training row counts both (180); truncation passes, audit-cell records, probe split, G4's 240 all stale; any residual error = full campaign abort under G1 | **FIXED** | Full independent enumeration produced (§3.4): per-variant table with derivation notes; Stage 2 = 92,160; campaign = 299,520 evaluation records, 450 trainings, 420 probes; G4 amended to 450; audit cell +7,680 records and +30 trainings enumerated; probe split fully enumerated (240 + 180); adjudication ADJ-1 adopts this count over the figure embedded in R1/R3's fixes |
| **R2-2** | major | 3.2 C9 + 4.2–4.4 | Three multiplicity defects: (i) truncation family asserted but never itemized, structurally impossible as uniform "3" on L2; (ii) O-A..O-E and KT-A3/KT-M1 outside every family with no statistic/units/margin/procedure, O-B margin dimensionally undefined; (iii) no mapping between Holm 16-cell families and any decision (gate consumes unadjusted labels) | **FIXED** | (i) C16 item (14) itemization (above); (ii) §4.4 O-test specification table (statistic, native units, margin, procedure, count, family status) — O-B swap→fifo restated as an integer-exact zero point null (stronger than the dimensionally undefined SESOI-margin equivalence; withdrawal recorded), deterministic subchecks declared outside statistics with justification, KT-A3/KT-M1 at seed-mean endpoint level with a mechanical draw-noise guard; (iii) explicit mapping sentence: Holm families gate NOTHING; the transfer gate consumes UNADJUSTED C7 labels by frozen design; adjusted values consumed only by two named paper sentences |
| **R2-3** | major | 3.2 C3/C4 + 4.2 | Kernel-swap stratum (contains THE primary endpoint) incompletely defined: raw-infer cells' kswap values/duplicates unstated; G10 has no defined allocation_rule for them; training kernel never pinned; "OOD axes get proportionally larger thresholds" false for the primary axis since R00 is stratum-identical | **FIXED** | Pinned paragraph in C4 (§3.2): training kernel = FIFO on the FIFO-generated corpus; kswap changes only the inference-M deployment kernel; raw-infer kswap cells = byte-identical ID duplicates recorded for coverage symmetry, allocation_rule pinned, n_draws == 16, duplicate byte-identity gated by G8; δ_s at kswap anchored to the ID-scale R00 by construction; the false Part 2b rationale explicitly corrected for the primary axis |
| **R2-4** | major | 3.2 C2(e) + 7.3 + D1_11 | Dead-letter condition: re-run clause can never fire (K already frozen, E-2 not built); authorized M1 generators sit outside the M0-only calibration point with "adds feedback channels" undefined | **FIXED** | Same C2(e) rewrite as R1-8 (jointly dispositioned): empirical dissolution of the M1 question (preflight runs on the actual D0 generator, so the abstract predicate never needs adjudication); caveat-only semantics; STOP-class decision path for material insufficiency |
| **R2-5** | major | 3.2 C2(b) + 4.4 + 6.5 | Preflight's own insufficiency finding (alloc_proprata_dev_mean draw-dominated at every authorized K) not propagated into the allocation-level confirmatory contrasts it touches (O-B, KT-A3 resample arm, O-D); no margin-vs-draw-noise reconciliation; δ/10 margin could sit inside the draw-noise floor | **FIXED** | All allocation-level confirmatory quantities restated at seed-mean level (draw noise folded into the interval via K-draw means); mechanical guard: any allocation-level margin below 10x the matched-scale preflight draw-noise upper-CI bound auto-labels "unresolved (draw-noise-dominated)" and can never fire a confirmatory claim (§4.4); the numeric anchor (√(W/16) ≈ 0.030 from W = 0.0141) recorded |
| **R2-6** | major | 3.2 C5 | Primary endpoint channel vector underdefined: aggregate vs per-actor granularity unpinned; the choice determines draw-sensitivity of the endpoint, s_ch computation, and δ_s scale, and the D0 generator build consumes it | **FIXED** | C5 pinned (§3.2): exactly two AGGREGATE engine-level conserving channels per clearing round {total executed volume units, total executed cash ticks}; truth-side draw-invariance (lumpability) vs simulator-side draw-sensitivity (clearing feedback) stated; s_ch resolved to the hash-sealed DGP-only sample branch; consequences for K-draw averaging stated auditable |
| **R2-7** | minor | 3.2 C3 | T_0, T_1, E_0, E_1 used inline but defined only in the incorporated contract — a precedence hop inside the frozen archive for the exact objects the instability criteria reference | **FIXED** | All four contrasts defined inline in the C3 restatement with subscript-order convention stated (§3.2) |
| **R2-8** | minor | 3.2 C6/C9 | h=1 (plausibly h=4) increment-coordinate R00 risks design degeneracy: near-deterministic one-step increments could auto-label 8 cells "unresolved", silently hardening the ≥ 8/16 gate while the denominator stays 16 | **FIXED** | Pre-stated in C9 (§3.2): the gate denominator remains 16 under per-cell reference degeneracy; degenerate cells count as not-material; never renormalized; gate failure never excused by degeneracy after results are seen; h=1 pre-flagged as the degeneracy-risk stratum |
| **R2-9** | minor | 2.1 R2-A | "TV = 1 at V* = 6" ladder constant uses an infeasible single-order witness x° = (6,0,0,0) (q_1 = 5 < 6) — a synthetic fiber member quoted beside feasible constants; invites a referee poke | **FIXED** | §2.1 R2-A relabeled: the feasible FIFO-prefix ladder leads (0.6429 / 0.8901 / 0.9950 / 0.9987); TV = 1 at V* = 6 explicitly marked the INFEASIBLE-SINGLE-ORDER WITNESS (empty intersection, q_1 = 5 < 6), never a pool-realizable constant; consistent with §2.5 which always carried 0.9987 |
| **R3-1** | blocker | 3.4 / Annex A.1–A.2 / C14 / G1 / C16 | Record-coverage and amendment-ledger cluster not freeze-consistent (stale C14, unpinned probe split, unenumerated truncation/A10/Stage-2 records, C16 (13)–(14) missing); a self-flagged inconsistency is still an inconsistency — package cannot freeze as-is; every non-hash TO-BE-PINNED must close at v2 | **FIXED** | Same restatement cluster as R1-1/R1-5/R2-1 (jointly dispositioned): restated C14 with the complete enumeration (299,520 / 450 / 420) ratified as C16 item (15); items (13)–(14) ratified; probe split and every record class enumerated; v2 contains exactly two D0-pinned items (freeze timestamp + freeze sha256), verified by sweep |
| **R3-2** | major | 4.7 (also 4.2) vs C3 / D1_14 | Periphery lists "reverse and pro-rata kernel swaps", contradicting the frozen kernel sentence (pro_rata is not an engine kernel, never executes; engine code implements exactly fifo + random_unit); invites the engine-realism attack it means to defuse; contract Part 2a.6 carries the same stale wording | **FIXED** | §4.7 line split: "reverse kernel swap (random_unit → FIFO at inference)" stays an executable exploratory item; pro-rata re-scoped to "S3 exact-arithmetic ONLY, never executed in the engine"; contract Part 2a.6 sentence marked superseded via the amendment banner (§3.1(F), Annex C-5); §4.2 pointer updated |
| **R3-3** | major | 6.3 / References | "Dyer et al. ICAIF 2023" column has no D-2 map row (the ONLY permitted citation source); its reasons restate the adjudicated Nagy et al. (2023, ICAIF) row and its "(map 2.2)" pointers dangle; per-cell map pointers absent from the prereg table | **FIXED** | Option (i) adopted: Dyer column replaced by **Nagy et al. (2023, ICAIF)** with the map §2.2 row as its reason and locator; per-cell map locators restored in the §6.3 header row (matching-ABM located at map §2.5 + condition 4, honestly recorded); provenance note in §6.3 states Dyer traces only to the D-3 framing and D-1 session record, never adjudicated; Dyer removed from References; §6.3 header claim now true for every column |
| **R3-4** | major | 4.2 / C16 item (14) | Truncation family "3 tests/block" membership never defined (two conditions → at most two vs-ID contrasts; third test unnamed; horizons and estimand form unstated); the contract's own Part 1 element 5 standard not carried to this second family | **FIXED** | Same itemization as R1-4(i) (jointly dispositioned): exact member contrasts, horizon h16, one-sided O-C direction, Holm ordering within the pair; per-L2 1-test family; recorded reason for the change from "3"; the Part 1 element 5 standard (undefined family = decorative multiplicity) now satisfied |
| **R3-5** | minor | 4.1 / 8.2 / C16 item (13) | Stage 2 on "preregistered first-15-seed subsets" without pinned seed values; G1/G2 and the record arithmetic need unambiguous frozen sets | **FIXED** | Stage-2 seed sets pinned: B2 = 11000–11014, B4 = 12000–12014, ascending within namespace (C1, C16 item (13), §3.4) |
| **R3-6** | minor | 2.2 (G2-1) | Frozen-fixture hash identity stated as "sequence 6/7", conflicting with the writeup's alignment (fifo tape SEQUENCE 7 [one record, quantity 2] = random-unit tape SEQUENCE 8 [two unit records], shared pre-hash da930600 → post-hash f0862093) | **FIXED** | §2.2 G2-1 repinned with exact sequences and hash roles (pre vs post, per-arm record indices) and the completed-request-boundary convention, matching the KT-G2 writeup §3 |
| **R3-7** | minor | 8.3 | STOP/REFRAME table labeled "verbatim" but drops two of the 22 inherited rows: the KT-A5 portability-kill REFRAME and the Stage-2 outcome-trigger protective clause — a weakening-by-omission hazard | **FIXED** | Both restored in §8.3 (KT-A5 REFRAME row; outcome-triggered Stage-2 launch = STOP-class protective clause with downgrade-to-exploratory consequence); header reworded to "verbatim rows, condensed presentation; the 22-item register is incorporated by reference WITHOUT EXCEPTION and without weakening" |
| **R3-8** | minor | Annex A.6 / 3.3 | Proposed "G2 rank-seed collision check" collides by name with gate G2 and lemma KT-G2 (three-way ambiguity) and would be a thirteenth gate | **FIXED** | Folded into the existing G2 gate specification as a namespace-disjointness sub-check enumerating every instrument namespace (S3 seeds, 20260972/73, 31000–31099, bootstrap seeds) vs training namespaces and each other (§3.3); no new gate, no naming collision |
| **R3-9** | minor | 1.4 / 3.1 companions | Stale-line inventory incomplete: the ops/killer-tests "Holm across the 8 mandatory cells" (two occurrences) and five `fea8b136` anchor typos across four hash-locked companions (one document internally contradictory) unflagged — audit hazards inside the frozen archive | **FIXED** | Consolidated Annex C superseded-wording errata register (C-1 through C-10): K=8 line; seed convention; the two "8 mandatory cells" lines; the five-line anchor-typo inventory with the canonical 64-hex form stated once; Part 2a.6; stale C14/C2(e)/C9 prints; v1's own G2-1 wording. Freeze-grade reconciliation path for string-matching auditors (§1.3(4)) |
| **R3-10** | minor | References | "Solver-in-the-Loop (Um et al., 2020)": the author string appears nowhere in the evidence map or session records; unverified bibliographic enrichment under a verified-citations-only rule with a documented bogus-citation incident in repo history | **FIXED** | Verification attempted against the publication record (NeurIPS 2020 proceedings) and failed to return usable evidence before freeze; per the reviewer's own fallback, References reverted to the map's title-only form "Solver-in-the-Loop (2020, NeurIPS)" with the failed-verification attempt recorded inline; no other author enrichment exists in the list |

## 4. Post-revision assessment (honest)

**What v2 closes.** All 28 issues are dispositioned FIXED with no rejections and no deferrals;
every formerly open "[TO BE PINNED AT D0]" item except the freeze timestamp and freeze sha256
is now pinned in the hashed text (counts, seeds, procedures, family memberships, gate
references, freeze mechanics, errata inventory). The statistical contract, restated C14, and
C16 items (13)–(16) form one internally consistent G1 target: 299,520 evaluation records,
450 checkpoints, 420 probes. No reviewer demand required weakening any honest condition,
status label, or concession — every KT-G/T status label in v2 is carried verbatim from v1,
and the two textual relabels (R2-9's infeasible-witness marking, O-B's exact-zero restatement)
strengthen precision rather than claims.

**What remains open before the D0 freeze (PI checklist, not v2-text gaps).**
1. **L1-4 RNG fix** (SPS edge sampling on global torch.rand) must land before D0 — v2 Annex
   A.7; cross-node byte-exact replay is otherwise contractual only by assumption.
2. **L2 CPU smoke** from the D1_13 code-only build (architecture + trainer + checkpoint
   format) must land and its compute anchors recorded; L2 V100-h figures remain planning
   estimates until then.
3. **E-2 preflight re-run** on the actual D0 corpus generator per the rewritten C2(e), with
   its caveat-only result recorded pre-freeze; a material endpoint-shaped insufficiency is a
   STOP-class PI decision item.
4. **PI ratification of the Annex B convention constants** (S3 seeds 20260974–76, bootstrap
   seed derivation, G9 stride, 10-seed subsets) at the v2 review — they follow existing repo
   conventions but are the one class of v2 additions the PI has not yet seen.
5. **Execution of the freeze mechanics** of §1.3 (commit → R2 immutable object → session log)
   on 2026-09-19.

**Verdict after revision: FREEZE-READY contingent on items 1–5.** The document package
(prereg v2 + amended contract + companions under the Annex C errata regime) is internally
consistent and hash-freezable as soon as the named pre-freeze engineering items land and the
PI signs the v2 review checklist. Nothing in the panel's record requires further revision
rounds; re-review is not required unless the E-2 preflight or the L1-4/L2 items change the
frozen semantics rather than merely landing.

---

*Provenance: authored by the preregistration-reviser agent; dispositions grounded in the
panel verdict JSON (workflow journal, D1_08), the v1 draft, the contract, the PI authorization
record D1_01–D1_14, the experiment plan, the theory appendix, the killer-tests/ops document,
the estimator menu, the simulator contracts, the lemma writeups, the D-2 evidence map, and the
K-preflight README — all read in full. Zero GPU, zero market data, zero confirmatory
endpoints, zero outcome access.*
