# DRAFT STATUS — Paper E (`papers/paper_e_matching_fiber/`) — v0.2 (integrated)

Stage: D_minus_1 (pre-D0). D0 outcome-blind freeze pinned **2026-09-19**.
Skeleton built 2026-09-07; four writer sections drafted 2026-09-07;
**v0.2 integration pass 2026-09-07** (this document records it).
Branch: `paper-d-iclr-2027-completion` (anonymized inside the manuscript).

## What this manuscript is

Merged GAMMA-led paper: **matching-fiber non-identifiability theorems for
market-clearing mechanisms** (T1 aggregate-sufficiency obstruction; T2 bounded
consumer floor + kernel-blind vacuity; T3 deployment exposed sets + H5
kernel-swap manipulation validity; V4 gauge-conflation remark) **plus a
preregistered mechanism-layer attribution cube** (ALPHA eight-cell design), on
the frozen lab-asset-v3 engine (bundle manifest
`fea8a136b0c3e19a00bddcb131a1540ca40fda6c1576dbc949001dbf76a9581c`).
**Theorems + preregistered design only; every empirical statement is
`\RESULTSPENDING`.**

## Claims authority (binding order)

1. `papers/proposal/ecomd_reexploration_prereg_v2_2026-09-06.md` — science.
   Status labels **verbatim-binding**; §8.1 nonclaims binding; Annex C errata.
2. Statistical contract v1 as amended at v2 (C1–C16, G1–G12) — statistics.
3. Theory appendix + five D-1 lemma writeups — statements and proofs.
4. D-2 evidence map + project CLAUDE.md mandatory list — the ONLY admissible
   citation sources.

## Audit-issue disposition (all 14 issues; 14 fixed, 0 rejected)

No issue was resolved by weakening a condition, concession, status label, or
nonclaim. Every disposition below preserves prereg v2 wording verbatim.

### Audit 1 — citation-integrity (A1.1–A1.4, minor)

| ID | Issue (gist) | Disposition |
|---|---|---|
| A1.1 | `refs.bib` `note={...}` fields render provenance/NEEDSVERIFY text into the printed bibliography | **Fixed.** All provenance/verification notes moved to `%` comments above each entry (source file keeps full provenance; rendered bibliography is clean). Key set unchanged. |
| A1.2 | `related.tex` cited `\citep{NEEDSVERIFY:transportation-polytopes-and-random-assignment-lotteries}` — map rows exist and should be seeded | **Fixed.** Three D-2-map rows seeded as `transportationpolytopes2004`, `extremepoints2024`, `smartlotteries2026` (title-only, NEEDSVERIFY convention in comments); related-work paragraph (a) rewritten to cite the three keys with an accurate one-clause characterization; placeholder macro retired (grep: no NEEDSVERIFY cite remains). |
| A1.3 | CLAUDE.md mandatory list says Maskawa (Entropy 2025) belongs "in every relevant paper" — is it relevant here? | **Fixed by recorded waiver, not by manuscript edit.** Paper E contains no volatility-cascade, fluctuation-theorem, or stylized-facts-estimation content; the entry stays in `refs.bib` with the waiver noted in its comment. Citing it here would be decorative, violating the no-overclaiming rule. |
| A1.4 | `mars2024` key vs ICLR-2025 publication-year mismatch; MarS author list unverified | **Fixed.** The D-2 map itself dual-dates the row ("MarS (2024, ICLR 2025)"); key kept for map traceability, publication form (booktitle ICLR, year 2025) governs, and the dual dating is documented in the entry's `%` comment. Author-list completion stays flagged NEEDSVERIFY for the post-freeze bibliographic pass (open item, below). |

### Audit 2 — coherence (B1–B10 / A2.1–A2.10; three major)

