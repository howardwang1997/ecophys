---
name: project-eurusd-weak-ofi
description: "eurusd EcoMD order-flow |rho| response to the kick is genuinely WEAK (~0.07) but seed-STABLE/reproducible (= production); NOT model-unstable (an earlier 'instability' read was a states-diff diagnostic bug). |rho| signature = robust seed-stable 4-asset effect (spx/ndx/gold/btc 0.66-0.70). Model `ofi` = post-kick coordinated-flow RESPONSE, not the imposed kick."
metadata:
  type: project
---

**Critical interpretation correction (2026-08-09).** EcoMD's logged `ofi` is the latent-agent
coordination ratio `sum(dpos) / sum(abs(dpos))`. It is **not** Cont--Kukanov--Stoikov limit-order-book
OFI, which is constructed from best-quote depth changes and trades. The stable response documented
below remains a valid model-internal quantity, but it must not be described as empirical OFI or directly
matched to the real-L2 observable in exp124 without a specified and validated observation operator.
Consequently, a positive real-L2 memory result alone would not validate an EcoMD prediction.

**Resolved 2026-06-24 (8-card H20, exp-123 `concave_d050_seed0` checkpoints, measuring the model's own
`ofi` = `traj.ofi_np()`, the quantity production logs).**

Seed-stability of the post-kick |ρ| spike (4 rollout seeds each, mag6):

| asset | mean \|ρ\| | cross-seed spread |
|---|---|---|
| spx | 0.697 | 0.002 |
| ndx | 0.659 | 0.005 |
| gold | 0.685 | 0.008 |
| btcusdt | 0.686 | 0.004 |
| **eurusd** | **0.071** | **0.017** |

- **All five assets are seed-STABLE.** spx/ndx/gold/btc strong (~0.66–0.70, spread <0.01); **eurusd
  genuinely weak (~0.07) but stable**, matching production (0.069). So the order-flow |ρ| signature is a
  **robust, seed-stable four-asset effect**; eurusd is a genuine weak-but-stable case, **not** instability
  and **not** "FX sub-threshold."
- **Correction of a 2026-06-24 earlier (wrong) read.** I first reported eurusd |ρ| as "model-unstable
  (~0.6 fresh vs 0.07 production, 50× gross-flow variance across seeds)." That was a **diagnostic bug**:
  I summed **outer-step state diffs** Σ(s_t−s_{t-1})/Σ|·|, which **include the imposed kick jump** (the
  kick is applied to `s` at the *start* of the step, `ecomd.py:790`, before forces). The model's `ofi`
  (`price_formation.py:463`, `dpos=pos_next−pos_prev` with `pos_prev` = the *kicked* `s`) measures the
  **post-kick coordinated FLOW RESPONSE**, excluding the kick itself. So states-diff (0.61) ≠ model ofi
  (0.07); only the model ofi is meaningful and it is stable.
- **Mechanism (the honest "why eurusd is weak"):** equities/NASDAQ/gold/crypto translate the coordinated
  kick into a coordinated order-flow response (|ρ|~0.7); the **low-volatility FX model does not** (|ρ|~0.07)
  — a stable, asset-dependent property of the trained dynamics. (eurusd's *tail* still revives at kick12;
  that part was always real.)

**How to apply.** Report the |ρ| order-flow signature as a **robust four-asset result** (eurusd a stable
weak case — say "marginal but equally stable ≈0.07", NOT "unstable"/"sub-threshold"). To measure |ρ| use
the model's `ofi` (post-kick flow response), **never** outer-step Σ state-diff (includes the kick).
Done in NCS/ML4PS/GenAI drafts + figure (commits after b4fa169e6, which had the wrong "unstable" wording).
Related: [[project_burnin_artifact]], [[project-h20-fleet-scheduling]] (trajectories on GPFS
`/AI4S/Users/howardwang/h204/ecophys/`).
