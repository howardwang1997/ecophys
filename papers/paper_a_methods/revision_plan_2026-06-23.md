# Paper A revision plan — figures / content / structure fixes (2026-06-23)

Scope: the three live submission drafts — `ncs/main.md` (NCS full-length, LOB §6 stays
**blank** by decision), `workshops/ml4ps/main.md`, `workshops/genai_finance/main.md` — plus the
shared figure pipeline and two stale planning docs. Derived from the 2026-06-23 review.

**Standing constraints (from the user, 2026-06-23):**
- NCS Results §6 (LOB order-flow test) **stays blank** — without Tardis L2 data NCS is not viable, and
  we are not decoupling it. Do **not** convert §6 to future-work.
- **Do not compress for length** in this pass. The NCS 3,500-word / GenAI·ML4PS 4-page limits are *not*
  binding yet; prefer adding precision over trimming. A length pass happens later, separately.

**Decisions (user, 2026-06-23):** C → **C-a** (real irreversibility estimator); F → **F-a** (re-plot);
B3 → **include** (dip statistic); E3-reorder → **include** (chronological x-axis); H → **archive** (move,
not banner).

## Execution split — Mac-now vs H20-gated (data finding, 2026-06-23)

The committed `experiments/123_driven_transient/*.json` are **summaries/fits**, not raw series; the raw
shocked-run trajectory npz are **gitignored** (only a 600-step *non-shocked* `_smoke/results_spx/` run is
local). Therefore:
- **Mac-now (unblocked):** all `.md` writing (A, B2, D, E1-label, E2, E4, E3-naming, G), figure-script
  edits that read committed JSONs (A1, A2, B1, E3 x-order), regenerate+propagate, and H (archive).
- **H20-gated (needs raw-trajectory regen):** **C-a** irreversibility estimator, **F-a** centered-window
  re-plot of fig_mechanism panel a, **B3** censoring-free dip statistic. Code lives in
  `ecomd/eval/entropy_production.py` + `scripts/analyze_{ofi_entropy,sim_ofi_transient}.py`; regen driver
  = `scripts/gpu_ofi_transient.sh` / `h20_e3b_save_trajectories.sh` (must log per-step raw ED + OFI on the
  control / kick6 / jump6 arms, ≥5 assets for C-a). Workflow: write+smoke on Mac → user runs regen on the
  next H20 slot → finalize figures + numbers.

**E1 resolved from data:** τ_OFI = spx 20.0 / ndx 20.0 / gold 22.9 / btc 24.0 → **mean 22±2**. The
fig_mechanism panel plots spx (20); the body's "22" is the 4-asset mean. Not a contradiction — **label
both** ("τ_OFI ≈ 20 for the plotted asset; 22±2 across four assets"), do not force one number.

**F confirmed real:** `t_peak=3250`, `shock=3000`, `window=500` → the windowed OFI-memory burst peaks
**+250 after** the shock (≈½ window). "Jumps at the shock" is imprecise; F-a must re-measure with a
centered window (raw data → H20) so the rise legitimately aligns with the shock, or honestly show
rise-at-shock / peak-at-+250 / decay with the window effect labeled.

---

## 0. Figure pipeline (must understand before editing any figure)

- **Canonical source:** `shared/make_figures.py` → writes the 5 figures (`fig_hero`, `fig_transient`,
  `fig_correction`, `fig_mechanism`, `fig_boundary`) to `shared/figures/{*.pdf,*.png}`.
  Reads data from `experiments/123_driven_transient/` (`windowed_hill_report.json`,
  `ofi_tau_report.json`, `null_test_report.json`, the warm-up/R1 report, etc.).
- **Propagation is MANUAL** — the same 5 files are copied into `ncs/figures/`,
  `workshops/ml4ps/figures/`, `workshops/genai_finance/figures/`. There is no sync script, and the
  copies are **currently stale** (shared/ newer than the three copies). Every figure edit therefore =
  edit `shared/make_figures.py` → run it → copy the 5 files into the 3 dirs.
