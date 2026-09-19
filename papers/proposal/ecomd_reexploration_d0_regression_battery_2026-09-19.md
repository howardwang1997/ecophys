# EcoMD reexploration — D0 regression battery v3 (2026-09-19 re-verification record)

Status: EXECUTED. Durable in-git record of the pre-freeze re-verification of the
2026-09-08 battery (`ecomd_reexploration_d0_regression_battery_2026-09-08.md`)
against the current tree. Raw receipts live outside git by design (`logs/private/`
is gitignored "sealed/private research state"): Mac
`logs/private/regression_v3_20260919/{summary.tsv,COMPLETE,logs/,postsync/}` and
node v100ts `/root/regv3/`; this document is the committed record (09-08 §0
precedent — v2 receipts in /tmp were volatile).

## 0. Scope and environment

- Host: v100ts, checkout `/root/ecophys-remote` (partial rsync face; git objects
  staged, HEAD ancestry empty except staged refs), env `ecophys-d0v2`
  (CPU torch 2.11.0), per the 2026-09-19 PI compute-location rule (no execution
  of any size on the Mac).
- Driver: `scripts/reg_battery_v3_driver_20260919.sh`, v2-equivalent semantics:
  one fresh pytest process per `tests/test_*.py`, `timeout 1200`, env bin
  prepended to PATH (conda openssl for the keccak/aave tests), and
  `-m "not slow"` ONLY for `test_bptt_checkpoint.py` (recorded 09-08 exclusion,
  unchanged; no test deleted or weakened).
- Tree state: mirror synced to full route-graph locator coverage before the
  post-sync epoch (commit-delta ffe196877..HEAD over the 09-08 file set, then
  papers/proposal ×191, tracked logs/ ×66, 5 tracked experiments/paper_g
  artifacts, 2 logs/private files for the mirror-green demonstration).

## 1. Results

154 files / 1562 tests. Two epochs (mid-sync and post-sync) produced an
**identical rc set**: 151 rc=0, 3 rc=1.

| vs 09-08 baseline (146 files) | count | detail |
|---|---|---|
| green both | 143 | no unexplained change |
| new since baseline, all rc=0 | 8 | test_d0_cleanup_archive, 6× test_paper_g_*, test_reexploration_reflexive |
| dropped | 0 | — |
| red→green | 1 | test_bptt_checkpoint (recorded `-m "not slow"` exclusion; narrowed selection, not an estimand-identical pass) |
| green→red | 1 | test_research_route_graph (§2.3) |
| red both | 2 | test_dynamic_graph (same failure), test_research_discovery (cause changed, §2.2) |

## 2. Dispositions of the three red files

### 2.1 test_dynamic_graph.py — carried forward, unchanged from 09-08

Single failure `test_default_off_equivalence`: pinned reference constant
0.263843 vs computed 0.0758 (identical on both epochs and on the 09-08 record —
no env drift; 0.18802 sometimes quoted is |pinned − computed|). The constant was
invalidated before the baseline by commit 15e139928 (L1-4 RNG fix); the 09-08
doc already dispositioned it pre-existing red on both platforms. Fix is
PI-optional re-pinning (no oracle change).

### 2.2 test_research_discovery.py — cause changed since 09-08; 2 residual failures

The 09-08 cause (forecast-ledger unregistered route) is since fixed. Post-sync
residuals:

1. `test_canonical_discovery_contract_validates` — `g_response_dx_20260912`
   launcher sha256 pin `f04ff05b…` matches neither the mirror working tree nor
   the mirror's partial-git history. **Node-only red** (09-08 doc §5.3.5
   git-history-binding class): canonical passes — the pinned blob is committed
   at 6727e7dad and the history fallback finds it in any full-history checkout
   (CI at fetch-depth:0 green; local validator rc=0).
2. `test_search_cycle_f1_deferral_does_not_invent_f2` — stale live-count pin
   `(36, 173, 0)` vs live ledger `(38, 191, 0)` (38 cycles / 191 raw questions,
   confirmed by the canonical validator output). **Canonical-red**,
   tree-independent. Fix is a PI re-pin/delta-assert decision (09-08 §5.1
   precedent).

### 2.3 test_research_route_graph.py — the one green→red; 2 stale pins + 1 governance finding

