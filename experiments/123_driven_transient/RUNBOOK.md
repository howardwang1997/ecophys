# exp 123 driven-transient — Stage-1 RUNBOOK (one page)

**Decides one thing:** is the model's heavy tail a **non-equilibrium driven transient** (P → positive
frontier paper) or a **t=0 startup artifact** (A → no paper)? Drive a steady state out of equilibrium
with a state_kick and watch whether the cube-law tail **revives then relaxes** like the burn-in.
Frozen spec + thresholds: `PREREG_2026-06-18.md`. Rationale: `DESIGN.md`. Branch: `feature/exp113-gabaix-solve`.

---

## 1. Pre-flight (on EACH of the 3 boxes)
```bash
git fetch --all && git checkout feature/exp113-gabaix-solve && git pull
bash scripts/h20_pull_from_r2.sh            # 5 assets' parquet present
```
Checkpoints were synced to R2 + deleted → the driver **reuse-or-retrains** (1 seed; fine for this
structural question). To drive the *exact* model, scp `concave_d050/checkpoint.pt` into its
`experiments/{113_gabaix_solve,114_concave_confirm}/results_*` dir first.

## 2. Launch — pick ONE
**A. one command** (needs `scripts/machines.local.json` filled), on the 8-card box:
```bash
bash scripts/gpu_exp123_stage1.sh fanout
```
**B. one command per box** (robust):
```bash
# 8-card  — spx FULL (the decision)
ASSET=spx ARMS="control kick3 kick6 kick12" NPROC=8 N_REAL=4 SEED_BASE=10000 OUT_TAG=m1 bash scripts/gpu_exp123_stage1.sh worker
# 2-card #1 — ndx replication
ASSET=ndx ARMS="control kick6" NPROC=2 N_REAL=15 SEED_BASE=20000 OUT_TAG=m2 bash scripts/gpu_exp123_stage1.sh worker
# 2-card #2 — R1 magnitude
NPROC=2 bash scripts/gpu_exp123_stage1.sh r1
```
Cost ≈ **1.5–2.5 h** (inference is cheap; +~1 h/asset only if it must retrain).

## 3. Eval (after all finish; rsync the two 2-card boxes' `experiments/123_driven_transient/results_*` + `r1_*` back to the 8-card box)
```bash
bash scripts/gpu_exp123_stage1.sh eval
```
Emits, per arm, `windowed_hill_report.json` (α_ED(t)) **and** the R1 `r1_warmup_report.json`.

---

## 4. Read the verdict (spx; α low = fat, α≈3 = cube law, α≥4 = light)

| | look at | PASS |
|---|---|---|
| **H1** steady light | control, steps [500, 3000) | α_ED ≥ 4, CI lo > 2 |
| **H2** shock revives | kick3/6/12, after step 3000 | α_ED **dips ≤ 2**, CI excludes control, **deepens with dose 3→6→12** |
| **H3** transient | recovery (~step 7000) | α_ED back to ≥ 4 |
| **H4** = burn-in | vs the t<500 template | post-shock min α in 3/2 ± 0.5, τ within 2× |
| **H5** *(bonus)* transfer law | TEST window | α_ret ≈ α_raw/δ ≈ 2 (δ=0.5) |

**The load-bearing signal is H2: the α_ED dip that deepens with dose.** Present → physics. Absent → artifact.

## 5. Decision → next step

- **H1 ∧ H2 ∧ H3 ∧ H4 pass → (P) PHYSICS.** Positive frontier paper EARNED ("fat tails = non-equilibrium
  driven transient; stationary state is light; α=ζ/δ decomposes it"). **Next:** Stage-2 — other shock arms
  (news/liquidity) + dose-response figure + more assets; update [[paper-a-target-neurips-2027-problem-diagnose-solve-framing]].
- **H2 fails at every dose → (A) ARTIFACT.** Fall back to the diagnose-centered 3-paradigm frontier; the
  burn-in finding becomes a rigor/methods section, not the headline. ~1–2 runs total, then stop.
- **H2 passes but H4 fails → AMBIGUOUS.** Do **not** publish the unification; a mechanism study is owed first.

## 6. R1 (independent of the gate — write it up either way)
`r1_warmup_report.json`: does the concave cell's **standard hill** flip `IN-BAND (drop0) → TOO-THIN (drop50)`?
- **Flips** → the 5-asset concave "solve" is burn-in-held → say so (the honest correction).
- **Holds in-band** → concave survives warmup discard → the solve stands; contamination was tail-transfer-only.

## 7. Knobs (env vars on the driver)
`N_STEPS` (8000) · `T_SHOCK` (3000) · `FRAC` (0.10) · `W/STRIDE/KFRAC` (500/100/0.1) · `SEED` (0) ·
`FORCE_RETRAIN=1` (ignore any local ckpt) · `DRY_RUN=1` (echo only). Doses = the `kickN` arm names.

> Discipline ([[feedback_preregistration]], [[feedback_no_downgrade]]): thresholds are frozen in
> PREREG — no post-hoc widening; an ambiguous result is escalated, never narrated as a pass.
