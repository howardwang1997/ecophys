# Paper G: bounded LRU decoder-transfer review

PRIVATE / INTERNAL research-selection record. 2026-09-13 NZ.
This is a source and analytic review, not an experimental result or publication artifact.

**Decision: park the exact candidate g33_lru_decoder_policy_transfer.** The physical question remains unresolved. A targeted six-work collision screen and source contract review do not yet establish an increment over noise-aware decoding and equal-budget adaptation, or qualify the acquisition/rights contract for the proposed empirical attribution. This is a nonterminal allocation decision, not a proof that policy transfer is uninteresting or impossible. Stop this source chain pending a substantive resource or contribution change.

This follows Cycle33 without adding a question or cycle. One additional primary work brings its total to eight, consuming its declared primary-work budget. Six QEC works are considered below; the two protein works are not counted toward this review. No full fifteen-work audit, forecast, machine card or scientific execution follows.

## Prior-work collision

| Primary work | Relevant contribution already occupied | Boundary for this candidate |
|---|---|---|
| [Xin et al., arXiv:2511.17460](https://arxiv.org/html/2511.17460v1), III.4 and VI.2 | Cross-leakage-rate evaluation; physical LRU conditions; simulations varying removal and readout parameters | These are not automatically the frozen-weight, hardware cross-policy estimand. Figure S7 describes point-specific training, so the phrase “same NN decoders” cannot establish shared weights. |
| [Overcoming leakage, 2023](https://www.nature.com/articles/s41567-023-02226-w) | Physical leakage removal and its effect on correlated errors | Hardware mechanism prior, not an independent replication of cross-policy ML transfer |
| [Varbanov et al., 2020](https://www.nature.com/articles/s41534-020-00330-w), Hidden Markov models | Temporal leakage inference from neighboring defects and ancillary readout | Its leakage detector and post-selection are not a complete all-shot logical decoder |
| [AlphaQubit, 2024](https://www.nature.com/articles/s41586-024-08148-8), Fig. 3 and Methods | Noise-model pretraining followed by limited experimental-data finetuning; noise-aware matching comparators | Generic hardware adaptation and a comparison only with untuned MWPM are insufficient novelty |
| [Dentelski et al., v3](https://arxiv.org/html/2606.08758v3), exchanged-score comparisons | Separation of hard decoding from confidence-based selection on shared shots | A confidence improvement is not itself improved all-shot correction |
| [Varbanov et al., PRR 7, 013029](https://doi.org/10.1103/PhysRevResearch.7.013029), [preprint v2, III.2–III.4](https://arxiv.org/html/2307.03280v2) | Noise-model-trained recurrent decoders evaluated on hardware; correlated matching/tensor-network comparisons and soft readout | Another recurrent decoder or simulation-to-hardware evaluation alone adds no distinct mechanism |

These papers do not present a matched pair of contradictory claims about the proposed intervention. The rival explanations below remain our hypotheses. This is a bounded collision review, not exhaustive novelty clearance or a completed, qualified F2 truth contract.

The [Xin submission history](https://arxiv.org/abs/2511.17460) identifies v1, submitted 21 November 2025. A later date rendered inside HTML does not create another submission version. The precise PDF-to-source release mapping is still not pinned; no execution provenance is inferred from the moving repository branch.

## What the author source establishes

The following selected source files were read, never executed. Their hashes are in the accompanying YAML.

- [Training entry point](https://raw.githubusercontent.com/MarcSerraPeralta/data-lru-integrated-with-measurement-for-qec/main/scripts_training_and_evaluation/train_memory.py): one configuration supplies the training and validation experiment and input channels.
- [Memory evaluation](https://raw.githubusercontent.com/MarcSerraPeralta/data-lru-integrated-with-measurement-for-qec/main/scripts_training_and_evaluation/evaluate_memory.py) and [stability evaluation](https://raw.githubusercontent.com/MarcSerraPeralta/data-lru-integrated-with-measurement-for-qec/main/scripts_training_and_evaluation/evaluate_stability.py): enumerate model directories within one named experiment, reload each model's configuration, and pass it to evaluation.
- [Training loader](https://raw.githubusercontent.com/MarcSerraPeralta/data-lru-integrated-with-measurement-for-qec/main/scripts_training_and_evaluation/lib/util.py) and [evaluation functions](https://raw.githubusercontent.com/MarcSerraPeralta/data-lru-integrated-with-measurement-for-qec/main/scripts_training_and_evaluation/lib/evaluation.py): read the requested split under config.experiment_dir. The inspected call chain does not explicitly cross two independently specified LRU directories. This does not exclude other configurations, scripts, releases or unpublished analyses.
- [Experimental preprocessing](https://raw.githubusercontent.com/MarcSerraPeralta/data-lru-integrated-with-measurement-for-qec/main/scripts_data_pre-processing/dclab-format_to_qrennd-format_memory-experiment_experimental-data.py): integer shot records become anc_meas[shot,round,ancilla] and data_meas[shot,data_qubit], with ideal measurements and coordinate metadata. LRU regime is carried by the parent directory; injected-leakage setting, round count and preparation are carried by subdirectory naming.
- [Input/label transformation](https://raw.githubusercontent.com/MarcSerraPeralta/data-lru-integrated-with-measurement-for-qec/main/scripts_training_and_evaluation/lib/preprocessing.py): for memory experiments, ternary value 2 supplies a leakage flag and is mapped to 1 for binary processing. The label is the parity of final data flips relative to the ideal preparation. Detector inputs and the final parity-check projection are distinct from this label.
- The inspected [software licence](https://raw.githubusercontent.com/MarcSerraPeralta/data-lru-integrated-with-measurement-for-qec/main/LICENSE) is MIT. It does not settle the experimental archive's independent rights.

The preprocessing script deterministically shuffles shots and reindexes them, with a 7.5% validation fraction from training input. Its output schema does not itself supply acquisition timestamps, calibration blocks or treatment assignment order. The raw archive may contain those records; absence from this interface does not prove absence from the archive. Reconstructing order may be possible with raw row identities and the permutation. A random shot split also does not itself provide an untouched chronological confirmation partition.

No archive, weights, prediction arrays or figure-data payload were inspected. Source readability establishes interface capability, not dataset completeness or measured model performance.

## Five-part question contract

1. **X:** circuit family, logical preparation protocol, round count, gate schedule, injection setting, readout channel definition, acquisition/calibration block, and complete relevant noise state. Memory and stability experiments remain separate tasks.
2. **do(A):** physical LRU on/off with the other protocol components fixed or explicitly measured. Training-policy choice and readout representation are separate factors. Merely grouping two acquisition campaigns does not identify a causal LRU effect.
3. **Y:** all-shot logical error risk at each fixed round count, with paired model comparisons on the same target shots. Risk-curve slopes are secondary, requiring a frozen fit range and model. Confidence and post-selection require separate metrics.
4. **H1:H0:** policy-specific dependencies require adaptation beyond a calibrated temporal noise model versus a low-dimensional noise update explaining transfer. Neither explanation currently has a verified effect size. A positive answer must identify reproducible residual error structure; a null answer must bound adaptation cost or excess risk at a predeclared useful tolerance.
5. **T:** the named hardware source is a partial truth asset. Observation and label interfaces exist. Assignment order, acquisition blocks, calibration/readout joins, archive rights and an untouched confirmation partition remain unqualified. Independent hardware replication is not established.

## Second killer control: a raw risk gap is not transfer failure

Write R_v(f) for risk on target regime v. The commonly tempting difference decomposes exactly:

\[
R_1(f_0)-R_0(f_0)
=\big[R_1(f_0)-R_1(f_1)\big]
 +\big[R_1(f_1)-R_0(f_0)\big].
\]

Only the first term compares trained models on the same target distribution. Even this term is relative to a learned comparator, not Bayes excess risk, and can have either sign.

As an elementary counterexample, let Y=X XOR E_v, with E_v independent Bernoulli noise of probability p_v<1/2 and the same X distribution in both regimes. Both Bayes classifiers are f_0(X)=f_1(X)=X. Taking p_0=0.01 and p_1=0.10 produces a raw nine-percentage-point risk increase while the same-target transfer penalty is exactly zero. This is an analytic toy, not a realizable LRU experiment, new theorem or empirical estimate.

The Cycle33 matched-occupancy/different-persistence chain remains useful, but matching a mean rate alone is a weak baseline. Under a correctly specified finite-state model with identified target transition and emission kernels, standard Bayesian filtering supplies the target state posterior:

\[
b_t(s)\ \propto\ E_v(x_t\mid s)\sum_{s'}P_v(s\mid s')b_{t-1}(s').
\]

A complete decoder additionally requires the joint logical-error state and its coupling to leakage. Independent per-qubit leakage beliefs alone need not be sufficient. Neither target-kernel identification nor the adequacy of this factorization is established for the chosen hardware. Consequently, “add a memory variable” or “replace transition parameters” is not yet a new algorithmic contribution.

## Decisive comparison and allocation

Any eventual experiment must compare frozen source weights, equal-target-label-budget finetuning, a shared-regime model, and a calibrated temporal/noise-aware decoder on identical target shots. Charge source pretraining, target calibration, labels, inference latency and seeds separately. Use uncertainty that respects acquisition blocks; millions of shots do not create millions of independent hardware interventions.

The smallest useful result would establish a stable residual beyond these controls, or a practically tight null bound on the need for adaptation. A four-cell table by itself does neither. Choosing a tolerance, sample size or hardware claim now would outrun the untouched-partition and acquisition contracts.

**Resume only** when a methods-linked manifest resolves the named acquisition/label/calibration/rights joins and supports an untouched target partition, or when a concrete methodological/theoretical result changes the incremental contribution. Any resumption needs a bounded review allocation after this cycle's eight-work cap; no source-chain continuation is implicit.

Next discovery work should use the already authorized cross-domain scope to start a new unsaturated, archetype-balanced cycle. This decision does not close quantum ML or require the entire field to satisfy a Nature-scale activation standard.

Paper G totals remain 65 formulations / 17 cycles / 0 machine cards. The full ICLR/ICML research objective remains active and incomplete.