- **In-figure text vs caption text:** plot titles / panel annotations are rendered *inside* the PNG
  (only changeable in `make_figures.py`); the `**Figure N.**` block in each `main.md` is the caption
  (changeable directly). Several fixes touch **both**.
- **Stale scripts to retire:** `workshops/ml4ps/make_figures.py` and
  `workshops/genai_finance/make_figures.py` build a 2-figure layout (`fig1_transient`,
  `fig2_mech_boundary`) that the workshop `.md` files **no longer reference** (they use the shared 5).
  Also `generate_figures.py` builds the superseded Pareto-ceiling set. → see item H.

---

## A. Soften "stationary" → "no systematic crash-driven heavy-up"  (P0)

Rationale (for the commit message / Methods): the claim "tails are stationary" is (i) contradicted by
our own Fig 5 — 3/5 episodes fall outside the calm-null ±1σ band, in inconsistent directions (china
heavier z=−2.2; celsius +1.9, luna +2.4 lighter), and (ii) an illegitimate affirmation of the null
with n=5, low-power data. We need only the weaker, fully-supported claim that crashes do **not**
systematically heavy-up the tail (pooled z=+1.03, wrong sign), plus the separate fact that the **calm**
tail is already heavy (α≈3) — which is what makes "EcoMD's light steady state lacks a stationary
heavy-tail source" land.

**A1 — `shared/make_figures.py`, `fig_boundary`, title (~L349):**
- before: `ax.set_title(f"Real return tails are stationary  (pooled $z={nt['pooled_z']:+.2f}$)")`
- after:  `ax.set_title(f"Real crash tails do not heavy-up  (pooled $z={nt['pooled_z']:+.2f}$)")`

**A2 — `shared/make_figures.py`, `fig_hero`, panel-c result 4 (~L135):**
- before: `("4  Real-market boundary", "returns stationary " + r"$\Rightarrow$" + " OF prediction", "#e3f2fd")`
- after:  `("4  Real-market boundary", "no crash heavy-up " + r"$\Rightarrow$" + " OF prediction", "#e3f2fd")`

**A3 — NCS `ncs/main.md`:**
- §6 conclusion (~L172-174): replace the "consistent with a stationary, approximately cube-law tail in
  calm and crash alike (Gabaix…; Gopikrishnan…)" sentence with the two-fact version:
  > *Real returns are already heavy-tailed in calm (Hill α≈3, the cube-law regime), and crashes do not
  > make them systematically heavier: the pooled effect is slightly lighter (z=+1.03), and although
  > three of five episodes move beyond the calm-null band they do so in inconsistent directions (one
  > heavier, two lighter). The driven-transient's prediction Δα≪0 is therefore falsified in real
  > returns. The relevant contrast is that the calm tail is **already** heavy — reality carries a
  > stationary heavy-tail source that EcoMD's light steady state lacks.*
- the "one of five episodes a significant heavier-tail hit — within the false-positive rate" clause
  (~L172): stop suppressing the two opposite-direction significant hits — say "one episode (china) is a
  significant heavier-tail hit and two (celsius, luna) are significantly lighter; the net is no
  systematic heavy-up."
- Discussion (~L218-219): `…places the return tail in the stationary-law camp (Gabaix 2003)` →
  `…shows the real return tail is already heavy in calm and is not driven heavier by crashes — the
  opposite of EcoMD's light-steady-state-plus-transient.`
- Fig 5 caption (~L411-414): `**Real return tails are stationary.**` → `**Real crash tails do not
  heavy-up.**`; keep the rest.
- Abstract (~L31): "Real return tails, by contrast, do not become heavier between calm and crash" — this
  is already correct/soft; leave as is (do **not** introduce "stationary" here).

