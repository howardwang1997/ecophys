# Experiment 151 result — fee-controller identifiability witness

**Formal decision:** `IDENTIFIABILITY_WITNESS_CONFIRMED`

**Formal run commit:** `46bca15f0a11b562da44b82ae7c87e18e6918b36`

**Raw artifact:** `artifacts/raw/witness.json`

**Raw artifact SHA256:** `6b81a0eddac2fc16697382128dff5621b75cb52d1bf8712e4a0f3193f431c649`

## Chronology and integrity

Experiment 150 remains permanently void because its formal seed loops were exposed before implementation and
freeze. Experiment 151 was preregistered at `49628f37fc9636eb78e5d9fffa5fbe7ac98c09c6` with a disjoint seed root
and unchanged scientific matrices, thresholds and interpretations. The implementation was committed and pushed
at `2110585aa587450f90f8a292739b060105cce48e`; the independent freeze was committed and pushed at the formal-run
commit above. The local and remote branch heads matched, the checkout was clean and the output was absent before
the sole formal attempt.

No Experiment 151 formal cell was run before freeze. The frozen command was executed once and exited zero. The
output now exists and the runner refuses overwrite; no rescue run is allowed.

## Frozen gates

| Gate | Result | Decisive value |
|---|---:|---|
| W1 exact alias and stability | pass | maximum development observed difference `4.16334e-16` versus `1e-12` gate; every response-distance, algebra, stability and finiteness check passed |
| W2 BPO impotence | pass | maximum gain displacement `6.27208e-9`; maximum observed divergence `3.51301e-10`; stack rank `2`, minimum singular value `0` |
| W3 non-proportional separation | pass | stack rank `4`, minimum singular value `0.012`; all four perturbations had `128/128` seeds above `1e-6` |
| W4 assumption audit | pass | separation requires invariant latent dynamics; regime-specific latent dynamics restore the alias |
| count contract | pass | 4 perturbations, 128 seeds, 1,024 development cells, 1,024 BPO and 512 non-proportional intervention cells |
| resource contract | pass | 14.8866 s wall, 14.8160 s CPU, 0.03989 GB peak RSS |

The minimum maximum-divergence over the 128 seeds was `1.50466e-5` for the execution-column perturbation,
`1.49687e-5` for the blob-column perturbation, `1.13746e-5` for the cross-resource perturbation and
`8.09087e-5` for the strong cross-resource perturbation. These all exceed the frozen `1e-6` threshold. In
contrast, the BPO execution-column divergence was at floating-point noise and the maximum over every BPO cell was
only `3.51301e-10`.

## Reporting audit

The raw artifact records the all-cell W1 conjunction and topology/perturbation summaries rather than a 1,536-row
per-cell table. The frozen config, implementation and hashes make the calculation reproducible, and every frozen
decision quantity is present either as an all-cell gate or a group summary. This compact representation is less
auditable than retaining every cell diagnostic, so no later work may relabel it as a per-cell audit dataset or
rerun Experiment 151 to expand the output. The limitation does not support a positive claim and is preserved with
the result.

## Binding interpretation

The generated witness confirms three narrow statements:

1. under one fixed controller gain, observationally distinct response matrices can produce exactly the same
   observed fee/use path after a compensating latent-state transformation;
2. Prague-to-BPO1/BPO2 gain changes are both numerically tiny and rank-deficient for this two-resource response;
3. a deliberately non-proportional full-rank gain change separates the frozen finite alias class only when the
   latent transition law is held invariant across regimes.

This is an elementary identification boundary, not a new theorem, real-market result, adaptive-demand estimate or
independent confirmation. If latent demand dynamics may change with the intervention, an alias can be rebuilt in
the new regime. Experiment 151 therefore does not unlock Base or Ethereum outcomes, remote workers or GPUs. The
V6 candidate must be judged against its still-missing invariance, prospective-intervention and independent-
replication contracts.

## Execution audit

- Python 3.11.15, NumPy 2.4.4 and PyYAML 6.0.3;
- one local Mac CPU process and one numerical thread;
- zero chain-outcome files, network calls, remote hosts and GPU-hours;
- both V100 workers and the RTX2060 remained idle and uncontacted.
