# Phase 0 — burn-in blast-radius verdict (Mac, no GPU, 2026-06-18)

**Question.** Is the ζ_ED burn-in contamination (`burnin_artifact_finding_2026-06-18.md`)
**confined** to the tail-transfer derivation, or does it reach the **standard 11-fact scoring**
that underwrites the whole "EcoMD fat-tail overshoot / concave-impact solve / Pareto ceiling"
narrative?

**Verdict: PROJECT-WIDE on the `hill_tail_index` fact (and tail-adjacent claims).** The standard
scoring pipeline computes Hill on a **burn-in-inclusive** per-step return series — the same
contamination mechanism the ζ_ED probe found. Confined-to-tail-transfer is **rejected**.

This is a code-path + direction verdict (high confidence). The exact per-cell magnitude of the
steady-state shift is **not** measured here (needs a GPU re-run with `--save-trajectory` + warmup
discard = R1); direction is certain, magnitude is predicted.

---

## Evidence

### D-A. The standard scoring is burn-in-inclusive (code, decisive)

The full chain, verified on `feature/exp113-gabaix-solve`:

```
ecomd/inference/run_large.py:107   returns = traj.log_returns_np()[1:]   # full series; [1:] drops only the t=0 diff
ecomd/physics/observables.py:61    def log_returns_np: return self.log_returns…  # verbatim, no warmup drop
ecomd/inference/run_large.py:118   facts = compute_all(returns, …)
ecomd/eval/stylized_facts.py:732   _run("hill_tail_index", lambda: hill_tail_index(r, side="both"))
```

There is **no warmup discard anywhere in the standard inference→scoring path.** Every standard
`hill_tail_index` in the project (089–099 ceiling, exp 109/112 overshoot, exp 113/114 concave
solve, the δ-grid) is therefore computed on a series that includes the ~20-step equilibration
transient — exactly the quantity the ζ_ED finding showed to dominate the Hill estimate.

### D-B. The concave "solve" sits inside the blast zone (saved facts, n=30, 5 assets)

Standard-pipeline Hill at N=10 000, n=30 seeds (`experiments/114_concave_confirm`, band [2,4]):

| asset | baseline hill | concave_d045 | concave_d050 |
|---|---|---|---|
| btcusdt | 1.23 ± 0.34 | 3.26 ± 0.84 | 3.00 ± 0.75 |
| eurusd  | 1.31 ± 0.41 | 3.29 ± 0.76 | 3.22 ± 0.93 |
| gold    | 1.38 ± 0.42 | 3.42 ± 0.88 | 2.92 ± 0.90 |
| ndx     | 1.34 ± 0.40 | 3.39 ± 0.78 | 3.25 ± 0.89 |
| spx     | —           | 3.24 ± 1.02 | —           |

The headline solve = **baseline ≈1.3 (TOO-FAT) → concave ≈3.0–3.4 (IN-BAND)**, replicated 5
assets. But the ζ_ED finding's D1 table (spx, same simulator, warmup sweep) shows the in-band
concave Hill is **burn-in-held**:

| | drop=0 \|ret\|α | drop=50 \|ret\|α |
|---|---|---|
| baseline   | 2.77 | **8.4**  |
| concave_d050 | 3.42 | **11.5** |

Direction is unambiguous: **discarding warmup moves Hill UP (tails thinner).** Applied to the
standard cells, the prediction is:

- **baseline** ≈1.3 (too-fat) → moves up, likely **out of** the too-fat regime in steady state.
- **concave** ≈3.0–3.4 (in-band) → moves up **past 4**, i.e. steady-state concave cells become
  **TOO-THIN and FAIL the band.** The 5-asset "in-band solve" is very likely a burn-in artifact.

So the most recent win (exp 113/114, and this branch) is contaminated the same way as the
tail-transfer headline — not a separate, safe result.

### D-C. What is NOT resolved here

- **Per-cell magnitude.** The raw per-step return series is **not** saved in `inference_merged.json`
  (only computed facts), and there are **0 trajectory `.npz` on Mac** (gitignored, on H20). So the
  exact steady-state Hill per cell cannot be re-scored on Mac — that is R1 (GPU re-run of 114 with
  `--save-trajectory` + warmup discard).
- **Non-tail facts.** The same `[1:]` series feeds all 11 facts via `compute_all`, so autocorr /
  acf2 / leverage / dfa etc. are *also* computed burn-in-inclusive. They are far less sensitive to
  the few extreme transient points (Hill keys on the top order statistics; the others don't), so
  the expected shift is small — but **unverified.** Cheap add-on to R1: report all 11 facts at
  drop ∈ {0,50,200}.

---

## Consequence for the paper (updates the A/B/C ladder)

Phase 0 lands on the **"project-wide"** branch ⇒ the stationary stylized-fact framing cannot be
salvaged by a one-line fix; the heavy-tail story has to move to where the tail genuinely lives.
This is the trigger for the **driven-transient** reframe (`experiments/123_driven_transient/DESIGN.md`):
the positive frontier paper = *"market fat tails are a non-equilibrium / driven transient; the
stationary model is light-tailed."*

**What survives Phase 0 unchanged:** the lemma α=ζ/δ; the Pareto-bounded ceiling **structure**
(no 11/11 — removing wrongly-credited Hill passes only lowers scores, strengthening "can't reach
11/11"); the ABIDES daily comparison (close-to-close aggregation, burn-in washed out). **What
Phase 0 puts on the contaminated list:** the "hill≈1.3 fat-tail overshoot" claim, the concave
in-band "solve", the δ-grid Hill·δ "1.5", and the δ*≈0.5 selection insofar as it used a Hill-band
criterion.

**Next:** R1 (magnitude) + the driven-transient experiment (earns or kills the physics story).
Both are GPU; design doc specifies them.
