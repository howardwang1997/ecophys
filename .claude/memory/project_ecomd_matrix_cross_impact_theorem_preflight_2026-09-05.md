---
name: EcoMD nonlinear matrix cross-impact theorem preflight
description: Universal safety over all convex-gradient readouts collapses an integrable matrix convolution to one scalar completely-positive kernel times identity. The result is a useful killer lemma but a short corollary of matrix positive type, scalar complete positivity and MIMO Zames-Falb; recent cross-impact theory and learning directly occupy the obvious exits.
type: project
---

# EcoMD nonlinear matrix cross-impact theorem preflight — 2026-09-05

- For `D=G*v` and `cost=int v^T grad F(D)`, require global all-input safety for every differentiable
  convex `F` with `grad F(0)=0`. Under an integrable causal matrix kernel, this holds exactly when
  `G=g I`, where `g=0` or `g` is a globally completely-positive scalar kernel.
- Necessity already follows from rank-one quadratic potentials. Matrix positive type requires
  `Herm(H Ghat)>=0` for every `H>=0`. Taking `H=uu^T` makes every real `u` a left eigenvector of
  `Ghat`; pairwise sums force one eigenvalue, hence `Ghat=z I` and `G=g I`. Restriction to one
  coordinate invokes Lee's scalar converse and forces complete positivity.
- Sufficiency is Lee's vector Bregman storage identity/Theorem 8.9 with one scalar complementary
  measure and `M=I`. It is also the convex-potential branch of Safonov--Kulkarni's MIMO
  Zames--Falb construction.
- Minimal separator: `G=diag(exp(-t),exp(-2t))`,
  `F(x)=0.5*(x1+x2)^2`, and constant `v=(1,-3/2)` on `[0,T]` give
  `C(T)=-T/8+5/16-exp(-T)/2+3 exp(-2T)/16`; `C(3)=-0.086928768151`. Each diagonal kernel is
  individually safe, but heterogeneous decay is unsafe under a coupled convex readout. Vanishing
  tails permit finite round-trip closure.
- The statement survives simultaneous invertible changes of state/flow coordinates with the dual
  readout transform; scalar identity is similarity invariant. It is not created by asset-unit
  choice.
- This is not an ICLR core theorem: it is a short corollary of Lee's linear matrix boundary plus
  scalar converse and classical MIMO Zames--Falb positivity preservation. `g_theta I + ICNN` is a
  component composition and loses heterogeneous asset memory by construction.
- Direct exits are occupied. Hey--Neuman--Tuschmann (arXiv:2510.06879) already learn concave
  multi-asset propagators offline with confidence bounds, shape projection and proprietary/public
  experiments. *Concave Cross Impact* (SSRN:5046242, revised 2026-07-18) already imposes
  factor-direction nonlinear geometry, performs metaorder calibration and advertises a new
  dynamically coupled impact-state treatment. Alfonsi--Schied--Kloeck cover matrix-valued positive
  type and commuting kernels.
- Predictive cross-impact on passive correlated flow, causal response to an assigned trade and
  universal no-manipulation are not one estimand. Their different conclusions do not form a valid
  unresolved fork without an assignment/interference contract.
- Decision: kill the universal-convex-readout matrix branch; retain the theorem and explicit
  separator as QA assets. A fixed market-native readout with genuinely noncommuting memory or the
  singular complementary-inverse branch may be re-audited only after a theorem exceeds Lee's
  conic/state-space certificates, MIMO IQC/passivity and current cross-impact work and supplies a
  causal truth contract.
- No candidate, implementation, outcome access, SSH or GPU work is authorized. All three workers
  remain idle.
