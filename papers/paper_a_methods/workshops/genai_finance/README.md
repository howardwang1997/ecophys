# GenAI-in-Finance workshop paper (EcoMD) — LaTeX project

NeurIPS Workshop on **Generative AI in Finance** (non-archival, ≤4pp main body, NeurIPS format).
Spine: `../genai_finance_spine.md`. Evidence map: `../README.md`.

## Build
```bash
cd papers/paper_a_methods/workshops/genai_finance
latexmk -pdf main.tex        # or: pdflatex main && bibtex main && pdflatex main && pdflatex main
```
`main.tex` **compiles as-is** with a NeurIPS-approximating fallback preamble (so you can iterate the
prose now). For the actual submission, drop the official **`neurips_2024.sty`** (and `.bst`) — from the
workshop CFP / NeurIPS site — into this directory; `main.tex` auto-detects and uses it. Add `[final]`
to the `\usepackage{neurips_2024}` line for the camera-ready (de-anonymized) version.

## Figures
Regenerate (fully from committed JSON — no gitignored data needed):
```bash
conda run -n ecophys python make_figures.py
```
- `figures/fig1_pitfall.pdf` — Hill index vs. warm-up discard (the inflation curve, both cells rising
  out of the cube-law band). Data: `r1_warmup_report.json`.
- `figures/fig2_control_fidelity.pdf` — (left) OFI memory burst-and-relax (coherent liquidation) vs.
  flat (price gap), from `ofi_transient_spx.json`; (right) per-episode + pooled Δα vs. the calm null,
  from `null_test_report.json`.

## Status / TODO
- [x] Full 4-page draft prose (abstract → discussion), every empirical claim tied to an exp-123 artifact.
- [x] **Real figures (2)** generated from the committed JSON reports (`make_figures.py`).
- [ ] Compile end-to-end (no TeX on the dev Mac — use Overleaf) + page-fit pass to ≤4pp.
- [ ] Drop in official `neurips_2024.sty` for the submission format.
- [ ] Author/affiliation for camera-ready (currently anonymized).
- [ ] Tighten references (verify Tóth et al. entry; the exact venue for the persistence/impact cite).
- [ ] Optional: Fig 1 left panel (sample paths + shock-interface schematic) if space allows.
