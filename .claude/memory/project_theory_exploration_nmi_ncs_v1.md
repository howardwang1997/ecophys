---
name: Dual-track NMI/NCS theory exploration v1
description: 2026-08-12 result—NMI has no survivor; NCS has one relaxation-exceedance conjectural mechanism under attack. Exp144 confirmed two negative controls. No theorem, data/GPU scale-up or novelty pass.
type: project
---

# Dual-track NMI/NCS theory exploration v1

Started on `theory-exploration-nmi-ncs-v1` from `main@fdf0c5f72` on 2026-08-12. The plan of record is
`papers/proposal/plan_theory_exploration_nmi_ncs_v1.md`.

The verified result tree `ba437a7d89bef3c78b7789f1f1fee2e864d88919` was fast-forwarded to remote `main` on
2026-08-12. The historical Plan v5 archive remained exactly `436dad6e7f80999584e44c4a616a1f213b9c814d`.

The shared mathematical object separates an audited fast mechanism `G`, learned event behavior `pi`, slower
adaptation `U` and explicit mechanism/intervention `M`. NMI requires a method/theorem that transfers beyond markets;
NCS requires a prospectively specified real response mechanism replicated across independent interventions.

The canonical graph is `research/theory_exploration/knowledge_graph.yaml`; human topology, source coverage,
candidate history, failures and venue routes live beside it. The validator is
`ecomd/research/theory_graph.py`. As of the formal result it contains 75 nodes, preserves append-only state changes,
requires proof/counterexample/benchmark links and has no automated `PASS` state.

## Iteration result

- S1 action lift: `RETIRED_PRIOR_ART` by sequential policy factorization and structural re-composition; exact
  mechanics do not repair policy-state off-support.
- S2 single-environment adaptation impossibility: `RETIRED_IDENTIFIABILITY`; generic observational equivalence
  without a constructive sharp boundary.
- S3 fast/slow response split: `RETIRED_PRIOR_ART` by Markov response, Duhamel and singular averaging.
- S4 predictive quotient: `RETIRED_PRIOR_ART` by PSR, bisimulation, causal abstraction and invariant block MDPs.
- S5 unseen intervention composition: `RETIRED_PRIOR_ART` by soft-intervention composition, homomorphism and effect
  invariance.
- NMI-T1 known-mechanism excitation: `RETIRED_PRIOR_ART`. Its simplest rank gain is ordinary stacked observability;
  controlled/switching-system identification and active intervention design cover the future-feedback form.
- NCS-M1: `ATTACKING`. The naive order-effect certificate is false. The remaining candidate is a replicated real
  response outside the simultaneous contraction/relaxation envelope of every prevalidated frozen mechanical/Markov
  baseline. Such exceedance rejects that baseline class; it does not alone identify beliefs or exclude every hidden
  slow state/confound.

The exact event-layer identity retained for architecture/research design is
`I(Z;Q_next | Q,A,M)=0` whenever the known fast mechanism noise is conditionally independent of `Z` after the
observed mechanism inputs. This is standard conditional independence, not a new theorem. It says exact mechanics
improve transition correctness but do not directly identify adaptive state; informative pressure must come from
future behavioral targets.

## Experiment 144

- Preregistration `3964b45c9`; implementation `24e709710`; freeze/run `0a07c0228`.
- Formal decision `NEGATIVE_CONTROLS_CONFIRMED`; candidate admission and novelty pass are both false.
- W1: single ranks `[1,1]`, stacked rank `2`, eigenvalues `[1,1]`, exact stacked-Gramian error `0`.
- W2: fixed non-adaptive stochastic operators produce `r_AB=0.455`, `r_BA=0.38`, difference `0.075`.
- Raw SHA-256 `92351520b073d6674c0629380020599273c2beada29faf06437546a421eddcf8`.
- Mac CPU only; zero market files, sealed periods, network during formal run and GPU-hours. No worker was contacted.

## Binding route decision

NMI is `NO_SURVIVOR`; do not train or benchmark NMI-T1. Prediction-target-conditioned identifiability is only a
future search direction and is already bordered by recent controlled-world-model/physical-parameter work.

NCS is `CONJECTURE_ONLY`; C0 prior-art/estimand distinction and C1 real intervention metadata/replication contract
are absent. The already-inspected US Tick Size Pilot may be development context but not sole headline replication,
because forward and reverse windows are published. Keep 2xV100 and RTX2060 idle; no paid or sealed data opens.

The old Plan v4 invariant-gradient v0/v1 G0 FAIL, entropy/TUR T0 G0 FAIL and anonymous-L2 belief
non-identifiability remain binding and are not reopened by this iteration.