Mid-sync epoch: 7 failures, all cascading from locator paths missing on the
incomplete mirror — 5 tracked `experiments/paper_g/` artifacts (sync-scope
artifact, since synced) + 2 gitignored `logs/private/` files (scp-ed to the
mirror for the demonstration). Post-sync residuals, exactly 2, both
**canonical-red and tree-independent**:

1. `tests/test_research_route_graph.py:58` pins "1995 evidence/artifact
   locators" vs live 1997 (graph legitimately grew: 91c08c767 g42 +1,
   21359e930 GAMMA activation +1; test last touched 55af5d0aa).
2. `tests/test_research_route_graph.py:73` open-routes dict pins
   `reexploration_merged_gamma_led_paper: parked` while 21359e930 set it
   `active` — a route-STATUS pin, so re-pinning 1995→1997 alone does not green
   the file.

Governance finding (canonical, new): route-graph locators
`nodes[0].artifacts[11]` (`logs/private/paper_g_dx_legacy_subject_alignment_20260912.md`)
and `response_dx_terminal_private_audit`
(`logs/private/paper_g_response_dx_terminal_audit_20260912.json`) reference files
that `.gitignore:280` deliberately never commits. Canonical validator green is
worktree-only for these two (is_file gate, validate_research_route_graph.py:391-397);
any tracked-content-only face (fresh clone, CI checkout, tarball without .git)
fails them. Exactly 2 such locators; the other ignored roots have zero
references. Timing: prereg §1.3(3)(i) lands the freeze commit on
paper-d-iclr-2027-completion and the required research-governance check on main
is pull_request-triggered — this disposition is **merge-blocking, not
freeze-blocking**.

## 3. Epoch control and adversarial verification

- The first (mid-sync) epoch certified the 151 greens against an incomplete
  mirror; the full post-sync rerun (19:59–20:31 +08:00) reproduced the identical
  rc set — no wrong-reason greens, no epoch-dependent outcomes. Wall time
  1936 s vs 1278 s (shared-node load; test_research_discovery 27 s → 553 s with
  an identical 2-failure set).
- `test_github_verification_liquidity_contract` mirror-red (09-08) → rc=0 (v3):
  the commit-delta staging added object 9d365a98f to the mirror's object store,
  so object-level `git show` resolves while HEAD ancestry stays empty. Not a
  test or tree change.
- Adversarial verification (Ultracode workflow wf_42a5920f-4e3, 15 agents):
  10 CONFIRMED / 3 PARTIAL / 1 REFUTED-as-worded over 7 claims; the material
  corrections (route-status pin kind; node-only launcher red; merge-vs-freeze
  timing; mid-sync epoch) are incorporated above. Both offline fail-closed
  validators green on canonical throughout.

## 4. PI decision items — ALL APPROVED 2026-09-20 ("都批准", decision
pi_battery_v3_dispositions_20260920) and executed

1. Four drifted test pins — re-pinned, each traced to its documented commit
   (dynamic_graph 0.263843→0.075823 via 15e139928; discovery f1
   (36,173,0)→(38,191,0); route_graph 1995→1997 via 91c08c767+21359e930;
   route_graph parked→active via 21359e930). Remote verification on v100ts:
   test_dynamic_graph rc=0, test_research_route_graph rc=0,
   test_research_discovery rc=1 with exactly the accepted node-only
   launcher failure (item 3).
2. Two gitignored route-graph locators — keep + document (this record).
   Consequence stands: merge-blocking at the post-freeze PR to main
   (pull_request-triggered governance check), NOT freeze-blocking; handling
   scheduled to that merge.
3. Node-only launcher-pin red — accepted as the 09-08 §5.3.5
   git-history-binding class (canonical + CI fetch-depth:0 green; blob at
   6727e7dad).
4. Mid-sync epoch — already resolved by the identical post-sync rerun (§3).
5. Durable record + script disposal — this document and the driver script
   committed; `scripts/rfx_diag_20260919.py` stays deliberately uncommitted.
6. Queue acceptance criterion — recorded amendment: "no unexplained
   regressions; every red dispositioned" (satisfied by this battery:
   3 red files, all dispositioned, zero unexplained).
7. Commit authorization — the battery change set authorized and committed.

Post-disposition battery state on the node: **153/154 green, 1 documented
node-only red**; canonical and CI faces fully green.
