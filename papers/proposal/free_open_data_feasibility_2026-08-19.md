# Free/open-data feasibility execution board — 2026-08-19

> **Archive scope.** This board records a parallel run forked from `bcb025bd9`. While it was executing, the
> canonical remote branch advanced through a separate exp137--143 chain and closed the original NCS method
> route at G0. These results remain reproducible diagnostics, but their experiment numbers and forward-looking
> decisions must not be merged into the canonical branch without renumbering and reconciliation.

## Purpose and claim boundary

This phase uses only already-held samples or public no-key services to remove implementation and data-source
risk before any purchase. It cannot substitute for the multi-day, multi-market confirmatory data in Plan v4,
and it does not upgrade the missing invariant-calibration novelty gate G0.

The active work is ordered by decision value:

1. qualify data paths without inspecting frozen targets;
2. validate dynamic observation semantics and strong observation-only controls on real messages;
3. measure the current fleet's valid numerical envelope;
4. only then decide which paid or collaborative data would change a scientific gate.

## Frozen experiment map

| Experiment | Free data / resource | Scientific purpose | Current status | Decision boundary |
|---|---|---|---|---|
| exp137 | five independent LOBSTER sample symbols | dynamic prices/queues, causal next-event evaluator, Markov/history/queue controls, latency/depth stress | feasibility PASS, 5/5 paths | one-day feasibility only; no EcoMD advantage or G3 |
| exp138 | SQD public Portal, nine EVM networks | target-free header coverage, continuity, repeatability and service envelope | Q0a PASS | Aave rows remain locked pending Q0b joins/cross-provider hashes |
| exp139 | two V100s + one RTX2060 | state-complete numerical/HBM envelope | FAIL overall; `N=500` PASS, `N>=2,000` non-finite | cap production config at supported size; more HBM is not a fix |

All three protocols were committed before their corresponding full run. Result artifacts retain source commit,
platform/device, configuration and hashes. Failed gates remain visible.

## Results available now

### SQD zero-target qualification

Nine of nine networks passed 36 repeated header windows. Across 72 stream calls, content repeats were exact,
median latency was 0.424 seconds, empirical p95 was 0.777 seconds and retry fraction was 2.78%. No logs,
transactions, traces, state diffs, protocol addresses or event topics were requested.

Next source gate Q0b must use frozen non-Aave fixtures to test joins, compare block hashes to an independent
provider, define gap/duplicate policy, and export an immutable content-hashed snapshot. Passing Q0a alone does
not authorize target extraction.

### CUDA envelope

All six `N=500` cells across the two V100s and RTX2060 passed exact chunk/resume and finite mechanics. No
`N>=2,000` cell passed. The failure reproduced across devices and seeds while HBM remained ample: `N=10,000`
reserved only 12.81 GiB on a 32 GiB V100. The limiting factor is numerical/dynamical stability, not GPU memory.

The RTX2060's default `ecophys` environment has a PyTorch/driver mismatch. Its existing
`ecophys-g0-regression` Conda environment is CUDA-compatible; no driver was changed.

### Dynamic real-message baseline

All five paths passed. Across 947,911 eligible chronological transitions, dynamic queue reconstruction was
exact on 927,811/927,811 visible type 1--4 messages. The combined observation-only model was strongest on every
symbol; its median gain over the unconditional baseline was 0.271 nats/event. With features stale by 5 and 20
events, median gain fell to 0.080 and 0.023. The global relevance gate passed 5/5 versus the required 4/5.
These are useful evaluator/baseline facts, not an EcoMD result.

## Data access findings

- The repository-held LOBSTER archives are sufficient for real dynamic-book implementation and one-day
  controls. Duplicate depth variants are excluded from independent-path counts.
- Tardis documentation still advertises first-of-month Binance L2 samples without an API key, but the official
  file URL returned Cloudflare HTTP 403 from the Mac and a second compute-node egress. Until access is restored
  or Tardis provides an academic route, it is a documented external blocker rather than an acquired dataset.
- Binance's public archive can supply trades/aggregate trades/bars but not historical L2 reconstruction.
- AEMO NEMWeb and Elexon Insights/BMRS remain the next no-purchase non-DeFi mechanism backends after the active
  L2 and Q0b gates. Starting them before the current evaluator is frozen would spread effort without resolving
  the main bottleneck.

## Compute queue

- When V100 connectivity returns, run a cross-node exp137 replication from the committed snapshot rather than
  changing the completed primary result. All five canonical paths are RTX2060 CUDA runs; AAPL, MSFT and SPY
  also have CPU portability checks. The largest held-out combined-NLL difference is 0.0164 nats/event and all
  six paired fits clear the frozen gate.
- Do not launch formal WP2 or large-`N` EcoMD training. The estimator novelty gate is still missing and exp139
  shows that the old random-weight configuration becomes non-finite before HBM is exhausted.
- After exp137, freeze a small stability diagnosis over integration step and parameter scale. Its purpose is to
  establish a valid production configuration, not to tune on a headline market outcome.

## Immediate decisions after exp137

1. The 5/5 result clears the frozen relevance gate, so keep these observation-only controls as mandatory G3
   baselines and proceed to Q0b plus a full continuous-time Hawkes implementation.
2. Do not purchase D1/D2 data until G2 and the observation schema gates required by Plan v4 pass. Free samples
   reduce plumbing risk but cannot establish temporal or cross-domain generalization.
3. Treat dynamic state, latency and event persistence as nuisance explanations that any EcoMD improvement must
   beat on the same future split; a comparison only to an unconditional baseline is no longer acceptable.