**A4 — `workshops/ml4ps/main.md`:** §6 (~L164-166): same edit — drop "consistent with a stationary…
tail in calm and crash alike"; insert the two-fact version (calm already heavy + no systematic
heavy-up). Fig 5 caption (~L174-176): retitle as in A3.

**A5 — `workshops/genai_finance/main.md`:** §5 (~L166-171): same — replace "consistent with a
stationary, approximately cube-law return tail in calm and crash alike" with the two-fact version. Fig 4
caption (~L181-183): the body title is "The real-data fidelity test" (fine); ensure no "stationary"
assertion leaks into the caption.

**Acceptance:** grep for `stationary` across the 3 `.md` + `make_figures.py` returns only (a) the
*reality-has-a-stationary-source* usage (intended) and (b) descriptions of the prior-literature "camp",
never a bare claim that *our* test shows stationarity.

---

## B. α≈0.5 is the Hill estimator floor, not a physical plateau  (P1)

The dose-response "saturating at the α≈0.5 floor" is censored: 0.5 is the windowed-Hill saturation
limit on this sample. Mark it, and stop reporting α=0.5 as a literal value.

**B1 — `shared/make_figures.py`, `fig_transient`, panel b (dose-response, ~L198-201):** add an explicit
floor marker, e.g. after the existing `axB.text("steady state")`:
```python
axB.axhline(0.5, color="0.7", ls="--", lw=0.8, zorder=0)
axB.text(0.06, 0.62, r"$\alpha\!=\!0.5$: Hill floor (censored)", fontsize=6.0, color="0.5")
```
(check axB y-limits include 0.5 with headroom; adjust the x/y of the label to the axis after a test
render.)

**B2 — wording, all 3 `.md` (and NCS Fig 2 caption):** replace every "saturating at the α≈0.5 floor" /
"craters to α_ED≈0.5" *as-a-value* with the censored framing. Canonical sentence to reuse:
> *…drives the tail far heavier than the cube law, down to the windowed-Hill resolution floor
> (α≈0.5 on this sample, below which the estimator saturates); we read this as "much heavier than
> cube-law", not as a literal α=0.5 fixed point — the upper plateau of the dose-response is
> estimator-censored.*
- NCS: ~L117-119, ~L126-127, Fig 2 caption ~L384-391.
- ml4ps: ~L75-83, Fig 2 caption ~L92-96.
- genai: ~L112-114.
- Keep the existing "below one → no finite mean" note but append: "(on a short windowed transient an
  estimated α<1 is partly small-sample; we do not interpret the precise floor value)."

**B3 — (optional, analysis only, no new sim):** add a censoring-free dip-depth statistic (windowed
top-k exceedance probability or kurtosis of ED) as a robustness panel/footnote, so the saturated end of
the sigmoid has a non-floored corroborator. Defer unless cheap on existing trajectories — flag as a
nice-to-have, not blocking.

**Acceptance:** no `.md` states α=0.5 as a physical value; Fig 2b shows the floor line + "censored"
label.

---

## C. ML4PS thermodynamic framing vs the flat entropy proxy  (P1, ML4PS-only — DECISION NEEDED)

The one irreversibility measure we computed (sign-level KL entropy-production proxy) is flat. For a
physics venue this invites "in what sense non-equilibrium?". Two routes — **pick one** (see "Decisions"):

- **C-(a) strengthen (recommended, cheap — uses existing 123 trajectories):** compute a stronger
  irreversibility estimator on the simulator transient — Flanagan-Lacasa visibility-graph irreversibility
  or a Zumbach time-asymmetry — and report it (even if also null, it directly answers the obvious
  question). New analysis script over committed/regenerable trajectories; adds one panel or a sentence.
- **C-(b) writing-only:** in ml4ps abstract+§2, state plainly *"we do not claim thermodynamic
  irreversibility; 'non-equilibrium' here is the dynamical-systems sense — driven, transient, relaxing,
  light steady state"*, and demote Seifert/fluctuation-theorem from framing to "a check that returned
  null". (ml4ps §2 ~L60-62 already has the seed of this; promote it to the abstract.)

