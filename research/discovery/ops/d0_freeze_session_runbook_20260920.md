# D0 freeze-session runbook + rehearsal record (2026-09-20)

Preparation artifact for the date-pinned D0 outcome-blind freeze **2026-10-09** (prereg v2
§1.3, as amended by C-12). NOT part of the frozen file set, NOT an amendment of any frozen
text. Produced by a 15-agent read-only readiness audit (7 resolvers + adversarial verify,
2026-09-20) plus a same-day mechanical rehearsal. Everything below is either (a) resolved
fact with evidence, (b) a rehearsed command sequence, or (c) an explicit PI one-liner listed
in §7. Nothing here executes the freeze early.

## 1. Resolved frozen path list (26 paths, deduplicated)

Prereg §1.3(2) enumerates 18 items; items (7) and (18) resolve to the same file, item (10)
expands to 5 files, (14) to 4, (16) to 3. Resolved list = 26 distinct repo-relative paths
(the exact list fed to the hash command):

```text
configs/reexploration/dgp/garch_student_t5.yaml
configs/reexploration/dgp/lab_asset.yaml
configs/reexploration/dgp/multiscale_logvol.yaml
ecomd/mechanisms/__init__.py
ecomd/mechanisms/through_m.py
ecomd/mechanisms/through_m_wrapper.py
experiments/lab_asset_a2/enrichment_20260906/enrichment_manifest.json
experiments/reexploration/k_preflight_20260906/results.json
experiments/reexploration/seed_stream_manifest_20260907/seeds_manifest.json
papers/proposal/ecomd_reexploration_analyzer_contract_2026-09-19.md
papers/proposal/ecomd_reexploration_contract_v1_2026-09-06.md
papers/proposal/ecomd_reexploration_d1_killer_tests_and_ops_2026-09-06.md
papers/proposal/ecomd_reexploration_d1_lemma_writeups_2026-09-06/kt_a2_tv_separation_and_kt_m2_template_table.md
papers/proposal/ecomd_reexploration_d1_lemma_writeups_2026-09-06/kt_g1_r2_non_lumpability_obstruction.md
papers/proposal/ecomd_reexploration_d1_lemma_writeups_2026-09-06/kt_g2_separation_lemma.md
papers/proposal/ecomd_reexploration_d1_lemma_writeups_2026-09-06/kt_g3_gauge_conflation_lemma_pair.md
papers/proposal/ecomd_reexploration_d1_lemma_writeups_2026-09-06/kt_g4_g5_chart_free_and_exposed_sets_2026-09-06.md
papers/proposal/ecomd_reexploration_d1_session1_record_2026-09-06.md
papers/proposal/ecomd_reexploration_d2_evidence_map_2026-09-06.md
papers/proposal/ecomd_reexploration_estimator_menu_2026-09-06.md
papers/proposal/ecomd_reexploration_experiment_plan_2026-09-06.md
papers/proposal/ecomd_reexploration_prereg_v2_2026-09-06.md
papers/proposal/ecomd_reexploration_simulator_contracts_2026-09-06.md
papers/proposal/ecomd_reexploration_theory_appendix_2026-09-06.md
scripts/lab_asset/dgp_request_generator.py
scripts/lab_asset/fiber_resampler.py
```

## 2. Expected-hash table (baseline 2026-09-20, HEAD ba293dc8e)

All 26 paths locally present (no iCloud placeholders; `experiments/reexploration/
k_preflight_20260906/results.json` is materialized), all tracked and clean. `shasum -a 256`,
LC_ALL=C lexicographic path order:

