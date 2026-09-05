# EcoMD known-gain Causal Chamber truth-asset preflight

**Date:** 2026-09-05  
**Work type:** reusable truth/control-asset preflight; not a topic cycle  
**Parent:** known-gain weak-design singularity follow-up  
**Decision:** `partial_capability`  
**Candidate harvesting:** not authorized  
**Dataset outcomes, external outreach, implementation, SSH, and GPU status:** not authorized

## 1. Named blocker and scope

The surviving known-gain result is an exact statistical singularity: for output-only cyclic systems,
relative gains expose circulatory orientation through a commutator, while co-trending gains erase the
first-order sign signal and leave only a quadratic magnitude signal. The preceding audit retained this
as a theorem-shaped residue but did not find a real controlled system with all of:

1. independently varied, quantitatively known gains;
2. externally known signed coupling coefficients;
3. complete output and innovation/control state under the same estimand; and
4. an untouched, independently governed same-estimand replication.

This preflight asks only whether a reusable asset now removes that blocker. It is infrastructure work
under the saturated-family rule, not a re-labelled candidate search. No released observation table was
downloaded or inspected. The evidence used here is limited to the paper, public repository inventory,
experiment generators/configuration metadata, license statements, access page, and a primary-paper
description of one nearby industrial benchmark.

## 2. Frozen estimand family

The asset must support the same model used by the theorem, not merely a graph-recovery analogue. For
environments or randomized blocks indexed by (e), freeze

\[
 R_e=(I-\Phi D_{\gamma_e})^{-1}\varepsilon_e,
 \qquad D_{\gamma_e}=\operatorname{diag}(\gamma_e),
 \qquad \operatorname{Cov}(\varepsilon_e\mid\gamma_e)=\Sigma.
\]

The primary estimand is the signed, quantitative feedback matrix (\Phi), especially its
(K)-circulatory tangent component for (K=\Sigma^{-1}). The gain vector must be assigned before the
corresponding response block and must scale declared columns of one invariant mechanism. Changing a
setpoint, changing an actuator's marginal distribution, or changing a sensor resolution is not a gain
intervention unless an independently specified physical map proves that it implements the same
(D_\gamma) action.

The minimum design must include both common-gain and differential-gain blocks. With two channels,

\[
 \eta_n^2=n^{-1}\sum_{t=1}^n(\gamma_{1t}-\gamma_{2t})^2
\]

must be chosen prospectively across the regular and singular regimes. The target is not generic edge
presence. It is signed orientation, magnitude, and honest abstention as (\eta_n\) approaches the
(n^{-1/4}) transition. A dynamic apparatus is eligible only after a frozen sampling or equilibrium
reduction links its controller and plant state to this estimand without hiding integral state, lagged
feedback, or gain-dependent disturbances inside (\varepsilon_e).

## 3. Asset audit

