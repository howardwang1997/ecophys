# Experiment 150 preregistration — closed-loop fee-controller identifiability witness

**Registered:** 2026-08-13, before implementation, tests, freeze or execution

**Branch:** `algorithmic-fee-market-dynamics-v6`

**Parent:** `133e8182f8f6120adcd92441a8a41d041d6a40e8`

**Scientific role:** generated identifiability and nontriviality attack only; no observed market evidence

**Clarification before implementation:** the witness is constructed separately at each topology's declared
development controller: Prague/Osaka for the BPO1/BPO2 comparison, and generated `K_0` for the generated
non-proportional comparison. This resolves an ambiguity between Sections 3 and 4 of the first committed text. No
matrix, seed, threshold, decision mapping or outcome was changed, and zero formal cells had executed.

## 1. Question

Does one exact controller regime identify a local behavioral fee-response matrix when latent demand has its own
state, and are the official BPO schedule changes large enough to break any resulting observational alias? Under a
strict additional assumption that latent demand dynamics are invariant across regimes, can one sufficiently
non-proportional controller change identify the response?

This experiment tests a claim boundary. It does not test whether real users adapt, whether the linear DGP is true,
or whether any estimator deserves an NMI claim.

## 2. Frozen linear witness class

Let `q_t in R^2` be normalized log fees, `y_t in R^2` normalized execution/blob excess use and `h_t in R^2` an
unobserved workload state. For controller gain matrix `K_r`,

\[
y_t=Aq_t+h_t,
\qquad q_{t+1}=q_t+K_r y_t,
\qquad h_{t+1}=\Phi h_t+\Gamma q_t+w_t.
\]

All matrices, initial states, noise arrays, regime lengths and tolerances are fixed in `config.yaml`. The reference
system uses `(A,Phi,Gamma)`. For each frozen nonzero alias perturbation `Delta`, define

\[
A'=A-\Delta,
\qquad h'_0=h_0+\Delta q_0,
\]

and, for the development gain `K_0`,

