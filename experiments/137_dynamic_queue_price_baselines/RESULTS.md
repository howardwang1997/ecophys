# Experiment 137 results — dynamic queue/price bridge with strong observation baselines

**Run date:** 2026-08-10

**Preregistration commits:** `69266f26`, followed by the pre-result executable-removal clarification
`fc9aff87`

**Implementation commit:** `ba763c7dd748d32ef71d5ae49efc41cec5b23f3b`

**Decision:** all 9 frozen hard gates PASS; the dynamic synthetic bridge may proceed to external-data and
continuous-time baseline work, but G3 remains open

## Execution audit

The formal run used two independent 16-core V100 hosts as CPU workers. Each worker ran one process with one
BLAS thread and `CUDA_VISIBLE_DEVICES=-1`, so neither V100 was used. Both sparse clones were clean at the exact
implementation commit. Shard 0 evaluated the 32 even stream IDs in 194.36 seconds; shard 1 evaluated the 32
odd IDs in 193.45 seconds. Parallel wall time was about 3.24 minutes and aggregate worker time was 387.82
seconds.

The merged artifact contains 64 streams, 2,560,000 generated events, 2,187,971 retained displayed events and
576 fitted models. Every fit converged and every recorded scalar was finite. The formal protocol hash is
`484f503cd0117fa3689be721d796f81c38887fa5f61a79e3dfdbe8033069900a`.

| Artifact | SHA-256 |
|---|---|
| `DYNAMIC_QUEUE_RESULTS.json` | `c41278c104cdaf36a1a5523c823bb92befa50453e0e71770ccedea229f6f9f17` |
| `shards/shard0_ba763c7d.json` | `dba20846b3e6013d0fbea922593420c0fe457c10cbda466a372698023f4227ff` |
| `shards/shard1_ba763c7d.json` | `1273b2fb94b72b2c71d427fb2bc976136f7706619236b5f41480d648f0d83640` |

## Frozen hard-gate decision

| Gate | Result |
|---|---:|
| exact counts, finite values, converged fits and complete two-shard merge | PASS |
| monolithic/chunked/serialized-resume state equality | PASS |
| exact independent reconstruction, positive queues and signed price moves | PASS |
| incremental latent truth beats the full observation baseline | PASS |
| zero-censor latent coefficient recovery | PASS |
| observation-only truth rejects a spurious latent contribution | PASS |
| independently permuted-latent control | PASS |
| current versus lag-3 identification at `rho=0.60` | PASS |
| all substantive/control gates survive 20% censoring | PASS |

All 64 message streams, book paths and terminal generator states were bit-exact under the frozen chunk and
resume schedule. Independent reconstruction recovered every after-event book, mid tick and price-move mark.
Every stream had up and down moves; the minimum counts were 609 up and 603 down. Cell-median move rates were
3.205%--4.356%, inside the frozen 0.2%--5.0% interval.

## Identification results

For latent-incremental truth, `joint` denotes `combined_current`, `obs` denotes `observation_full`, and all
likelihood differences are held-out nats per retained displayed event. The generating current-latent
coefficient is 0.65.

| `rho` | censor | move rate | joint - obs | joint - latent | current - lag3 | fitted latent | abs permuted gain |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.60 | 0% | 3.219% | 0.109740 | 0.053627 | 0.108066 | 0.656896 | 0.000020 |
| 0.60 | 20% | 3.205% | 0.113615 | 0.050668 | 0.111087 | 0.657767 | 0.000041 |
| 0.95 | 0% | 4.340% | 0.056553 | 0.056375 | 0.029691 | 0.654677 | 0.000020 |
| 0.95 | 20% | 4.333% | 0.064832 | 0.051593 | 0.031043 | 0.674135 | 0.000074 |

The latent driver adds information beyond both the observed queue/marked-flow history and the latent-only
model in every stress cell. At zero censoring, the recovered median coefficient differs from 0.65 by 1.06% at
`rho=0.60` and 0.72% at `rho=0.95`, well within the frozen 15% tolerance. The smaller current-versus-lag-3 gap
at `rho=0.95` retains the preregistered temporal-identifiability warning.

For observation-only truth, the critical negative control is that adding the current latent must not improve
the strongest observation model.

| `rho` | censor | move rate | obs - latent | joint - obs | median abs latent coefficient | abs permuted gain |
|---:|---:|---:|---:|---:|---:|---:|
| 0.60 | 0% | 4.356% | 0.159173 | -0.000001 | 0.005928 | 0.000100 |
| 0.60 | 20% | 4.278% | 0.157063 | -0.000019 | 0.007037 | 0.000058 |
| 0.95 | 0% | 4.258% | 0.158950 | -0.000043 | 0.004148 | 0.000017 |
| 0.95 | 20% | 4.305% | 0.155535 | -0.000000 | 0.005162 | 0.000044 |

The observation-only baseline beats the latent-only model by 0.156--0.159 nats/event, while the joint model's
increment over the observation baseline is zero to slightly negative and its latent coefficient remains near
zero. Thus the evaluator does not manufacture latent value merely by adding another feature. All controls also
survive prospective 20% displayed-message censoring.

## Scientific boundary and next gate

This experiment closes a synthetic engineering and falsification gap: aggregate queues now deplete into price
moves, the complete state resumes exactly, the same messages reconstruct exactly, and queue-reactive plus
discrete marked-Hawkes-logit baselines can reject a spurious latent driver under the declared DGP.

It does **not** validate EcoMD against a market or clear G3. Messages are generated by a logistic family that is
also represented in the evaluator; queue reset after depletion is deterministic; queues are aggregate rather
than individual-order; event time is not continuous; and `marked_hawkes` is not a continuous-time Hawkes
likelihood. The result gives no evidence that real order flow is driven by `latent_flow_alignment`, does not
externally anchor its sign, and does not unlock paid L2.

The next observation-bridge gate is a separately preregistered out-of-family test using externally sourced
messages, externally validated timestamp/sign conventions, and a real continuous-time marked point-process
baseline. Free sample data should be exhausted first; paid data remains gated. In parallel, G0 still requires a
genuinely new invariant-sensitivity estimator or theorem before any large GPU campaign is justified.
