---
document: D0 calendar + freeze-date proposal (PI decision item)
authored: 2026-09-08
status: PROPOSAL — awaiting PI freeze-date decision; no date is changed by this document
basis: papers/proposal/ecomd_reexploration_d1_killer_tests_and_ops_2026-09-06.md §4–§5
  (session table, 3-week plan / 4-week hard ceiling); prereg v2 §1.2, §4.1, §8.2
decision_record: D1_18 (pre-freeze preparation track, 2026-09-08 "批准"/"为什么现在不做？")
---

# D0 freeze-date options and post-D0 calendar (proposal)

## 1. Pre-freeze readiness audit (2026-09-08, post regression-battery launch)

| # | Pre-freeze item | Status |
|---|---|---|
| 1 | Prereg v2 complete (28/28 panel issues; Annex B ratified D1_15) | DONE |
| 2 | Erratum C-11 (Neural Mechanics citation) applied + governance recorded (D1_17) | DONE 2026-09-08 |
| 3 | Nine [D0 BUILD] receipts with sha256 (E-1..E-5, L1-1/2/5, L2-2); independent verifier pass | DONE 2026-09-07 |
| 4 | E-2 preflight re-run on actual D0 generator: K=16 sufficient, no STOP | DONE 2026-09-07 |
| 5 | L1-4 RNG fix; L2 CPU smoke (D1_13) | DONE |
| 6 | Forecast-ledger d1 entries filed (gamma/alpha/merged) | DONE (ledger lines 87/108/128) |
| 7 | Remote pytest regression battery (v100ts, ecophys-d0v2, CPU-only; D1_18(a)) | RUNNING 2026-09-08, result gates any earlier freeze |
| 8 | **Analyzer contract** (freeze-list file per prereg §1.3: one-shot G1–G12 order, input record schema, bootstrap mechanics, macro emission; ops Pre-D0 row "analyzer macros + dummies") | **MISSING — must be authored + hashed pre-freeze** |
| 9 | **Cleanup scripts authored + Mac dry-run** (listing/hashes only; ops §4.1) feeding D0-S1 (D1_09) | **MISSING — must land pre-freeze (node execution stays D0-gated)** |
| 10 | Reflexive policy impl + Mac smoke (N≤500; ops Pre-D0 row) | **MISSING — not freeze-blocking if landed by D0+12 (cell runs days 14–16); schedule with items 8–9** |
| 11 | Freeze hash inventory from the nine receipts + freeze mechanics execution | Freeze-session work (D0), not separable |

Items 8–10 were planned as Pre-D0 ("Mac, legal now") in the ops timeline and are authorized under
the existing D1 blanket/build scope; they are Mac-legal (docs, config, listing/hashes, N≤500 CPU
smoke). Estimated effort: analyzer contract is the long pole (derive entirely from frozen
C1–C16/G1–G12/Annex B text + adversarial audit against the prereg); cleanup scripts + dry-run are
small; reflexive impl + smoke is medium.

## 2. Freeze-date options

| Option | Freeze date | Pre-freeze build window (items 8–10) | Hard campaign ceiling (D0+28) | Notes |
|---|---|---|---|---|
| A (pinned) | Sat 2026-09-19 | 09-09 → 09-18 (~10 days) | 2026-10-17 | Zero-risk buffer; ceiling coincides with verification_liquidity unseal (2026-10-17 UTC, unrelated domain, calendar crowding only) |
| B1 (aggressive) | Fri 2026-09-11 | 09-09 → 09-10 (2 days) + battery green today | 2026-10-09 | Only if all three builds land in 2 days; no slip room |
| **B2 (recommended)** | **Sat 2026-09-12** | 09-09 → 09-11 (3 days) | 2026-10-10 | All three builds + battery-green + one review pass; still 7 days of campaign margin gained |

There is no scientific reason to hold 09-19: prereg v2 is complete and ratified, the E-2 preflight
validated K=16, and outcome-blind discipline is indifferent to the freeze date. The 09-19 pin was
planning buffer (D1_08 reference calendar). The binding constraint is build readiness (items 8–10),
not science. Earlier freeze ⇒ Stage-2 completes ~10-10 vs ~10-17, giving a clean week of margin
before the verification_liquidity holdout unseal and any late-October venue checkpoints.

