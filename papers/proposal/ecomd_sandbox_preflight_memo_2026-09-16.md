# Exploration-sandbox preflight memo — 2026-09-16

Scope: precondition work for any g38/g42 exploration-sandbox authorization, per the
strategy review of 2026-09-16 and the PI's selection of the sandbox-preflight option.
No sandbox is authorized by this memo. No scientific claim is made or supported here.

## 1. Adversarial launcher review — outcome

A 19-agent adversarial review of the enforcing launcher
(`scripts/run_research_discovery_sandbox.py`), the quarantine handler, and their
interaction with the validator produced 14 findings; after deduplication, 13 distinct
defects, all confirmed on re-examination. Root causes:

- All enforcement state (budgets, quarantine mandate, protected history) derived from
  the mutable working tree and the local git object database, with no anchor outside
  them. `git restore`, ledger erasure, or ref forgery reset everything.
- The branch config was digest-validated at load but bind-mounted by path at run: a
  TOCTOU swap executed unvalidated bytes while the ledger recorded the validated digest.

## 2. Fixes landed (commit 4173f9e6f)

- Out-of-tree hash-chained anchor at
  `~/.ecomd/discovery_sandbox_anchors/<sandbox_id>.jsonl`; enforcement refuses erased,
  rewritten, terminal, base-rotated, and corrupt-chain anchors.
- Config digest re-verified before `branch_opened`, between open and container start,
  and after container exit; any mismatch fails closed to an unfinished branch, which
  the quarantine path then terminalizes.
- Working-tree manifest re-checked against the genesis `manifest_sha256`.
- Finished-branch receipts re-hashed against their ledger digests in launcher and handler.
- Expired sandboxes with unfinished branches can now be quarantined (validation pinned
  to `min(now, expires_at - 1s)`); previously an expired interrupted branch was
  unquarantinable and the sandbox could never terminalize.
- `branch_opened` records `launcher_base_ref`/`launcher_base_commit` provenance.
- Sandbox lock moved out of `/tmp` with a post-acquisition inode check.
- Container capture opens its sinks before `Popen` and holds the loop in `try`.
- Quarantine resumes after a crash between appends and completes the taint registry for
  a terminal sandbox missing its entry.

Verification: `tests/test_run_research_discovery_sandbox.py` 23/23; sandbox/branch
subset of `tests/test_research_discovery.py` green; ruff and `mypy --strict` clean on
the governance scope.

## 3. Launcher-pin governance defect — found and fixed while restoring validation

Manifests pin `execution_contract.launcher`/`incident_handler` digests, and the
validator hashed the working-tree file. Two consequences, both observed:

1. Any edit to a shared launcher script permanently broke validation of every terminal
   manifest pinning it. Two sandboxes pinning different versions of one shared path
   could never both pass.
2. The response-DX authorization (2026-09-12) existed only as untracked files; its
   freeze commits (9d9071196, ac49b0e21) are contained by no branch and would not
   have survived reflog GC. The pinned bytes were one `git gc` away from being
   unverifiable.

Resolution:

- Commits 6727e7dad + 52a328c01 land the authorization (genesis ledger, manifest,
  decision, inputs, pinned launcher/handler bytes) and then the terminal record
  (execution ledger, branch evidence, result, taint entry) as separate commits, as the
  authorization-only rule requires.
- The validator now accepts, for terminal sandboxes only, a committed version of the
  pinned file (git history, capped at 64 commits) in addition to the working tree.
  Live sandboxes still require the working-tree file to match exactly. Covered by four
  new tests, including the never-committed case and the live-sandbox strict case.

State: `validate_research_discovery.py --base-ref HEAD` green; canonical contract test
green (counts refreshed to evidence 1390 / 191 raw questions / 38 cycles).

## 4. Required check + force pushes — resolved 2026-09-16 (public repository)

While the repository was private, both the branch-protection and rulesets APIs returned
403 (GitHub Free): "Upgrade to GitHub Pro or make this repository public." The PI selected
the public-repository option. Before executing it, the 2026-09-05 private setting was
traced to its actual rationale: Paper D ICLR-2027 double-blind protection — the repository
had been public before, original commit IDs in formal provenance were the leak channel,
and the change was recorded as reversible after the ICLR 2027 decision, with the abstract
deadline on 2026-09-18. The PI re-confirmed the flip with that context disclosed.

Pre-flip credential scan: tracked tree clean (keyword hits are research-context false
positives; `.env.r2.example` holds empty placeholders only); a full-history filename scan
found only the two example env templates, placeholder-empty in every committed version;
`.env.r2` is gitignored and `logs/private/` untracked. `howardwang1997/ecophys` is public
as of 2026-09-16, and `main` carries the required `research-governance` check (strict),
force pushes and deletion disabled, and administrator bypass off. Launcher-side
compensating controls from the original option 3 remain in force; first-launch
`--base-ref` is still recorded rather than externally enforced.

## 5. Named residuals (documented, not fixed)

- A same-uid attacker can erase `~/.ecomd` (anchor root). The anchor raises the bar
  against accident and self-discipline failure, not against a deliberate local attacker.
- A millisecond-scale window remains in which the config can be swapped between the
  final re-hash and `Popen`. A staging-copy approach was considered and rejected:
  stray branch files break artifact-schema strictness.
- First-launch `--base-ref` is operator trust; provenance is recorded, not enforced.
- Required-CI-check and force-push disable were platform-blocked until 2026-09-16; now
  satisfied via the public repository and `main` protection (Section 4).

## 6. What remains before any execution authorization

1. A separate authorization-only merge for the Bourse 0.4.0 execution design.
2. the g42 fixed-knot learned-moves sandbox manifest and decision record (PI selection
   2026-09-16; g38 not selected; per-sandbox launcher copies under `sandbox_inputs/<id>/`
   are preferred over shared `scripts/` pins; the fixture already follows this shape).
3. ~~PI decision on Section 4~~ resolved 2026-09-16: platform gate satisfied (Section 4).
4. Consider an out-of-band backup of the anchor root if sandbox runs resume.

Not a search cycle: no ledger entry, no new literature, no registry change, no card,
no execution. Paper G 107/31/0 unchanged; evidence 1390 unchanged.
