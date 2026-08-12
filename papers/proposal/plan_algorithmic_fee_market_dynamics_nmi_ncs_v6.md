# Plan v6 — Exact controllers and adaptive demand in algorithmic fee markets

**Frozen:** 2026-08-13

**Branch:** `algorithmic-fee-market-dynamics-v6`

**Parent:** `main@efe14ad44a0ce208d082672e2c2f7d55de119606`

**Initial state:** `SCOUT`; no chain outcome, fee series, transaction, paid dataset, remote host or GPU authorized

## 1. Why this iteration exists

V5 found a real annual market-rule feedback loop but failed before outcomes because the available independent
cutoff units could not jointly control false positives and detect the frozen 5% effect. More compute could not add
information. V6 therefore changes the scientific object while keeping the venue targets fixed: study a high-rate
algorithmic resource market whose controller is public and exactly executable, whose behavioral demand remains
unknown, and whose parameter changes can potentially support prospective out-of-regime prediction.

The lead system is Ethereum's execution-gas and blob-gas fee markets. This is not a cryptocurrency-price paper.
The object is a coupled computational resource-allocation system in which protocol-defined feedback controllers
update prices and strategic users, builders and rollups adapt resource demand. EcoMD is not the data generator,
discovery system or headline.

## 2. Scientific object

For block or slot index `t`, let

\[
p_t=(p_t^{\mathrm{exec}},p_t^{\mathrm{blob}}),\qquad
u_t=(u_t^{\mathrm{exec}},u_t^{\mathrm{blob}}),
\]

where `p` contains protocol base fees and `u` contains declared resource use. Let `theta_r` denote the controller
parameters active in fork or parameter regime `r`. The protocol supplies an exact, versioned update

\[
p_{t+1}=F_{\theta_r}(p_t,u_t),
\]

including integer arithmetic, caps/floors, target loads and any reflected excess-resource state. Strategic demand
is not known:

\[
u_t=D(p_t,x_t,z_t,r)+\varepsilon_t,
\]

where `x_t` is observed workload/context and `z_t` is unobserved demand, batching or strategy state. The exact
controller removes transition ambiguity conditional on its inputs; it does not identify `D` or make price
variation exogenous.

Around a declared operating region, a local approximation has closed-loop operator

\[
\delta p_{t+1}\approx
\left(\partial_pF_{\theta_r}+\partial_uF_{\theta_r}J_D\right)\delta p_t
+\partial_uF_{\theta_r}\eta_t,
\qquad
J_D=\partial_p\mathbb E[u_t\mid p_t,x_t,z_t,r].
\]

This equation is a specification target, not a novelty claim. Its eigenvalues, damping and cross-resource modes
are meaningful only if `J_D` is identified and stable enough to predict a new controller regime.

## 3. Frozen candidate claims

### V6-NCS-1 — transferable closed-loop response law

The primary candidate is a prospective prediction, not a descriptive correlation:

> A response operator estimated before a declared controller-capacity change, combined with the exact new
> controller and without refitting behavioral parameters, predicts the direction, damping and uncertainty of the
> joint execution/blob resource response after the change; the prediction transfers to an independent parameter
> change or independently administered compatible system.

The minimum publishable object is the joint response of resource use and protocol fees. A blob-only occupancy
plot, an already-known fee reduction, a post-hoc fitted impulse response or a single successful upgrade is not the
claim. The result must distinguish substitution between resources from common demand, batching and secular load.

### V6-NMI-1 — mechanism-constrained closed-loop identification

NMI is conditional on a method or theorem that identifies or honestly bounds the behavioral cross-response in a
known deterministic controller under latent nonstationary demand. It must have a distinct estimand, assumptions or
finite-sample/partial-identification guarantee beyond closed-loop system identification, instrumental variables,
state-space demand models and standard structural estimation. It must validate on at least two non-blockchain
controlled-resource systems. A differentiable implementation of `F_theta`, a controller-aware loss or a market
application is not enough.

## 4. Mandatory counterexplanations

Any apparent coupled mode must survive all of the following:

1. common workload shocks drive both resources without substitution;
2. rollup release schedules, batching clocks and bridge-specific policy changes mimic relaxation or oscillation;
3. protocol upgrades change execution rules, client behavior or supply dimensions beyond the focal controller;
4. anticipation and migration occur before the announced activation;
5. integer rounding, minimum increments, reflection at zero and saturation create mechanical state dependence;
6. missing/reorged slots, builder selection and censoring distort block-level use;
7. deterministic price feedback makes naive demand-on-price regression simultaneous and biased;
8. serial dependence makes the number of blocks much larger than the effective number of innovations;
9. a fixed latent-demand state reproduces the finite response without behavioral adaptation;
10. a model fit after the intervention merely interpolates the observed regime.

## 5. Admission gates

### G0 — exact mechanism

- Archive primary protocol specifications and fork-specific constants.
- Implement executable integer-arithmetic oracles for both resource controllers.
- Match official consensus/execution test vectors bit-for-bit across every included regime.
- Reject any analysis row whose client/fork/parameter version is unresolved.

### N0 — novelty and nearest-composition audit

- Audit primary work on dynamic transaction-fee mechanisms, EIP-1559 stability, empirical fee response,
  multi-resource pricing, congestion control, closed-loop system identification and structural demand.
- Write the proposed statement beside the nearest theorem/empirical result, assumption by assumption.
- Retire NMI if the method is ordinary closed-loop identification plus an exact transition.
- Retire NCS if transferable post-change joint modes have already been estimated and independently replicated.

### D0 — free data contract

- Identify a licence-compatible, hashable source for block headers, receipts/transactions, blob sidecars or blob
  commitments, fork versions and rollup attribution needed by the estimand.
- Record source, API/export version, time coverage, licence, expected bytes, rate limits and reconstruction checks.
- Confirm that at least one development change and one untouched validation/replication change exist without
  inspecting outcome paths.
- Freeze transaction/rollup inclusion rules and never infer missing blob data as zero.

### I0 — identification

- Draw a fork-level causal graph with controller parameters, prices, resource use, workload, release schedules,
  builder/validator selection and contemporaneous protocol changes.
- Define which parameter variation is externally set and which response component remains endogenous.
- Supply negative controls, anticipation windows, unaffected-resource controls and a fixed latent-state oracle.
- If no design separates parameter change from concurrent demand/software changes, close NCS before outcomes.

### P0 — metadata-scale generated feasibility

- Use only metadata-supported block counts, intervention counts, missingness bounds and conservative correlation
  lengths; do not tune a DGP to a viewed fee or usage path.
- Calibrate type-I error, coverage and power for common shocks, batching, trend breaks, serial dependence,
  saturation, rounding, missing slots and heterogeneous rollups.
- Define the minimum scientifically consequential response before simulation.
- A fail retires the design. No seed changes, threshold relaxation or real-series inspection may rescue it.

## 6. Outcome protocol if all pre-outcome gates pass

1. Freeze development, temporal validation and external replication regimes by protocol activation, never by
   observed response.
2. Fit behavioral parameters only on the development pre-change period.
3. Transform the announced controller parameters through the exact oracle and issue a signed response forecast
   with intervals before opening the post-change path.
4. Evaluate the entire response vector, not a favorable horizon, resource or rollup.
5. Permit one model revision using development only; seal validation again under a new commit.
6. Open the external replication once. Failure remains the headline and cannot be averaged away by pooling.

## 7. Required baselines

- exact controller with price-insensitive stationary demand;
- exact controller with time-varying but non-adaptive latent demand;
- seasonal/state-space and Hawkes or count-process workload baselines where appropriate;
- reduced-form event study with honest serial/cluster uncertainty;
- standard closed-loop subspace/state-space identification;
- instrumental-variable or structural-demand estimator when its assumptions are plausible;
- post-change refit as a descriptive upper bound, never the prospective comparator;
- simple persistence and calendar baselines.

No neural model is justified until it improves sealed transfer over these transparent baselines and its added state
has an operational interpretation or falsifiable ablation.

## 8. Data requirements

### T0 — authorized now

