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
`main.tex` shows captioned placeholder boxes until the real PDFs exist. Generate them into `figures/`:
- `figures/fig1_pitfall.pdf` — (left) sample paths + stylized-fact panel + shock-interface schematic;
  (right) Hill index vs. warm-up discard length (the inflation curve). Data: `r1_warmup_report.json`.
- `figures/fig2_control_fidelity.pdf` — (left) OFI memory/|ρ|/saturation burst-and-relax (coherent
  liquidation) vs. flat (price gap), from `ofi_transient_spx.json`; (right) per-episode + pooled Δα
  vs. the calm null, from `null_test_crash_tails.py` / `data/real/`.

Extend `../generate_figures.py` to emit these two PDFs from the committed JSON reports.

## Status / TODO
- [x] Full 4-page draft prose (abstract → discussion), every empirical claim tied to an exp-123 artifact.
- [ ] Real figures (2) from the JSON reports.
- [ ] Drop in official `neurips_2024.sty` + page-fit pass to ≤4pp.
- [ ] Author/affiliation for camera-ready (currently anonymized).
- [ ] Tighten references (verify Tóth et al. entry; the exact venue for the persistence/impact cite).
