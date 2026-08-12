# V6 pre-outcome audit — algorithmic fee-market dynamics

**Audit frozen:** 2026-08-13  
**Outcome access:** none; no chain fee, utilization, transaction, rollup or reliability value was opened  
**Decision:** G0 `PROTOCOL_ORACLE_CONFORMANCE_PASS`; `NMI_NO_SURVIVOR`; NCS `PROSPECTIVE_CANDIDATE`, blocked
before outcomes by intervention and replication

## 1. What was audited

The audit asks whether the V6 object is executable, distinguishable from prior work, reconstructable from free
licensed data and causally identifiable before any empirical response is viewed. It uses official specifications,
official test fixtures, primary papers and dataset catalog/schema/licence pages only. Public articles that already
summarize BPO outcomes were recorded as contamination evidence; their outcome values and figures were not used.

## 2. Exact controller contract

For execution gas, EIP-1559 updates the next base fee from the parent base fee, gas used and gas target with integer
division, denominator 8 and a minimum upward increment of one wei. For blob gas, EIP-4844 carries an integer excess
state and evaluates `fake_exponential(1, excess, base_fee_update_fraction)`. The active block's blob schedule is
used at a fork boundary; the inherited parent excess is not rescaled.

EIP-7918 adds a protocol-internal cross-resource branch. With `G=2**17`, `C=2**13`, parent excess `e`, parent blob
use `u`, parent execution base fee `q`, current target `T`, maximum `M` and update fraction `F`,

\[
b_F(e)=\operatorname{fake\_exponential}(1,e,F),
\]

and, after the lower-bound check `e+u<G T`,

\[
e^+=
\begin{cases}
e+u(M-T)//M,& Cq>G b_F(e),\\
e+u-GT,& Cq\le G b_F(e).
\end{cases}
\]

The strict inequality, current schedule and parent execution fee are binding semantics. The reserve branch does not
replace the opcode fee by a floating-point maximum; it alters the integer excess-state recurrence.

| Regime | Activation | Target | Maximum | Update fraction | Status |
|---|---:|---:|---:|---:|---|
| Prague/Pectra | 2025-05-07 | 6 | 9 | 5,007,716 | historical |
| Osaka/Fusaka | 2025-12-03 | 6 | 9 | 5,007,716 | broad mechanism fork |
| BPO1 | 2025-12-09 14:21:11 UTC | 10 | 15 | 8,346,193 | completed |
| BPO2 | 2026-01-07 01:01:11 UTC | 14 | 21 | 11,684,671 | completed |
| BPO3 | unset | unset | unset | unset | draft, prospective only |

EIP-8134 and EIP-8135 state that BPO1/2 change only blob parameters, but BPO1 follows Fusaka by less than six days.
It is therefore a poor clean development intervention for behavioral attribution. BPO2 is cleaner mechanically,
but it is neither untouched nor an independent governance/system replication. EIP-8138 creates a genuine future
sealing opportunity, but its activation and parameter cells remain blank; its motivational derivation is not an
executable mainnet contract.

## 3. Nearest-result audit

| Neighbor | What it already supplies | Consequence for V6 |
|---|---|---|
| EIP-1559 dynamics | stability, convergence conditions and possible chaotic behavior of adaptive base fees | controller dynamics are not a new theory object |
| closed-loop system identification | identification parameterizations that explicitly account for known feedback | an exact controller plus a learned response is not an NMI method |
| optimal dynamic fees for blockchain resources | multi-resource demand cross-effects, optimal controllers and Ethereum calibration | broad cross-resource Jacobian/control framing is occupied |
| causal gas-demand elasticity | lagged-fee IV estimates designed to address congestion endogeneity on L1/L2 | causal elasticity itself is occupied and naive regression is invalid |
| EIP-7999 | unified multidimensional fee state, normalized resource limits and reserve coupling | normalized multidimensional fee generalization is protocol prior art |
| public BPO analyses | post-BPO network and blob outcomes have already been studied publicly | BPO1/2 cannot be claimed as untouched confirmation |

No equation-level method candidate survived outside this composition. `V6-NMI-1` is therefore
`RETIRED_PRIOR_ART`. This does not retire the NCS phenomenon route: an honestly sealed, no-behavioral-refit forecast
of a future controller change could still be scientifically useful, but it is not yet an admitted experiment.

