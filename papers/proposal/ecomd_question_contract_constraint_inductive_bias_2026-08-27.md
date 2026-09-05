# D-3 question contract: do physical conservation constraints buy generalization, or launder error?

Date: 2026-08-27

Status: **out-of-scope paper-only question contract under the standing PI scope amendment; not a
topic card; no implementation, compute, dataset purchase, or outcome access authorized; supersedes
the "shallow screening" method of pre-study rounds 1--4**

Method note: this contract replaces breadth-first keyword screening with the repo's own D-3
standard (native object, rival explanations sharing one estimand, one discriminating result,
positive and null value). The 15-work evidence manifest (D-2) is deliberately not opened yet;
it follows only if this contract survives PI review.

## Native scientific object

A learned simulator `f_θ` of a dynamical system with an exact known invariant `C` (conserved
mass / energy / momentum), trained on in-distribution (ID) trajectories, evaluated on
out-of-distribution (OOD) initial conditions, forcings, or parameter regimes. The invariant is
imposed by one of three mechanism levels:

1. **hard architectural constraint** (the architecture can only express C-conserving maps);
2. **soft loss penalty** (constraint residual added to the training objective);
3. **post-hoc projection** (unconstrained model plus conservative correction).

The object is *not* a market object; this is the out-of-scope amendment.

## The question

**When the learned simulator is forced to conserve exactly, does its OOD dynamical error fall,
or does the error instead migrate into C-conserving-but-dynamically-wrong channels?**

## Rival explanations (same estimand: OOD state error under matched ID error)

- **H1 constraint-as-inductive-bias.** Restricting the hypothesis class to C-conserving maps
  removes a subset of wrong models that includes the OOD-failing ones. Prediction: at matched ID
  error, OOD error strictly decreases; the reduction persists across mechanism levels.
- **H2 constraint-as-error-laundering.** The optimizer meets the constraint by inventing
  spurious C-conserving transport (redistribution channels that carry no physical flux).
  Prediction: the non-conservative component of OOD error shrinks, but the conservative-but-wrong
  component grows by a compensating amount; net OOD error unchanged or worse.
- **H3 mechanism-dependent sign.** The outcome is governed by the mechanism level: hard
  constraints behave as H1, soft penalties as H2 (because a soft residual is trivially
  satisfiable by conservative wrong flows), and projections add a bounded bias with no
  generalization claim at all.

These share one estimand, one metric family, and one conditioning set; they make opposite
sign predictions on the *decomposed* OOD error.

## Discriminating observable

Decompose OOD error into (a) the component removable by the optimal C-preserving correction
(= conservative-channel error) and (b) the residual violation of `C` (= non-conservative
error), measured at **matched in-distribution error and matched training budget** — the control
the existing per-paper reports mostly omit. H1 predicts (b)→0 with (a) reduced; H2 predicts
(b)→0 with (a) inflated; H3 predicts the split by mechanism level. One number adjudicates:
the change in total OOD error at matched ID fidelity, read jointly with the decomposition.

## Why both answers matter

- **H1 confirmed:** first coordinated evidence that conservation constraints are a trustworthy
  OOD guarantee across simulator families — directly changes practice in ML-for-PDE/climate/
  materials, where constraints are now added on faith.
- **H2/H3 confirmed:** a cautionary mechanism result ("constraint satisfaction is not dynamical
  accuracy; soft penalties launder error into conservative channels") with an actionable
  prescription (measure the decomposition, not the residual). A clean negative is publishable
  because the practice it audits is widespread and load-bearing.

## Cheapest falsifying sequence (repo rule: exact toy before scale)

1. **One-system toy (CPU/1-GPU days):** a system where the decomposition is analytically
   tractable — e.g., discrete advection or a Hamiltonian pair with known energy — trained at
   three mechanism levels. If the conservative-channel decomposition shows no measurable H2
   signature even in the most favorable toy, H2 is starved early and the contract narrows to
   H1-vs-H3.
2. **Three-family audit (2×V100, weeks, public data only):** e.g., MeshGraphNets-class mesh
   dynamics, PDEBench-class PDE surrogates, and one physics-identity-rich JAX/diffrax system;
   ≥5 seeds per cell (repo seed-lottery rule), pre-registered decomposition and decision rule.
3. Only after (2) shows a stable sign: any external/real-data bridge or venue escalation.

## Honest prior (uncalibrated reviewer estimate)

Survives a rigorous D-2 manifest audit: ~60% (the nearest neighbors — constraint-accuracy
tradeoff reports in the climate/PINN literature — document fragments but not the matched-ID,
decomposed, multi-family adjudication; the manifest must verify this precisely). Conditional
on a crisp replicated mechanism finding: NeurIPS/ICML-main plausible (15--25%), TMLR floor,
NMI only with a broad cross-system plus real-physics bridge (5--10%). If the toy starves H2
and the audit reduces to "constraints help, monotonically," the paper weakens to a benchmark
note — that degradation path is stated now, before any evidence is collected.

## What this contract does not do

No topic-card status, no cycle, no forecast entry, no compute authorization. Step 1 is a
bounded next action requiring a separate PI authorization before any run.
