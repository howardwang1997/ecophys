# Merge analysis: priority-rent Paper 1 and simulator-validation Paper 2

Date: 2026-08-27

Status: **superseded in recommendation** by `ecomd_path_reexploration_2026-08-27.md` (same day,
later session): the merge-compatible design requiring simulator lineages to be frozen before the
human experiment is withdrawn from the executable path. The structural analysis in Sections 1--3
remains valid; the experiment no longer waits for any simulator work.

PI direction: continue the live route, and consider merging the two planned papers into one.
This note analyzes the merge and recommends a merge-compatible design in which the final
one-paper-versus-two-papers choice stays open until results exist.

## 1. The structural constraint that governs everything

A simulator-validation claim is prospective only if the prediction freeze predates outcome
access. Therefore the fork is not "merge or not" but "where the prediction freeze sits":

- **Option A — one experiment, two papers.** Both simulator lineages (EcoMD-class and an
  LLM-agent lineage) freeze their predictions of the randomized rule-change treatment effects
  before the human experiment runs; the economics paper and the simulator-validation paper are
  then written from the same prospectively frozen predictions and the same truth asset.
- **Option B — one merged paper.** Same freeze; a single NMI-centric submission carrying the
  human causal result and the two-lineage validation as twin pillars.
- **Option C — sequence (previous default).** Paper 1 runs first without any prediction freeze;
  Paper 2 then needs a *fresh* rule-change family with newly sealed outcomes, because Paper 1's
  published outcomes can no longer validate a prediction retroactively.

Under A and B the merge choice can be deferred to manuscript stage, because both papers draw on
the same prospectively frozen artifact. Under C it cannot. The enabling move is identical:
**freeze predictions before outcomes.**

## 2. What merging buys

- One truth asset serves both the causal claim and the validation claim; the marginal cost of
  the second paper falls to simulator work plus analysis.
- An NMI submission with human randomized ground truth is far harder to dismiss than either a
  lab-economics paper or a simulator benchmark alone; it directly answers "validated against
  what?".
- One pre-registration, one ethics package, one replication contract.

## 3. What merging costs or risks

- **Timeline coupling.** The human experiment waits for both simulator lineages to be frozen and
  benchmarked (equal-budget baselines, hard-negative regimes, cost–accuracy reporting). Option C
  publishes first and fastest; A/B delay the first submission by the simulator development time.
- **Venue tension.** NMI requires the AI-method contribution to be central. If the simulator
  component arrives thin (one rule change, two lineages, modest prediction accuracy), a merged
  paper risks rejection at NMI *and* misfit at the economics venues in one shot. Two papers let
  each claim find its natural referee.
- **Risk pooling.** If the human primary endpoint is inconclusive, the validation target is a
  wide interval; the merged paper weakens with it. Under Option A the economics paper has the
  same exposure, but the validation paper could still be reframed around the secondaries or a
  second rule family.
- **Contamination control.** Simulator calibration must use only public or prior data; no pilot
  outcome may reach either lineage before the freeze. This is a governance requirement, not a
  preference, and it binds the merged design hardest.

## 4. NMI sufficiency check for the merged form

Against the protocol's Nature-scale evidence contract: two independent system lineages —
satisfiable (learned differentiable simulator + LLM-agent simulator are genuinely independent
families); hard negatives and cost–accuracy frontier — must be built; real same-loop bridge —
this is precisely the sealed randomized human market; error control — prospective scoring rule
frozen pre-outcome. The irreducible-core risk is reviewer judgment that "predict one treatment
effect in one laboratory market" is an application, not a method. Mitigation: pre-commit a
*frozen battery* of predictions (primary speed endpoint, depth, spread, efficiency, surplus,
per-round learning slopes) across both arms and both rule families, so the paper evaluates a
predictive methodology rather than one number.

## 5. Recommendation

Adopt **Option A infrastructure with the B/C decision deferred**:

1. Build and freeze the two simulator lineages and their prediction battery before any human
   outcome access (this also preserves the C-sequencing fallback: if simulator work stalls, run
   the experiment anyway and fall back to Option C with a second rule family later).
2. Keep Paper 1's scientific contract exactly as repaired (primary speed endpoint; economics
   ladder unchanged). The prediction battery is registered as a separable module.
3. At manuscript stage, choose B (one NMI paper) if both pillars are strong; otherwise A (two
   companion papers with cross-disclosure) — both remain honest because the freeze was
   prospective.

No EcoMD integration, LLM-agent implementation, platform deployment, or participant work is
authorized by this note; each still requires its own outcome-blind decision.