**This document changes no date.** The freeze date is a PI decision; until the PI explicitly moves
it, 2026-09-19 stands (D1_18 bounds note).

## 3. Post-D0 calendar (from ops §5 session table; shown for the recommended B2, with A offsets)

| Session | Ops day | B2 (freeze 09-12) | A (freeze 09-19) | Content |
|---|---|---|---|---|
| D0-S1 | 0–1 | 09-12 → 09-13 | 09-19 → 09-20 | Node cleanup → R2 relocation → verify ≥40% free; env sync + pip-freeze hash; CUDA torch install (disk-tight until cleanup completes); focused tests; seed-999 CUDA preflight; launch receipts |
| D0-S2 | 1–2 | 09-13 → 09-14 | 09-20 → 09-21 | D1 corpus generation (dual-arm, 30 data_seeds) + byte-exact re-derivation on both nodes |
| D0-S3 | 2–16 | 09-14 → 09-28 | 09-21 → 10-05 | Stage-1 training streams (GPU-a L1, GPU-b L2); first-record gate day 2–3; reflexive cell days 14–16; drift-subset retention. Stage-2 mechanical trigger t2: Stage 1 complete by D0+26 (B2: 10-08 / A: 10-15) |
| D0-S4 | 16–17 | 09-28 → 09-29 | 10-05 → 10-06 | Record-coverage + checkpoint-lock gates (G1–G12); one-shot analyzer execution; Stage-2 go/no-go via t1–t4 (mechanical only) |
| D0-S5 | 17–28 | 09-29 → 10-10 | 10-06 → 10-17 | Stage 2 if triggered (D2 corpora, training, eval, analyzer); else buffer/verification |
| D0-S6 | 28–29 | 10-10 → 10-11 | 10-17 → 10-18 | Final manifests, per-file hashes, R2 upload, freeze audit, work log |
| D1/D2 writing | post-S4/S6 | from ≈09-29 / done after 10-11 | from ≈10-06 / done after 10-18 | Paper E RESULTSPENDING fills + abstract after both workers complete and analyzers publish; D2 completion = outcome writing, not compute |

Standing constraints unaffected by either option: Stage-2 shrink ladder (slip > 5 d → variant A at
12 seeds; slip > D0+26 d or burn > 1,150 V100-h → cancel Stage 2); 4-week hard ceiling reserved
for the shrink ladder, not slippage; verification_liquidity holdout sealed until 2026-10-17 UTC;
Paper D terminal (abstract 2026-09-18 AoE, uploads 2026-09-25).

## 4. Recommended sequence to B2

1. 09-08 (today): battery green (item 7); this proposal to the PI.
2. 09-09 → 09-10: build item 8 (analyzer contract, workflow: draft from frozen clauses →
   adversarial audit vs prereg v2 → verifier); build item 9 (cleanup scripts + Mac dry-run against
   the Paper D deployment manifests, listing/hashes only).
3. 09-10 → 09-11: build item 10 (reflexive policy impl + Mac smoke N≤500); final compile + commit;
   freeze-file-list existence check (every §1.3 item present + hashed inventory assembled).
4. 09-12 (PI confirms): D0 freeze session — commit exactly the frozen file set → per-file sha256 +
   commit hash + timestamp → r2://ecophys/alpha_cube_d0_20261209… (archive name follows the chosen
   date; prereg §1.3 names `alpha_cube_d0_20260919/` — an earlier freeze requires the same
   one-line Annex-B(j)-style date amendment recorded BEFORE hashing, else keep the object name
   20260919 with the true timestamp inside freeze_record.json) → session log with etag.

Note on the archive name: prereg Annex B(j) pins "2026-09-19" as the freeze date and §1.3 pins the
R2 object path containing it. Moving the date therefore needs a single recorded pre-freeze
amendment (Annex B(j) + §1.3 path), lawful exactly like C-11, BEFORE the hash. This is a 2-line
edit + governance addendum; flagged here so it is not discovered mid-freeze.
