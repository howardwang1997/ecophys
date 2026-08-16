# From scalar event hunting to executable vector policy shocks

**Date:** 2026-08-16

**Decision:** make an executable policy-shock compiler the v14 mainline. A cross-deployment scalar scan may remain
a cheap breadth diagnostic, but it is no longer the paper's scientific center.

## 1. Why the scalar route is no longer the right main story

The zero-account gates have now rejected two superficially attractive scalar interventions for different reasons:

- Compound supply-cap increases survived mechanics checks, but none was exactly binding at T−1, so the proposed
  treated population was not identified.
- Aave Ethereum contains 18 emitted LT decreases, but only four preserve emitted LTV/bonus and all four are bundled
  with many same-transaction Configurator changes. The strict scalar candidate count is zero.

Relaxing either gate would be post-hoc. More importantly, both failures reveal the same structural fact: real
institutional interventions are executable programs, not isolated scalar labels. They alter several constraints,
assets and state routes at once. A world model that needs a hand-picked one-dimensional shock is solving the wrong
problem.

## 2. Proposed paper-level object

The new object is an **Executable Policy Shock Compiler (EPSC)**:

> Given versioned protocol code, an executed governance transaction and authoritative pre/post state, compile the
> intervention into an exact sparse state-transition operator; compose it with a learned multiscale adaptation
> model; and predict out-of-event agent and market responses under held-out executable policy programs.

The immediate transition is not learned when code determines it. Learning begins with heterogeneous adaptation,
uncertain execution context and slow market feedback. This preserves the useful lesson from EcoMD while removing
EcoMD from the role of sole scientific evidence.

For pre-event state (S^-), executable program (p), version (v) and exact interpreter
(mathcal{T}_{v,p}),

\[
S^{0+}=\mathcal{T}_{v,p}(S^-), \qquad
S^{t+1}=\mathcal{A}_\phi(S^t,\mathcal{T}_{v,p},Z^t)+\varepsilon^t.
\]

`T` is source/state/receipt matched. `A` is learned. A vector intervention is one treatment program, not a set of
independently identified scalar effects.

## 3. Claim ladder

### C0 — compiler conformance

For every admitted event, replayed code and historical state reproduce all changed coordinates, emitted events,
accounting identities and relevant boundary crossings exactly. This is a software/scientific validity claim, not
an ML claim.

### C1 — OOD intervention prediction

Conditioning on the compiled operator improves calibrated prediction on held-out governance programs, times and
deployments over strong time-series, survival/point-process and raw-parameter baselines. Selection and splits are
frozen before participant outcomes are opened.

### C2 — multiscale consistency

Account-level predicted marks aggregate to reserve/protocol totals within explicit accounting residual tolerances,
while slow context captures shared market regimes. Exact event mechanics plus learned adaptation should outperform
fully learned or fully hand-coded alternatives at both micro and aggregate horizons.

### C3 — scientific insight

Only after C0--C2: quantify which features of executable shocks—boundary mass, vector dimension, constraint
activation, concentration and cross-asset coupling—govern adaptation speed and failure modes. This is descriptive
and predictive unless a separate causal design is valid.

## 4. Multiscale architecture

1. **Policy-program layer:** source/version/receipt/call-path compiler produces a sparse operator and uncertainty
   mask. No neural approximation of known state writes.
2. **Instantaneous account layer:** exact account-specific dose and boundary transition, with explicit zero routes
   for unaffected/eMode/disabled-collateral accounts.
3. **Fast adaptation layer:** marked temporal point process or discrete event transformer for repay, supply,
   withdraw, borrow, configuration change, liquidation and exit hazards.
4. **Meso aggregation layer:** reserve and asset graph with conservation/accounting projections. This layer couples
   accounts affected by different coordinates of the same program.
5. **Slow context layer:** market liquidity, volatility, gas, governance anticipation and deployment regime.
6. **Long-horizon calibration layer:** invariant-measure or distributional calibration method from Plan v4,
   validated on EcoMD and at least one non-EcoMD dynamical system.

The mechanism layer remains nonlearned because it is known. The compiler's uncertainty, incomplete source mapping,
agent adaptation and regime dynamics are learned or statistically estimated.

## 5. Evidence topology and immediate gates

### B0 — bundle breadth, zero accounts

- The development-only Ethereum replay is complete: 77 transaction bundles, 27 with a known-predecessor net
  change, five with a net LT decrease, zero pure emitted-LT vectors, one execution-path round trip and 54
  unknown-predecessor asset occurrences. All seven integrity gates pass. These explored counts set no support
  threshold and authorize protocol design only.
- Use the now-frozen official-address/source inventory across the nine preselected new deployments.
- Count all configuration-program transactions with the same inclusive rules; do not search only for LT events.
- Apply the frozen program/topic/width/time support requirements for train/validation/test.

No threshold will be chosen from the already explored Ethereum counts. A new B0 protocol must state the minimum
support before opening other deployments.

B0 v1 now fixes that contract before new-chain access. Ethereum remains development-only. Train is
Arbitrum/Avalanche/Optimism/Polygon, validation is Base/Gnosis, and untouched test is BNB/Linea/Scroll. Every named
new deployment must have at least ten Configurator-program transactions; the conjunctive split minima are
120/40/60 programs and the total minimum is 220, with additional topic, multi-log, upgrade, time-span and quarter
requirements. All Configurator-log transactions are included without parameter, direction or scalar-purity
filtering. Full protocol: `experiments/v14_aave_v3_cross_deployment_program_directory/PREREGISTRATION.md`.

