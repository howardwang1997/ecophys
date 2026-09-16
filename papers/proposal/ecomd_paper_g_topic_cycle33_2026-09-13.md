# Paper G Cycle33: protein-function and quantum-decoding questions

2026-09-13, Pacific/Auckland. Four F1 screens: three closed formulations,
one provisional empirical-intervention question. No completed F2, F3,
forecast, machine card, or scientific execution.

The previous turn made progress by resolving the chemical candidate's
allocation status. That question remains parked. This round explores
unsaturated native objects under the existing cross-domain ICLR/ICML scope.
The cycle start precedes primary searches and question generation; individual
questions were developed during reading and are not prospective experimental
preregistrations.

## Results

| Question | Archetype | F1 decision | Reason |
|---|---|---|---|
| Separate protein epistasis from nonlinear assay response | Measurement | Closed | MAVE-NN directly addresses the generic proposal. |
| Use neural decoder confidence to measure logical-error risk | Measurement | Closed | Calibration and crossed decoder/score comparisons already have direct parents. |
| Interpret temperature-resistant protein function as improved stability | Empirical intervention | Closed | A primary experiment already distinguishes activity from stability; a distinct ML result was not specified. |
| Transfer a learned decoder across physical leakage-removal policies | Empirical intervention | Deferred | A named controlled experiment supports the native comparison; policy-transfer novelty and release qualification remain open. |

Seven primary works are retained, below the eight-work cap. Author repository
documentation is an additional resource record, not a research work.
The canonical graph had no exact prior formulation for these objects.
Broad similarities to past uncertainty or dynamical-system questions are
not treated as proof of duplication.

## 1. Protein epistasis versus nonlinear measurement

**Object.** A genotype-to-function map measured by a multiplexed variant assay.
The action is a specified mutation combination; the observable is the assay
readout under a fixed protocol.

**Rivals.** Observed nonadditivity represents molecular interactions, or it
arises from an additive latent phenotype followed by a nonlinear measurement.
Comparing combinatorial variants with an explicitly calibrated readout can
separate these explanations. A positive result identifies molecular
interactions; a null result prevents assigning assay nonlinearity to biology.

**Elementary control.** Let the latent values for wild type, two single
mutants and their double mutant be \(0,1,1,2\). With readout \(y=\phi^2\),
the observed interaction is \(4-1-1+0=2\), despite additive latent effects.
The readout is monotone over this example's latent range.

