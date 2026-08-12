# V6 scale and replication audit — fee-controller nontriviality

**Audited:** 2026-08-13

**Outcome access:** none; only public controller parameters, deployment metadata and transaction receipts

**Decision:** the BPO capacity sequence is an almost exact scale oracle, Base supplies useful same-chain
non-proportional attacks but no independent replication, and V6-NCS-1 moves from `FORMALIZING` to `ATTACKING`

## 1. Why this attack is binding

Experiment 149 established that the controller implementation is exact. That is necessary but creates a harder
scientific question: can a proposed behavioral model predict anything that is not already implied by the
controller and a change of units? A successful forecast across BPO1 or BPO2 is not evidence of adaptive demand if
the old and new mechanisms are the same normalized map.

This audit was completed before opening any execution/blob fee, gas-use, occupancy, transaction-composition or
rollup outcome path. The numerical calculations below use protocol constants only. The Base registry records
operation parameters, timestamps and L1 execution receipts; these are intervention metadata, not the L2 response
outcomes that V6 would eventually predict.

## 2. BPO is almost a pure scale family

Write the blob schedule as target `T`, maximum `M`, update fraction `F` and gas per blob `G=131072`. EIP-7892 and
the BPO registry give:

| Regime | `T` | `M` | `F` | `M/T` | `F/T` |
|---|---:|---:|---:|---:|---:|
| Prague/Osaka | 6 | 9 | 5,007,716 | 1.5 | 834,619.333333 |
| BPO1 | 10 | 15 | 8,346,193 | 1.5 | 834,619.300000 |
| BPO2 | 14 | 21 | 11,684,671 | 1.5 | 834,619.357143 |

Relative to Prague, the discrepancies in `F/T` are only `-3.99384e-8` for BPO1 and `+2.85274e-8` for BPO2.
Away from integer floors, reflection and the EIP-7918 reserve branch, the full-block log-fee increments are
respectively `0.0785220248113`, `0.0785220279474` and `0.0785220225713`. These imply one-block increases of
`8.168717886%`, `8.168718225%` and `8.168717643%`; the corresponding empty-block decreases are
`14.533358974%`, `14.533359510%` and `14.533358592%`.

The exact integer oracle is nearly as restrictive. At standardized excess states
`e=G*T*s`, on the quarter grid `s=0,0.25,...,64`, all three `fake_exponential` fee values are bit-identical. On
integer standardized states `s=0,...,2000`, the first disagreement occurs only at `s=74`, where the three values
are `[111442, 111442, 111441]`; the maximum relative spread over the full grid is `2.15e-5`.

Therefore the declared BPO schedules are controller-scale equivalent for every scientifically consequential
comparison tested here. Rational blob-count support, inherited unscaled excess, integer flooring, reflection and
EIP-7918 can still produce exact differences, but a method must isolate and outperform those mechanical effects.
It cannot call normalized-path agreement transfer learning.

The deterministic calculation is executable with:

```bash
conda run -n ecophys python -m ecomd.research.fee_controller_scale_audit
```

## 3. Execution-fee controller coordinates

For an OP Stack EIP-1559 controller with gas limit `L`, elasticity `E`, denominator `D` and target `T=L/E`, the
continuous relative update away from integer/floor branches is

\[
\frac{b_{t+1}-b_t}{b_t}=\frac{u_t/T-1}{D}.
\]

If `r_t=u_t/L`, the same update is `(E r_t-1)/D`. Thus the controller separates into:

- target scale `T`, which sets the absolute resource unit;
- elasticity `E`, which sets saturation in target units;
- denominator `D`, which sets feedback gain.

This is an algebraic coordinate decomposition of the published controller, not a new theorem. It nevertheless
specifies a hard experimental topology. Proportional changes in `L` and `E` that preserve `T`, or schedules that
preserve both normalized gain and saturation, are weak transfer tests. Denominator-only changes, target changes
and joint changes that alter `(T,E,D)` are non-proportional tests.

## 4. Frozen Base intervention topology

The official Base deployment repository was frozen at commit
`12116aa7e58d3c6fc86de45075759e05a1c113be` (2026-08-07). It records the actual governance calls for the same
Base `SystemConfig` address through seven receipt-backed operations and one operation whose README says executed
but whose record file is absent at this commit.

