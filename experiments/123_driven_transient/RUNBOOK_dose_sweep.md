# exp 123 — full dose sweep for the 4 non-SPX assets (RUNBOOK)

**Goal.** Today the dose–response figure (`fig_transient` panel b) is one full S&P 500 sweep plus a few
scattered points for ndx/gold/btc/eurusd. This run gives each of the four a full sweep so the figure
becomes **five real sigmoid curves** instead of "SPX + points". Nothing new to write — it reuses the
tested `scripts/gpu_exp123_stage1.sh worker`/`eval` path; arbitrary `kick<float>` arms already work
(`run_arm` passes `--shock-mag ${arm#kick}`).

**Dose grid** (matches the existing SPX arms):
```
DOSES="kick0.05 kick0.1 kick0.2 kick0.3 kick0.5 kick1 kick2 kick3 kick6 kick12"
```
EUR/USD has a higher threshold (it only revived at mag 12 in Stage 1), so extend its high end:
```
DOSES_FX="kick0.5 kick1 kick2 kick3 kick6 kick8 kick12 kick16 kick20"
```

---

## 1. Pre-flight (each box)
```bash
git fetch --all && git checkout feature/paper-a-figures-voice && git pull
bash scripts/h20_pull_from_r2.sh            # 5 assets' parquet present
```
Checkpoints were synced to R2 + deleted, so the driver reuse-or-retrains (1 seed; fine for a structural
dose curve). To drive the *exact* calibrated model, scp each asset's `concave_d050/checkpoint.pt` into
its `experiments/{113_gabaix_solve,114_concave_confirm}/results_*` dir first.

## 2. Launch — one asset per box, in parallel
```bash
# h20_1 (8-card): NASDAQ, full grid
ASSET=ndx     ARMS="control kick0.05 kick0.1 kick0.2 kick0.3 kick0.5 kick1 kick2 kick3 kick6 kick12" \
  NPROC=8 N_REAL=8 SEED_BASE=30000 OUT_TAG=ds bash scripts/gpu_exp123_stage1.sh worker

# h20_2 (2-card): gold, full grid
ASSET=gold    ARMS="control kick0.05 kick0.1 kick0.2 kick0.3 kick0.5 kick1 kick2 kick3 kick6 kick12" \
  NPROC=2 N_REAL=8 SEED_BASE=31000 OUT_TAG=ds bash scripts/gpu_exp123_stage1.sh worker

# h20_3 (2-card): BTC, full grid
ASSET=btcusdt ARMS="control kick0.05 kick0.1 kick0.2 kick0.3 kick0.5 kick1 kick2 kick3 kick6 kick12" \
  NPROC=2 N_REAL=8 SEED_BASE=32000 OUT_TAG=ds bash scripts/gpu_exp123_stage1.sh worker

# h20_1 again after ndx (or any free box): EUR/USD, extended high-end grid
ASSET=eurusd  ARMS="control kick0.5 kick1 kick2 kick3 kick6 kick8 kick12 kick16 kick20" \
  NPROC=8 N_REAL=8 SEED_BASE=33000 OUT_TAG=ds bash scripts/gpu_exp123_stage1.sh worker
```
Inference is cheap; cost is dominated by a one-off retrain per asset if the checkpoint is not cached
(~1 h/asset). Budget ≈ 3–5 h wall-clock if retraining, ≈1 h if cached. (Rates per
[[h20-fleet-scheduling-calibration]] — plan from the measured 62 min/cfg/card, not my estimate.)

## 3. Eval (on the 8-card box, after rsync-ing the 2-card boxes' `results_*` back)
```bash
bash scripts/gpu_exp123_stage1.sh eval        # emits windowed_hill_report.json per new arm
```
Sanity per asset: control α_ED ≥ 4 in [500,3000); kick* dips toward ≈0.5 and **deepens with dose**;
recovery back to ≥4. If an asset never dips even at its top dose, note it (asset-dependent threshold) —
the figure handles missing/threshold assets gracefully.

## 4. Sync results back + regenerate the figure (Mac)
```bash
# push the new results_{ndx,gold,btcusdt,eurusd}_kick*/windowed_hill_report.json to R2, pull on Mac, then:
conda run -n ecophys python papers/paper_a_methods/shared/make_figures.py
# fig_transient panel (b) auto-draws a connected curve for any asset with >=4 doses (else markers),
# so it upgrades to five curves with no code change. Redistribute:
for d in ncs workshops/ml4ps workshops/genai_finance; do
  cp papers/paper_a_methods/shared/figures/fig_transient.{png,pdf} papers/paper_a_methods/$d/figures/
done
```

## 5. Paper edits after it lands
- `fig_transient` caption (all three papers): "S&P 500 sweep plus four assets as points" → "five-asset
  sigmoid dose–response", keeping the asset-dependent-threshold sentence (FX rightmost).
- The "four of five assets" OFI-generalization claim is unaffected (that is the OFI signature, a
  separate panel); only the **tail** dose–response becomes five full curves.