\[
\Phi'=\Phi+\Delta K_0,
\qquad
\Gamma'=\Gamma-\Phi\Delta+
\Delta(I+K_0 A').
\]

Both systems receive the same frozen innovation `w_t`. Direct substitution then gives the pathwise invariant
`h'_t=h_t+Delta q_t` and hence `y'_t=y_t`, `q'_t=q_t` for every development observation. The two systems have a
different behavioral response matrix whenever `Delta != 0`.

This construction is an elementary closed-loop state-coordinate alias, not a new theorem. The formal run exists
to verify it against the exact frozen arithmetic and intervention geometries and to prevent an invalid empirical
identification claim.

## 3. Frozen controller regimes

### 3.1 BPO scale family

The execution diagonal is fixed at `1/8`. The blob diagonal is the ideal normalized EIP-4844 gain
`G*T/F`, with `G=131072`, for Prague/Osaka, BPO1 and BPO2. The schedule constants are exactly those in
EIP-7892 and Experiment 149. No observed fee or utilization value is used.

The formal report must calculate the Euclidean gain displacement from Prague to BPO1/BPO2. The current metadata
audit predicts order `1e-9`; the result is a protocol-constant diagnostic, not a blind discovery.

### 3.2 Non-proportional gain change

The generated development controller is `K_0=diag(1/50,1/50)`. The generated test controller is
`K_1=diag(1/125,1/25)`, deliberately changing the two resource gains in opposite directions. It is inspired only
by the topology of official Base denominator changes and is not claimed to be one real Base operation.

## 4. Frozen formal tasks

For each of the four perturbation matrices in `config.yaml`, both topology-specific development controllers and
every one of 128 SHA256-derived innovation seeds:

1. construct `(Phi',Gamma')` using the topology's development gain: Prague/Osaka for the BPO topology and
   generated `K_0` for the non-proportional topology;
2. run the reference and transformed system for 512 blocks under that development gain with shared innovations;
3. verify maximum absolute difference across all observed `q_t,y_t` is at most `1e-12`;
4. continue both systems for 128 zero-innovation blocks under each intervention geometry, without changing any
   behavioral or latent-state parameter;
5. record the maximum and RMS observed divergence for BPO1, BPO2 and the non-proportional gain;
6. calculate the rank and singular values of the intervention stack
   `S=[(K_r-K_0)^T tensor I_2]`, which maps `vec(Delta)` to the latent-transition change required to maintain the
   alias under another gain;
7. verify the exact algebraic residuals for `Phi'-Phi-Delta K_0` and the frozen `Gamma'` identity.

The exact innovation label is
`15020260813|<topology>|<perturbation_id>|<seed_index>`. The first eight SHA256 digest bytes, interpreted as an
unsigned big-endian integer, seed NumPy's `default_rng`. Reference and transformed systems in a cell share the
resulting innovation array; different topology labels intentionally produce independent arrays.

The report contains aggregate maxima/minima, ranks and gate decisions only. Individual generated paths are not
needed for interpretation.

## 5. Frozen decision gates

### W1 — exact single-regime alias

Every perturbation/seed cell must satisfy:

- `||A-A'||_F >= 0.20`;
- development maximum observed difference `<=1e-12`;
- both algebraic construction residuals `<=1e-14`;
- finite values and spectral radii `<0.995` for both latent transition matrices.

Failure is `IMPLEMENTATION_OR_SPEC_FAILURE`, because the declared witness was not reproduced.

### W2 — BPO intervention impotence

For both BPO1 and BPO2:

- controller-gain displacement from Prague is `<1e-7` in Frobenius norm;
- maximum observed divergence across all cells is `<1e-7`.

Passing W2 means these official schedule changes do not practically separate the frozen aliases at the declared
precision. It is a negative identifiability result, not a positive scientific claim.

### W3 — non-proportional separation

For every perturbation matrix, across 128 seeds:

- at least 95% of seeds have maximum observed divergence `>=1e-6` under `K_1`;
- the intervention stack has rank 4 and minimum singular value `>=0.01`;
- the corresponding BPO intervention stack has rank at most 2 and minimum singular value `<1e-7`.

Passing W3 shows only that a sufficiently diverse second controller is capable of separating this finite witness
class under invariant latent dynamics.

### W4 — assumption audit

The output and interpretation must state:

- if `(Phi,Gamma)` may change freely across regimes, the transformed system can be reconstructed for each new
  `K_r`, so any finite collection remains aliased;
- therefore W3 depends on latent-dynamics invariance and cannot establish causal behavioral adaptation by itself;
- Base same-chain episodes and BPO1/2 are not independent replication;
- no real-data gate changes after this result.

The overall expected decision is `IDENTIFIABILITY_WITNESS_CONFIRMED` only if W1--W4 all pass. Any W2 or W3 failure
is `INTERVENTION_GEOMETRY_INSUFFICIENT`. A numerical, hash, count, stability or resource-contract failure is
`IMPLEMENTATION_OR_SPEC_FAILURE`. There is no threshold relaxation, seed replacement or rerun rescue.

## 6. Binding research decision

Even a full pass implies:

1. one controller regime cannot identify behavioral fee response without restrictions on latent dynamics;
2. BPO1/2 do not add practically independent controller excitation;
3. non-proportional interventions may identify the frozen linear class only after assuming latent dynamics are
   invariant across regimes.

Consequently a pass must not unlock chain outcomes. V6 can proceed only by writing a credible, testable latent-
dynamics invariance/partial-identification contract plus a future intervention and independent replication. If no
such contract can be defended after this witness, V6-NCS-1 must be retired as `RETIRED_IDENTIFIABILITY`; it may not
be rescued by fitting a more expressive model.

## 7. Chronology and resource boundary

1. Commit and push this preregistration, config and README before implementation.
2. Implement an independent deterministic module and focused tests; no formal task may execute during development.
3. Commit and push implementation, then separately freeze exact hashes and dependency versions.
4. From a clean remote-verified checkout, execute exactly once and write a complete-only JSON artifact.
5. Preserve a pass or failure unchanged and update all ledgers, graph, memory and plan.

Authorized resources are one local Mac CPU process, one numerical thread, at most 1 CPU core-hour, 2 GB RAM and
10 minutes. Network, chain data, R2, remote hosts, V100s, RTX2060 and all GPUs are prohibited. The two V100 workers
and RTX2060 remain idle and unqueued.
