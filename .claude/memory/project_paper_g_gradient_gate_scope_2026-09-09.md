# Paper G gradient-reliability comparison and scope audit

PRIVATE / INTERNAL. Development evidence only.

Decision not_trigger;zero removed blockers or candidate harvesting. Onoda et al.
arXiv2604.18161v1(April20;official ICLR2026 venue confirmed) retains the
rare-gradient behavior in Suh et al.ICML2022. Better variance control on a
different task suite is not an opposite gradient prediction for one frozen
fluid-control problem. HydroGym's differentiable control does not change this.

Classical exact control: for Gaussian input and scalar f in Gaussian H1,
Vg+2*norm(E grad f)^2-2*Var(f)/sigma^2>=0. Subtract the linear/constant
projection and use Lehec2008 lemma2.3,refined Gaussian Poincare. Hermite deficit
contains only degrees>=3 with weights degree-2. Quadratics are null;cubic is
positive. Onoda's population inequality follows without a near-quadratic
restriction;this does not certify the estimated moments or a finite-batch gate.
Whitening gives the covariance-weighted form;keep sampling units consistent.

Finite-batch control: zero function and a smooth positive bump on(r-h,r+h),r>h,
yield identical value/derivative observations with probability(1-p)^N,while
their smoothed mean gradients differ by E[X*f(X)]/sigma^2>0. On that transcript
the scalar gate passes for both. Any discriminator on the fixed iid batch has
sum of errors at least(1-p)^N. Fixed-gap claims require explicit amplitude/tail
bounds;targeted queries and whole-function access are outside this control.
This is elementary support indistinguishability,not a novel minimax theorem,
source implementation finding or measured failure of a published controller.

Next: a distinct method needs a target/access/tail/precision/cost contract beyond
existing composite gradients. Population validity,empirical moment reliability
and gradient/controller quality are different requirements. No new cycle,
forecast,card,scientific implementation,raw outcomes or compute.

Formal: papers/proposal/ecomd_paper_g_gradient_gate_scope_audit_2026-09-09.md.
Contract: research/paper_g/gradient_gate_scope_audit_20260909.yaml.

Verified 2026-09-09T10:42:47Z: graph293 /edges274 /locators1281;evidence905;
re-entry115 /qualified0;cycles21 /raw133 /cards0 unchanged. Scoped canonical
validation,source/contract/trigger parity,18 existing tests and git diff --check
passed. Search,protocol and forecast bytes unchanged. Receipt:`logs/private/paper_g_gradient_gate_20260909_verification.md`.