## 4. Free-data contract

EthPandaOps Xatu publishes public Parquet under CC BY 4.0. Its catalog exposes finalized, deduplicated canonical
execution and consensus tables, blob-sidecar events and 1,000-block canonical execution partitions. This supports
a free, hashable reconstruction path for headers, resource use, canonicality and availability. It does not by
itself provide a causal instrument or a stable rollup attribution table.

The data gate is therefore `CONDITIONAL_PASS_FIELDS`:

- raw controller fields and canonicality have a free licensed route;
- rollup inclusion and attribution still need a frozen address/provenance contract;
- BPO3 is not yet a finalized intervention;
- no independent, independently administered replication has been registered;
- no outcome file may be downloaded until the intervention and identification contracts pass.

## 5. Identification audit

The controller parameter is externally specified, but demand, batching and release activity are not. Prices are
feedback states, not exogenous treatments. A credible NCS test must separate:

- the deterministic state carryover and integer fork transition;
- common workload from substitution between execution and blob resources;
- release/batching clocks and anticipation from controller response;
- Fusaka/PeerDAS and client changes from the later BPO parameter change;
- fixed latent demand-state dynamics from behavioral adaptation;
- same-chain temporal validation from genuinely independent replication.

BPO1/2 can only be development material. They cannot fill the untouched replication cell, and BPO1 is too close to
Fusaka to anchor a clean behavioral law. BPO3 may be sealed prospectively once an official activation, all three
parameters and client test vectors exist. Even then, a second independently administered resource controller or a
later untouched policy change is mandatory.

## 6. Gate decision and queue

| Gate | Decision | Reason |
|---|---|---|
| G0 exact mechanism | `PASS_EXP149` | 97 official cases/107 blocks and 86 observable blob fees match bit-for-bit; zero mismatch |
| N0 NMI | `FAIL_NO_SURVIVOR` | direct composition of closed-loop ID, IV, structural demand and multi-resource fee control |
| N0 NCS | `CONDITIONAL_SURVIVOR` | prospective no-refit response transfer not found as an independently replicated result |
| D0 fields | `CONDITIONAL_PASS_FIELDS` | free CC BY Xatu path exists; attribution and replication remain unresolved |
| I0 | `BLOCKED_FUTURE_INTERVENTION_REPLICATION` | BPO3 is unset and no independent replication is sealed |
| P0 generated feasibility | `LOCKED_UNTIL_G0` | identification simulation is premature before protocol conformance |

Experiment 149 passed and is immutable; raw artifact SHA256 is
`2a124acc5881204a69b34b0024c4d51387ca4060bf2525c44f1f2ff17ff3873a`. The next permissible work is a separately
preregistered generated identifiability attack using no observed chain outcomes. Real-data download, V100/RTX2060
contact and GPU work remain locked. If BPO3 is finalized, freeze its
metadata and forecast protocol before opening any post-activation values; if no independent replication is found,
route any eventual single-system result below NCS rather than weakening the claim.

## 7. Primary sources

- [EIP-1559](https://eips.ethereum.org/EIPS/eip-1559)
- [EIP-4844](https://eips.ethereum.org/EIPS/eip-4844)
- [EIP-7892](https://eips.ethereum.org/EIPS/eip-7892)
- [EIP-7918](https://eips.ethereum.org/EIPS/eip-7918)
- [EIP-8134](https://eips.ethereum.org/EIPS/eip-8134)
- [EIP-8135](https://eips.ethereum.org/EIPS/eip-8135)
- [EIP-8138](https://eips.ethereum.org/EIPS/eip-8138)
- [EIP-7999](https://eips.ethereum.org/EIPS/eip-7999)
- [Ethereum execution specifications and fixtures](https://github.com/ethereum/execution-specs)
- [Optimal Dynamic Fees for Blockchain Resources](https://arxiv.org/abs/2309.12735)
- [A Dual System-Level Parameterization for Identification from Closed-Loop Data](https://arxiv.org/abs/2304.02379)
- [Price Elasticity of Gas Demand on L1 and L2](https://arxiv.org/abs/2606.13555)
- [Xatu public data catalog](https://github.com/ethpandaops/xatu-data)
