# Experiment 149 preregistration — fee-controller protocol oracle

**Registered:** 2026-08-13, before implementation, freeze or formal execution  
**Purpose:** G0 implementation conformance only  
**Scientific evidence:** none; a pass cannot establish novelty, identification, demand behavior or market physics

## Question

Does the independent EcoPhys integer implementation of EIP-1559, EIP-4844 and EIP-7918 reproduce selected
official Ethereum execution-spec fixtures bit-for-bit across Osaka, Osaka-to-BPO1 and BPO1-to-BPO2?

## Frozen input

The sole formal input is the official `ethereum/execution-specs` release `tests@v20.0.1` `fixtures.tar.gz`, source
commit `87aba1a38a476b31f819a2390eb481527e6dc683`, exactly 423,237,039 bytes and SHA256
`3586193db06d4d5745d5e90b3c3008c2255a4e19ccd8f11a3ce887aec8c0b17c`.

Only the five members and member hashes in `config.yaml` are in scope. They contain 97 test cases and 107 valid
blocks: 86 steady-Osaka cases, one direct Osaka-to-BPO1 boundary case, five two-block Osaka-to-BPO1 cases and five
two-block BPO1-to-BPO2 cases. The archive and fixtures are protocol-generated test data, not observed chain data.

## Independent calculations

For every valid block, calculate from its parent and the schedule active for the current timestamp:

1. EIP-1559 execution base fee, using exact integer division and the minimum upward increment;
2. EIP-7918 excess blob gas, including the strict reserve inequality, lower-bound return, current schedule and
   parent execution base fee;
3. EIP-4844 blob base fee from the current header excess using exact `fake_exponential`.

Compare (1) and (2) with every block header. Compare (3) wherever the fixture's dedicated `0x4a600055` contract
records `BLOBBASEFEE` in storage slot zero. Fixture metadata, schedule values, file hashes and aggregate counts are
also checked.

## Frozen gates

`PROTOCOL_ORACLE_CONFORMANCE_PASS` requires all of the following in the one formal attempt:

- archive SHA256 and size match;
- every selected member SHA256 matches;
- exactly 5 members, 97 cases, 107 blocks, 132 transactions and 122 blob transactions are parsed;
- every block has the expected execution base fee and excess blob gas;
- every observable blob-base-fee storage value matches;
- Osaka, Osaka-to-BPO1 and BPO1-to-BPO2 are all exercised;
- zero parse, schedule, version or comparison failure.

Any mismatch yields `IMPLEMENTATION_OR_SPEC_FAILURE`. There is no partial pass, tolerance, seed, fit, model,
hyperparameter or rerun. A failure may be diagnosed only in a separately registered repair experiment.

## Execution and leakage controls

- Formal command: `conda run -n ecophys python -m ecomd.research.fee_controller_oracle --config
  experiments/149_fee_controller_protocol_oracle/config.yaml --fixture-archive <verified archive> --output
  experiments/149_fee_controller_protocol_oracle/artifacts/raw/conformance.json`.
- One local Mac CPU process, one numerical thread, less than 1 CPU core-hour and 2 GB RAM.
- Network disabled during execution; no R2, remote host, V100, RTX2060 or GPU.
- No chain fee, usage, transaction, rollup, reliability, paid or sealed outcome is read.
- Output is complete-only and records config/input/code/dependency hashes, runtime, counts and every mismatch.

## Decision after the run

A pass unlocks only a separate preregistration for generated identification stress tests. It does not unlock real
data. Real outcomes remain blocked by the unset BPO3 contract and missing independent replication. A fail closes
G0 for this implementation until a prospectively registered repair.