| ID | Issue (gist) | Disposition |
|---|---|---|
| B1 (major) | Prereg-named results (Theorem 1, Lemma 0, Prop 1b, Corollary 2, Prop 3.5, T1/T-1/T-2, V4 Lemmas A/B, Lemma D) printed through the shared auto-number, so each object had two names and prose hardcodes ("Theorem~1", "Lemma~0") mismatched | **Fixed.** New `preregthm` environment in `main.tex` (bold header + `\phantomsection`/`\@currentlabel` so `\ref` prints the bare prereg name). 11 conversions: Theorem 1, Proposition 1b, Corollary 2, Proposition 3.5, Lemma 0, Theorems T-1/T-2, Lemma A, Lemma B, Lemma D, Theorem T1. G2-k/R2-*/KT/H5-layer lemmas stay auto-numbered. Prose hardcodes audited against the printed names. |
| B2 | Rank–nullity parenthetical in `setup.tex` was mathematically wrong (implied the pullback is always trivial) | **Fixed.** Now states the correct content: `dim ker B` free directions are added; the pullback is trivial only in the full-column-rank case (`ker B = {0}`). |
| B3 | Double-blind scrub: branch name, internal codename (`ecomd_v2`), `r2://ecophys/` bucket, main-text ruling IDs (`D1_01/D1_12/D1_14`) | **Fixed** in all rendered text: lineage codenames anonymized (`setup.tex`, `cube.tex`); ruling IDs replaced by "frozen preregistration ruling/decision; internal id anonymized" (`setup.tex`, `cube.tex`, `app_engine_b.tex`); branch name and R2 bucket anonymized in `app_prereg_c.tex`; estimator module path reduced to basename with an anchor-policy sentence (`app_engine_b.tex`). See the anonymization policy below for the deliberate keeps. |
| B4 | EP2 pointer cited `sec:setup` for the three-way distinction that actually lives in `sec:t3h5` | **Fixed.** `cube.tex` EP2 now references Section 6 (`sec:t3h5`). |
| B5 | Lemma D Stirling prefactor: a stray leading `N\,` in the numerator was inconsistent with the writeup's own `prefactor(mu)` collapse | **Fixed.** Numerator now `sqrt(n(N-n)K(N-K))`, which collapses exactly to the printed `prefactor(mu) = (2π)^{-1/2} N^{3/2}/sqrt(K(N-K)n(N-n))`; the `2/sigma` bound and all spot-check constants (0.1399, 2.816, 0.0916) unchanged. No theorem constant was altered. |
| B6 | Notation collisions: bare `K_pi/K_1/K_2/K_hat` vs `K=16` vs `K_split` vs Lemma D's `(N,K,n)`; deployment map `D` vs deeper-level set `D` vs H5 DGP instance; V4 quotient `Q`; Lemma D mode `m*` vs pool order count `m*` | **Fixed.** Renames: kernels `\mathcal{K}_pi/\mathcal{K}_1/\mathcal{K}_2/\mathcal{K}_s/\hat{\mathcal{K}}`; deeper set `\mathcal{D}`; H5 DGP instance `\mathsf{d}`; V4 quotient `\mathsf{Q}`; Lemma D mode `x^\dagger`. Deployment map `D` and pool count `m^*` keep the prereg's own symbols. New "Notation disambiguation" paragraph in `setup.tex` fixes every role once, up front. Grep-verified: no bare `K_1/K_2/\hat{K}`, `|D|`, or quotient-`Q` remains. |
| B7 | H5 ladder presented the aggregate print as flowing through / nested in the key-equalized attribution projection — a false sigma-algebra inclusion | **Fixed.** H5 setup now states two deterministic projections of `F_exec`: `F_exec ↠ Π_att` (key-equalized attribution) and `F_exec ↠ g_agg`, explicitly NOT nested in either order (aggregate print carries untouched-level prices; count vector carries maker attribution), with `\mathsf{d}` the DGP instance. |
| B8 (a/b) | Placeholder discipline: duplicated/`RESULTSPENDING` sentences, inconsistent placeholder forms | **Fixed.** Single `\RESULTSPENDING{}` macro everywhere; the cube and scope closing sentences were deduplicated into one binding statement each. |
| B9 | T3 rescue-lever wording drifted from the three-way distinction's terms | **Fixed.** Lever named "deployment redesign at fixed information for operator set-identification", matching `related.tex` (g) and EP2; KT-M1 now points at the gauge-twin contrast of the cube. |
| B10 | Terms used before definition (`u`-invariance before `def:exposed`; `S3`, `S1a`, STOP-class, O-B/O-C at first use) | **Fixed.** Inline `u`-invariance definition inserted before `def:exposed` in `t3h5.tex`; S3/S1a/STOP-class glossed at first use (`setup.tex`, with pointers to EP3/EP4/`sec:scope-stop`); O-B/O-C glossed as preregistered prediction IDs (Table of O-orderings). |

