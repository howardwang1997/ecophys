# Paper G: bounded response exploration preflight

PRIVATE / INTERNAL. PRE-AUTHORIZATION ONLY — DO NOT RUN.
No candidate, new search cycle, qualified trigger, or status promotion.

## Decision to review

Propose one disposable CPU campaign to resolve the empirical uncertainty
explicitly retained by the G29 closure: finite-budget nonlinear behavior of
history predictors and ordinary correctly labelled impulse augmentation.
The [closure](ecomd_paper_g_history_response_resolution_2026-09-09.md) establishes
neither practical prevalence nor finite-sample performance. Its linear fixture
is already resolved; this proposal does not rerun it or claim that its generic
failure or remedy is novel.

The current literature-only route has diminishing decision value. A bounded
negative result here would stop further response-method work for this fixture.
A residual discrepancy would only motivate a separate contribution analysis;
it would not establish novelty, a new physical mechanism, or a publishable
benchmark. The broader Paper G objective remains ICML main, NMI or NCS.

The repository connection is its learned PDE rollout and constraint-attribution
program, together with G29's history/physical-response boundary. This asset
cannot establish a financial-market mechanism. The bounded fork is between
(A) ordinary matched pulse supervision sufficing for the declared mean response
while retaining useful history, and (B) a reproducible response discrepancy
remaining in a competent history predictor under that same supervision.
Branch B would describe only these fitted models and budgets; it would not
identify an intrinsic memory/response tradeoff or exclude optimization effects.
The value of this probe is a stopping decision about this fixture, not a
publication forecast. It passes no novelty gate merely by being proposed.

Requested scope: preparation of an original disposable implementation, an
outcome-free dependency/image and isolation freeze, independent runtime review,
and one campaign after its separate immutable machine authorization is merged.
The existing protocol's guards remain binding. Nothing in this preflight
authorizes implementation, image creation, outcome access, or execution now.

## Scientific object and reference

Use the finite Fourier–Galerkin viscous Burgers system on `[0,2*pi)`, viscosity
`nu=0.05`, retained modes `-16,...,16`, real field, and zero mean. Its exact
finite-dimensional definition is

`du_k/dt = -(i*k/2) sum_{p+q=k} u_p*u_q - nu*k^2*u_k`,

with the convolution over retained modes and `u_-k=conj(u_k)`. Products must
implement this convolution without aliasing. This is the stipulated discrete
truth, not a certified continuum solution or a model of a financial market.

Initial fields use independent standard Gaussian sine/cosine coefficients in
modes 1–8, divided by mode index and normalized to spatial RMS one. Record all
32 real state coefficients. Generate 40 observation intervals of length 0.05.
Reference integration uses DOP853 with `rtol=1e-10, atol=1e-12`. The first branch
cross-checks against fixed-step RK4 at 0.00125 and 0.000625, using identical
states, pulses and observation times. Require relative state disagreement
below `1e-5` and mean-mode drift below `1e-12`; otherwise stop the campaign.
The check subset is the first eight sorted units from each of the three
partitions, their unforced trajectories, and all four paired contrasts at
index 15. Compare both RK4 resolutions with DOP853 at all recorded times;
normalize state differences by `max(norm(reference state),1e-12)`. This finite
check is an accuracy screen on these cases, not an interval error certificate.
These two algorithms are a numerical check, not independent scientific lineages.

Use two declared observation regimes of this same system: all modes 1–16,
and only modes 1–4. The latter omits physical modes 5–16; it is explicitly
partial observation. Each history contains four consecutive observations.
Initial-state, training and evaluation units are shared across observation
regimes. No result may be interpreted as proving that history is universally
harmful or that four frames identify every latent state.

## Legal intervention and primary estimand

After recording the history, apply `u -> u +/- a*b_k`, where
`b_k(x)=sqrt(2)*cos(k*x)`, `k in {1,4}`, and `a in {0.02,0.04}`.
Evaluation resets occur at observation index 15, physical time 0.75; history
indices are 12–15, and the final response is at physical time 1.00. Time 0.25
in the response formula below means elapsed time since reset.
Hold every earlier frame and omitted mode fixed. No force remains after this
instantaneous reset. Follow the same finite-dimensional dynamics for five
observation intervals. This has a complete pre-reset/post-reset lifecycle;
there is no replacement of the entire history or unknown future input.

