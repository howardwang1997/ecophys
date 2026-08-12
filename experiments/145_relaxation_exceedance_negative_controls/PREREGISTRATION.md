# Experiment 145 — relaxation-exceedance attribution negative controls

**Frozen:** 2026-08-12  
**Branch:** `theory-exploration-nmi-ncs-v2`  
**Parent plan:** `dca7ce36d`  
**Scientific role:** exact counterexamples only; no theorem novelty, adaptation claim or data/compute gate can pass

## 1. Question

Does persistence beyond a declared frozen Markov relaxation envelope identify an adaptive or learned response?

The experiment evaluates two time-homogeneous, non-adaptive constructions. Confirming them means that envelope
exceedance rejects only the declared baseline class. It does not distinguish learning from omitted state or from a
fixed process with a longer memory than the baseline class permits.

## 2. Frozen fixtures

All values are fixed in `config.yaml` and evaluated in float64 at absolute tolerance `1e-12`.

### W1 — omitted fixed slow mode

The audited baseline class is represented by a scalar contraction bound `d=0.6`, zero additional error and unit
initial amplitude. Its lag-`L` envelope is

\[
B_L=d^L.
\]

The data-generating counterexample has a hidden scalar state

\[
S_{t+1}=\rho S_t,\qquad Y_t=S_t,qquad \rho=0.9,
\]

with fixed `rho`, no parameter update, no history-dependent transition and no learning. For every frozen lag
`L=1,...,8`, the expected response `rho^L` must exceed `B_L`. The witness decision is
`CONFIRMED_HIDDEN_SLOW_MODE_EXCEEDANCE` only if all values are finite, `0<=d<rho<1`, every declared lag is a
positive integer and every margin is strictly positive beyond tolerance.

### W2 — arbitrary finite path from a fixed clock chain

Use the bounded sequence

\[
r=(0.25,-0.10,0.60,0.20,-0.35,0.05).
\]

Construct a time-homogeneous deterministic Markov chain on six states with transition `i -> i+1` and an absorbing
last state, initial distribution concentrated on state zero, and observable `f(i)=r_i`. The expected response at
lags `0,...,5` must equal `r` exactly within tolerance. The transition matrix must be row stochastic and fixed; its
one-step Dobrushin contraction coefficient is expected to be `1.0`. The witness decision is
`CONFIRMED_FIXED_CLOCK_REPRESENTATION` only if all checks pass.

This finite-horizon construction is not asserted to be a parsimonious market model. It is an impossibility witness:
an observed finite response path alone cannot exclude a fixed hidden-state explanation.

## 3. Frozen decision rule

| W1 | W2 | Overall decision | Interpretation |
|---|---|---|---|
| confirmed | confirmed | `ATTRIBUTION_NOT_IDENTIFIED` | relaxation exceedance rejects a specified class, not non-adaptation generally |
| otherwise | any | `IMPLEMENTATION_OR_SPEC_FAILURE` | diagnose the fixture; draw no scientific conclusion |
| any | otherwise | `IMPLEMENTATION_OR_SPEC_FAILURE` | diagnose the fixture; draw no scientific conclusion |

The result schema must record `candidate_admission: false`, `novelty_pass: false` and
`adaptation_identified: false`. There is deliberately no positive scientific state.

## 4. Artifact and chronology contract

- Frozen configuration: `experiments/145_relaxation_exceedance_negative_controls/config.yaml`.
- Runner: `experiments/145_relaxation_exceedance_negative_controls/run_negative_controls.py`, implemented only
  after this preregistration is committed.
- Raw output: `experiments/145_relaxation_exceedance_negative_controls/artifacts/raw/negative_controls.json`.
- The runner must refuse a dirty checkout, refuse overwrite and verify a later implementation freeze containing
  hashes of the config, runner, witness module and focused test.
- A repair must use Experiment 146; the formal Experiment 145 raw artifact is immutable.

## 5. Resource and data boundary

- Inputs: constants in `config.yaml` only.
- Market, paid, R2, user and sealed data: forbidden.
- Network during the formal run: forbidden.
- Compute: one Mac CPU process, expected under one second, zero GPU-hours.
- V100-A, V100-B and RTX2060 are not contacted.