The sealed v1 run at pushed commit `707956291...` terminated before any successful log response: 66 Arbitrum
chain/header calls succeeded, while 14 logical Provider `eth_getLogs` ranges returned HTTP 403 on every allowed
attempt down to block 0. This is an infrastructure failure, not a breadth decision. V1 is immutable and cannot be
retried; a successor must first freeze a target-row-free transport canary while preserving the scientific contract.

### B1 — exact vector compiler, zero accounts

For every selected program, decode receipts and calldata, map the complete call cone to historical verified source,
replay T−1/T reserve state and produce an exact changed-coordinate vector. Temporary in-transaction round trips are
represented in the execution trace but have zero terminal coordinate change. Unknown topic/source/state or an
unexplained write fails the event.

### B2 — enumerable denominator and accounting replay

Enumerate all potentially affected on-chain account addresses, reconstruct T−1 balances/configuration/indexes and
reconcile aggregates with zero unexplained nonzero positions. Compute the exact program-specific account operator.
This is still outcome-blind.

### B3 — frozen prediction task and G1

Freeze event/deployment/time splits, horizons, marks, censoring, baselines and calibration metrics. Only then open
participant actions and realized responses. G1 requires compiler conformance, denominator completeness, support,
an untouched test program/deployment and a credible prediction task. Component-level causal claims require a
separate design and are not assumed.

## 6. Cross-deployment scalar scan: role and limit

Applying the unchanged scalar isolation rule to additional Aave deployments is cheap and legitimate if the chain,
deployments and support threshold are precommitted. It can answer whether clean scalar shocks exist elsewhere and
may provide an interpretable ablation.

It should not become the mainline because:

- finding one event still leaves weak sample support and governance endogeneity;
- failure is likely when risk updates are systematically bundled; and
- a single event study does not supply the computational novelty expected by NCS or NMI.

Run it only as a bounded B0 sub-audit, never as a hunt that changes chains or thresholds after each failure.

## 7. Data requirements

| Gate | Free/open inputs first | Possible later requirement | Participant outcomes? |
|---|---|---|---|
| B0 | official address books, source commits, provider/configurator logs, headers | more archive endpoints for breadth | No |
| B1 | transactions, receipts, calldata, raw/call traces, verified historical source, T−1/T protocol state | independent archive state or verified proofs | No |
| B2 | reserve/account-owner events, user/reserve/index/config/oracle state, aggregate totals | paid archive node or partner export if free reconciliation fails | No |
| B3 design | pre-event gas/market/governance covariates and support diagnostics | licensed market data behind a new gate | No |
| Post-G1 | successful calls/actions, liquidations, prices/liquidity and held-out responses | scalable archive/vendor/partner data | Yes |

Every asset needs source, retrieval time, licence/terms, immutable block range, raw/content hash and preprocessing
hash. Crash periods remain evaluation-only. No future plan may assume H20.

## 8. Compute requirements

- B0 and current structural replay: Mac CPU/network, seconds to hours, zero GPU.
- Frozen B0 v1: one CPU/network worker, about 1.5--4 hours expected, with hard caps of 50,000 HTTP attempts,
  512 MiB responses, 250,000 logs and 50,000 programs. It can use a V100 host's CPU only; no GPU process starts.
- B1: CPU/network/trace parsing; shard by deployment/program. The V100 hosts and RTX 2060 can supply CPU workers,
  but GPU is unnecessary.
- B2: archive I/O, RAM and CPU dominate. Scale by deployment, block and address batch; checkpoint all manifests.
- Post-G1 baselines: the two 32-GB V100 workers are enough for small point-process/transformer feasibility and
  three-seed ablations.
- Full cross-deployment model: add heterogeneous non-H20 workers, keeping GPU types in separate benchmarked pools.
  Exact event compilation and reconciliation remain CPU jobs.

No GPU job is currently authorized or queued.

The frozen Ethereum replay and standalone verification are archived in
`experiments/v14_aave_v3_bundle_structure_feasibility/RESULTS.md`; summary SHA-256 is
`922312a9c75a64cfe66a1ef828140df938929e4bc6fbac9200a3a1f6fa9d9db9`.

## 9. NCS versus NMI

### Nature Computational Science primary route

Lead with the computational method: executable intervention compilation, accounting-constrained multiscale
simulation and long-horizon calibration. Require broad scientific validation, interpretable failure analysis and
at least one backend beyond Aave/EcoMD. Prediction gains matter, but method validity and scientific utility are the
center.

### Nature Machine Intelligence stretch route

Require a stronger learning contribution: operator-conditioned architecture, systematic OOD generalization across
programs/deployments, scaling laws, uncertainty calibration and substantial gains over competitive sequence/world-
model baselines. One protocol family is unlikely to suffice. Data and GPU needs are materially higher.

The current evidence supports NCS-oriented method development. It does not yet support an NMI claim.

## 10. Kill conditions

Stop or reframe if any of the following holds:

- B0 lacks enough programs for untouched deployment/time splits;
- historical code/state cannot compile transactions without unexplained writes;
- account aggregates cannot be reconciled;
- governance anticipation or common shocks make the prediction task trivial or nontransportable;
- the exact operator adds no held-out predictive/calibration value over raw program features;
- results hold only in EcoMD or one Aave deployment; or
- full performance depends on unavailable/licence-incompatible data.

The fallback is a transparent protocol-governance benchmark or software/data paper, not a weakened universal or
causal claim.
