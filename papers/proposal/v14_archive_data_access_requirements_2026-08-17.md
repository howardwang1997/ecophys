# V14 archive-data access requirements after the free-RPC gate

**Date:** 2026-08-17

**Decision:** stop unauthenticated endpoint guessing. Reopen cross-deployment B0 only through an explicit resource
decision and a separately frozen target-free qualification.

## 1. Why access is now a first-class dependency

B0 v1 failed before a successful target log. Transport canary v1 then showed that no existing host/endpoint plan
covered all nine deployments. Repair v2 fixed Polygon/Base range handling but the sole predeclared BNB provider was
rate-limited on both eligible egresses. These are infrastructure results, not estimates of Aave program support.

The project has therefore exhausted the current no-auth endpoint route. Trying providers one by one after seeing
their failures creates an unbounded, outcome-conditioned search and still supplies no reproducible retention or
licence contract. The next data step is procurement/partnership design, not another RPC probe.

## 2. Minimum B0 capability contract

A candidate resource must cover all nine frozen non-development deployments without changing their train,
validation and untouched-test roles. Before an Aave address is queried, its documentation and target-free
qualification must establish:

1. correct chain identity and canonical historical headers through the frozen cutoff;
2. historical `eth_getLogs` from deployment genesis for arbitrary addresses and all topics;
3. a documented range, pagination or continuation rule with deterministic error semantics;
4. rate and response limits that fit the unchanged 50,000-attempt and 512-MiB B0 caps;
5. retention guarantees long enough to reproduce the run, not merely a current “archive” label;
6. stable authentication and secret rotation without credentials in Git or artifacts;
7. permission to retain request/response hashes, normalized event rows and derived publication artifacts;
8. a support/escalation path for historical omissions, reorg inconsistencies and silent truncation; and
9. two-source exact header replication for every derived cutoff.

For deployment `d`, let `B_d` be its cutoff block, `s_d` the qualified inclusive range span and `A_d` the number
of Provider-derived Configurator surfaces. Before target Configurator logs open, a new protocol must show that the
projected log calls

\[
N_{\mathrm{logs}}
=\sum_d\left\lceil\frac{B_d+1}{s_{d,\mathrm{provider}}}\right\rceil
+\sum_d A_d\left\lceil\frac{B_d+1}{s_{d,\mathrm{configurator}}}\right\rceil
\]

plus cutoff/header retries fit the frozen HTTP cap. Polygon's observed span of 62 is transport-reachable but is not
yet a feasible full-history plan. A provider that technically returns one block at a time does not satisfy this
contract.

## 3. Later B1/B2 capability contract

B0 access alone does not qualify a resource for compiler or account work. A future B1/B2 resource also needs:

- complete transactions, calldata, receipts and ordered logs;
- call traces with explicit completeness/timeout semantics;
- historical verified source and deployed-bytecode identity by implementation interval;
- historical `eth_getCode`, storage and block-parameter `eth_call`, or independently verifiable state proofs;
- deterministic batch behavior at declared block hashes, not only block numbers;
- complete reserve/account-owner event history and enumerable address reconstruction;
- enough historical state throughput to close reserve/accounting totals without sampling accounts; and
- publication/reviewer access terms for the derived benchmark and audit trail.

These capabilities remain locked until B0 scientifically passes. Listing them now prevents buying a log-only plan
that cannot support the actual compiler study.

## 4. Acceptable acquisition routes

| Route | Evidence required before use | Main risk | Current status |
|---|---|---|---|
| Institutional archive service | written chain/method/retention/licence terms; target-free sample qualification | quota or publication restrictions | seek access |
| Research collaboration | named data custodian; immutable export manifest; provenance and redistribution agreement | opaque preprocessing or non-reproducible access | seek partner |
| Paid multi-chain provider | current written quote plus method/range/retention SLA and derived-data rights | cost and vendor dependence | quote later; no purchase authorized |
| Self-hosted archive nodes | per-chain hardware/sync/storage plan, canonical snapshots and ongoing operations owner | multi-terabyte storage and maintenance | outside current no-expansion tier |
| Public no-auth endpoint | documentary retention/rate contract and new target-free qualification | throttling, pruning, silent policy change | current route closed |

No route receives preference from a target event count. If multiple resources qualify, choose by the predeclared
order: scientific completeness, reproducibility/licence, retention, independent verification, then cost and wall
time.

## 5. Target-free qualification package

Before purchase, partnership transfer or target access, freeze a small qualification protocol containing:

- exact provider/product/region and credential class;
- all nine chain IDs and historical cutoff-header probes;
- zero-address log queries at genesis, deployment-era and recent fixed blocks;
- fixed small, medium and required-production range sizes;
- historical code/state probes only if B1/B2 capability is being purchased;
- response hash, byte, latency, pagination and error ledgers;
- at least two eligible egresses where the contract requires egress robustness;
- explicit pass/fail rules and no post-observation endpoint replacement; and
- a signed/licence evidence file stored separately from secrets.

A qualification PASS authorizes a versioned B0 design only. It does not authorize direct target execution.

## 6. Data and compute envelope

The access decision itself needs only documents, quotes and target-free samples: Mac CPU plus existing workers as
network egresses, minutes, no GPU and no market outcomes. A later qualified B0 retains the original 50,000 HTTP,
512-MiB, 250,000-log and 50,000-program caps unless a new scientific/resource protocol is frozen before target
access. B1/B2 storage and CPU are deliberately unbudgeted until B0 support exists.

The two V100 GPUs remain irrelevant to archive retrieval; their CPUs may later run independent shards. H20 is not
part of any plan. Data and compute can expand, but expansion must solve a declared capability gap rather than hide
an endpoint failure.

## 7. Decision needed from collaborators or vendors

The useful request is not “send us market data.” It is:

> Provide reproducible historical EVM logs for the nine named Aave V3 deployments through the frozen cutoff, with
> documented range/retention limits and rights to retain normalized derived rows; optionally provide the B1/B2
> transaction, trace and historical-state capabilities listed above.

The partner can be an RPC/archive provider, blockchain data infrastructure group, protocol analytics team,
university systems lab or institution already licensed for the data. It is not geographically restricted. No
participant identity or proprietary trading record is needed for B0.
