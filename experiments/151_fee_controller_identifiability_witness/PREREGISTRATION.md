# Experiment 151 preregistration — clean fee-controller identifiability witness

**Registered:** 2026-08-13, before Experiment 151 implementation, tests, freeze or execution

**Branch:** `algorithmic-fee-market-dynamics-v6`

**Parent:** `a8a75171a22c65b889090f640724c5e10ebe8e52`

**Scientific role:** generated identifiability and nontriviality attack only; no observed market evidence

## 1. Reason for a new experiment

Experiment 150 is permanently `VOID_PREMATURE_FORMAL_CELL_EXECUTION`: an ad hoc command executed its complete
seed loops before an implementation commit or freeze existed. Its exposed aggregate divergences are disclosed in
`experiments/150_fee_controller_identifiability_witness/PROTOCOL_DEVIATION_VOID.md`.

Experiment 151 is not a blind independent confirmation. It is a process-controlled reproducibility repair with a
disjoint seed root. It inherits Experiment 150's response/latent matrices, perturbations, regime lengths,
intervention geometries, numerical gates and interpretation without relaxation. The only scientific-config change
is seed root `15120260813`; the topology-baseline clarification and explicit seed labels are incorporated from the
start. No exposed Experiment 150 value was used to tune any choice.

## 2. Frozen linear witness class

Let normalized log fees, normalized excess use and latent workload be `q_t,y_t,h_t in R^2`:

\[
y_t=Aq_t+h_t,
\qquad q_{t+1}=q_t+K_r y_t,
\qquad h_{t+1}=\Phi h_t+\Gamma q_t+w_t.
\]

For each nonzero perturbation `Delta` and a declared development gain `K_0`, define

\[
A'=A-\Delta,
\quad h'_0=h_0+\Delta q_0,
\quad \Phi'=\Phi+\Delta K_0,
\quad \Gamma'=\Gamma-\Phi\Delta+\Delta(I+K_0 A').
\]

When the same innovations drive both systems, direct substitution yields `h'_t=h_t+Delta q_t` and therefore
identical observed `q_t,y_t` under `K_0`, despite `A' != A`. This is an elementary state-coordinate alias and a
negative-control witness, not a novelty theorem.

## 3. Frozen topology-specific comparisons

### BPO topology

The development gain is Prague/Osaka
`diag(1/8, G*6/5007716)`, `G=131072`. BPO1 and BPO2 change the second diagonal to
`G*10/8346193` and `G*14/11684671`. The alias transformation is constructed at Prague and left fixed through each
BPO intervention.

### Generated non-proportional topology

The development gain is `diag(1/50,1/50)`. The intervention is `diag(1/125,1/25)`, changing the two resource gains
in opposite directions. This is a generated topology inspired by public parameter variation, not one real Base
operation.

For each topology, perturbation and seed, run 512 shared-innovation development blocks, then branch from the same
end state into 128 zero-innovation intervention blocks. Do not reconstruct `(Phi',Gamma')` after intervention.

## 4. Frozen tasks and seed contract

The four perturbations, 128 seeds, matrices and counts are in `config.yaml`. Seed label:

```text
15120260813|<topology>|<perturbation_id>|<seed_index>
```

The first eight SHA256 digest bytes, interpreted as an unsigned big-endian integer, seed NumPy `default_rng`.
Reference/transformed systems in a cell share the innovation array.

For every cell, record only aggregate diagnostics:

1. response-matrix Frobenius distance;
2. development maximum observed difference across `q,y`;
3. algebraic residuals for the frozen `Phi'` and `Gamma'` identities;
4. both latent-transition spectral radii and finiteness;
5. post-intervention maximum and RMS observed divergence;
6. fraction of seeds meeting the divergence threshold per perturbation;
7. rank and singular values of `S=(K_r-K_0)^T tensor I_2`.

## 5. Frozen gates and decisions

### W1 exact alias and stable implementation

Every topology/perturbation/seed must have:

- `||A-A'||_F >= 0.20`;
- development maximum observed difference `<=1e-12`;
- both algebraic residuals `<=1e-14`;
- finite values and both latent-transition spectral radii `<0.995`.

### W2 BPO impotence

For BPO1 and BPO2:

- gain displacement from Prague `<1e-7`;
- maximum post-intervention observed divergence across all cells `<1e-7`;
- intervention stack rank at most 2 and minimum singular value `<1e-7`.

### W3 non-proportional separation

For every perturbation:

- at least 95% of 128 seeds have maximum observed divergence `>=1e-6`;
- intervention stack rank is 4;
- its minimum singular value is `>=0.01`.

### W4 assumption audit

The result must say that if latent dynamics may change freely by regime, the alias can be reconstructed for every
new `K_r`; W3 therefore depends on latent-dynamics invariance and does not identify real adaptation. It must also
state that BPO1/2 and Base same-chain episodes are not independent replication and that no real-data gate changes.

All W1--W4 pass gives `IDENTIFIABILITY_WITNESS_CONFIRMED`. W2/W3 failure gives
`INTERVENTION_GEOMETRY_INSUFFICIENT`. Hash, count, stability, arithmetic or resource failure gives
`IMPLEMENTATION_OR_SPEC_FAILURE`. No seed replacement, threshold relaxation, matrix change or rerun is allowed.

## 6. Binding interpretation

A pass means one controller regime cannot identify `A` without restrictions on latent dynamics; BPO1/2 add
negligible excitation; and a non-proportional second gain separates this finite class only under an explicit
invariance assumption. It does not unlock chain outcomes. V6 must next either supply a credible testable
invariance/partial-identification contract plus a future intervention and independent replication, or retire the
NCS candidate as `RETIRED_IDENTIFIABILITY`.

## 7. Chronology and resources

1. Push this preregistration/config/README before implementation.
2. Implement the module and focused tests; development tests may use only hand fixtures and seed indices outside
   `0..127` (specifically 10,000 and 10,001), never a formal Experiment 151 cell.
3. Push implementation, then separately commit/push `FREEZE.yaml` with exact hashes and dependency versions.
4. From a clean remote-verified checkout, execute exactly once to a complete-only JSON artifact.
5. Preserve and interpret any result without rescue.

One local Mac CPU process and one numerical thread are authorized, with at most 1 CPU core-hour, 2 GB RAM and 10
minutes. Network, chain outcomes, R2, remote hosts, V100s, RTX2060 and all GPUs are prohibited. Both V100 workers
and the RTX2060 remain idle and unqueued.