| Asset | What is genuinely available | Same-estimand verdict |
|---|---|---|
| [Causal Chambers paper](https://www.nature.com/articles/s42256-024-00964-x) | Two automated physical devices, user-specified protocols, manipulable actuators/sensor parameters, and assignment functions that may be arbitrary stochastic or deterministic programs. The wind-tunnel pressure-control configuration adds a feedback cycle from pressure to fan loads. | **Partial capability.** A real programmable feedback system exists. However, the published graph truth is qualitative edge truth: an edge means an intervention changes a later measurement distribution. The authors explicitly warn that missing edges need not mean absent effects and that unmeasured confounding remains. This is not signed numerical (\Phi) truth. |
| [`wt_pressure_control_v1`](https://github.com/juangamella/causal-chamber/tree/2f059123f4ac6f4724338154825630bf4ab74ac0/datasets/wt_pressure_control_v1) | One `hatch_0` experiment with (N=10{,}000), fixed exogenous variables, and a PID controller maintaining downwind pressure. Generator and protocol construction are public. | **Failed.** It contains one fixed controller regime, not randomized controller-channel gains or a common-versus-relative gain sweep. |
| [`wt_pc_validate_v1`](https://github.com/juangamella/causal-chamber/tree/2f059123f4ac6f4724338154825630bf4ab74ac0/datasets/wt_pc_validate_v1) | A randomized validation experiment for the pressure-to-loads graph edge. The pinned configuration has one row, (N=50), and pressure targets 93,000 and 95,000; the generator randomly assigns these two target values. | **Failed.** The treatment is a pressure setpoint, not a PID coefficient or known column gain. It validates qualitative edge existence, not signed feedback-matrix recovery or the weak-gain boundary. |
| [`lt_interventions_standard_v1`](https://github.com/juangamella/causal-chamber/tree/2f059123f4ac6f4724338154825630bf4ab74ac0/datasets/lt_interventions_standard_v1) | Single-target interventions of multiple strengths on light-tunnel manipulable variables, with public protocols and permissive licenses. | **Failed.** These shift actuator or sensor-parameter distributions in the standard feed-forward configuration. Intervention strength is not feedback gain, and no cyclic signed coefficient truth is exposed. |
| [Causal Chamber Remote Lab](https://www.causalchamber.ai/) | The official page says researchers can run real-time experiments on a physical chamber through a Python interface; access is obtained through a request form. The paper says assignment functions can introduce effects of varying strength. | **Unverified future capability.** Public pages do not establish entitlement, price, admissible control laws, safety limits, queue allocation, publication/release rights, or whether full controller state can be logged. Requesting access or proposing a custom experiment is external outreach and is not authorized. |
| [ESS accelerator cryoplant benchmark](https://proceedings.mlr.press/v236/mogensen24a.html) | A real industrial time series with a large cyclic component associated with coolant flow and an expert-built causal graph. | **Failed as replication.** It is passive; operating setpoints differ across three periods but are not released. Edge strengths are qualitative, observations are partial, and the authors characterize the graph as the gist of a structure for which other graphs may also be defensible. It supplies neither known gains nor signed numerical coupling truth. |

The public Causal Chamber datasets and software have a favorable rights baseline: the repository
states that released datasets use CC BY 4.0 and experiment software uses MIT terms. This clears reuse
rights only for already released material. It does not establish the terms or guaranteed release of a
new Remote Lab experiment.

## 4. Four distinctions that prevent a false activation

### 4.1 Graph truth is not coefficient truth

The chamber paper's edge semantics support evaluation of qualitative causal discovery. The known-gain
theorem requires externally known signs and magnitudes for (\Phi), or a separate calibration whose
uncertainty is included in the target. A binary statement that pressure affects fan loads cannot score
orientation or the (n^{-1/4}) boundary.

### 4.2 Setpoint changes are not gain changes

The pressure-control validation generator samples between two pressure values and then measures the
system. It does not randomize proportional, integral, derivative, or channel-specific controller
coefficients. Treating its two numeric setpoints as (gamma_1,gamma_2) would change the estimand after
seeing the available schema.

### 4.3 Programmability is not a released experiment

The onboard language may in principle implement feedback laws of varying strength. That establishes
an engineering possibility, not a present data asset. Until the precise assignments, allowable ranges,
failure handling, complete state log, rights, and confirmation policy are fixed, the possibility cannot
remove a discovery blocker.

### 4.4 Two chambers are not automatically independent replication

The light and wind tunnels contain different physical mechanisms, but their datasets, apparatus
design, software, and governance belong to one project. Moreover, only the current wind configuration
has a published feedback cycle. They cannot be counted as two independently governed, same-estimand
truth lineages merely because there are two boxes.

## 5. Frozen capability-build contract for any future re-audit

This section records requirements only. It does not authorize data collection, access requests,
implementation, or outcome inspection.

### 5.1 Assignment and interference

- Randomize at least two independently addressable feedback gains, including common-gain and
  relative-gain contrasts, from a prospectively fixed design.
- Log the actual applied gain and actuator command, not only the requested value.
- Hold setpoints and all non-target controller/plant settings fixed within a block, or randomize them
  orthogonally and include them in the frozen estimand.
- Define warm-up and washout periods; reset or log controller integral and derivative state so that
  carryover is not mistaken for a gain effect.
- Predeclare clipping, saturation, safety overrides, network latency, missed commands, and any block
  exclusion. A gain that changes the rate of safety intervention violates the invariant-mechanism
  interpretation unless modeled explicitly.
- Use stability-certified gain ranges and stop the physical protocol on a prospectively specified
  state/safety boundary.

### 5.2 Event lifecycle and replay prestate

Every retained block must include a versioned experiment protocol, randomization seed and realized
assignment order; chamber/firmware/controller code versions; all P/I/D or custom controller
coefficients; integrator, derivative-filter, and pending-command state at block start; actuator and
sensor calibration; timestamps on requested and realized commands and measurements; complete sensor
and actuator streams; warm-up/washout flags; dropped or retried operations; safety overrides; and a
terminal status. A table of measured outputs plus a protocol generator is insufficient if the hidden
controller state can change the response law.

### 5.3 Rights, release, and ethics

- New-run terms must explicitly permit method development, publication, redistribution of the frozen
  dataset and protocol, and independent reanalysis.
- The resource allocation, fees, experiment limits, embargo, and release guarantee must be written
  before collection. A non-binding access form is not such a contract.
- No human-subject issue is apparent for the apparatus itself, but operator safety, equipment limits,
  remote-service rules, and any institutional requirements remain controlling.

### 5.4 Untouched confirmation partition

Published chamber data cannot be relabelled as a pristine confirmation set after this source audit.
Any future study needs a prospectively generated development partition and an untouched confirmation
run whose assignment seed and outcome location are sealed before estimator tuning. Confirmation must
include both regular and singular-design blocks and must be released even if the method fails.

### 5.5 Independent replication

At least one separately governed apparatus must implement the same declared gain action and expose the
same signed coupling target. A second run on another chamber controlled by the same project is useful
robustness evidence but does not alone meet the independent-lineage requirement. The ESS cryoplant is
not a substitute because its interventions, truth, and observation model differ.

### 5.6 Cost and stop rules

Remote Lab price, access latency, run limits, and permissible controller modifications are unknown;
therefore no resource estimate is defensible. Stop before any outreach, purchase, protocol submission,
dataset download, or method implementation. Even if a complete chamber asset becomes available, do
not activate experiments until the separate theorem package supplies arbitrary-support identification,
a matching estimator/upper bound, and uniform inference through sign nonidentification.

## 6. Decision and exact trigger boundary

**Decision:** retain Causal Chambers as a `partial_capability` lead. It is the first audited source in
this branch that combines a real physical plant, a documented feedback cycle, public experiment
software, and in-principle programmable link strength. It removes no current route blocker because the
released experiments do not instantiate the frozen gain intervention or quantitative truth, and no
independent same-estimand confirmation system is available.

Re-audit only after a public, immutable release or an independently supplied written contract exposes
all of the following before outcomes are opened:

1. the exact feedback assignment and independently varied gain schedule, with a non-degenerate
   relative-gain design;
2. signed quantitative coupling truth or an external calibration with frozen uncertainty;
3. complete controller/plant prestate and event lifecycle sufficient to distinguish a gain change
   from setpoint, lag, saturation, or innovation drift;
4. reusable publication and redistribution rights plus an untouched confirmation partition; and
5. a separately governed same-estimand physical replication.

A new dataset name, more samples under the fixed PID, a binary setpoint intervention, access-request
approval, or two devices under one project is not a trigger. There is no machine card, no experiment
plan, and no justified use of the A800 or either V100 for this branch.
