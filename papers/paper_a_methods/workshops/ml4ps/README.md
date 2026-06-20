# ML4PS workshop paper (EcoMD) — LaTeX project

NeurIPS Workshop on **Machine Learning and the Physical Sciences** (non-archival, ≤4pp, NeurIPS format).
Spine: `../ml4ps_spine.md`. Evidence map: `../README.md`. Sibling: `../genai_finance/` (the
generative-modeling angle — keep distinct).

## Build
```bash
cd papers/paper_a_methods/workshops/ml4ps
latexmk -pdf main.tex      # compiles with a NeurIPS-approximating fallback if neurips_2024.sty absent
```
For submission, drop the official `neurips_2024.sty`/`.bst` into this dir (`main.tex` auto-detects);
add `[final]` for camera-ready.

## Figures (regenerate fully from committed JSON — no gitignored data needed)
```bash
conda run -n ecophys python make_figures.py
```
- `figures/fig1_transient.pdf` — (left) order-flow tail $\alpha_{\mathrm{ED}}(t)$ dip-and-recover
  (control vs coherent shock) with the exp-relaxation fit ($\tau\!\approx\!240$); (right) the sigmoid
  dose-response. Data: `results_spx_{control,kick*}/windowed_hill_report.json`, `tau_report_spx.json`.
- `figures/fig2_mech_boundary.pdf` — (a) Hill vs warm-up discard; (b) OFI memory burst-and-relax
  (coherent shock vs inert price gap); (c) real-crash $\Delta\alpha$ vs the calm null. Data:
  `r1_warmup_report.json`, `ofi_transient_spx.json`, `null_test_report.json`.

## Reviewer-2 hardening pass (done 2026-06-20)
Pre-empted the physics-referee objections inline:
- *"Real physics or a forced analogy?"* → §2: because EcoMD **is** a driven overdamped Langevin
  many-body system, "steady state / relaxation time / driven transient" are precise dynamical
  statements about this system, not metaphors for real markets (the real-market question is §6).
- *"The transient is by construction."* → §3: the steady state being **light** (opposite of real
  markets, not built in), the finite τ, the sigmoid dose-response, and the mechanism-specificity are
  all **emergent**.
- *"The light steady state is just a bad model."* → §6: it is a **structural** property (no stationary
  heavy-tail source), not a training shortfall; the light steady state is itself the finding.
- *"The stochastic-thermo connection is name-dropping."* → §5: reframed as a **forward-pointer** — a
  driven, relaxing, time-asymmetric signal is where stochastic thermodynamics predicts entropy
  production; quantifying it is an explicit next step "we do not claim to have established here."
- Added a **Limitations** paragraph (single simulator; pitfall-generality conjecture; crypto-only test
  → paid LOB data is the decisive follow-up).

## Status / TODO
- [x] Full 4-page draft prose; every empirical claim tied to an exp-123 artifact.
- [x] Real figures (2) from committed JSON (`make_figures.py`).
- [x] **Reviewer-2 hardening pass** (physics objections pre-empted; thermo connection made honest).
- [ ] Compile end-to-end (no TeX on the dev Mac → Overleaf) + page-fit pass to ≤4pp (~1813 words +
      2 figs → comfortable).
- [ ] Drop in official `neurips_2024.sty`; de-anonymize for camera-ready.
- [ ] Verify the Tóth et al. reference entry.

## Distinctness vs the sibling
Headline = the **physics** (non-eq driven transient + relaxation + the order-flow signature + the
real-data stationarity boundary). The burn-in finding is framed as non-equilibrium stationarity
hygiene (not generative-model evaluation), shocks as a physics probe (not scenario controls). Lead
with §3 (the transient) and §5–6 (mechanism + boundary).
