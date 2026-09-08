---
document: Remote regression battery work record (D1_18(a) closure evidence)
authored: 2026-09-08
status: WORK RECORD — battery complete; one canonical governance finding pending PI
  fix decision; no GPU, no outcome access, no frozen-bundle writes occurred
decision_record: D1_18(a) (pre-freeze preparation track, pi_reexploration_d1_
  authorization_20260906.yaml addendum D1_ADD_prefreeze_erratum_c11_20260908)
code_face_verified: commit ffe196877 (paper-d-iclr-2027-completion); record landed in
  commit bb5f7de36
worker: v100ts (/root/ecophys-remote, conda env ecophys-d0v2, CPU-only throughout)
---

# Remote pytest regression battery — work record (2026-09-08)

## 1. Goal and scope

D1_18(a) directed a full pytest regression battery on the remote worker as pre-freeze
code-face verification: run every test in the repository against the exact commit the
D0 campaign will execute, on the machine class that will run it, before any freeze-date
decision is acted on. Everything ran on v100ts (CPU-only); the Mac performed file edits,
single-test spot checks (seconds each), and syncs only, per the 2026-09-06 compute-
location rule.

## 2. Incident record

### 2.1 First launch: environment abort at collection (29 errors)

The first battery launch aborted during collection with 29 errors in two classes:

1. Missing pip modules in env ecophys-d0v2: `pyarrow` (21 files), `jsonschema` (3),
   `matplotlib` (1), `statsmodels` (1).
2. Unsynchronized trees that tests reach into (the remote was a code-face mirror):
   `papers/paper_d_constraints/` (tests import `make_pdebench_*` from its `figures/`),
   `experiments/lab_asset_a2/`, and — discovered progressively across reruns —
   `research/`, `.claude/`, `results/`, `data/sample/`, `data/raw/yfinance/`,
   `data/raw/binance/` (symlink farm into `data/sample/binance/`), and
   `experiments/{080_baselines_30seed, 108_neural_sde_scout, 113_gabaix_solve,
   114_concave_confirm}`.

After module install and the first syncs, a collection-only pass was clean: **0
collection errors** (pytest-reported 147 files / 1,396 tests; see §6 note on counting).

### 2.2 Monolithic run OOM-killed at ~8%

The full `pytest tests/` single-process run was killed by the kernel OOM killer at
roughly 8% progress:

```
[二 9月  8 00:10:06 2026] Out of memory: Killed process 3556584 (python)
  total-vm:39617804kB, anon-rss:29694904kB
```

A single pytest process reached ~29.7 GB anonymous RSS on the 32 GB node. Per-file
isolation identified the allocator:
`tests/test_bptt_checkpoint.py::test_chunk_64_runs_under_checkpoint`
(`@pytest.mark.slow`; 200 agents x 64 steps, `create_graph=True` — GPU-node-sized by
design; "Sanity: large chunk + checkpoint completes without OOM at small N"). The repo
pytest config (`addopts = "-ra -q"`, `testpaths = ["tests", "ecomd"]`) has **no
slow-marker exclusion**, so any plain invocation attempts it. It OOMs any CPU host,
including the Mac.

Also recorded: the first completion watcher used `pgrep -f "pytest tests/"`, which
matched its own ssh command line and would never have exited; killed and replaced with
bracket patterns (`[p]ytest`) and, in the final design, marker files instead of process
matching.

### 2.3 v2 design: per-file isolation battery

Each `tests/test_*.py` file runs in a fresh process with a 1200 s timeout; per-file
exit codes append to a summary; one file's OOM or hang cannot kill the battery. The
slow-marked bptt test was excluded via `-m "not slow"` in that file's rerun only
(deferred to node execution at D0-S1 focused tests; no test was deleted or weakened).

## 3. Environment completion ledger (v100ts, env ecophys-d0v2)

All changes are on the worker only; nothing here touches the frozen face.

| Change | Reason | Note |
|---|---|---|
| pip `arch` | garch / stylized-facts tests | tiny, pure-python |
| conda `openssl` 3.6.4 (env-level) | system OpenSSL 3.0 lacks `dgst -keccak-256`; aave family shells out to `openssl` | battery reruns prepend the env `bin` to PATH |
| `git init` + empty HEAD commit `f889de6a` | `test_fact_surrogate` runs `git rev-parse HEAD`; mirror had no `.git` | history objects deliberately NOT fabricated (§5.4) |
| torch **2.14.0+cpu → 2.11.0+cpu** | align the verification node to the development env (local 2.11.0); installed-unpinned torch had drifted to latest | did not change `test_dynamic_graph` (its failure is not version-caused, §5.1) |
| 13 tree syncs (rsync -a; `data/raw/binance` with `-L`) | tests reach into docs/data/results trees beyond the code face | binance parquets are symlinks into `data/sample/binance/`; `-L` copies the 7.5 MB of real files so snapshot hashes resolve |

## 4. Final tally (146 `test_*.py` files enumerated)

**142 green on the remote mirror**, including every Paper-E / D0-campaign load-bearing
suite: lab-asset-v3 conformance (27), fiber resampler, corpus projector, estimator
menu, `experiments/constraint_attribution_iclr`, ecomd model/training modules, K- and
seed-discipline tests.

4 red, each dispositioned with evidence:

| # | File | Disposition | Evidence |
|---|---|---|---|
| 1 | `test_dynamic_graph.py` (1 of 6 tests) | **pre-existing red on BOTH platforms** — stale hardcoded baseline | assertion expects `0.263843` (comment: "verified repeatedly during arch-extensions sprint"); Mac and x86 both compute ≈`0.0758` (0.07582287…), deterministic across torch 2.11/2.14; verified red on the Mac 2026-09-08 |
| 2 | `test_research_discovery.py` | **CANONICAL RED — real finding**, see §5.2 | `DiscoveryValidationError: forecast ledger.forecasts[3].subject_route_id is unknown: reexploration_merged_gamma_led_paper`; reproduced identically on the Mac |
| 3 | `test_research_route_graph.py` | canonical **green locally** (verified); mirror red only because node artifact paths span the full 5.5 G `experiments/` tree | local `test_canonical_graph_validates_offline` passes; remote error is artifact-path reachability |
| 4 | `test_github_verification_liquidity_contract.py` | canonical **green locally** (verified); needs `git show 9d365a98f:configs/...` (history closure ≈ 80.6k objects) | deliberately not fabricating partial history on the mirror |

## 5. Findings and follow-ups

### 5.1 Stale baseline constant (low priority, PI-optional)

`test_default_off_equivalence` pins a Tier-4.2-era trajectory constant that the
current code no longer reproduces on any platform. Not Paper-E load-bearing (edge
gating is default-off legacy). Optional test-only fix: re-pin the constant with a
dated note, or compare gating-off against a dynamically computed baseline. Any such
edit is pre-freeze-legal (tests face) and must be committed.

### 5.2 The canonical finding: ledger references an unregistered route

Six forecast-ledger entries (d1 series, first filed 2026-09-06) carry
`subject_route_id: reexploration_merged_gamma_led_paper`. The canonical route
knowledge graph (`.claude/memory/research_route_knowledge_graph.yaml`) contains **no
node with that id** — its only `status: active` route is `verification_liquidity`. The
string "reexplor" appears nowhere in the graph. The 2026-09-06 reexploration
authorization (Paper E route) was recorded in decision YAMLs, memory, and the ledger,
but never registered as a graph node; the graph is therefore stale relative to the
ledger, and `test_canonical_discovery_contract_validates` fails on the canonical repo
itself.

Proposed fix (pending PI approval, C-11 precedent): register a `research_route` node
`reexploration_merged_gamma_led_paper` (status active, opened_at 2026-09-06, phase per
protocol, locators to the D1 authorization files), re-run the discovery validators,
and note the amendment in the session log. The knowledge graph is **not** in the
freeze hash chain, so this does not touch the frozen face. Until fixed, freeze-
readiness item 7 (battery green) is green-except-this-finding.

### 5.3 Operational lessons carried into D0

1. CPU batteries must run per-file (or with `-m "not slow"`): one slow-marked
   GPU-sized test can OOM any monolithic run on this node class.
2. The worker env must pin torch to the development version (2.11.0) — unpinned
   installs drift; the D0-S1 CUDA install should pin the matching CUDA build.
3. Any aave-family or keccak-dependent run needs the env openssl on PATH
   (`/root/miniconda3/envs/ecophys-d0v2/bin`).
4. `data/raw/binance` is a symlink farm into `data/sample/binance/` — sync with `-L`
   or stage both; snapshot validators hash real bytes.
5. Repo-hygiene tests split into two classes: those valid on a code-face mirror, and
   canonical-repo-integrity tests (git-history binding; full-tree artifact
   reachability) that only make sense on the canonical repo / CI. The battery receipt
   records the split rather than forcing the mirror to fake canonical state.

### 5.4 What was deliberately NOT done

- No history objects were pushed or fabricated on the mirror (`git show`-dependent
  tests stay canonical-only).
- The 5.5 G full `experiments/` sync was declined (≈85 min link time) — only the
  trees the campaign and the failing tests actually need were staged.
- No test was deleted, weakened, or edited; the only exclusion (`-m "not slow"` for
  one file's rerun) is recorded here.

## 6. Receipts

- Per-file summaries on worker: `/tmp/regv2/summary.tsv` (+ `rerun1/`, `rerun2/`);
  volatile across reboots — this document is the durable record.
- Log tail of the OOM-killed monolithic run: `PYTEST_EXIT=137`, progress ≈8%.
- Local spot checks (canonical): `github_verification_*` 7/7 green;
  `test_research_route_graph.py::test_canonical_graph_validates_offline` green;
  `test_research_discovery.py::test_canonical_discovery_contract_validates` **red**
  (the §5.2 finding); `tests/test_exp127_v100_worker.py` 3/3 green.
- Counting note: pytest's collection pass reports 147 files / 1,396 tests while
  `find tests -name "test_*.py"` enumerates 146; no `*_test.py` files exist. The
  1-file difference is a counting-convention artifact (not an untested file: every
  file matched by pytest's own default patterns was run or explicitly dispositioned
  in the rerun rounds).

## 7. Standing constraints (unchanged, restated)

No GPU allocation before D0; no confirmatory execution, analyzer run, or outcome
inspection; no market-data access or purchase (the binance/yfinance syncs move
existing repo-internal fixtures for tests only); frozen a2_exit_20260905 bundle
untouched; verification_liquidity sealed until 2026-10-17 UTC; Paper D terminal;
K=16 immutable; prereg v2 remains the freeze candidate.

## 8. Pending PI decisions (as of this document)

1. Register the reexploration route node in the knowledge graph (§5.2) — gates the
   clean "battery green" statement.
2. Freeze date: A (2026-09-19) / B1 (09-11) / B2 (09-12, recommended) per
   `ecomd_reexploration_d0_calendar_proposal_2026-09-08.md`.
3. Paper E title: option A (drop clause, recommended) / B / C per
   `ecomd_paper_f_recording_design_concept_2026-09-08.md` §1.
4. Optional: `test_default_off_equivalence` constant re-pin (§5.1).