```text
793bb7f2992a2a0adb13d338dbe1f99a4ccb05b9ea7c29e5350da9bf4577aff3  configs/reexploration/dgp/garch_student_t5.yaml
06b9691af333be8a6891ee1213032a785e61c03c3c26e8f8a4beb159b202c801  configs/reexploration/dgp/lab_asset.yaml
5d853b6fab4b5eb4c14a136afece188ff7c33c62d64166da978bfe9868c2c4b3  configs/reexploration/dgp/multiscale_logvol.yaml
274ec4bceea3bdd4e9345595988ac75980c26486f5a27103288db87f910b97f0  ecomd/mechanisms/__init__.py
fb50bb4f1baec856001a1da31b9bdc6242669bfd49effdabb7fa374a665dc179  ecomd/mechanisms/through_m.py
4b0eeeafd0f44aec7c7dc26ca9571385d5a8a7cfb7a4d07dfae98c1e25ccb87d  ecomd/mechanisms/through_m_wrapper.py
17bad1b6366c0749fb24faa75732e1883184dd955a756e5ddd286aa9c4a3b916  experiments/lab_asset_a2/enrichment_20260906/enrichment_manifest.json
f61e410cd59c37b5624504a3cdf057c701b4b682067f948d2f8528ace018c2d4  experiments/reexploration/k_preflight_20260906/results.json
361679c4a56e8e7fe7d393499ed22f5c9f61bef81706a1befa8ca7df27ea32f8  experiments/reexploration/seed_stream_manifest_20260907/seeds_manifest.json
a25a0281111a9761667a16e72e019d94a6ff77eaa238b88905f30c38d012209a  papers/proposal/ecomd_reexploration_analyzer_contract_2026-09-19.md
845e6b7e4f21b93da9038c5bd255ff963787a832eb48000eb5ae060698700b9c  papers/proposal/ecomd_reexploration_contract_v1_2026-09-06.md
428b057b3527e733ec87b78fbd8a76e6dc0595d45c06949ab46d973501694da0  papers/proposal/ecomd_reexploration_d1_killer_tests_and_ops_2026-09-06.md
46f205131234ad7937d7a46d890a3c8bb144558ffbea16c5c33ba5a41a210bd5  papers/proposal/ecomd_reexploration_d1_lemma_writeups_2026-09-06/kt_a2_tv_separation_and_kt_m2_template_table.md
20da181eeef97c03ab6d29596ba1ad4e421cce9fa52becccef7e7f6bc6aabf14  papers/proposal/ecomd_reexploration_d1_lemma_writeups_2026-09-06/kt_g1_r2_non_lumpability_obstruction.md
31a502d4834b2f4a986252efa98a5fee044fe042712c45413fe48917e898fcf0  papers/proposal/ecomd_reexploration_d1_lemma_writeups_2026-09-06/kt_g2_separation_lemma.md
8416496e6975b3352fe22777239809a8105ce9f9773c3e2957fc7925f6dd0acb  papers/proposal/ecomd_reexploration_d1_lemma_writeups_2026-09-06/kt_g3_gauge_conflation_lemma_pair.md
d8c47b5fe5da44d3ce889d432d26dcf49ee080915b1e7243489a81dbc4635841  papers/proposal/ecomd_reexploration_d1_lemma_writeups_2026-09-06/kt_g4_g5_chart_free_and_exposed_sets_2026-09-06.md
db0fba0bcb38d9141449ba79773a3d7790b9e6708bbe676255a1f53d0c92f1f6  papers/proposal/ecomd_reexploration_d1_session1_record_2026-09-06.md
42b7174eb03320abd97e5da69f13bdb17c1bc7c7151cd440325148ca59d2b257  papers/proposal/ecomd_reexploration_d2_evidence_map_2026-09-06.md
3f6e7f4afb798a2df5fd835508096d7a08e7453ed7eb08bfdb3b108c906a24d5  papers/proposal/ecomd_reexploration_estimator_menu_2026-09-06.md
848091928f93cbc0e6136974c53357fda7acc71bcfea6fe9fabd8dbd8a221f3a  papers/proposal/ecomd_reexploration_experiment_plan_2026-09-06.md
42393bb6c3943dc20b4783812da0f5b34241494644ff079485f5f44adbb38eb4  papers/proposal/ecomd_reexploration_prereg_v2_2026-09-06.md
e99b23221519f69aca41c74e1c963ff891c78f9d32e9d1f18eb99e5a82e9e71c  papers/proposal/ecomd_reexploration_simulator_contracts_2026-09-06.md
247ee94f626da673ac6ba49af5e714696276f63c6f33ba8dca4627fc33abfbbd  papers/proposal/ecomd_reexploration_theory_appendix_2026-09-06.md
2cef5a334cc7f0020459062e3f37d76aab55d4440c8a305e50a222bfd4d72152  scripts/lab_asset/dgp_request_generator.py
023f0be3a8a808b85ac964012b1c701f651c5db04be28bf3a1463ed2281f6d32  scripts/lab_asset/fiber_resampler.py
```

