---
name: Dual-track NMI/NCS theory exploration v2
description: Completed negative continuation from v1. NMI has no target-task survivor; NCS relaxation exceedance fails mechanism identification; registry has no sealed replication. Data and GPUs remain locked.
type: project
---

# Dual-track NMI/NCS theory exploration v2

Started on `theory-exploration-nmi-ncs-v2` from integrated `main@648fd96da` and completed on 2026-08-12. Plan and
outcome of record:
`papers/proposal/plan_theory_exploration_nmi_ncs_v2.md`.

Inherited decisions are binding: v1 NMI `NO_SURVIVOR`, v1 NCS `CONJECTURE_ONLY`, and exp144
`NEGATIVE_CONTROLS_CONFIRMED`. V2 may inspect primary literature and public rule/date/schema/licence metadata, but
not treatment outcomes or sealed values. It uses <=50 CPU core-hours and zero GPU-hours; no worker is contacted.

## Binding v2 decisions

- NMI: `NMI_NO_SURVIVOR`. Masked-prediction identifiability directly covers target completeness, matrix-power
  ambiguity kills a generic monotone horizon threshold, complementary targets are partition intersection/tensor
  identifiability, and universal task order is Blackwell comparison.
- NCS: `NCS_C0_FAIL_IDENTIFICATION`. Exceeding a prospective contraction envelope rejects the selected model
  class; it does not identify learning, belief or adaptation.
- Data: `ready_for_data_contract: false`. Registry v2 has ten cases: two development-only, eight rejected and zero
  sealed candidates. Public snippets exposed published summaries for both development cases; the recorded protocol
  deviation permanently forbids relabelling them as sealed.

Experiment 145 formally confirmed two exact non-adaptive counterexamples. A fixed hidden mode with contraction
`0.9` exceeded a declared `0.6^L` envelope at every frozen lag. A fixed time-homogeneous Markov clock reproduced an
arbitrary six-point finite response with max error zero. Raw SHA-256:
`9b752b4ad428ceb56d82483f94cf7e3c92d26ed3869cbe8a7ddbfbe75c5c5d4f`.

Resource use was Mac CPU only, 0.0 GPU-hours, zero market files, zero sealed periods and zero worker contacts. Do
not queue V100/RTX2060 jobs, open outcome data or purchase data on this line. The envelope may be reused only as a
prospective model-checking diagnostic. Reopening an adaptation claim requires an independently justified
state-completeness/structural separator plus a fresh development-and-sealed-replication contract.
