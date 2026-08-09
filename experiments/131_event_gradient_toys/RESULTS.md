# Experiment 131 results — discrete-event invariant-gradient baselines

**Run date:** 2026-08-10  
**Artifact:** `EVENT_GRADIENT_RESULTS.json`  
**Decision:** baseline/harness audit PASS; no candidate method; G0 remains AMBER

## Frozen gates

All seven preregistered gates passed. The analytic formulas agree with independent numerical checks to below
`3.2e-11`. With a fixed seed, `create_graph=True/False` produced exactly the same CPU trajectory and terminal
RNG state while both modes retained finite model-parameter gradients.

The slow two-state chain (`alpha + beta = 0.04`) is the clearest initialization-bias control:

| Estimator | Relative bias | 90% coverage | Mean transitions |
|---|---:|---:|---:|
| fresh-short LR | -12.61% | 6.25% | 24 |
| persistent-detached LR | -38.01% | 0.00% | 2,072 |
| full-long LR | +0.47% | 89.06% | 2,072 |
| stationary oracle LR | +0.30% | 95.31% | 25 |
| finite difference CRN | -3.06% | 95.31% | 4,144 |

Carrying a state but resetting the score is not a steady-state sensitivity estimator. In this cell it is more
biased than a fresh 24-step trajectory despite paying for the 2,048-step burn.

For the compound-Poisson AR/OU control, the established coupled finite-difference baseline passes the frozen
medium and slow gates:

| Mixing parameter `a` | Estimator | Relative bias | 90% coverage |
|---:|---|---:|---:|
| 0.80 | coupled finite difference | -2.93% | 92.19% |
| 0.97 | coupled finite difference | +5.64% | 92.19% |
| 0.97 | fresh-short LR | -26.08% | 71.88% |
| 0.97 | persistent-detached LR | -31.63% | 82.81% |
| 0.97 | full-long LR | +42.14% | 93.75% |

The slow full-long LR technically satisfies the preregistered coverage alternative, but its replicate standard
deviation is about `204.6` for a truth of `2.073`; it is therefore a high-variance correctness control, not a
competitive estimator. The deliberately naive pathwise derivative of the Poisson rate returns zero and remains
labelled invalid.

## Interpretation

This experiment validates the event-gradient harness, analytic truths and known baselines. It does not improve
the accuracy--cost frontier and does not introduce the fail-visible, mixing-aware estimator required by G0.
The strongest immediate baseline for the jump-rate cell is coupled finite difference; any candidate must be
compared against it at matched simulator cost rather than only against short BPTT.

