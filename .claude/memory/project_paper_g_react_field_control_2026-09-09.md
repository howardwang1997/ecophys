# Paper G REACT physical-control truth preflight

PRIVATE / INTERNAL. Development material only.

Decision partial_capability;no blocker removed,no candidate/cycle/card.
REACT supplies a real wind-tunnel source lane connected to the neural-PDE
control work. Five source texts pinned at
e1fc212b5b3929890626b66824676afda12c2458 were read and hashed,never executed.
The selected arXiv2509.11002v2 text is dated May14,2026. Older Zenodo15801190
metadata is restricted with CC-BY-4.0 and no public file entries;the newer
paper points to20086963,whose independent access/version contract is not yet
qualified. Neither release identity nor raw-data conformance is claimed.

Reusable exact control: stable scalar plant dX=(-aX+bU)dt+sigma*dW,
feedback U=-kX,q=bk,r=a+q,stationary variance V=sigma²/(2r).
Replay U_R=-kZ from a stationary feedback copy driven independently gives
V_R=sigma²/(2a)+q²V/[a(a+r)]. Both action processes have the same entire
stationary Gaussian law,but V<V0<V_R. The state-action cross moment changes
from -kV to kqV/(a+r). This is classical covariance algebra,not a novel
nonlinear mechanism or a measured failure of the external controller.

With driving-noise correlation rho,the exact gap is
V_R,rho-V=q*sigma²*(1-rho)/[a(a+r)]. Same initial state and same disturbance
with the same feedback-generated action tape give identical finite-time paths.
Action marginal matching does not fix its coupling with the controlled state.

Field interpretation: run-level randomized policy effects need not demand full
turbulent-state replay. Random physical initial conditions do not randomize
treatment order; logged feedback histories alone do not identify arbitrary
off-policy effects. Keep electrical actuator consumption separate from abstract
fluid power and action penalties. Same-facility repeatability is not independent
truth. Generic history/control and variance-cost contribution blockers remain.

Next: qualify a needed assignment/clock/rights asset and a distinct contribution
before re-entry. Stop collecting this source's metadata without that trigger.
No outcomes,scientific execution,hardware contact or compute authorized.

Formal: papers/proposal/ecomd_paper_g_react_field_control_preflight_2026-09-09.md.
Contract: research/paper_g/react_field_control_preflight_20260909.yaml.
Manifest: research/paper_g/react_field_source_manifest_20260909.json.

Verified 2026-09-09T11:04:50Z: graph293 /edges274 /locators1287;evidence908;
re-entry116 /qualified0;cycles21 /raw133 /cards0 unchanged. Scoped canonical
validation,all six cached source/metadata hashes,source/contract/trigger parity,
18 existing tests and git diff --check passed. Search,protocol and forecast
bytes unchanged. Receipt:`logs/private/paper_g_react_field_20260909_verification.md`.
