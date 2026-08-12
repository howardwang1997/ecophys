# Experiment 150 protocol deviation — experiment void

**Recorded:** 2026-08-13 immediately after detection

**Decision:** `VOID_PREMATURE_FORMAL_CELL_EXECUTION`

## What happened

After the preregistration and its topology clarification were pushed, but before any implementation commit,
focused test or `FREEZE.yaml` existed, an ad hoc Conda Python command intended as a small algebra check executed
the full frozen seed loops. It evaluated all four perturbations, all 128 Experiment 150 seeds, both BPO
interventions and the generated non-proportional intervention. It printed aggregate development and intervention
divergences to the tool transcript.

The command did not use a formal runner, verify repository hashes, enforce a clean checkout, install a network
audit hook or write a result artifact. This is nevertheless outcome access for the generated protocol. Experiment
150 therefore cannot receive a formal result and must never be rerun.

## Information exposed

The transcript exposed that:

- maximum development alias error was at most `3.3306690738754696e-16`;
- BPO1/BPO2 maximum divergences were at most `4.073617554389841e-10` and
  `2.909721907862206e-10`, respectively;
- the execution-column perturbation remained equal to floating-point precision because BPO changes only the blob
  gain;
- all 128 seeds for every perturbation exceeded the frozen `1e-6` divergence threshold under the generated
  non-proportional intervention;
- the smallest exposed non-proportional maximum divergence across seeds was `8.761103083416294e-06`.

These values are contaminated development information. They may be reported as the reason Experiment 150 is
void, but they are not a preregistered formal result and must not be used to relax or tune matrices, thresholds,
steps or interpretations.

## Containment

- No chain fee, gas-use, transaction, occupancy, rollup, paid, sealed or user data was read.
- No file, checkpoint or artifact was written by the command.
- Network, remote-host and GPU use were zero; V100s and RTX2060 remained idle and uncontacted.
- Experiment 150 is permanently closed and no `FREEZE.yaml` or `RESULTS.md` may be created for it.
- Any clean executable verification requires a new experiment number, a disjoint seed root and the original
  scientific gates unchanged. It must disclose this exposure and cannot be called blind discovery or independent
  empirical replication.

## Research interpretation

The deviation does not alter the pathwise algebra, which can be checked symbolically. It does invalidate
Experiment 150 as a process-controlled computational result. Research-integrity chronology takes precedence over
the fact that the exposed values were consistent with the preregistered direction.
