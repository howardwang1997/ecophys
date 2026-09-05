# Formal A-3 treatment-selection audit (2026-09-05)

Machine decision: `research/discovery/decisions/truth_asset_a3_treatment_selection_audit_20260905.yaml`
(SHA-256 `028f9530e51e3d7c19dd314b7b4a84443ca788175eda8fd518d1883d84eb90c7`).
Procedure: frozen in the A-3 capability-build plan ("Treatment selection: deferred, procedure
frozen"). This audit is **outcome-blind**: no market outcome was accessed, no effect-direction
expectation motivates any ranking, and no human/participant/outreach action occurred.

## Selection verdict

- **Primary treatment: equal-price queue-priority rule — strict FIFO versus uniform random
  sampling of resting units at the execution price (anti-splitting unit kernel).**
- **Backup: minimum resting time** (conditional on a frozen fork derivation; no schema change
  required).
- One candidate family is **disqualified** (resting-depth visibility: direct human-subject
  same-family prior). Zero-candidate stop rule not triggered.

## Adjudication against the frozen disqualifiers

### Family 1 — equal-price queue priority (FIFO vs pro-rata vs randomized tie-break): SURVIVES

- **Collision:** the searched manifest v2 of 2026-08-27
  (`ecomd_random_unit_priority_collision_manifest_v2_2026-08-27.md`, 10+ cited primary works
  with DOIs) found no human-subject same-estimand comparison. Lim (2026, SSRN 6574208) is a
  controlled dual-engine simulation plus theory neighbor; Khapko & Zoican (2021, JFM) is the
  closest human speed-investment laboratory market but keeps time priority fixed (no allocation
  treatment); Angel & Weaver (1998/99) is observational (Toronto pro-rata); the named occupied
  institution comparisons (Aldrich & López Vargas 2019; Guler et al. 2025) are different
  treatments.
- **Assignment/grammar:** implemented and frozen in the A-2 bundle (`lab-asset-v3` fixtures
  under both arms prove the tape grammar is arm-invariant; the random-unit arm differs only in
  allocation draws and unit-execution granularity). Zero marginal engineering cost.
- **Discriminating fork:** frozen in `ecomd_tie_priority_c2_fork_derivation_2026-08-26.md`:
  Lemma 1 (pathwise aggregate invariance under exchangeable populations — predicts a **zero**
  effect on the aggregate path law) versus Lemma 2 (threshold-family strategic queue-value
  response — predicts a **positive order-one** touch-depth change under randomized priority).
  Two serious model families with opposite predictions on the primary contrast.
- **Variant choice within the family:** random-unit (not pro-rata), per the frozen thesis v2:
  pro-rata induces size competition already studied observationally (Angel & Weaver) and the C2
  fork is derived for uniform random priority; the unit kernel blocks allocation-probability
  gaming by child-order splitting.

### Family 2 — cancellation/replace cost schedule: SURVIVES, RANKED 3

- **Collision (searched this session):** "When is the order-to-trade ratio fee effective?"
  (J. Fin. Markets 2022, S1386418122000532) is field/empirical Eurex evidence, not an assigned
  human laboratory treatment; "The Effects of Make and Take Fees in Experimental Markets"
  (Chapman ESI working paper) is human-lab but taxes executions (make/take), not
  cancellations; Füllbrunn (2022, JEBO) tests market regulations in experimental asset markets
  but not a cancellation-fee arm. No direct same-estimand human prior found.
- **Assignment/grammar:** feasible but a cancel/replace fee mutates cash outside executions, so
  the unified tape schema needs fee fields (schema v4 re-freeze plus new fixtures): one extra
  engineering iteration.
- **Fork:** plausible (market-maker quoting models predict wider spreads/fewer quotes under
  cancel costs; spoofing/flickering-deterrence models predict tighter effective spreads), but no
  frozen derivation exists.

### Family 3 — resting-depth visibility: DISQUALIFIED (direct prior collision)

- Hendershott et al. (2022), "Transparency in fragmented markets: Experimental evidence"
  (J. Fin. Markets, S1386418122000258): human-subject laboratory limit-order markets with a
  hide-orders treatment — "allowing traders to hide their orders encourages limit order usage."
  This occupies the displayed-versus-hidden resting-liquidity treatment family in human
  markets with adjacent response estimands (limit order usage, spread, depth).
- Boulatov, George & Kaya (2013, RFS) already own the theory (display expropriates
  informational rents). Both a serious prior theory and a prior human experiment exist.

### Family 4 — minimum resting time: SURVIVES, SELECTED AS BACKUP

- **Collision (searched this session):** no human-subject laboratory treatment found. The
  literature is regulatory (ASIC scrapped its MRT plan; Michigan law review compilation),
  agent-based simulation (SciencesPo HAL: MRT reduces relative number of flash crashes in an
  ABM with low-latency traders), and theory ("Optimal Decisions in a Time Priority Queue":
  MRT-constrained cancellation). Khapko & Zoican (2021) speed bumps delay messages rather than
  locking resting orders — adjacent mechanism, not the same treatment.
- **Assignment/grammar:** the frozen lab-asset-v3 grammar already supports it with **zero schema
  change**: a cancel during the minimum resting window is the existing reason-coded
  `cancel_too_late` rejection.
- **Fork:** the ABM flash-crash-reduction prediction versus quoting-flexibility costs (wider
  spreads, slower quote repair) is a plausible opposite-sign fork, but it is not yet frozen in a
  derivation artifact. **Backup status is conditional on a future frozen fork derivation.**

### Family 5 — order-size unitization: SURVIVES COLLISION, RANKED 4

- **Collision (searched this session):** no human-subject minimum-order-size/quantity-grid
  laboratory comparison surfaced; adjacent literatures are tick size (price grid) and queue
  position (Garriott et al. 2025, J. Fin. Markets). Provisionally survives.
- **Assignment/grammar:** quantity-grid violations need a new reason code (schema v4).
- **Fork:** none established; no frozen derivation and no sharp opposite-prediction pair named.

## Searched-manifest additions (this session)

| Work | Lane | Finding |
|---|---|---|
| Hendershott et al. 2022, JFM (S1386418122000258) | human lab | hidden-orders treatment occupies family 3 |
| Boulatov et al. 2013, RFS | theory | display-vs-hide liquidity theory occupies family 3 |
| JFM 2022 OTR-fee study (S1386418122000532) | field | Eurex OTR evidence, not a lab assignment |
| Chapman ESI WP, make/take fees | human lab | execution-fee treatment, not cancellation cost |
| Füllbrunn 2022, JEBO | human lab | regulation testing, no cancellation-fee arm |
| Springer s11156-017-0632-2 (HFT/tick/MRT) | survey/regulatory | MRT debate, no human experiment |
| SciencesPo HAL ABM (low-latency regulation) | simulation | MRT reduces flash crashes in ABM |
| "Optimal Decisions in a Time Priority Queue" | theory | MRT-constrained cancellation theory |
| Garriott et al. 2025, JFM (S1386418125000229) | theory/empirical | queue-position value, adjacent to family 5 |

Search coverage note: one targeted search per family (plus two refinement searches for
cancellation costs and minimum resting time) against Google-indexed literature; combined with
the 2026-08-27 ten-work manifest for family 1. This is a bounded selection audit, not the
fifteen-work hostile neighborhood required for a topic cycle; per the A-3 plan the
disqualifier standard is "existing same-estimand human-subject prior," for which these
manifests are the searched evidence.

## Consequences

- The primary treatment's arms are exactly the two arms already frozen, conformance-qualified
  and replay-validated in the A-2 bundle; no further engineering iteration is required before
  A-1.
- Any future re-audit trigger: a newly surfaced direct human same-estimand comparison for
  queue-priority (per the 2026-08-27 manifest's re-audit triggers) voids this selection.
- This selection creates no topic card, no route status and no re-entry authorization; the A-3
  plan's A-1 rung (site contact, ethics, preregistration) now has its treatment frozen and
  requires a new PI-authorized machine decision before any external contact.
