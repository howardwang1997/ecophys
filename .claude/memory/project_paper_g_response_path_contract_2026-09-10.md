# Paper G response-path contract — 2026-09-10

PRIVATE / INTERNAL. Public evidence eligible:false. Decision:not_trigger.
Original objective remains active and unachieved; no candidate/cycle/card.

Formal: `papers/proposal/ecomd_paper_g_response_path_contract_2026-09-10.md`.
Contract: `research/paper_g/response_path_contract_20260910.yaml`.
Manifest: `research/paper_g/response_path_source_manifest_20260910.json`.

- Previous turn progress revalidated: graph293/274/1374,evidence962,
  triggers128/qualified0. This turn completes its response-method audit.
- Existing Zou/Lie/Marzouk2603.20467v2 explicitly includes kinetic Langevin
  in Remark3. Its overdamped numerical examples do not leave an inertial
  theorem gap. Lemma7/Proposition11 need moments and a reference moment bound;
  gradient regularity and empirical-estimator validity are separate conditions.
  New scoped record extends an existing source, not a newly discovered paper.
- BKR1906.09282v4 Theorem1 and AppendixD.3 give direct observable/stopped-
  entropy parents with noise-range drift changes and martingale hypotheses.
  KGK2303.14696v1 Table1/IV–V/A.1–A.2 already analyze integrator-dependent
  phase-space support and path reweighting. No generic method novelty remains.
- Paper-only kinetic contract: common initial state and fixed bath, r=F1-F0,
  KL(P1_H||P0_H)=E1 integral|r|^2/(4*gamma*Tb)dt under Girsanov conditions.
  Bounded r supplies a finite-horizon envelope. Training-set RMSE does not
  supply the required occupation norm or a finite-sample confidence bound.
- Standard hit-probability/capped-time bounds retained as controls only.
  **Do not substitute capped times for the target response:** Bigiv6 4.4/4.6
  measures velocity-correlation spectra and the low-frequency diffusion limit.
  Velocity products need suitable moments; infinite-lag spectra need a decay
  envelope and appropriate stationary preparation. Neither is qualified.
- Explicit bounded-force support control: F0=-k*q,F1=F0+epsilon*tanh(q),
  k>0,epsilon!=0. Continuous laws have finite entropy on fixed horizons.
  BAOAB supports obey vprime+v-2*(qprime-q)/h=h*(F(qprime)-F(q))/2.
  Their intersection requires qprime=q, probability0, so the conditional
  one-step full phase-space laws are singular for every h>0. This is a known
  splitting mechanism instantiated by hand, not a new nonconservative effect.
- ABOBA has force-independent support qprime=q+h*(v+vprime)/2 and conditional
  Gaussian KL h^2*(1+c)^2*r(qmid)^2/[8*Tb*(1-c^2)],c=exp(-gamma*h).
  Exactness is for that kernel, not continuum response. No blanket extension
  to position-only or coarsely saved data, all force pairs or software behavior.
- Distinct constant gamma*Tb gives distinct continuous velocity quadratic
  variation and singular full path laws. Same covariance only removes that
  obstruction; friction changes still need analysis. Forward-model KL is
  separate from physical entropy production and prior mean residual work.
- **Stop generic kinetic/KL-loss/stopped-entropy/reweighting/integrator-support
  expansion.** Next check a matched primary mechanism prediction for the
  Bigi liquid-water velocity spectrum/diffusion response under the same force,
  bath,preparation and conditioning. Different estimands are not a disagreement.
  No qualified trigger means no relabelled candidate harvesting.
- Three scoped source records,six locators,four reusable controls,one audit;
  graph293/274/1380,evidence965,triggers129/qualified0. Search21cycles/
  133raw/0cards unchanged. No route status or named blocker changed.
- Three article HTML caches; two new selected primary works and two reused
  readings. No source-code/model/array/archive payload, notebook, numerical/
  symbolic scientific execution, simulation,GPU/SSH,outreach or publication.
  Paper D evidence and permissions excluded. Records remain private.
- Verification receipt:
  `logs/private/paper_g_response_path_20260910_verification.md`.
