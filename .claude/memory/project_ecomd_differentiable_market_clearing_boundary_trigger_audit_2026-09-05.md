---
name: EcoMD differentiable market-clearing boundary trigger audit
description: A new differentiable DC-OPF planning paper provides a clean two-boundary stress case, but its support lag is caused by the outer fixed-charge relaxation and every obvious repair reduces to established differentiable or mixed-integer optimization.
type: project
---

# EcoMD differentiable market-clearing boundary trigger audit

- Mungo, Scholl, and Quera-Bofarull (arXiv:2609.02646v1, 2026-09-02) differentiate a
  convex DC-OPF clear and optimize a 50 MW allocation over six candidate buses, 36 operating
  states, and two small synthetic network instances. They compare with enumeration of all 63
  nonempty site supports.
- Keep two boundaries distinct. The **inner boundary** changes line/offer active sets and can make
  the LMP Jacobian nonsmooth. The **outer boundary** changes the built-site support under an exact
  fixed charge. These are not one failure mechanism.
- The paper's 1,944 random directional checks require a stable active-set stencil. It additionally
  scans 18 transitions per topology and performs one-sided checks; a narrow GeoDe offer regime has
  maximum relative discrepancy 0.334 at requested distance `1e-3`. These are honest numerical
  limits, not the cause of the main decision error.
- Appendix C directly attributes the late site closures to the outer smooth count and its terminal
  temperature: the relaxed objective shrinks the secondary site past the exact breakpoint, becomes
  bistable, and the trained paths follow that surrogate curve.
- Exact killer lemma: for fixed support `S`, the objective is `V_S + kappa |S|`; the fixed charge is
  constant and has zero continuous derivative on the support stratum. The breakpoint against `T`
  depends on the nonlocal comparison `V_S + kappa|S| = V_T + kappa|T|`. Perfect DC-OPF gradients
  cannot reveal an unvisited support's value.
- A trajectory-conditioned gradient/margin heat map is useful QA but not an ICLR residual. PEAR and
  dQP occupy active-set/regret geometry; LPGD, perturbed optimizers, and Identity with Projection
  occupy surrogate backward repairs; differentiable feasibility-pump and primitive-direction work
  occupy relax/round and continuous-plus-discrete search; Mosaic already couples finite-difference
  gradient tests with end-to-end optimization benchmarks.
- Distinct forward and backward site-count temperatures are a declared heuristic, not a derivative
  of the exact physical objective. The prior off-state-extension witness remains binding: exact
  forward agreement cannot canonize a surrogate backward rule.
- Adding EcoMD changes the DC-OPF/support truth contract and supplies no real assigned
  counterfactual. A factorial attribution cube would repeat Paper D's logic and a mechanism the new
  source already isolated, so more networks, seeds or GPUs cannot create novelty.
- Decision: `not_trigger`, zero blockers removed, no candidate harvesting, outcome access,
  implementation, simulation, SSH or GPU. Re-entry requires a cross-boundary decision-risk or
  abstention theorem with a matching lower bound, irreducible to the named parents, exact decision
  truth on two independent systems, and a market-native bridge.
