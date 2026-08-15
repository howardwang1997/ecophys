# Compound III source-metadata preflight v1 result

**Protocol commit:** `aa501def3`

**Decision:** `INFRASTRUCTURE_FAILURE_NO_SOURCE_AUDIT`

## Result

The nine focused tests passed in the clean detached worktree. The first orchestration command then found that the
new experiment directory was absent from the inherited sparse-checkout materialization, so the runner process did
not start. After materializing the committed directory without changing the worktree, the exact frozen script
entry point exited immediately:

```text
ModuleNotFoundError: No module named 'ecomd.research'
```

Direct execution set Python's import root to the experiment directory, while the Conda environment did not have
this worktree installed as a package. The failure occurred on the wrapper's first import, before argument parsing,
manifest loading, Git inspection or reading any Compound source file. No summary artifact was created. No chain
RPC, governance payload, account state, participant action, response, paid data, remote worker or GPU was used.

This is not a failure of any scientific or source-conformance gate. V1 remains immutable. The only admissible
repair is to invoke the already committed package module from the repository root:

```bash
conda run -n ecophys python -m ecomd.research.compound_v3_metadata ...
```

The source commit, six markets, permitted files, nine gates, decisions and every data/compute lock remain
unchanged. V2 must be committed and pushed before that command is executed.