Rehearsal commit-level hash over this manifest (placeholder-state prereg bytes, NOT a freeze
value): `56e368eb55d20441895c715e656df2103b12554531ec454878aee9cd58a2e211`. At the real
freeze the prereg row changes (pin fields filled) and nothing else should.

Pinned-hash cross-checks that already pass: K-preflight `f61e410c…18c2d4` (matches, Mac and
v100ts byte-identical); bundle anchor `fea8a136…9581c` (matches, Mac and v100ts).

## 3. Resolution decisions baked into the list (audit-confirmed)

1. **Items (7)+(18) same file.** `d1_killer_tests_and_ops` is the killer-tests doc AND the
   ops plan (analyzer-contract OPS row; gamma-activation decision text). Hash once; the
   18-item enumeration deduplicates to one path. A literal double-hash would change the
   commit-level aggregate.
2. **Item (10).** No MANIFEST file exists or is generated; the 5 per-file hashes ARE the
   directory manifest (recorded as such in freeze_record.json).
3. **Item (13) — string-vs-file trap.** The pinned `703ca36e…c4b` is sha256 of the
   `PREREG_STATEMENT` string inside `scripts/lab_asset/fiber_resampler.py` (asserted by
   `tests/test_fiber_resampler.py:562-566`), NOT the file. The freeze chain hashes the FILE
   (`023f0be3…`); the statement pin is satisfied by the passing test (run remotely) and both
   values are recorded distinctly. Hashing the file and comparing to `703ca36e` would
   false-alarm and stall the freeze.
4. **Item (14).** Generator = `scripts/lab_asset/dgp_request_generator.py` (DGPConfig
   production defaults in-module; do NOT hash the superseded
   `k_preflight_20260906/dgp_stream.py`). Config = the 3-file Hydra group
   `configs/reexploration/dgp/*.yaml`.
5. **Item (16).** The 3-file `ecomd/mechanisms` package (wrapper included; excluding it
   would leave a package file unhashed). Estimator tests are gate surfaces, not frozen
   modules.
6. **Item (2) "as amended".** The restatements live in prereg v2 §3.1, not in the contract
   bytes; the chain binds both files; freeze_record.json notes this reading.
7. **Known-stale companion text** (K=8, anchor typo `fea8b136…`, seed namespaces) is
   intentional per §1.3(4) — not byte drift; do not "fix" it.
8. **Auxiliary hashes recorded outside the commit-level chain:** e2-preflight-rerun
   `results.json` (its README asks it be hashed alongside; §1.3(2) does not name it),
   `bundle_manifest.json` (`fea8a136…`), the statement-string pin, the E-5 config-tree hash
   list from `d0_build_receipts_20260907/E-5/`.

## 4. R2 upload route (rehearsed end-to-end 2026-09-20)

`rclone` exists on NO host (Mac, v100ts, v100bts all probed; no config anywhere). The only
working R2 channel is Mac boto3: `ecomd/data/r2_sync.py` + repo-local `.env.r2` (mode 600,
created 2026-04-23). §1.3(3)(ii) mandates the object path and etag capture, not the tool, so
boto3 satisfies the clause. Freeze-day commands (Mac, seconds-scale governance I/O —
interpretation recorded in the session log for PI veto):

```bash
cd /Users/howardwang/Desktop/playground/ecophys
# pre-check: real prefix still empty
conda run --no-capture-output -n ecophys python -c \
  "from ecomd.data.r2_sync import R2Config,_client,_list_keys; c=R2Config.from_env(); print(list(_list_keys(_client(c),c.bucket,'alpha_cube_d0_20261009/')))"
# upload + etag
conda run --no-capture-output -n ecophys python -c \
  "from pathlib import Path; from ecomd.data.r2_sync import R2Config,_client,_remote_etag,upload; c=R2Config.from_env(); upload(Path('<repo>/freeze_record.json'),'alpha_cube_d0_20261009/freeze_record.json'); print('ETAG',_remote_etag(_client(c),c.bucket,'alpha_cube_d0_20261009/freeze_record.json'))"
```

