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

## Reviewer-2 hardening pass (done 2026-06-20)
Pre-empted the likely referee objections inline:
- *"Everyone already discards burn-in / the pitfall is trivial."* → §3: the artifact is **rewarded**,
  not caught (the warm-up-inclusive heavier reading sits closer to the cube-law target, so the scorer
  registers a *better* match); low cross-seed variance reinforces the illusion → it survives practice.
- *"Is EcoMD novel enough?"* → intro: contribution is the eval pitfall + controllability + fidelity,
  not the simulator; differentiability is the hook for the shock interface; pitfall framed model-agnostic.
- *"The corrected protocol is vague."* → §3: a concrete 3-step recipe (sliding window vs $W$; discard to
  plateau $W^\star$; report score + sensitivity curve, flag transient-contaminated facts).
- *"The coherent OFI is by construction."* → §4: the burst is partly imposed; the emergent content is
  the **relaxation** + the contrast with the inert price gap.
- *"Crypto-only / 5 episodes."* → §5 + Limitations: scope stated honestly; robust to vol-standardization.
- Added a **Limitations** paragraph (pitfall-generality conjecture + data scope) and tightened.

## Status / TODO
- [x] Full 4-page draft prose (abstract → discussion), every empirical claim tied to an exp-123 artifact.
- [x] **Real figures (2)** generated from the committed JSON reports (`make_figures.py`).
- [x] **Reviewer-2 hardening pass** (objections pre-empted, related work + protocol strengthened).
- [ ] Compile end-to-end (no TeX on the dev Mac — use Overleaf) + page-fit pass to ≤4pp (now ~2050
      words + 2 figs + table → likely needs a ~100–150 word trim; candidates: the §6 takeaway recap).
- [ ] Drop in official `neurips_2024.sty` for the submission format.
- [ ] Author/affiliation for camera-ready (currently anonymized).
- [ ] Tighten references (verify Tóth et al. entry; the exact venue for the persistence/impact cite).
- [ ] Optional: Fig 1 left panel (sample paths + shock-interface schematic) if space allows.
