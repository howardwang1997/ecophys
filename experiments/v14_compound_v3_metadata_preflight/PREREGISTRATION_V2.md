# Compound III zero-row source-metadata preflight v2

**Frozen date:** 2026-08-16

**Parent protocol:** commit `aa501def3`

**Repair scope:** runner invocation only.

## Immutable carry-over

V2 carries forward without change:

- official Comet repository and commit `f766f51583c23acc33b2a7824654ef2029a96804`;
- the six exact Ethereum-mainnet market paths;
- permitted source, deployment and licence files;
- all nine conjunctive gates and both decisions;
- the reconnaissance disclosure and source-conformance interpretation; and
- every prohibition on chain, governance, account, action, response, paid-data, remote-worker and GPU access.

V1 passed its tests but its frozen direct-script entry point failed at the wrapper import before any source read.
No artifact exists. V2 replaces only that invocation with Python package-module execution from the repository
root. The collector implementation and machine manifest remain byte-identical to the pushed parent protocol.

## V2 execution rule

Run exactly once from a clean detached worktree containing this committed repair. Before launch, materializing the
committed experiment directory through sparse-checkout is allowed and must leave `git status --porcelain` empty.
The official source checkout must independently match the frozen remote/commit and be clean.

The command is specified in `RUNBOOK_V2.md`. A new import, path or environment failure produces another immutable
infrastructure result; no in-place repair or alternate environment is allowed.