Rehearsal evidence 2026-09-20: real prefix EMPTY (pre-freeze emptiness confirmed); rehearsal
object `r2://ecophys/rehearsals/d0_freeze_rehearsal_20260920/freeze_record.json` uploaded,
etag `8970a22db6006920cbb2fe073b265c09` (MD5 single-part), 7279 bytes, local sha256
`0116b009eda859fa86b771eb5db6ee871d8e997a26b20658d849fc7fc7e69270`. April credentials live.
Record local sha256 + byte size next to the etag (MD5 etag alone is not integrity).

Separate follow-up (NOT freeze-blocking): `scripts/d0_cleanup_archive.py` hard-requires
rclone (`shutil.which` guard) — rclone must be installed + a remote configured on the D0-S1
node before that tooling's upload/delete phases can run at campaign launch.

## 5. Freeze-session command sequence (2026-10-09, execute verbatim)

Order is §1.3(3)-mandatory; a failure at any step stops the freeze (no partial freeze). All
git invocations carry `-c core.checkStat=minimal -c core.trustctime=false`; staging is
explicit-path only (working tree carries must-not-ride-along private dirt: 5
`papers/paper_d_constraints/` paths + `output/pdf/` + untracked `revision-submission/` +
`scripts/rfx_diag_20260919.py` + the private paper_d memory file — none ever staged).

0. Precondition: `git branch --show-current` → `paper-d-iclr-2027-completion`; `ls
   .git/index.lock` absent (if present: `ps` for git processes, remove only if none); all
   26 frozen paths present, no `.icloud` placeholders (restore path if evicted: one-shot-flag
   `git checkout -- <path>`, then re-verify hash against §2).
1. Validators green: both offline fail-closed validators on v100ts (env `ecophys-d0v2`) AND
   locally (seconds-scale); record both outputs.
2. Fill the four prereg pin sites (wording in §6) — the ONLY frozen-file edit of the session;
   fill BEFORE hashing (hashed bytes must equal committed bytes).
3. Hash per §1.3(1) with commands + stdout recorded verbatim in the session log:
   `LC_ALL=C sort -u /tmp/frozen_paths.txt -o /tmp/frozen_paths.txt && LC_ALL=C sort -c
   /tmp/frozen_paths.txt` (path list = §1 exactly); `while IFS= read -r f; do shasum -a 256
   -- "$f"; done < /tmp/frozen_paths.txt | tee /tmp/per_file_freeze_manifest.txt`;
   `shasum -a 256 /tmp/per_file_freeze_manifest.txt` → **commit-level freeze sha256**. Never
   `shasum -b` (changes separator to `*`); repo-relative paths from repo root; final LF is
   part of the hashed bytes.
4. Freeze commit: stage exactly `papers/proposal/ecomd_reexploration_prereg_v2_2026-09-06.md`
   (the only changed frozen file), commit; verify `git show --name-only --pretty=format:
   HEAD` lists only the prereg; `git status --porcelain -- <26 paths>` empty; `git ls-tree -r
   HEAD -- <26 paths>` all present. Record `git rev-parse HEAD` (40-hex SHA-1 id) AND
   `git cat-file commit HEAD | shasum -a 256` (true sha256 of the commit object) — §1.3(3)(i)
   "commit sha256" is literally unsatisfiable in this sha1-format repo; record both labeled.
5. Step (ii): build `freeze_record.json` (fields: freeze_timestamp UTC ISO-8601; ordered
   frozen_paths; per_file {path: sha256}; commit_level_freeze_sha256; git_commit_id_sha1;
   git_commit_object_sha256; resolved_defaults from §3; auxiliary hashes; commands_verbatim)
   and upload per §4; capture etag + local sha256 + size.
6. Step (iii): session-log entry in `logs/2026-10-09.md` (hash commands + stdout verbatim,
   commit id, etag), then a SECOND commit staging only that log file.
7. Record the FLAG-12 line: "L1-4 LANDED pre-freeze: commit 15e139928 (2026-09-06) threads
   the rollout generator into TypedRelationalPotential._sample_edges (ecomd.py,
   ecomd_v2.py, 13 tests); FLAG-12 not raised; G8/G9 L1 byte-identity premise contracted."