NCS and GenAI are not physics venues → only the lighter C-(b) wording hygiene applies there (already
mostly present; no action beyond B/A).

---

## D. OFI memory → 1.0 is partly tautological; re-weight the argument + the prediction  (P1)

The at-shock OFI jump to ~1.0 is mechanically imposed by the kick. It currently anchors both the
"order-flow signature" and the Phase-2 prediction. Shift weight to the emergent observables.

**D1 — all 3 `.md`, the OFI-jump sentence** (NCS ~L145-146; ml4ps ~L128; genai ~L117-119): lead with the
caveat, then the emergent content:
> *By construction the kick imposes momentary coherence, so the at-shock peak (≈1.0) is not itself
> informative; the non-trivial, emergent content is (i) the finite-time relaxation τ_OFI, (ii) the
> graded dose-response, and (iii) the contrast with the inert price gap. We read the signature from
> these three, not from the peak value.*

**D2 — NCS Phase-2 prediction wording (~L188-193):** make the *prediction* about the relaxation
timescale + dose-response **shape**, not "OFI memory bursts toward perfect persistence" (real LOB OFI is
always positively autocorrelated → "bursts to 1.0" is not falsifiable). Predict: "real crash OFI memory
**relaxes on a finite τ with a severity-graded dose-response**, where the return tail is stationary."
(This keeps §6 blank but states a sharper frozen hypothesis.)

**Acceptance:** in each draft the OFI peak value is explicitly framed as imposed; the falsifiable content
is τ + dose-response shape.

---

## E. Internal consistency: τ_OFI, τ reporting, event names, SPX≈NDX  (P2, mostly mechanical)

**E1 — τ_OFI 20 vs 22.** The figure prints `sp['tau_ofi']:.0f` from
`experiments/123_driven_transient/ofi_tau_report.json` (so the figure is correct to the fit); the body
text hardcodes "≈22". **Resolve to the JSON value:** read `ofi_tau_report.json → assets.spx.tau_ofi`,
round it, and set **all body+caption** mentions to that single value (likely 20). Locations: NCS ~L152 &
caption ~L403; ml4ps ~L135 & ~L150; genai ~L126 & ~L152. After this, body and figure agree.

**E2 — τ reporting口径.** Standardize one phrasing everywhere:
> *no single relaxation time: τ_ED ranges from ~20 (onset, fit-resolution floor) to ~236 (saturation),
> mean 134±95, CV≈71%.*
- Delete stray representative-value uses (e.g. claim_and_roadmap's "~10³ steps" if reused in any draft —
  it is not currently in the 3 drafts, so this is a no-op for them; keep the note for internal docs).
- Fig 2a caption / panel: label the full-recovery time as "full recovery ~1k steps (= several τ)" so it
  is not confused with the τ value. (NCS Fig 2 caption ~L384; transient panel a text.)

**E3 — real-event naming (three systems → one).** pilot = China-ban/Celsius; NCS body = "May-2021
sell-off"/"June-2022 deleveraging"; Fig 5 x-axis = china/celsius. Pick the **Fig-5 short labels** as
canonical and gloss once in Methods/caption:
`COVID-2020, China-2021, Celsius-2022, Luna-2022, FTX-2022` with a one-line full-name gloss.
- NCS body §6 (~L167) + Methods (~L327-329): replace "May-2021 sell-off / June-2022 deleveraging" with
  the canonical labels + gloss.
- ml4ps §6 (~L159) and genai §5 (~L161): same.
- Note in caption that x-axis order is by event grouping, **not** strict chronology (Luna May-22 plotted
  after Celsius Jun-22). Optionally reorder the x-axis in `fig_boundary` to true chronology.