| ID | Executed UTC | Change `(L,E,D)` | Target change | Evidence and role |
|---|---|---|---|---|
| A | 2025-05-27 20:53:02 | `(140m,2,250)` to `(140m,2,50)` | `70m` to `70m` | denominator-only gain attack; receipt-backed |
| B | 2025-06-18 21:49:02 | `(140m,2,50)` to `(150m,3,50)` | `70m` to `50m` | gain fixed; target and saturation change; receipt-backed |
| C | 2025-10-29 16:36:14.673 | `(150m,3,50)` to `(200m,4,50)` | `50m` to `50m` | target-preserving scale/saturation attack; receipt-backed |
| D | unresolved | `(200m,4,50)` to `(250m,4,50)` | `50m` to `62.5m` | target-only capacity change; README executed, no frozen record |
| E | 2025-11-12 16:43:25.898 | `(250m,4,50)` to `(300m,5,50)` | `62.5m` to `60m` | target and saturation change; receipt-backed |
| F | 2025-12-18 19:08:49 | `(300m,5,50)` to `(375m,6,50)` | `60m` to `62.5m` | also changes DA scalar `312` to `325`; receipt-backed |
| G | 2026-02-04 13:27:25.877 | `(375m,6,50)` to `(375m,6,125)` | `62.5m` to `62.5m` | denominator-only, but near a minimum-base-fee change; receipt-backed |
| H | 2026-03-25 20:46:37.995 | `(375m,6,125)` to `(400m,5,100)` | `62.5m` to `80m` | also changes DA scalar `139` to `148`; preserves maximum +4% step; receipt-backed |

Operation B's script calldata sets `150,000,000`, despite a README summary typo that says 15 million. Operation D
must not be assigned an exact time or block until an execution record or independent official receipt is frozen.
The February denominator change is not clean behavioral evidence because Base's configuration changelog records a
nearby minimum-base-fee change. Operations F and H are explicitly bundled with DA-scalar changes. These facts are
confounders to preserve, not inconveniences to average away.

Base is a useful blind historical development topology because it contains gain-only, target-preserving and
non-proportional changes. It is not an external replication: all episodes are one chain, one SystemConfig sequence
and one administrator history. The active task directory in the frozen repository contains only `.gitkeep`, so
there is no unexecuted parameter task that can currently be sealed as a future Base intervention.

## 5. Independent-system search

OP Mainnet, World Chain, Celo and opBNB expose compatible or related configurable fee controllers. The official
sources inspected establish configurations or controller semantics, but no future, finalized, unexecuted
parameter intervention with frozen activation metadata was found. They remain a catalog of replication candidates,
not a replication contract. A different chain with the same OP Stack code is still only independent if the
administration, intervention decision and untouched evaluation are independently frozen.

## 6. Nontriviality and admission gates

Any generated or real V6 estimator must now satisfy all of the following:

1. compare against an exact controller plus scale-equivariant oracle;
2. report performance separately for scale-equivalent and non-proportional parameter changes;
3. show that any claimed behavioral gain is larger than integer rounding, inherited-state and reserve-branch
   mechanics;
4. use Base only as historical same-chain development/transport stress;
5. reserve one finalized future intervention and one independently administered replication before outcomes;
6. fail closed when latent workload drift or bundled software/fee changes make the behavioral response
   unidentified.

The immediate candidate state is `ATTACKING`, not ready for outcomes. NMI remains retired. For NCS, generated P0
may test whether a transparent response estimator can beat the scale oracle under non-proportional changes and
whether it fails safely under latent drift. A P0 pass would still not fill I0, BPO3 or replication.

## 7. Primary sources

- [EIP-4844](https://eips.ethereum.org/EIPS/eip-4844)
- [EIP-7892](https://eips.ethereum.org/EIPS/eip-7892)
- [OP Stack Holocene SystemConfig](https://specs.optimism.io/protocol/holocene/system-config.html)
- [OP Stack gas target and limit guide](https://docs.optimism.io/chain-operators/guides/management/gas-target-limit)
- [Base contract deployments at the frozen commit](https://github.com/base/contract-deployments/tree/12116aa7e58d3c6fc86de45075759e05a1c113be)
- [Base configuration changelog](https://docs.base.org/base-chain/network-information/configuration-changelog)
- [OP Mainnet Holocene proposal](https://gov.optimism.io/t/upgrade-proposal-11-holocene-network-upgrade/9313)
- [Celo L2 deployment specifications](https://specs.celo.org/deployments.html)