[MAVE-NN](https://link.springer.com/article/10.1186/s13059-022-02661-7)
already models a genotype-to-latent-phenotype map followed by a probabilistic
measurement process, with global-epistasis and noise models. Its discussion
also distinguishes what single- and multiple-mutation libraries support.
Thus the generic proposal to add an assay layer to a sequence predictor does
not supply an independent contribution. Close this formulation; retain the
latent/readout distinction as a required comparator.

## 2. Neural decoder confidence as logical-risk measurement

**Object.** The probability that a fixed quantum decoder's logical decision
is wrong, conditional on an observed syndrome history.
The decision is whether to accept or flag a shot at a declared acceptance rate.

**Rivals.** Better confidence reflects calibrated uncertainty, or the apparent
advantage mainly comes from better hard decisions and a different score
scale. Cross scores and hard decoders on identical syndromes; assess risk at
matched acceptance and calibration on separate data. Positive value is useful
risk information; null value is a bound on what the soft output adds.

**Elementary control.** Multiplying a binary logit by two preserves hard
decisions and confidence ordering but changes implied probabilities.
For an originally calibrated 0.9-confidence stratum, the transformed
probability is \(0.9^2/(0.9^2+0.1^2)\), about 0.988, while correctness
remains 0.9. Ranking, hard accuracy and calibration are separate properties.

[AlphaQubit](https://www.nature.com/articles/s41586-024-08148-8.pdf)
already reports output calibration in Extended Data Figure6.
[Dentelski, version3](https://arxiv.org/html/2606.08758v3)
compares GNN confidence with the matching logical gap and exchanges scores
between decoders, separating decision accuracy from score discrimination.
The work also qualifies calibration under noise changes. These are direct
parents for the generic measurement proposal. Close it; a new confidence
name or another reliability diagram is insufficient.

## 3. Temperature-resistant function versus thermal stability

**Object.** Functional output of the same bacterial-kinase variant across
assigned temperatures, with an independent stability measurement.

**Rivals.** High-temperature function improves because folding stability
improves, or because higher activity leaves more functional margin.
Paired temperature responses with activity and stability controls separate
these explanations. A positive result would support stability-guided design;
a null result would redirect the design target toward activity or other
mechanisms.

**Elementary control.** Set \(A_g(T)=c_g r(T)\), with \(r(T_0)=1\),
\(r(T_1)=0.4\), and variant amplitudes \(c_1=1,c_2=2\).
At a functional threshold of 0.7, both pass at \(T_0\), but only variant2
passes at \(T_1\). Their fractional temperature responses are identical.
This is a bookkeeping control, not a protein mechanism result.

[Ghose et al.](https://www.sciencedirect.com/science/article/pii/S2211124725012173)
already report temperature-resistant variants with increased enzymatic
activity rather than improved stability, and limits of computational stability
prediction for their observations. The inspected scope is the publisher's
summary and highlights; detailed assay, assignment and release contracts were
not verified. The generic biological distinction is therefore prior art.
No separate predictive or mechanistic ML result was specified in this screen.
Close this formulation, without concluding that condition-dependent protein
prediction is solved. MAVE-NN remains relevant to any later attempt to infer
latent activity from a nonlinear readout.

## 4. Retained question: decoding after a hardware policy change

**Native state and action.** Fix a quantum memory/stability circuit, its
round count, logical preparation, physical leakage-injection setting and
measurement protocol. Switch the hardware leakage reduction unit (LRU)
off or on. A leakage event here means population outside the computational
qubit subspace. It is distinct from data leakage in machine learning.

**Response.** Logical error risk when decoder parameters trained in one LRU
regime are held fixed and evaluated in another, relative to a decoder trained
for the target regime. All target labels and physical calibration information
used for adaptation must be charged to the comparison budget.

**Rivals.**

- The learned use of leakage flags captures sufficiently transferable
  error information; a policy switch mainly changes a few calibratable
  noise parameters.
- The decoder relies on policy-specific leakage persistence and correlations;
  changing the physical removal mechanism requires adaptation beyond nominal
  rate calibration.

These are proposed explanations, not conflicting published experimental
claims. The question concerns a physical intervention's effect on predictive
transfer, not a universal assertion that every neural decoder must fail.

### A concrete experimental capability

[Xin et al.](https://arxiv.org/html/2511.17460v1) describe physical LRU on/off
conditions, controlled leakage injection, logical preparations and shot-level
train/validation/test designs. Their comparison includes binary and ternary
readout information obtained from the same measurement records. They also
test training at different leakage rates. That existing rate-transfer result
must be acknowledged.

The inspected sections do not establish the proposed crossed transfer of
frozen weights between LRU regimes. This is an unresolved literature question,
not a claim of absence from the full release. Their
[author repository](https://github.com/MarcSerraPeralta/data-lru-integrated-with-measurement-for-qec)
links experimental data, preprocessing and training/evaluation scripts.
No archive, weights or outcome payload was accessed. File-level reuse rights,
block timing and complete observation/label joins still require qualification.

[McEwen et al.](https://www.nature.com/articles/s41567-023-02226-w)
provide an earlier physical leakage-removal parent. It does not turn the
selected small-code experiments into an independently replicated transfer
benchmark. The first empirical claim must stay within the circuits actually
supported by the chosen resource.

### Why matching a rate is insufficient, and why this is not a theorem paper

For a stationary two-state leakage chain with occupation probability \(\pi\),
choose transitions

\[
P(0\to1)=\pi(1-\rho),\qquad
P(1\to0)=(1-\pi)(1-\rho).
\]

Then \(E[L_t]=\pi\) and
\(\operatorname{Cov}(L_t,L_{t+k})=\pi(1-\pi)\rho^k\).
For \(\pi=0.1\), persistence values 0.9 and 0.1 give the same occupation but
lag-one covariances 0.081 and 0.009.
This elementary chain illustrates different temporal information at matched
occupancy; it does not prove that the experimental controls realize that
matching or predict a decoder's error rate.

[Varbanov et al.](https://www.nature.com/articles/s41534-020-00330-w)
already use hidden Markov models for leakage detection. A calibrated temporal
noise model is therefore a mandatory parent baseline. Merely fitting a
two-state chain or adding an LRU indicator to a network is not a new method.

Likewise, under one fixed target distribution an optimal decoder allowed
extra flags can ignore them, so its minimum risk cannot be higher than that
of a decoder denied those flags. A transferred learned decoder can behave
differently. Any observed penalty must be attributed to learning/transfer
under the declared information contract, not to extra physical information
being intrinsically harmful.

### Cheapest decisive comparison and advancement conditions

Construct, after separate authorization, the four risks \(R_{u\to v}\) for
training regime \(u\) and evaluation regime \(v\), each in \(\{0,1\}\).
Keep the target shots identical across evaluated decoders; use target-native
training as a labelled-data reference rather than a free oracle.
Compare frozen transfer, equal-budget fine-tuning, a shared-regime model and
a leakage-aware temporal baseline. Binary/ternary comparisons must preserve
their actual information relationship; they are not independently randomized
hardware treatments merely because they have different labels.

A positive result could identify a physical mechanism for transfer failure
and a useful adaptation rule. A null result could establish that existing
calibration transfers adequately within the tested policy range, avoiding
unnecessary retraining. Neither answer is observed here.

Before F2 completion, verify whether the public scripts or full paper already
include cross-LRU evaluation, qualify the dataset's conditions and rights,
and identify a residual beyond standard noise-model recalibration or
fine-tuning. Record acquisition blocks and drift controls before calling a
between-run difference a causal policy effect. No new hardware is required
for this source-contract work.

**Venue gate.** A four-cell transfer table alone is unlikely to justify
ICLR/ICML main. Advancement needs either a transferable mechanistic
measurement result or a method with a defensible gain over strong
noise-aware baselines, at a declared adaptation and decoding cost.
Broader code-distance, hardware and logical-operation claims remain
unqualified. Retain F1 only; no acceptance probability is asserted.

## Accounting and next action

The four question contracts and decisions are recorded in the Cycle33 screen,
search ledger, graph and memory. Paper G now has 65 formulations in 17 cycles,
with zero machine cards. The detailed ledger has 24 cycles and 149 raw
questions; historical-inclusive accounting is 33 cycles and 205 raw questions.
These are screening counts, not viable-paper counts.

The next bounded task is the exact QEC candidate's prior-art and source-contract
screen. The parked chemical topic stays parked. No implementation, scientific
run, dataset/model outcome access, hardware work, delegation or publication
has been performed.
