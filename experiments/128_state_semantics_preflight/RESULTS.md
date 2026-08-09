# Experiment 128 results — CPU and V100 mechanics preflight

**Run date:** 2026-08-09  
**Artifacts:** `CPU_PREFLIGHT_RESULTS.json`, `V100_PROBE_V1_FAILED.json`,
`V100_DIAGNOSTIC_RESULTS.json`, `V100_PROBE_V2_RESULTS.json`
**Decision:** CPU and versioned V100 mechanics preflight PASS; scientific/confirmatory gate not evaluated

## Outcome

All 10 frozen cells completed with finite losses, gradients and evaluation trajectories. Every arm began from
the same parameter hash within a seed, and all interventions led to distinct trained parameter hashes. The five
arm harness is therefore mechanically active rather than a collection of no-op configuration labels.

| Market | A historical eval loss | A' force | B state+force | C jump+force | D combined | D − A |
|---|---:|---:|---:|---:|---:|---:|
| SPX | 0.50661 | 0.50238 | 0.48095 | 0.51365 | 0.49739 | -0.00922 |
| BTCUSDT | 0.25532 | 0.24838 | 0.22979 | 0.26260 | 0.23646 | -0.01886 |

The one-seed, four-iteration result happens to favor D over A on both markets. It is not a performance claim:
the run is deliberately too short to estimate seed variance, long-horizon fidelity or even optimizer ranking.
It only clears the path to a larger, preregistered screen.

## Factor activation

Using evaluation-loss contrasts:

| Contrast | SPX | BTCUSDT | Interpretation |
|---|---:|---:|---|
| A' − A | -0.00424 | -0.00694 | partial-force repair is active |
| B − A' | -0.02142 | -0.01860 | full state/clock path is active |
| C − A' | +0.01127 | +0.01422 | sampled-jump training path is active |
| D − A | -0.00922 | -0.01886 | joint path differs and remains trainable |

Signs are not interpreted as treatment effects because there is one training seed and the outcome was viewed
after only four iterations.

## Regression evidence

The new state-complete API passed six CPU tests:

1. monolithic rollout equals an arbitrary chunk partition exactly;
2. serialized checkpoint-resume equals uninterrupted rollout exactly;
3. a detach boundary does not change forward dynamics;
4. attached arbitrary chunks reproduce monolithic parameter gradients;
5. jump trajectories are exactly equal for `create_graph=True/False` under the corrected law, while gradients
   remain live;
6. absolute-clock mismatch hard fails.

The checkpoint test found and led to repair of an additional historical defect: force evaluation could include
a total-derivative path through context when state retained its autograd history, while a serialized/detached
state used the intended partial derivative. Reproduction-only flags retain both historical force and jump
semantics for control arms; corrected semantics are the defaults.

## Resource observation

The committed artifact records about 7.92 seconds across the ten CPU training loops on this Mac. Import, target
construction and evaluation overhead are excluded. This timing is only a harness smoke and must not be
extrapolated to `N=10,000`.

## V100 negative result, diagnosis and versioned rerun

The first V100 run is retained as a failure rather than overwritten. At `N=500`, `dt=0.02`, 32 parity steps
and a 512-step untrained rollout:

- arbitrary chunks and serialized resume were bit-exact;
- `create_graph=True/False` differed by at most `2.38e-7`, so the original bit-exact CUDA rule failed;
- the 512-step random-model rollout produced non-finite values.

The follow-up diagnostic separated these effects. The terminal RNG states were exactly equal in both autograd
modes. A no-jump control showed the same `1.19e-7`--`2.38e-7` discrepancy, so the residual is a generic fp32
CUDA graph-construction floor rather than evidence of a different jump draw. In the stability sweep, the full
`dt=0.02` configuration first became non-finite at step 362 for the diagnostic seed; disabling feedback or
reducing `dt` to 0.005 remained finite for 512 steps. Other architecture-changing ablations were not stable,
so the diagnostic does not identify one mechanism as the unique cause.

Probe v2 was declared post-diagnostic and used `dt=0.005` plus a CUDA parity rule of exactly equal RNG state
and state/return error no greater than `1e-6`. It passed all 11 checks:

- chunk and checkpoint-resume trajectory/final-state differences: exactly zero;
- jump RNG state: exactly equal; maximum return/state discrepancies: `1.79e-7` / `1.19e-7`;
- gradients: present and finite;
- 512-step rollout and absolute clock: finite and correct;
- wall time: 4.78 seconds;
- peak CUDA memory: 496,798,720 allocated and 526,385,152 reserved bytes.

The device reported by PyTorch was `Tesla PG503-216` under PyTorch 2.3.1 + CUDA 12.1. V2 demonstrates that
the API works on the available V100 under a diagnosed stable integration setting. It does not erase v1, prove
production-scale stability or establish market fidelity.

## Decision

- PASS: mechanics, factor activation and state/jump/checkpoint correctness on CPU.
- PASS: versioned single-V100 state/resume/parity mechanics at `N=500`, with v1 failure retained.
- PENDING: atomic distributed checkpoint/resume, production scale and preemption tests.
- NOT RUN: multi-seed WP2 screen, frozen long-horizon primary metric, `T=8,000` evaluation.
- PROHIBITED CLAIM: the current result does not show improved market fidelity or validate EcoMD.