For `Y_k(u)=<b_k,u>` using the spatial-average inner product, the primary target
is the ensemble mean paired finite-amplitude response

`R_k(a)=mean_i[(Y_k(u_i^+(0.25))-Y_k(u_i^-(0.25)))/(2*a)]`.

Use the same initial realizations and reset times for reference and predictors.
Earlier history weights remain unchanged. Evaluate all four `(k,a)` contrasts;
none is selected after seeing the results. Compare ensemble responses, not a
claim that a partial-state predictor can recover each hidden realization's
response. Per-realization errors are secondary diagnostics only. Require
reference responses at the two amplitudes to differ by at most 5% of
`max(abs(R_k(0.02)),0.1)` to interpret the probe as approximately linear.
Otherwise report finite-amplitude responses and stop the linear-response lead.

## Methods and matched accounting

Use a complete two-by-two comparison: current observation or four-frame
history, each trained with or without correctly labelled physical pulses.
The current-only augmented arm is essential: comparing only an augmented
history model with an unaugmented current model confounds observation and
training support. All models use two hidden tanh layers with equal width.
For full observation, widths are 92 (current) and 64 (history), giving 14,568
and 14,496 parameters. For partial observation, widths are 74 and 64, giving
6,816 and 6,792 parameters. Augmentation changes no architecture. The count
includes every bias; output dimensions are respectively 32 and 8. No search.
Predict next-state increments; omission of the zero mode preserves the declared
mean in all models. Fit normalization on training units only. Use Adam, learning
rate `1e-3`, batch size 128, at most 200 epochs, and fixed initialization seeds
201 and 202. Select the final epoch; no best-seed or best-checkpoint selection.

Each fit uses exactly 4,000 labelled one-step training examples. Define the
unforced pool by 128 training units and current indices 3–34 (4,096 windows).
Order it with a frozen PCG64 permutation, seed 301. Ordinary arms use the
first 4,000 windows; augmented arms use the first 2,000 plus 2,000 pulse-path
windows. The latter come from 200 paired reset cases, 50 per `(k,a)` contrast,
with both signs followed for five steps: `200 x 2 x 5 = 2,000` labels.
For each contrast, select the first 50 distinct `(training unit, reset index)`
pairs from the pool with indices 3–30 using PCG64 seeds 310–313 in the frozen
order `(1,.02),(1,.04),(4,.02),(4,.04)`. These choices precede outcomes.
For later windows in a pulse path, use the correctly evolved post-reset
history. A first-step-only augmentation would leave the subsequent changed
histories untrained and would not be a matched rollout-support control.

Training and evaluation use the same directions and amplitudes. Fit shared
per-coordinate means and standard deviations from all unforced training-unit
states at indices 0–40; floor each standard deviation at `1e-8`. Share these
constants across arms, use the same constants for every history frame, and
normalize increments by scale alone. The 4,000 count concerns supervised examples, not total
solver calls: trajectory generation, checks and evaluation have extra cost.
Report that cost separately and keep it inside the campaign cap. Evaluate
forecasts and response using the same five-step autoregressive procedure,
including a sham reset.

Use 128 training initial-state units, 32 diagnostic units and 32 response units,
all disposable. Model initialization changes do not create new physical units.
Both initialization results and every fixed contrast must be reported. The
small campaign is not powered to support a publication claim. Uncertainty
summaries, if produced, describe exploration only and never gate confirmation.
Diagnostic units supply the unforced forecast screen at indices 15–20;
response units supply the paired intervention screen. No checkpoint selection
or parameter adjustment uses either partition. Define forecast NRMSE as the
square root of pooled squared observation error over units and the five output
times, divided by the square root of pooled squared reference observations
over the same entries. All units share the zero-mean Fourier convention.

## Budget and stopping decisions

- 16 branches maximum: `4 methods x 2 observation regimes x 2 initializations`.
  The first branch performs reference qualification before its fit; a failed
  check prevents that fit and all later branches. This is one declared request,
  not an unrecorded extra execution. Qualification results are operational only.
