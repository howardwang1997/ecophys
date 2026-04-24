---
name: Pre-registration and rigor clauses (plan v3 binding)
description: Three hard rigor clauses user explicitly accepted 2026-04-24 as condition for pursuing Nature Physics flagship. Violating any clause automatically downgrades paper from Nature Physics to PRL. These govern all Paper B experimental design.
type: feedback
originSessionId: 8e49c8c5-5aca-4713-a84c-51220094fb28
---
# Pre-registration and scientific rigor clauses

User accepted 2026-04-24 as binding condition for the Nature Physics flagship path (plan v3). These three clauses shape all Paper B experimental design and reviewer-defense strategy.

## Clause 1 — Surrogate data can falsify

All primary-claim experiments run on both real market data AND synthetic surrogate data (IID Student-t matching kurtosis + GARCH(1,1)-t matching vol clustering). If surrogate data also satisfies the claim, the claim is declared a pipeline artifact and the paper downgrades.

**Why**: This is the modern standard for detecting "discovered universality" that is actually measurement bias (the Johansen-Sornette LPPL critique). 90% of universality claims in physics-of-finance fail this test when run retroactively.

**How to apply**: For every primary claim (A1/B2/B3), the experiment script must produce three parallel result files: real, IID-null, GARCH-null. Paper B can only claim the thing if the null files disagree with the real file by more than the claim's stated precision.

## Clause 2 — Sanity check failures cascade to paper downgrade

Seven mandatory sanity checks (S1–S7 in plan v3 §6.2) must all pass before Paper B proceeds to Nature Physics submission. Any single failure forces downgrade.

The seven:
- S1 IID null (same as Clause 1)
- S2 GARCH-t null (same as Clause 1)
- S3 Markov-toy model recovers known ΔF within 5%
- S4 Single-market baseline does not produce false universality
- S5 Dropout test: removing any single crash event changes ν by < 0.1
- S6 Across-regime split: 2000–2010 training / 2010–2024 testing gives consistent ν
- S7 Definition robustness: 3 different T_eff definitions give consistent ν

**Why**: Nature Physics referees in 2020s routinely run robustness analysis themselves if the submitted paper's appendix is thin. Pre-committing to the 7 checks beats them to the punch.

**How to apply**: Before Gate 2 (M3.5, Wk 30), the full S1–S7 pipeline must be operational and all seven must pass on the 3-market pilot. Any failure triggers immediate retreat to Paper A arXiv + 2-PRL-split plan.

## Clause 3 — arXiv pre-registration locks crash list and protocols

At Wk 26 (M3, concurrent with Paper A arXiv preprint), publicly commit via arXiv to:
- Exact list of crash events to be analyzed
- Single chosen T_eff definition (no post-hoc switching between 3 candidates)
- ν estimation protocol (window size, bootstrap method, CI definition)
- Falsification criteria for each claim

After this publication, the list is frozen. Cannot silently drop inconvenient events or add new ones that happen to fit.

**Why**: Researcher degrees of freedom (Simmons et al. 2011 in psychology) turn noise into apparent effects. Pre-registration is the only clean way to eliminate them. Nature Physics is increasingly enforcing this for universality papers.

**Side benefit**: arXiv preprint at Wk 26 also stakes priority independent of Paper B timing, which was a plan v2 concern about TradeFM or Chopra-group publications.

**How to apply**: The pre-registration document template is in plan v3 Appendix B. Draft it starting at M2 (Wk 16), publish at Wk 26 alongside Paper A arXiv preprint.

## Operational consequence for Claude

When designing any Paper B experiment:
- Always produce surrogate-data comparison files, not just real-data files
- Always run full 7-item sanity check protocol in addition to the headline experiment
- Never suggest changing the T_eff definition, crash list, or estimation protocol after Wk 26

When user considers relaxing any clause mid-project:
- Push back firmly
- Remind that accepting rigor was explicit Wk 17 decision
- Offer the retreat path (downgrade to PRL) rather than silent relaxation

When writing Paper B drafts:
- Robustness appendix is load-bearing, not optional
- Every claim's falsification criteria must be cited from pre-registration document
- Sanity check results belong in main text, not hidden in supplementary
