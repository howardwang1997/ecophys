# Experiment 149 result — protocol oracle conformance

**Formal decision:** `PROTOCOL_ORACLE_CONFORMANCE_PASS`  
**Formal run commit:** `a599841517546c2908aa70d7daf840fa035bb8a7`  
**Raw artifact:** `artifacts/raw/conformance.json`  
**Raw artifact SHA256:** `2a124acc5881204a69b34b0024c4d51387ca4060bf2525c44f1f2ff17ff3873a`

## Frozen gates

| Gate | Result |
|---|---:|
| archive size/SHA256 | pass; 423,237,039 bytes; `3586193db06d...` |
| selected members | 5/5; all member hashes pass |
| fixture cases | 97/97 |
| valid blocks | 107/107 |
| transactions | 132/132 |
| blob transactions | 122/122 |
| execution-base-fee comparisons | 107/107 exact |
| excess-blob-gas comparisons | 107/107 exact |
| observable BLOBBASEFEE storage comparisons | 86/86 exact |
| networks | Osaka; Osaka-to-BPO1; BPO1-to-BPO2 |
| active schedules | Osaka; BPO1; BPO2 |
| total mismatches | 0 |

The run used the preregistered official execution-specs release and selected fixture members. It reproduced the
strict EIP-7918 reserve boundary, EIP-4844 integer exponential, EIP-1559 execution-fee update, current-schedule fork
semantics and inherited excess state without tolerance or floating-point approximation.

## Execution audit

- runtime: 15.0653 seconds;
- peak RSS: 0.25061 GB;
- one controller process and one numerical thread;
- Python 3.11.15 and PyYAML 6.0.3;
- zero chain-outcome files, network calls, remote hosts and GPU-hours;
- both V100 workers and the RTX2060 remained idle and uncontacted.

## Binding interpretation

This result passes V6 G0 for the selected protocol versions. It establishes only that the independent local
controller implementation conforms to the selected official fixtures. It is not evidence for a new theorem,
behavioral demand, substitution, market physics, causal identification, NMI readiness or NCS readiness.

Real outcomes remain locked. NMI remains `NO_SURVIVOR`; NCS remains a conditional prospective candidate blocked
on finalized BPO3 metadata, a credible identification design and independent replication. The only newly
permissible next experiment is a separately preregistered generated identification stress test with no observed
chain outcome.