**E4 — SPX≈NDX.** Both are US equity indices (correlated); "five asset classes" overstates diversity.
All 3 `.md`: change "across five assets (equities, NASDAQ, gold, crypto, FX)" → "across five calibrated
assets spanning four classes (two equity indices — S&P 500 and NASDAQ — a metal, a crypto, and an FX
pair)", and soften any "universal across asset classes" to acknowledge the two equity indices are not
independent. Locations: NCS ~L126, ~L388; ml4ps ~L82; genai ~L123.

---

## F. Fig 4a (mechanism) windowing — peak lags the shock  (P2)

The OFI-memory burst peaks ~200 steps **after** the shock (windowed quantity), but the text says "jumps
**at** the shock". Two options:
- **F-(a) re-plot (preferred):** in `fig_mechanism` panel a, center/causal-align the memory window so the
  peak sits at t=0 (shock). Requires checking how `t_peak` is used (~L266-281).
- **F-(b) caption-only:** add to the Fig 4 caption (all 3 `.md`) "(windowed; the memory curve lags the
  shock by ≈ one window width)".
Default to F-(b) now (cheap), F-(a) if the re-plot is quick.

---

## G. GenAI-Finance: add a goodness-of-fit sentence  (P2)

The GenAI draft sells EcoMD as a "useful controllable generator" but shows no stylized-fact fidelity.
Add to `workshops/genai_finance/main.md` §2 (~L56) or §5:
> *Post-correction, EcoMD matches volatility clustering (ACF of |r|) and the leverage effect, but **not**
> the stationary heavy tail — which is precisely the fidelity bound this paper reports.*
(Verify the "matches clustering + leverage" claim against the latest warm-up-discarded scores before
committing the specific facts; if only some hold, state only those. This is the one item that needs a
quick data check, not just writing.)

---

## H. Project hygiene: mark superseded artifacts  (P2, low-risk)

- `outline.md`, `draft_sections.md`: prepend a banner
  `> **SUPERSEDED (2026-06-19)** by the driven-transient reframe — kept for history; see
  claim_and_roadmap_2026-06-19.md` (or move to `archive/`).
- `workshops/ml4ps/make_figures.py`, `workshops/genai_finance/make_figures.py`: these build a 2-figure
  layout the `.md` no longer uses. Either delete, or add a header noting the live figures come from
  `shared/make_figures.py` (recommend: header note + keep, to avoid losing reusable plot code).
- `generate_figures.py` (superseded Pareto-ceiling set): add a SUPERSEDED header.

---

## Execution order (batches)

1. **Mechanical text (no figures):** E1, E2, E3, E4, H. Lowest risk; do first, one commit.
2. **Substantive wording:** A3–A5, B2, D1–D2, C-(b) wording, G (after the quick fidelity check),
   F-(b) caption. One commit per theme (A / B / D / C / G) for reviewable diffs.
3. **Figure script edits:** A1, A2 (soften titles), B1 (α-floor marker), F-(a) if chosen, C-(a) panel if
   chosen, E3 x-axis order if chosen — all in `shared/make_figures.py`.
4. **Regenerate + propagate (single procedure):**
   ```
   conda run -n ecophys python papers/paper_a_methods/shared/make_figures.py
   for d in ncs workshops/ml4ps workshops/genai_finance; do
     cp papers/paper_a_methods/shared/figures/fig_{hero,transient,correction,mechanism,boundary}.{pdf,png} \
        papers/paper_a_methods/$d/figures/
   done
   ```
   (This also resolves the pre-existing shared↔copies drift.)
5. **Verify** (checklist below), then update `logs/2026-06-23.md` per work-log discipline.

## Verification checklist

- [ ] `grep -rn stationary papers/paper_a_methods/{ncs,workshops/*}/main.md shared/make_figures.py` — only
      intended uses remain (reality-has-a-source / literature-camp), no bare "our test shows stationary".
