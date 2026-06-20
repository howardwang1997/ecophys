# Paper A — two-workshop spine drafts (2026-06-20)

Per the decided submission ladder (`papers/proposal/paper_a_ncs_worklist_2026-06-19.md`): Paper A is
first split into **two non-archival NeurIPS workshop papers**, then recombined + extended for the
NCS→ICLR→TMLR ladder. These spines are the working skeletons (abstract + section-by-section content +
figure plan + claims-discipline checklist) for each.

| spine | venue | headline contribution | lead sections |
|---|---|---|---|
| `ml4ps_spine.md` | ML & the Physical Sciences | the **physics**: heavy tails = a non-equilibrium driven transient + relaxation + the real-data stationarity boundary + the order-flow non-eq signature | §3 transient, §5–6 mechanism + boundary |
| `genai_finance_spine.md` | Generative AI in Finance | the **generative-modeling methodology**: differentiable controllable scenario generator + the warmup-scoring **evaluation pitfall** + honest fidelity bounds | §3 evaluation pitfall, §4 controllable scenarios |

## Shared evidence (exp 123) — both papers draw from this, framed differently
- burn-in measurement correction (R1): `r1_warmup_report.json`, `burnin_artifact_finding_2026-06-18.md`
- in-sim driven transient (5 assets, dose-response, τ): exp 123 Stage 1/1.5/2a/2d verdicts, `tau_report_spx.json`
- channel specificity (price_jump inert, tail + OFI): `verdict_spx_jump.json`, `ofi_transient_spx.json`
- real-data stationarity boundary (5 crashes + null test): `stage3_realdata_pilot_2026-06-19.md`, `null_test_crash_tails.py`

## Distinctness guard (same-conference dedupe risk)
Both target NeurIPS workshops. They must lead with **different headline contributions** (physics vs
generative-eval methodology), frame the shared burn-in finding through different lenses (non-eq
stationarity vs eval hygiene), and ideally headline different figures. If submitting both, email the
organizers to confirm a related-but-distinct pair is acceptable. See each spine's "Distinctness" §.

## Note
`../outline.md` and `../draft_sections.md` are **pre-pivot (stale)** — they encode the refuted
"7/11 calibrated tool / stationary concave solve" spine. Do not reuse; these workshop spines + the
`claim_and_roadmap_2026-06-19.md` are the current source of truth.