- 10,800 CPU-seconds total: 1,200 for reference checks and 600 per fit, including
  regeneration of its frozen data and evaluation. First branch reservation is
  1,800 seconds; each remaining branch reserves 600. One CPU core per branch.
  Fixed order: full then partial observation; within each, current/unaugmented,
  current/augmented, history/unaugmented, history/augmented; within each arm,
  initialization 201 then 202. No model-selection or pruning changes this order.
- 1,000,000,000 stored bytes; at most 60,000,000 output bytes per branch.
- Zero GPU time, paid services, dataset purchases, outreach or production changes.
- Expire seven days after machine authorization; no automatic budget extension.

Stop at any reference, replay, isolation or budget failure. Stop as inconclusive
if no predictor in a regime attains five-step forecast NRMSE below 0.10, or if
the two initializations disagree on the screening decision. This threshold is
a prospective engineering screen, not a validated definition of model quality.

For competent models, report normalized response error
`abs(R_model-R_ref)/max(abs(R_ref),0.1)`. For each observation regime, if the
augmented history model has all four errors below 0.10 in both initializations
without more than 20% deterioration relative to its unaugmented history
forecast NRMSE, stop further response-method work on that regime of this fixture.
This is a decision about the mean target only: cancelling realization-level
errors can remain. Also report per-unit response RMSE, without using it to
replace the primary target after inspection.

A residual branch merits a subsequent contribution audit only if both
initializations satisfy all of the following in the partial-observation regime:
the augmented history model is forecast-competent; its forecast NRMSE is at
least 20% lower than the augmented current-only model's; and at least one
same fixed contrast has response error above 0.25 for augmented history and
below 0.10 for augmented current-only. Report every contrast, including those
that disagree. This isolates an empirical combination of useful history and
worse mean response within the frozen comparison; it is not a causal theorem
about history or a novel method. Other outcomes, including both augmented
models failing, intermediate response errors, no history benefit, or seed
disagreement, stop as inconclusive rather than invite an automatic retry.
All numerical thresholds are provisional exploration screens. Known support
mismatch, missing-state uncertainty, forecast failure, or ordinary training
limitations are not scientific discoveries. No result automatically authorizes
a new candidate, a bigger experiment or a claim.

## Provenance, confirmation and prerequisites

No existing Paper D outcomes, checkpoints, raw data or crash periods are used.
The proposed numerical implementation is original disposable analysis; upstream
package licences and transitive dependencies must be frozen before image build.
Local package metadata was inspected only to assess preparation feasibility;
it is not an OCI runtime qualification.

All units and outputs are permanently `sandbox_exploratory_tainted`. Each
branch regenerates data from its frozen config, so no host repository or
previous outcome tree must be mounted. The image has no network, secrets,
confirmation data or GPU access; only a read-only config and bounded stdout tar
channel are allowed. Every branch request precedes execution in the hash chain.

Before running, materialize sorted exploration identifiers; freeze provenance,
dependency lock, code/config/image digests and campaign fingerprint. Reserve
confirmation identifiers through the protocol's future-public-randomness rule,
whose values must not exist until after DX termination and a later D0 freeze.
Known withheld numeric seeds do not qualify. If a valid partition cannot be
frozen, stop preparation. Independent confirmation and scientific replication
need separate future contracts; this campaign does not supply them.

The August 25 Colima conformance report concerns its pinned probe image only.
It cannot certify this proposed scientific image or replace independent runtime
review. A separate authorization-only merge must precede every scientific
branch. No operational defect, repair or failed preparation may enter public
research evidence. The current authorized-sandbox count remains zero.
An ambiguous interruption follows the existing quarantine rule: prove the
named container absent, assume exposure, charge its full reservation and
terminalize; never retry that branch.

The September 8 Paper G development and re-entry decisions authorize named M0
inventory/access experiments and theorem checks. The September 6 blanket
decision names ten pre-D0 market-asset actions. Neither contains this Burgers
campaign; their source authorization text is preserved without extending the
recorded scope by inference. The present request therefore remains separate.

This preflight is the reviewable scope, not a completed sandbox manifest. The
remaining image, unit, review and machine-decision prerequisites are explicit
so that approval cannot be mistaken for a claim that they have already passed.