- Official protocol specifications, test vectors, fork calendars and parameter schedules.
- Primary papers and dataset catalog/schema/licence pages.
- Metadata-only counts for blocks/files/time coverage; no fee, occupancy, transaction or rollup outcome value.

### T1 — free generated and mechanism validation

- Official controller test vectors and generated demand paths.
- No chain outcome, paid source or sealed period.
- Expected storage below 5 GB.

### T2 — free public-chain development after G0/N0/D0/I0/P0

- Versioned block/header fields, transactions/receipts and blob availability sufficient to reconstruct the frozen
  resource vector and exact controller state.
- Rollup attribution only from a frozen public registry or contract-address provenance table.
- Target 0.1--2 TB raw/derived depending on node/export route and retained transaction payloads.
- Every shard needs chain ID, block/slot range, canonicality rule, source/version, retrieval time, licence, raw hash,
  schema hash and transform hash.

### T3 — independent replication and cross-system scope

- A later untouched controller-parameter change or independently administered compatible chain/resource market.
- For NMI, two non-blockchain systems with known price/capacity controllers and observable resource demand.
- Expansion to commercial archive access is allowed only after free development evidence and a licence/value gate;
  buying the same effective information does not reopen a failed design.

## 9. Compute requirements

### T0 — current authorization

- Mac CPU at most 30 core-hours for documents, specifications, graph maintenance and metadata parsers.
- Zero remote-worker contact, zero GPU-hours and no queued job.

### T1 — exact mechanism and generated feasibility

- 100--1,000 CPU core-hours for test-vector replay, dependence-aware generated calibration and estimator attacks.
- CPU work may later use either V100 host or the RTX2060 host, with GPUs idle, only after a separate experiment
  preregistration.
- At most 20 V100-equivalent GPU-hours only if a necessary estimator cannot be evaluated transparently on CPU;
  currently locked.

### T2 — chain reconstruction and development analysis

- 1,000--20,000 CPU core-hours, 128--512 GB aggregate RAM and 0.1--2 TB fast storage.
- Zero to 200 V100-equivalent GPU-hours; SQL/columnar parsing, robust inference and block/rollup job arrays are
  expected to dominate.
- Parallelize by immutable block range, regime, rollup and bootstrap cluster. Do not use distributed training for
  independent jobs.

### T3 — replicated paper-scale modeling

- 20,000--200,000 CPU core-hours, 2--20 TB storage and 200--4,000 V100-equivalent GPU-hours only after measured
  T2 costs and a surviving claim.
- Capacity may expand beyond the current two V100 32 GB workers and one RTX2060 to additional compatible CPU/GPU
  pools. H20 is excluded from every budget and execution assumption.
- Separate heterogeneous GPU pools and benchmark each against a canonical V100 job. More compute never substitutes
  for a second intervention, valid instrument or untouched replication.

## 10. Venue routing

### Nature Computational Science

Requires an exact-mechanism, prospectively predictive and independently replicated law about adaptive demand in a
computational resource market. The contribution must matter beyond Ethereum configuration and explain when a
known controller plus estimated response transfers across parameter regimes. A careful single-upgrade event study
routes to a specialist economics/blockchain venue, not NCS.

### Nature Machine Intelligence

Requires a non-equivalent learning/identification method with a formal guarantee and cross-domain validation. If
the solution is established system identification, IV or structural demand estimation with a differentiable
controller, NMI is closed even if the NCS phenomenon survives.

### Honest prior probabilities at freeze

- V6-NCS-1 reaching a defensible Nature Computational Science Article: `5%--10%` before novelty/data/identification
  audit; the high-rate data improve feasibility, but concurrent forks and endogenous prices are serious risks.
- V6-NMI-1 reaching a defensible Nature Machine Intelligence Article: `1%--3%`; the generic method neighborhood is
  heavily occupied and no theorem candidate has yet survived.
- A strong specialist paper conditional on a clean data contract and prospective transfer: `20%--35%`.

These are planning probabilities, not acceptance predictions.

## 11. Stop and anti-rescue rules