- [ ] No `.md` reports α=0.5 as a physical value; Fig 2b shows "censored" floor line.
- [ ] τ_OFI: body number == figure number (== JSON) in all 3 drafts.
- [ ] One τ口径 sentence reused verbatim; "full recovery ~1k steps (= several τ)" labeled.
- [ ] Event names identical across body / Methods / Fig 5 in each draft.
- [ ] "five assets / four classes" wording with SPX≈NDX acknowledged.
- [ ] OFI peak framed as imposed; prediction = τ + dose-response shape.
- [ ] ML4PS: decision C-(a)/(b) applied.
- [ ] GenAI: fidelity sentence present and data-checked.
- [ ] 5 figures regenerated from shared/ and copied into all 3 dirs (mtimes match).
- [ ] Superseded banners on outline.md / draft_sections.md / stale make_figures scripts.
- [ ] NCS Results §6 still blank (unchanged, by decision).

## STATUS 2026-06-23 — Mac-now DONE, H20-gated coded+smoked

**Done & verified (Mac):**
- Figures: A1/A2 (titles softened), B1 (α=0.5 censored floor), E3 (chronological x-order) → regenerated +
  propagated to all 3 draft dirs (fixed the pre-existing drift). Only fig_boundary/hero/transient PNGs
  changed; correction/mechanism byte-identical.
- Writing, all 3 drafts: A (soften "stationary"→"no crash heavy-up", honest 3/5 deviation), B2 (α floor
  censored), D1/D2 (OFI imposed; prediction = τ + shape), E1 (τ_OFI 20/22 labeled), E2/E4 (τ口径,
  four-classes), E3 (event names + Methods gloss), G (GenAI goodness-of-fit), C-b wording + ML4PS C-a slot.
  Grep-clean of leftover overclaims.
- H: outline.md, draft_sections.md, generate_figures.py, fig1_attribution.py, both stale workshop
  make_figures.py → `archive/` (+ archive/README, workshops/README pointer). Workshop `.tex` marked STALE.
- C-a/F-a/B3 code: `ecomd/eval/time_irreversibility.py` (DHVG + Zumbach), `scripts/analyze_transient_extras.py`,
  `tests/test_time_irreversibility.py` (4/4 pass), fig_mechanism forward-compatible (panel a → real centered
  series when present; panel d → DHVG overlay when present; fallback byte-identical), driver wired.

**H20 handback (run on the next GPU slot, then I finalize):**
```
# on H20, repo root, per asset (spx already has trajectories from the prior ofi run; others need regen):
for A in spx ndx gold btcusdt eurusd; do ASSET=$A DAEMON=0 bash scripts/gpu_ofi_transient.sh; done
#   → regenerates control/kick6/jump6 rollouts (OFI+ED logged), runs analyze_sim_ofi_transient.py
#     AND analyze_transient_extras.py, commits ofi_transient/irrev_dhvg/dip_stat/ofi_memory_centered JSONs.
# back on Mac after pull:
conda run -n ecophys python papers/paper_a_methods/shared/make_figures.py   # auto-upgrades panels a & d
# then cp shared/figures/* into the 3 draft dirs (propagate step in §"Execution order").
```
**Then I finalize:** fig_mechanism panel a (real burst peak at shock) + panel d (DHVG verdict); insert the
ML4PS C-a result (replace the `[C-a: result pending]` slot) and state whether the stronger estimator
bursts or stays flat; fold the B3 dip statistic (kurtosis / exceedance) into the §"driven transient"
text so the dose-response floor no longer rests on the censored Hill α.

## Decisions needed before execution

1. **C (ML4PS):** strengthen with a real irreversibility estimator (C-a, ~half-day on existing
   trajectories) or writing-only demotion (C-b, minutes)?
2. **F (Fig 4a):** re-plot to align the peak (F-a) or caption note (F-b)?
3. **B3 / E3-reorder:** include the censoring-free dip statistic and the chronological x-axis reorder, or
   defer both as nice-to-haves?
4. **H:** banner-and-keep vs delete the stale scripts / move stale docs to `archive/`?
