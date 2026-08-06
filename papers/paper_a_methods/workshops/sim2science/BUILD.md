# Build and release checks

The source uses the official NeurIPS 2026 workshop style with
`\usepackage[dblblindworkshop]{neurips_2026}` and `\workshoptitle{Sim2Science}`.

## Generate figures

From the repository root:

```bash
conda run -n ecophys python papers/paper_a_methods/workshops/sim2science/make_figures.py
```

Figure generation is deterministic: PDF and PNG metadata use fixed anonymous values. The learned
figure is emitted only after `experiments/127_workshop_claim_gates/LEARNED_RESULTS.json` exists.

Generate the pre-held-out-declared dependence checks from that frozen result:

```bash
conda run -n ecophys python \
  experiments/127_workshop_claim_gates/analyze_learned_robustness.py
```

Synchronize the five learned-result macros from that frozen JSON, then verify idempotence without
`--write`:

```bash
conda run -n ecophys python papers/paper_a_methods/workshops/sim2science/apply_learned_results.py \
  --write
conda run -n ecophys python papers/paper_a_methods/workshops/sim2science/apply_learned_results.py
```

## Compile

The locally verified command is:

```bash
cd papers/paper_a_methods/workshops/sim2science
conda run -n ecophys-tex tectonic -X compile main.tex --keep-logs --keep-intermediates
```

Tectonic 0.17 emits one upstream `lineno.sty` invalid-byte warning from the official template bundle;
the current log has no undefined citation/reference and no overfull or underfull box. A conventional
`latexmk -pdf main.tex` build is also supported when a full TeX distribution is available.

## Automated PDF checks

The final PDF must be copied to `output/pdf/` and checked there:

```bash
conda run -n ecophys python papers/paper_a_methods/workshops/sim2science/check_submission.py \
  output/pdf/sim2science_ecomd_2026_submission.pdf
```

The checker verifies the 50 MB ceiling, letter page size, absence of draft placeholders and local
paths, references beginning no later than page 5, anonymous metadata, and embedded fonts. It does not
replace visual inspection.

Render every final page and inspect at 100% zoom:

```bash
pdftoppm -png -r 150 output/pdf/sim2science_ecomd_2026_submission.pdf \
  tmp/pdfs/sim2science_final
```

Record the final hash with `shasum -a 256`. After OpenReview upload, download the platform copy and
repeat the same automated and visual checks.
