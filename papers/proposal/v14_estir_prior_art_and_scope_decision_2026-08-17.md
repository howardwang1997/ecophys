# ESTIR prior-art kill audit and scope decision

**Date:** 2026-08-17

**Decision:** `KILL_STANDALONE_EVM_IR_AND_SYNTHETIC_RESPONSE_CLAIMS_KEEP_EVIDENCE_ADAPTER_ONLY`

## 1. Outcome

ESTIR v1 remains a useful internal software contract, but it is not a research contribution and must not grow into
an independently implemented EVM semantics. The next version will not add rollback, call frames, gas, dynamic
storage or event semantics as home-grown opcodes. Those obligations already belong to mature executable
specifications, clients and analysis toolchains.

The retained research question is narrower and empirical:

> After exact execution evidence has been compiled into account-specific doses and an explicit uncertainty mask,
> does that representation improve calibrated prediction on held-out policy programs and deployments over raw
> transaction, terminal-delta and strong history-only baselines?

A real, prospectively sealed answer can support the larger NCS story. ESTIR or a generated trace benchmark cannot.

## 2. Prior art that kills the broad compiler claim

| Proposed object | Existing primary evidence | Scope consequence |
|---|---|---|
| Complete executable EVM semantics | [KEVM](https://fsl.cs.illinois.edu/publications/hildenbrandt-saxena-zhu-rodrigues-daian-guth-moore-zhang-park-rosu-2018-csf.html) provides an executable formal EVM bytecode semantics and evaluates it against the official Ethereum tests. | Do not claim a new executable EVM semantics. |
| Maintained reference execution and fixtures | The Ethereum Foundation's [Execution Layer Specifications](https://github.com/ethereum/execution-specs) are an executable Python reference implementation with generated client-validation fixtures and a reference EVM CLI. | Pin a fork/version and test against the reference; do not substitute a toy interpreter for consensus semantics. |
| EVM-to-high-level IR | [EthIR](https://arxiv.org/abs/1805.07208) translates EVM CFGs into guarded rule-based representations for high-level analysis. | “EVM bytecode to analyzable rules” is not novel. |
| Dependency-explicit decompilation | [Gigahorse](https://yanniss.github.io/gigahorse-icse19.pdf) decompiles EVM bytecode into three-address code with explicit control/data dependencies at blockchain scale. | Dependency-aware IR and decompilation are not sufficient novelty. |
| Call trees, logs and state differences | Geth's [built-in tracers](https://geth.ethereum.org/docs/developers/evm-tracing/built-in-tracers) expose nested call frames, optional logs and pre/post state differences. | Consume and cross-check execution evidence; do not re-create a tracer from governance events. |
| Fine-grained dynamic trace analysis | [OpenTracer](https://arxiv.org/abs/2407.10039) parses instruction traces into invocation trees and decoded storage accesses and has been applied to 350,800 transactions. | Trace decoding by itself is established systems work. |
| Known-mechanism plus learned remainder | [Universal Differential Equations](https://arxiv.org/abs/2001.04385) explicitly combines scientific models with learned components. | “Keep known mechanics exact, learn the rest” is good design but not a standalone novelty claim. |
| Learning across input operators | [DeepONet](https://doi.org/10.1038/s42256-021-00302-5) and the [Fourier Neural Operator](https://arxiv.org/abs/2010.08895) learn mappings across families of operators/equations. | Calling the policy program an operator does not create ML novelty. |
| Action-conditioned world dynamics | [PlaNet](https://proceedings.mlr.press/v97/hafner19a.html) models stochastic and deterministic latent transitions for planning under actions. | Conditioning a world model on an intervention is established; the burden is structural OOD evidence and method gain. |

These works do not solve the proposed economic prediction problem. They do establish that the syntax of the
architecture—executable semantics, an IR, traces, exact known dynamics plus a learned remainder, and
action/operator conditioning—cannot carry the paper's novelty.

## 3. The exact value-of-trace identities

Let `X` contain the pre-event observations and terminal compiled operator, `Z` contain additional ordered trace
evidence, and `Y` be the future participant or market response. Under Bayes-optimal log loss,

\[
R^*(X)-R^*(X,Z)=H(Y\mid X)-H(Y\mid X,Z)=I(Y;Z\mid X).
\]

For squared error with vector-valued `Y`, the orthogonal-projection identity is

\[
R^*(X)-R^*(X,Z)
=\mathbb E\left[\left\|\mathbb E[Y\mid X,Z]-\mathbb E[Y\mid X]\right\|_2^2\right].
\]

These are standard information/projection identities, not new theorems. They expose the decisive issue: retaining a
trace matters predictively only when the real response distribution contains information in that trace beyond the
prestate and terminal operator.

This also kills a tempting but circular experiment. A synthetic response generator can make
`I(Y;Z | X)` positive or zero by construction, so a trace-aware model's success on labels that we designed would
mostly verify the generator. Generated fixtures remain appropriate for schema, determinism, rollback and
conformance tests, but not for authorizing a scientific response-model claim.

## 4. Retained role of ESTIR

ESTIR becomes a normalized output vocabulary behind an **execution-evidence adapter**:

- it stores an ordered, path-bearing representation and terminal sparse effects;
- it records code/fork/state provenance and explicit unknown or unsupported semantics;
- its inputs must come from reference/client execution evidence and authoritative T-1/T state;
- its adapter is tested against version-pinned official fixtures and at least two independent evidence paths where
  feasible; and
- it never claims to be the EVM, a decompiler, or the source of intervention effects.

The adapter contract is specified in
`papers/proposal/v14_execution_evidence_adapter_contract_2026-08-17.md`. Implementation is deferred until B0
passes and a small frozen B1 sample fixes the actual provider/client schemas. Implementing it now would optimize an
interface against invented data.

## 5. Next admissible work

1. Obtain an explicit archive resource that satisfies the already frozen nine-deployment B0 capability contract.
2. Run a separate target-free qualification; only a pass permits a versioned B0 protocol.
3. If B0 passes support, freeze B1 over a small outcome-blind sample and implement only the evidence adapters needed
   by those pinned sources.
4. Require reference-fixture, cross-evidence, receipt/log and pre/post-state conformance before B2.
5. After B2 establishes an enumerable denominator, freeze outcomes, representations, baselines and metrics in B3.
6. Measure the value of compiled evidence only on validation and untouched real programs. Report both the
   terminal-to-trace increment and the raw-program-to-compiled increment under proper scores.

No synthetic response training, account/outcome query or GPU job is authorized by this audit. The V100 and RTX
queues remain empty. Current productive work is the data-access decision; more interpreter engineering is not a
substitute.

## 6. Venue consequence

- **NCS:** still possible only if the full method couples verified intervention evidence, accounting-consistent
  multiscale prediction and a genuinely useful long-horizon calibration contribution, with real held-out programs
  and at least one non-Aave/non-EcoMD backend.
- **NMI:** currently unsupported. It would additionally require a non-equivalent learning method, broad OOD
  benchmarks and material gains over raw-token, sequence/world-model and operator-learning baselines.
- **Software/data fallback:** a high-quality adapter or benchmark could be publishable elsewhere, but it must not be
  presented as the flagship scientific contribution without the real response result.

## 7. Stop rules

- Stop ESTIR feature expansion if the feature already exists in EELS, KEVM, a reference client or an established
  trace/decompilation tool and no response-specific requirement distinguishes it.
- Stop a generated-response experiment if its headline result follows from how its labels were constructed.
- Stop the compiler claim if independent pre/post state, bytecode/fork identity or rollback/log conformance cannot
  be established.
- Stop the NCS/NMI route if the compiled representation adds no sealed real OOD value beyond strong raw and
  terminal baselines.