- Freeze and push this plan before inspecting any chain outcome series or empirical figure.
- Do not use block count as sample size without a preregistered dependence/effective-unit calculation.
- Do not call deterministic controller persistence behavioral memory.
- Do not regress demand on endogenous protocol price and label the coefficient causal.
- Do not select fork, horizon, resource, rollup, bandwidth or sign after viewing responses.
- Do not use EcoMD or generated demand to manufacture a real phenomenon.
- If novelty, data, identification or generated power fails, preserve V6 append-only and change the scientific
  object again. Compute and data scale-up remain locked.

## 12. Immediate work queue

1. Commit and push this frozen plan and its graph/lineage entry.
2. Audit official controller specifications, fork parameter schedules and test-vector availability.
3. Audit primary theory and empirical work against both frozen candidates.
4. Audit only catalog/schema/licence metadata for free block/blob/transaction reconstruction and independent
   interventions.
5. Produce a joint G0/N0/D0/I0 decision. Only a survivor may receive a separate generated-feasibility
   preregistration.

## 13. Pre-outcome audit decision — 2026-08-13

The audit in `research/theory_exploration/algorithmic_fee_market_audit_v6.md` was completed without opening any
chain outcome. Three distinctions now control the route:

1. EIP-1559, EIP-4844 and EIP-7918 provide an exactly executable integer controller, including a strict
   execution-fee-dependent blob-state branch and unscaled state carryover at BPO transitions.
2. Closed-loop identification, IV gas-demand estimation and multi-resource dynamic-fee optimization already
   occupy the generic NMI method composition. `V6-NMI-1` is retired as `RETIRED_PRIOR_ART`.
3. The NCS no-refit forecast remains a conditional prospective candidate, but BPO1/2 are development-only and
   BPO3 has no finalized activation or parameters. No independent replication is registered.

The gate state after the formal Experiment 149 result is G0 `PASS_EXP149`, N0/NMI `FAIL_NO_SURVIVOR`, N0/NCS
`CONDITIONAL_SURVIVOR`, D0 `CONDITIONAL_PASS_FIELDS`, I0 `BLOCKED_FUTURE_INTERVENTION_REPLICATION`, and P0 now
eligible for a separate generated-only preregistration.

Experiment 149 replayed 97 official fixture cases and 107 blocks across Osaka, Osaka-to-BPO1 and BPO1-to-BPO2.
All 107 execution-fee values, all 107 excess-state values and all 86 observable blob-fee values matched exactly;
raw SHA256 `2a124acc5881204a69b34b0024c4d51387ca4060bf2525c44f1f2ff17ff3873a`. This passes implementation
conformance only and authorizes at most a separate generated-identification stress test, not real data. The two
V100 workers, RTX2060, remote hosts and all GPUs remain idle and unqueued.

## 14. Nontriviality attack and revised queue — 2026-08-13

The scale audit changes what counts as a successful V6 result. Prague/Osaka, BPO1 and BPO2 preserve `M/T=1.5`
and their `F/T` values differ by less than `4e-8` relatively. Exact standardized blob-fee values remain equal or
within `2.15e-5` over the declared audit grid. A BPO forecast can therefore be solved almost completely by an
exact-controller scale oracle. V6-NCS-1 is now `ATTACKING`, and any estimator must beat this oracle on
non-proportional controller changes before real-data admission.

The frozen Base deployment sequence supplies historical gain-only, target-preserving, target-changing and joint
parameter topologies. It is development/transport stress only: the episodes share one chain and administrator,
some bundle DA-scalar or minimum-fee changes, and no future task exists in the frozen active directory. No
independently administered sealed intervention has been identified.

The revised work queue is:

1. freeze a generated-only Experiment 150 before implementation;
2. test exact scale oracle, transparent pre-change response estimators and fixed-latent-demand countermodels on
   scale-equivalent and non-proportional parameter changes;
3. require fail-closed behavior under latent drift and bundled changes;
4. keep Base and BPO1/2 historical outcomes sealed until P0 passes, without treating either as confirmation;
5. monitor BPO3 and independently administered systems for finalized future interventions, but do not queue a
   remote host or GPU merely while waiting.

Even a generated P0 pass does not satisfy I0, unlock outcomes or restore NMI.
