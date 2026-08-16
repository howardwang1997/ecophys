# Aave V3 liquidation-threshold source/effect preflight v1 — result

**Protocol commit:** `fdb1dc41497a4eca9e740dbd196061208e61c584`

**Pinned Aave source commit:** `cff15de6d1271b0c800fc001f4aea4c263e8a597`

**Manifest SHA-256:** `2656f0966d2e0c74b74eb2b147ef6e50bcb7838b078edef6e3552d66b2933ccc`

**Summary SHA-256:** `355928afb19ab4b4a8f6de0b786986e9aa4542e1394a3acac7b14dc1ebbc85e9`

## Decision

`PASS_SOURCE_EFFECT_IDENTITY_AUTHORIZE_AAVE_CHAIN_EVENT_INVENTORY_DESIGN_ONLY`

All twelve conjunctive gates passed. This authorizes only a separately frozen Ethereum deployment/version and
liquidation-threshold event-inventory **design**. It does not establish that an eligible event exists; it does not
authorize event scanning, governance payload access, account reconstruction, participant responses, G1 admission
or GPU work.

## Execution integrity

The protocol was committed, pushed and reproduced at the remote branch before source staging. The audit ran once
from a clean detached EcoPhys worktree at the exact protocol commit. Its separate source worktree had the official
remote, exact detached source commit, clean status and exactly the fourteen sparse files in the manifest. Both
success/failure paths were absent before launch. The first run wrote `artifacts/summary.json`; no `failure.json`
exists, and v1 was not rerun.

The source inventory contains fourteen files, 197,890 bytes, 63 required normalized markers and distinct SHA-256
hashes. Inventory SHA-256 is `61984d36118a448c451c98ad9be9fefb0882174f11466eff3e8e12be0912bb79`.
Every marker, all seven `configureReserveAsCollateral` transition checks, all five deterministic identity checks
and every access lock passed. The artifact retains no raw source body.

## Source-certified operator

For the strict eligible route—positive changed-reserve collateral, positive debt, base LT not overridden by eMode,
strict positive LT decrease, unchanged LTV/bonus and fixed T−1 balances/prices/indexes/other configuration—the
pinned arithmetic supports

\[
W^+ = W^- - C_j^-(L_j^- - L_j^+), \qquad
H^+ = \operatorname{wadDivHalfUp}(W^+,D^-)/10{,}000.
\]

The deterministic direct self-check moved HF from `1.066666666666666666` to `0.933333333333333333`, crossing the
HF=1 boundary while satisfying the exact weighted identity and monotonicity. This is a synthetic known-answer
case, not an observed Aave account or effect size. The eMode-override and disabled-collateral self-checks both had
exactly zero direct base-LT effect.

The source also certifies why candidate filtering must be strict:

- `configureReserveAsCollateral` does not iterate or write user configurations, but its frozen-reserve path can
  write pending LTV; frozen reserves remain excluded;
- ConfigEngine `KEEP_CURRENT` is `type(uint256).max - 42`, not `uint256.max`;
- ConfigEngine expresses `liqBonus` as the increment above 100% and adds `100_00` before PoolConfigurator, so
  event payloads must be normalized to actual reserve configuration; and
- `HF < 1` is necessary but not sufficient for executable liquidation because reserve active/pause/grace and
  other eligibility conditions remain.

## Independent verification

`verify_artifact.py` does not import the collector. It rejects duplicate YAML/JSON keys, pins both artifact hashes,
re-reads the raw fourteen-file checkout, recomputes every file hash/byte count/marker, rebuilds the source inventory
hash, independently extracts and checks the configurator transition, recomputes all three toy routes and every
gate, checks all access locks and rejects embedded raw source/response bodies. It passed with raw-source replay,
fourteen files, 197,890 bytes and twelve gates.

## Corrigendum to the frozen reconnaissance disclosure

The frozen manifest calls the pre-freeze GitHub API calibration total “197858 bytes.” That number was computed as
Python `len(decoded_text)`, so it is 197,858 Unicode characters, not bytes. The UTF-8 checkout contains 197,890
bytes; the 32-byte difference comes from non-ASCII licence characters. The fixed source paths, contents, hashes,
markers, gates, access boundary and decision are unaffected. The manifest is left immutable and this result is the
canonical correction.

## Scientific interpretation and next gate

A0 certifies that Aave offers a cleaner *possible* direct-account shock than Compound's retired cap-increase route:
the event layer can be exact and nonlearned, while account adaptation is the learnable object. It is not yet a
paper result. The main risks now move to empirical identification:

1. there may be no strict unbundled LT decrease after frozen/eMode/config-bundle exclusions;
2. current V3.7 source may not match historical deployments;
3. a complete pre-event account denominator may not reconcile to authoritative state;
4. governance changes may be endogenous to already-moving risk; and
5. development reconnaissance may leave too few untouched confirmation events.

The next allowed work is A1 protocol design: freeze deployments, proxy versions, block range, event signatures,
execution clocks, exact request/resource caps and deterministic exclusions before opening any historical event.
Account, action and response rows remain locked through A1. Both V100s and the RTX 2060 remain idle; H20 is not
assumed.
