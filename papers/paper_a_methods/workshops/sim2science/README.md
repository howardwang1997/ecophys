# Sim2Science submission

Target: NeurIPS 2026 Workshop **Sim2Science: ML with Imperfect Scientific Models**.

- Track: 5-page Workshop Paper (references, checklist, and appendix excluded).
- Review: double blind.
- Template: official NeurIPS 2026 `dblblindworkshop` style, with
  `\workshoptitle{Sim2Science}`.
- Deadline: 2026-08-29 23:59 AoE (2026-08-30 23:59 Auckland).
- Notification: 2026-09-29.
- Archival status: non-archival; accepted papers are linked from the workshop website.
- Special obligation: nominate one author as reciprocal reviewer and complete two assigned reviews.

Official sources, checked 2026-08-07:

- <https://www.sim2science.com/cfp.html>
- <https://neurips.cc/Conferences/2026/Dates>

## Scientific scope

This is the experiment-127 **Paper E**. Its claim is a model-specific simulator audit: an
initialization transient can contaminate fixed-horizon fidelity scoring in a learned market
simulator, and a calibration-only stationarity gate can expose the contamination while preserving a
fixed scoring length. It does **not** claim that the transient is market physics, that the gate is a
universal stationarity test, or that EcoMD's steady-state tail is realistic.

## Build

```bash
latexmk -pdf main.tex
```

The release candidate must be built from this directory. Before submission, verify five content
pages, double-blind metadata, the completed checklist, embedded fonts, and the PDF SHA-256.

## Evidence

- Frozen protocol: `../../../../experiments/127_workshop_claim_gates/PREREG.md`
- Full decision record: `../../../../experiments/127_workshop_claim_gates/RESULTS.md`
- Analytic result: `../../../../experiments/127_workshop_claim_gates/ANALYTIC_RESULTS.json`
- Learned result: pending completion of the two-V100 execution.
