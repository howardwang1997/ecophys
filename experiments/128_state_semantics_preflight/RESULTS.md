# Experiment 128 results — CPU mechanics preflight

**Run date:** 2026-08-09  
**Artifact:** `CPU_PREFLIGHT_RESULTS.json`  
**Decision:** CPU preflight PASS; scientific/confirmatory gate not evaluated

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

The ten CPU cells used about 7.87 seconds inside their training loops on this Mac; total command time was about
16 seconds including imports, data targets and 10 evaluation rollouts. This timing is only a harness smoke and
must not be extrapolated to `N=10,000`.

## Decision

- PASS: mechanics, factor activation, state/jump/checkpoint correctness on CPU.
- PENDING: V100 parity/VRAM probe.
- NOT RUN: multi-seed WP2 screen, frozen long-horizon primary metric, `T=8,000` evaluation.
- PROHIBITED CLAIM: the current result does not show improved market fidelity or validate EcoMD.