### Failed-writer stubs

Recon found none: every section file carries full drafted content; no stub
placeholders remained before integration.

## Harmonization record (task step 3)

- **Title**: one title everywhere — the skeleton title is kept (main.tex;
  intro writer's recommendation comment concurs; DRAFT_STATUS records it).
- **Notation**: B6 sweep above; `notation.tex` macros used throughout.
- **Dedupe seams**: cube/scope closing status sentences; related-work lane (a)
  vs T1 scope concessions now complementary (map-vs-theorem roles).
- **Cross-references**: B4 fix + full compile with zero undefined references
  (the only "undefined" string in the log is the prose phrase "occasionally
  undefined").
- **Placeholders**: uniform `\RESULTSPENDING{}` (red, self-describing).

## Anonymization policy (double-blind; repo private since 2026-09-05)

Anonymized in rendered text: branch name; internal project codenames
(`ecomd_v2` and the `ecomd/` package prefix); `r2://ecophys/` bucket;
main-text ruling IDs. **Deliberate keeps**: (i) `sha256` hashes and manifest
values (freeze-integrity anchors); (ii) the frozen bootstrap RNG string
`ecomd_reexploration_v2_bootstrap` (`cube.tex`, clause C8 derivation) — it is
a load-bearing frozen constant whose alteration would change preregistered
seed derivations, and it is covered by the Appendix-C double-blind note;
(iii) relative artifact paths of the frozen lab-asset bundles in Appendices
B/C (engineering grounding; no author linkage); (iv) `D1_xx` ruling IDs inside
the Appendix-C amendment ledger and errata register, where the ledger is the
subject. Camera-ready restores names per `app:prereg-blind`.

## Compile

    cd papers/paper_e_matching_fiber
    /opt/homebrew/bin/tectonic --keep-logs main.tex

`tectonic` 0.17.0 is the ONLY TeX engine on this Mac (no pdflatex/latexmk/
bibtex binaries; tectonic runs bibtex internally). Single light compile per
session (PI standing rule: no heavy computation on this Mac).

**v0.2 compile status: SUCCESS** (2026-09-07). `main.pdf`, **69 pages**,
~530 KiB. Zero LaTeX errors; zero undefined references/citations. Residual
warnings only: over/underfull hboxes (tables in Appendices B/C, widest
8.4 pt) and bibtex "need author or key" sorting notices for the title-only
NEEDSVERIFY entries — expected under the verification convention, to be
resolved in the post-freeze bibliographic completion pass. Bibliography
mechanism is single (natbib [numbers,sort&compress] + plainnat + refs.bib).

**Post-full-bib-verification compile: SUCCESS** (2026-09-07, after the
complete 40/40 refs.bib verification in item 3). Zero LaTeX errors, zero
undefined references/citations; 39 of 40 entries cited and rendering
(`maskawa2025` uncited per the A1.3 waiver). Spot-checked against the
regenerated `.bbl`: `chopra2023` renders the real 7-author AAMAS record,
`neuralmechanics2020` renders as Kunin et al. (2021), `diffsimpolicy2026`
renders the exact nested double-quoted title verbatim, `solverinloop2020`
stays title-only, `paperd` renders as Anonymous (2026). bibtex log is now
error-free with only the two expected `solverinloop2020` author-less sorting
warnings (down from 22 notices at v0.2). Engineering note for future editors:
bibtex treats a bare `@` in `%` comment lines as an entry-start token —
write entry types in comments without the `@` (e.g., "retyped article ->
misc"), or bibtex emits "expecting `{` or `(`" errors (introduced and fixed
2026-09-07).

## What is deliberately absent (unchanged from skeleton contract)

- **All empirical results** (D0 freeze 2026-09-19). Permitted numbers only:
  theorem constants, frozen design constants, instrument hashes.
- The **D0 freeze sha256 and freeze timestamp** — the only two TO-BE-PINNED
  items; must not exist before 2026-09-19.
- The **final abstract** (post-D2 rewrite; current abstract carries the
  pre-D0 theorem+design contract).
- **Venue-specific style** (venue-neutral 11pt article; no vendored
  conference styles; `papers/paper_d_constraints/` untouched).

## Independent bib-verification audit (2026-09-07, post completion)

Independent auditor re-loaded ~30/40 entries from authoritative pages
(arXiv abs/export API, Crossref, PMLR, IFAAMAS, OpenReview) and compared
field-by-field, weighted toward corrected entries and including all five
identity-critical corrections: **zero fabricated or wrong bib fields**;
mechanical checks all pass (key set identical to git HEAD, 40 entries, only
refs.bib + DRAFT_STATUS.md modified, verify stamps on 39/40 with paperd the
documented exception). Verdict `issues_found` was driven entirely by
prose-consistency findings, all dispositioned same day:

| Finding | Disposition |
|---|---|
| related.tex fabricated quotation: ``the noise law determines the stochastic fiber'' attributed to `perturbargmax2024` (0 hits in arXiv:2406.02180) | **Fixed.** De-quoted and recast as our characterization ("owns the principle that the noise law determines the selection distribution for the state-free argmax family"); the concept-level scoping claim was audit-judged defensible, only the quotation marks were false. |
| related.tex lane (f): "Neural Mechanics builds conservation laws into the weight structure --- both function-preserving by construction" | **Fixed.** Real record (Kunin et al., ICLR 2021, "Neural Mechanics: Symmetry and Broken Conservation Laws in Deep Learning Dynamics") DERIVES conservation laws of the training dynamics from architectural symmetry. Rewritten accordingly; the function-preserving-by-construction property now attaches to `quotientdiffusion2026` alone. |
| v4.tex same defect inside the V4 remark's citation clause | **Fixed.** Now "in the same symmetry family, the conservation laws Neural Mechanics derives for the training dynamics". V4's not-a-gauge content and Lemma v4-a argument untouched. |
| cube.tex over-attribution: "the perturb-argmax surrogate of probability-proportional-to-remaining draws \citep{perturbargmax2024}" | **Fixed.** Citation now scopes to the perturb-then-argmax construction only ("a perturb-then-argmax surrogate \citep{...} of ..."); estimator semantics, pinned noise, and frozen constants untouched. |
| refs.bib `kineticsim2026` % comment claimed "no journal-ref/Comments/DOI" | **Fixed.** arXiv v2 carries a Comments string ("12 pages, 7 figures, 5 tables. IEEE format"); comment corrected. Fields/type unaffected. |

Cleared by the same audit (recorded, no action): `chopra2023` prose
("establishes the differentiable-agent-based-model feasibility") judged
defensible under the corrected record; `mars2024` prose defensible;
`maskawa2025` confirmed single author Jun-ichi Maskawa (not the Nobel
laureate) and confirmed uncited per the A1.3 waiver; `solverinloop2020`
title-only form is the documented prereg ruling R3-10; `duruisseaux2024`
prose (train-x-infer template, Fourier/Leray projection) supported by the
abstract. Additional self-check beyond the audit: the `lossbasis2026`
quotation "the loss does not see the basis, but Adam does" is verbatim the
paper's TITLE (arXiv:2608.05136) — legitimate quotation, kept. Residual
low-risk note: `chopra2023` end page 1857 from the editor's record (start
page 1848 independently confirmed on the IFAAMAS contents page).



1. **D0 freeze sha256 + timestamp** — pinned at D0 (2026-09-19) only;
   Appendix C placeholders stay empty until then.
2. **Post-D2 outcome writing** — every `\RESULTSPENDING{}` site; final
   abstract rewrite.
3. **NEEDSVERIFY bibliographic completion — COMPLETE 2026-09-07 (full
   coverage, 40/40 entries; five verifier clusters integrated idempotently
   by the editor from the on-disk state; never from memory; no key changed,
   no entry added or removed).** 31 entries corrected against loaded
   authoritative pages (arXiv abs pages, arXiv export API, Crossref REST,
   PMLR publisher pages, OpenReview metadata/API, IFAAMAS proceedings
   contents, Springer chapter page, MDPI article page, Project Euclid); 8
   entries confirmed with fields already correct (`cont2001`, `soudry2017`,
   `lossbasis2026`, `walkingfiber2025`, `counterfactualoperator2025`,
   `extremepoints2024`, `smartlotteries2026`, `solverinloop2020` — the last
   deliberately kept title-only per prereg ruling R3-10); `paperd` is
   internal-by-design. **Zero unverifiable entries; zero fabricated
   fields.** Every corrected entry's `%` comment carries its evidence URL
   and a "verified ... 2026-09-07" stamp; all stale NEEDSVERIFY flags
   cleared.
   - **Identity-critical corrections (PI should be aware):**
     - `chopra2023`: the previous title "GradABM: Learning Agent-Based
       Market Simulators from Data" matches NO publication (official IFAAMAS
       AAMAS 2023 proceedings contents, arXiv site search, DBLP search and
       the author's full DBLP listing all return 0 hits). Corrected to the
       real AAMAS 2023 paper "Differentiable Agent-based Epidemiology"
       (Chopra, Rodríguez, Subramanian, Quera-Bofarull, Krishnamurthy,
       Prakash, Raskar; pp. 1848--1857; arXiv:2207.09714), which introduces
       the GradABM framework and matches the D-2 map row's "epi feasibility"
       note. The removed Dyer ICAIF 2023 market-side row was NOT
       reintroduced as a substitute (prereg v2 removal stands).
     - `neuralmechanics2020`: the exact previous title ("...Conservation
       Laws in Vision", ICLR 2020) exists nowhere in the publication record;
       identity resolves via the D-2 map row's "weight-space conservation
       laws" pin to Kunin, Sagastuy-Brena, Ganguli, Yamins, Tanaka, "Neural
       Mechanics: Symmetry and Broken Conservation Laws in Deep Learning
       Dynamics", ICLR 2021 Poster, arXiv:2012.04728 — title, venue-year
       (2020→2021) and authors changed; key kept for map traceability.
       **Explicit PI sign-off requested** (flagged in the entry comment): if
       a different vision-specific paper was intended, no such paper exists
       in the searched record and the entry must be treated as unverifiable
       rather than silently retargeted.
     - `maskawa2025`: author given name corrected Hideki → **Jun-ichi**
       Maskawa (Seijo University; NOT the Nobel laureate — a different
       person); Entropy 27(4):435, DOI 10.3390/e27040435 added.
     - `perturbargmax2024`: first author is **Hedda** Cohen Indelman (bib
       had "Gil"); exact long title restored.
     - `diffsimpolicy2026`: exact nested title restored — Does "Do
       Differentiable Simulators Give Better Policy Gradients?" Give Better
       Policy Gradients? (ICLR 2026, arXiv:2604.18161); the previous flat
       form collided with the distinct Suh et al. ICML 2022 paper.
   - **Entry-type corrections (no venue existed to cite):**
     `fibers2014`, `sinkhornlinearization2026`, `matchingengineabm2021`
     retyped to arXiv-preprint `@misc` (no journal-ref/venue in the record
     for any of the three; matchingengineabm2021's presumed journal does not
     exist); `mongegap2023` `@misc`→`@inproceedings` (ICML 2023, PMLR v202,
     pp. 34709--34733); `diffsimpolicy2026` `@misc`→`@inproceedings`
     (ICLR 2026).
   - **Et-al / title-only expansions completed:** `toth2011` (full 6-author
     list; published title + "in Financial Markets"; PRX 1(2), DOI),
     `batatia2022` (5 authors; NeurIPS 35), `diaconissturmfels1998`
     (26(1):363--397 + DOI), `taskbased2017` (Donti/Amos/Kolter; title
     suffix restored; NIPS 30, pp. 5484--5494), `gumbelsoftmax2016`
     (title-merge resolved to Maddison/Mnih/Teh arXiv:1611.00712; the
     companion Jang/Gu/Poole arXiv:1611.01144 is recorded in the entry
     comment only, no entry added), `dpiot2022` (Chiu/Wang/Shafto; PMLR
     v162, pp. 3925--3946), `propertiesmechanisms2022`
     (Ahuja/Hartford/Bengio; ICLR 2022 Spotlight), `quotientdiffusion2026`
     (7 authors; ICLR 2026 Oral confirmed), `duruisseaux2024` (4 authors;
     title gains final word "Frameworks"; ICML 2024 AI for Science
     Workshop), `nagy2023` (7 authors; full two-part title; ICAIF '23,
     pp. 91--99, DOI), `mars2024` (7 authors; full title — **A1.4 author
     list now closed**), plus the market-model `@misc` completions
     `marketgpt2024` (Wheeler/Varner; identity pinned by four independent
     enumerations), `tablabm2025` (Olby/Baggott/Stillman), `tradefm2026`
     (5 authors), `m3_2026` (5 authors; exact title), `kineticsim2026`
     (Jayakody/Jayakody), `gendfl2025` (5 authors; arXiv-only — cite as
     arXiv:2502.05468, never from memory as IJCAI), `trades2025`
     (Berti/Prenkaj/Velardi; ECAI 2025, FAIA 413, pp. 3703--3710, DOI),
     `surrogateldfl2025` (4 authors with exact diacritics), and
     `dexclosedloop2026` (single author Wang; exact title).
   - t4-cluster re-check against the fresh verdicts: `dolob2026`
     re-corrected (primary class [cs.AI], not [q-fin.TR] — the one field
     the partial run left wrong); `transportationpolytopes2004` note editor
     order set to Springer's cite line (Bienstock, Nemhauser) and stamp
     refreshed to the Springer evidence URL.
   - `paperd` double-blind safety re-checked 2026-09-07: fields are
     `Anonymous` + descriptive title + year only — no author, repo, branch,
     or URL leakage. Unchanged.
   - Uncited sweep 2026-09-07 (`main.tex` + `notation.tex` +
     `sections/*.tex`; the two `NEEDSVERIFY:` cite strings sit in `%`
     comments): `maskawa2025` is the only refs.bib entry never cited (A1.3
     waiver stands; entry kept). All other 39 entries are cited at least
     once.
4. **maskawa2025 waiver** — PI-recorded here (A1.3); revisit only if
   volatility-cascade content ever enters the paper.
5. **Camera-ready name restoration** — anonymized internal names per the
   policy above.
6. **Venue decision** — style/limit adaptation deferred until venue choice.
7. **Cosmetic pass** (optional): over/underfull boxes in appendix tables.
