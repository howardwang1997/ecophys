# Paper G: REACT physical-control source preflight

PRIVATE / INTERNAL. Development source assessment and elementary mathematical
controls; not public research evidence or a new topic. Started 2026-09-09
10:43:42 UTC. Decision: `partial_capability`; no recorded blocker removed.

The repository's neural-PDE program needs a physical intervention bridge with
an identifiable response. This assessment asks whether a named external asset
supplies that capability. It does not open another cycle in the saturated
history-response family. Existing generic-method and variance-cost contribution
blockers remain binding.

## Primary source and version boundaries

[Zhang et al., arXiv2509.11002v2](https://arxiv.org/html/2509.11002v2), dated
14 May 2026, describes real wind-tunnel control with rear flaps, pressure sensing,
force measurement and planar PIV. Selected reading covers sections 2–4,
8.6–8.10, 8.12–8.14 and availability. It reports a 100 Hz hardware loop,
previous-observation inference followed by timed actuation and sensing, and
electrically measured actuation cost. Its replay test uses a recorded action
sequence in a separate run from another random initial condition. Its reported
performance evaluation uses baseline-then-control runs; this is not a declared
randomized order. The current data citation is
[Zenodo20086963](https://doi.org/10.5281/zenodo.20086963). No outcome replication,
final journal publication, complete-state reset or release identity is claimed.

The [REACT source](https://github.com/RigasLab/REACT/tree/e1fc212b5b3929890626b66824676afda12c2458)
is pinned at `e1fc212b5b3929890626b66824676afda12c2458`. Five selected text
files, including the Apache-2.0 license, describe a physical UDP environment,
online episodic histories and offline replay-buffer use. They were read and
hashed, never imported. This is a selected interface snapshot, not a complete
software/dependency archive or demonstrated identity with the paper's runs.

The repository links a different [official data record15801190](https://zenodo.org/records/15801190).
Its downloaded metadata declares restricted access and CC-BY-4.0, with no
public file entries in that response. The description names synchronized
64-channel pressure and 26-channel auxiliary arrays, including forces, flap
power and actions, plus closed-loop/replay and PIV folders. This is descriptive
schema, not file conformance or confirmed access. Record20086963's independent
access/file/version contract remains unverified; the older record cannot stand
in for it. Retrieval operations belong only in the private verification receipt.

## Exact feedback-versus-replay control

This is classical linear stochastic-control algebra, not a novelty claim or
a model fitted to the wind tunnel. Let a,b,k,sigma be strictly positive,
q=bk, r=a+q. The native scalar plant is

\[
dX_t=(-aX_t+bU_t)dt+\sigma dW_t.
\]

Under feedback U=-kX, its stationary law is Ornstein–Uhlenbeck with
V=Var(X)=sigma²/(2r). The uncontrolled stationary variance is
V0=sigma²/(2a).

Generate a recorded tape from a stationary copy Z:

\[
dZ_t=-rZ_tdt+\sigma dB_t,\qquad U_t^{R}=-kZ_t,
\qquad dY_t=(-aY_t-qZ_t)dt+\sigma dW_t.
\]

First take B and W independent and the joint (Y,Z) process stationary, as
defined by stable integrals over the infinite past. This removes a transient
initialization explanation. The feedback and replay action processes have the
same entire stationary Gaussian law, with covariance
k²V exp(-r|t-s|). This is stronger than matching RMS or a single spectrum bin.
Their coupling with the controlled plant is different.

Itô covariance balance gives

\[
0=-(a+r)C-qV,\quad C=\operatorname{Cov}(Y,Z)
 =-\frac{qV}{a+r},
\]
\[
0=-2aV_R-2qC+\sigma^2,\qquad
V_R=\frac{\sigma^2}{2a}+\frac{q^2V}{a(a+r)}.
\]

Consequently V < V0 < VR. The benefit of feedback over independent replay is

\[
V_R-V=\frac{q\sigma^2}{a(a+r)}>0.
\]

The instantaneous quadratic-state energy transfer b E[state × action]
also changes: E[XU]=-kV, whereas E[YU^R]=kqV/(a+r)>0.
The action-only quadratic cost is identical. This abstract transfer is not
the wind-tunnel actuator's electrical consumption, and neither quantity is
universally an action-norm penalty.

A second control makes the disturbance coupling explicit. Set
d<B,W>_t=rho dt, rho in [-1,1]. The same balances now yield

\[
C_\rho=\frac{-qV+\rho\sigma^2}{a+r},\qquad
V_{R,\rho}-V=\frac{q\sigma^2(1-\rho)}{a(a+r)}.
\]

At rho=1 the stationary replay equals the feedback process. More generally,
for finite-time paths, replaying the tape generated from the very same initial
state and the very same disturbance realization gives Y=X by pathwise
uniqueness. With k=0 both policies are identical. These are exact nulls;
independent replay is the rho=0 contrast. Holding the action's marginal law
fixed does not hold its joint law with the plant or disturbances fixed.

This control supports a narrow inference: a feedback/replay difference need
not require nonlinear rephasing, a particular instability mechanism, learning,
or a specific neural architecture. It does not refute any separate mechanism
evidence in REACT, nor show that the published policy is equivalent to this
linear controller. Its scientific use here is a development calibration control.

## Truth and intervention contract

For a future field comparison, freeze a finite physical horizon T, facility
and operating condition c, policy pi and tape-generator distribution G.
Define J as integrated aerodynamic saving minus measured electrical actuator
consumption, with an explicit baseline convention. A potential target is
E[J(pi)|c] - E[J(replay from G)|c] across assigned runs. This target differs
from a pathwise derivative, an impulse response at a complete flow state, and
the value of an arbitrary unseen policy inferred from logged feedback data.
The present source assessment qualifies none of those field estimates.

Necessary identification conditions depend on that target:

- For a run-level average policy contrast, valid randomized or justified
  exchangeable assignment can suffice without complete turbulent-state resets.
  Record run/block IDs, assignment probabilities or the alternative identifying
  assumptions, operating conditions, policy/tape origin, washout and carryover.
  Random physical initial conditions alone do not randomize treatment order.
- For off-policy identification, specify behavior-policy versions and histories,
  action support and the assumptions controlling sequential confounding.
  A file of observed actions and rewards alone is not that contract.
- For deterministic replay or a pathwise response, additionally require the
  relevant complete initial state, driving disturbances, policy hidden state,
  observation/filter state, actuator dynamics, action application clock and
  system dynamics. Partial pressure/PIV observations are not automatically such
  a checkpoint. Do not impose this stronger contract on ordinary randomized ITT.

The lifecycle record must resolve sensor sampling and inference order, action
command versus applied angle, calibration and units, physical timestamps and
missing/late-message handling, episode/baseline boundaries, policy updates,
termination, reset/washout and acquisition alignment. This is a requirements
list, not a claim that an inspected implementation malfunctioned.

Selected root code rights do not establish hardware, dependencies, data or
derived-release rights. No new participant or facility work is contemplated.
All inspected text and published results are development material. No untouched
whole-source confirmation partition or independent same-target replication is
qualified. Several runs from one facility can estimate repeatability; they do
not by themselves supply independent physical truth or research lineages.

The current cost is five source texts, one metadata document, selected primary
reading and paper algebra: zero solver steps or raw outcome files. No sample
size or precision is certified by the formulas. Any later field design needs
a physical effect threshold, run-level variance and dependence assumptions,
power/precision, actuator and facility budgets. A new method also needs the
same estimand, access and cost matched to established control/estimation baselines.

Stop this preflight at partial capability. Revisit only when the newer release
supplies the needed assignment/clock/rights contract and a distinct contribution
or matched primary disagreement removes an existing blocker. Generic feedback
benefit, architecture replacement, elementary covariance balance or additional
metadata cannot reopen the route. No question harvest, new cycle, forecast,
machine card, scientific execution or outcome access follows from this record.

Contract and provenance:
`research/paper_g/react_field_control_preflight_20260909.yaml` and
`research/paper_g/react_field_source_manifest_20260909.json`.