Tree-contains reading of "commit containing exactly the frozen file set" (audit-argued,
PI-blessed at session open): all 26 paths present in the commit TREE at their recorded
hashes and clean; the freeze commit itself is the prereg pin-fill commit; which
tree-containing commit is THE freeze commit is singled out by the recorded commit id in
freeze_record.json. A diff-equals reading is impossible (would require churning pinned
hashes, violating §1.3(4)) and would forbid the step-(iii) log commit.

## 6. Pin-field fill drafts (four sites, applied at step 2)

`<TS>` = UTC ISO-8601 minute precision, `date -u +%Y-%m-%dT%H:%MZ`, one canonical string
reused in document, record, commit message, and log. The timestamp embeds pre-hash (no
circularity); the freeze sha256 does NOT embed (it hashes this file's bytes) — pointer
wording instead, lawful per panel ADJ-4 ("only the freeze timestamp and freeze sha256 remain
D0-pinned") + §1.3(3) as the canonical recording location. NOT edited: line 830/1501
narrative statements and the panel response (historical per C-12).

- **Site A** (front-matter ~13-14): replace the `freeze_policy:` tail with: "sha256-frozen
  at D0 2026-10-09, executed <TS> (UTC ISO-8601; the instant the Section 1.3(1) hash command
  ran); the freeze sha256 is not embeddable in this document (it hashes this file's own
  bytes) and is pinned per Section 1.3(3) in r2://ecophys/alpha_cube_d0_20261009/
  freeze_record.json and the D0 session log; no [TO BE PINNED AT D0] item remains."
- **Site B** (line ~56 version-chain cell): "Executed <TS> (UTC ISO-8601); freeze sha256 =
  the Section 1.3(2) commit-level hash, pinned in r2://ecophys/alpha_cube_d0_20261009/
  freeze_record.json and the D0 session log with R2 etag (not embeddable here: it hashes
  this file's bytes); per-file hashes and git commit id in the same record."
- **Site C** (line ~1258 annex cell): "Timestamp <TS> (UTC ISO-8601), pinned here; freeze
  sha256 pinned externally per Section 1.3(3) in r2://ecophys/alpha_cube_d0_20261009/
  freeze_record.json + D0 session log (self-embedding excluded by construction)."
- **Site D** (line ~1398-1400 tail): "; frozen <TS> (UTC) with the freeze sha256 recorded
  per Section 1.3(3) in r2://ecophys/alpha_cube_d0_20261009/freeze_record.json and the D0
  session log (not embeddable in this document, which it hashes)."

## 7. PI one-liners needed at (or before) session open

1. Item (7)=(18) same-file resolution + §3 defaults (or PI names different artifacts).
2. Tree-contains reading of §1.3(3)(i) + the dual commit-id record (sha1 id + object
   sha256).
3. Mac boto3 as the freeze-record upload channel (governance I/O, not an experiment).
4. Keep `scripts/rfx_diag_20260919.py` untracked through the freeze (deliberate-uncommitted
   list).
5. Confirm .env.r2 credential backup exists PI-side (gitignored; unrecoverable from repo).

## 8. Failure paths (pre-planned; all end in §1.3(3) STOP, none in silent repair)

| Failure | Response |
|---|---|
| R2 unreachable / credential dead | Stop after step (i) is committed; resume = complete (ii)/(iii) with completion timestamp recorded; never re-hash silently. (Rehearsal 09-20 says credentials live.) |
| iCloud eviction of a frozen path | All 26 are git-tracked: one-shot-flag `git checkout -- <path>`, re-hash, proceed. `.env.r2` is the only gitignored dependency — PI-side backup. |
| Hash mismatch vs §2 table | Stop; only lawful repair is a PI-approved pre-hash erratum on the C-11/C-12 precedent, recorded before any freeze hash. Never a silent edit. |
| Validators red | Fix registry data first; the freeze commit must not mix validator repairs into the frozen set. |
| No remote host reachable | Stop (C-12 forbids Mac-side validator execution); retry when connectivity returns. |

## 9. Known-typos to copy verbatim (do not "correct" on the day)

Real object path `alpha_cube_d0_20261009` (C-12 amended). Typo inventory seen in the wild:
`20260919` (pre-amendment), `20261209` (calendar proposal), `YYYYMMDD` (ops doc
placeholder), `20260909` (this audit's own task text). Copy the path from prereg v2
§1.3(3)(ii) on the day.
