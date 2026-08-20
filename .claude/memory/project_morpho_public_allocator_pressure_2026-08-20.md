---
name: morpho-public-allocator-pressure-2026-08-20
description: "Closed source-bound Public Allocator route: T0 accounting passed, but the single formal D0 v2 failed at transport before support interpretation."
metadata:
  node_type: memory
  type: project
---

# Morpho Public Allocator pressure displacement — 2026-08-20

This is a new route on branch `morpho-public-liquidity-contagion-feasibility-2026-08-20`, created from the
immutable close of the hidden-bot Morpho D0A. It does not identify or use private bots. The actor is the official,
publicly callable, code-bound Public Allocator contract.

For an atomic target borrow `x` accompanied by routed supply `r=sum f_i`, pressure
`q_i=B_i-0.9S_i` changes by `+0.9f_i` at each donor and `x-0.9r` at the target. Network pressure rises by exactly
`x`. When `0<=r<=x`, every touched market receives nonnegative pressure even though demand occurs only at the
target. A fully JIT-funded borrow displaces 90% of new pressure to donor markets and leaves 10% at the target.
This is a source-bound accounting lemma, not new theory.

The official contract at commit `51f92e57624099c5c3a4c9fdd88ed1ec2b16ac84` updates each donor's flow caps as
`(maxIn+f,maxOut-f)` and the target's as `(maxIn-r,maxOut+r)`. Hence per-market `maxIn+maxOut` is conserved between
admin resets: caps are directional displacement budgets, not replenishing rate limits. One-vault target capacity
is `min(maxIn_target, sum_i min(maxOut_i, vault_supply_i))` under the stated enabled/reallocation assumptions.

The broad story is occupied: Morpho and Contango already document shared liquidity and donor-rate effects;
Zbandut--Goldstein already describe mutualized liquidity stress/curator contagion; 2026 industry analyses already
attribute Resolv loss amplification to Public Allocator flows; max-flow and conservation are classical. The only
eligible residual is a prospective event-level field result that routed fraction predicts delayed local
AdaptiveCurveIRM memory and participant response along the vault--market graph. A contemporaneous balance check
or known exploit retelling fails novelty.

T0 plan/config:

- `papers/proposal/morpho_public_allocator_pressure_t0_plan_2026-08-20.md`;
- `configs/empirical_physics/morpho_public_allocator_pressure_t0_v1.yaml`.

T0 uses pinned source and synthetic arrays only. Historical events, flows, rates, utilization, Resolv data,
EcoMD and GPUs remain forbidden. A mathematical pass authorizes nothing beyond a separately frozen event-support
D0. NMI requires a prospective agent externality/design intervention; NCS additionally needs a general
reaction--transport inference method and a second independent adaptive-resource system.

Implementation was committed and pushed at `4a480108e1090dc88460b52c4f8ffd6a81738b72`: typed
pressure/cap/capacity utilities, a deterministic 10,000-trial formal runner, and focused tests. The runner also
rejects dirty tracked worktrees in either pinned upstream source clone, closing the
`HEAD`-matches-but-files-differ audit hole. Seventeen targeted tests, Ruff and strict mypy pass.

The one formal T0 run from that clean upstream-matched SHA passed all seven frozen gates. Canonical payload
SHA-256 is `f6b765d249ca75a0355db3007508201b41eab257367a15194c0e52a8625ea2a6`; independent read-back matches.
The largest normalized residual was `4.3482e-16`. Scientific decision remains
`math_encoding_pass_novelty_and_field_support_remain_amber`: this verifies accounting only. All historical,
event and outcome data plus EcoMD and GPUs remained untouched. Next authorized step is a separately frozen D0
event-identity/support audit; do not retrieve history before that contract is committed and pushed.

D0 was subsequently designed without opening event history. It fixes only Ethereum and Base from the official
SDK at `eb27628b8`, with finalized endpoints at Ethereum block 25,795,523 and Base block 50,214,705; SQD and
independent RPC headers match. The outcome-blind identity proxy requires a Public Allocator withdrawal/terminal
sequence followed later in the same receipt by an exact-Morpho Borrow whose market topic matches the target.
Amounts remain undecoded, so these are atomic routing--borrow candidates, not yet genuine JIT events. Frozen
support requires 500 pooled, 100 per chain, 90-day spans, 30 active dates, 3 vaults and 4 edges per chain, 12
edges pooled, exact classification/receipt verification and no unresolved transport discrepancy. D1 must later
retain 300 after amount compatibility and AdaptiveCurveIRM binding. Plan/config are pending commit; no event count
has been queried and no D0 implementation exists yet.

The D0 freeze was committed and pushed at `9edea240a`; config SHA is `bc6fc21c…c60`. The local implementation now
adds opt-in full-topic/timestamp SQD identities, an identity-only RPC sanitizer that never accesses log `data`,
receipt-order allocation grouping, later target-matched Borrow classification, canonical digests and
aggregate-only support summaries. The formal runner enforces a committed qualification artifact before full D0.
Pinned-source audit, 50 affected regression tests, Ruff and strict mypy pass. This is implementation evidence
only: qualification has not run, no event count or identity is known, and no GPU/remote worker has been used.

Formal qualification from clean pushed `15faa4027` passed all six frozen shards. Ethereum event counts are
0/335/231 and Base 0/220/2 for deployment/midpoint/cutoff; every SQD identity set exactly equals its full-RPC set,
and all cutoff headers match. Canonical payload SHA is `d59b0184…edfe`, independently reproduced. No receipt,
Borrow event or full interval was opened, so these are transport counts rather than candidate support. The first
execution channel hid console output but completed the artifact; the identical diagnostic retry stopped at the
existing-output guard before network access.

The first serial full-v1 invocation from clean pushed `05c74b71b` was technically stopped after about eleven
minutes. It had a live network connection but wrote no artifact and exposed no event/support count. Qualification
pagination implies roughly 5,800 Ethereum and 59,000 Base Portal pages at the observed mean, or an optimistic
pooled lower bound near 22,000; the serial design therefore projected to roughly 8--24 hours before receipt work.
This is not a D0 result. Transport amendment v2 (`b549efa4…34a4`) keeps the parent-config hash and every
scientific/data gate fixed, but uses exact disjoint block shards, eight Portal workers, four paced receipt workers,
independently launched Ethereum/Base chain artifacts and a same-SHA exact merge. The amendment implementation has
12 focused tests;
the 65-test affected suite, Ruff and strict mypy pass. A new exact-digest qualification must be committed and pass
before both V100 hosts may run one CPU/network chain each with CUDA hidden. No amount, outcome or GPU use is
authorized.

Formal v2 qualification from clean pushed `68bf0ecef` passed. All 48 disjoint 1,250-block pieces completed; each
of the six reconstructed unions exactly reproduces its v1 event count and canonical identity digest and remains
exactly equal to the fixed full-RPC set. Canonical payload SHA is `d9b28e65…65de`, independently reproduced; file
SHA is `4c42da0e…4343`. Wall time was 96.62 s. Ethereum/Base had one recoverable Portal retry each and no RPC split
or retry. No receipt, Borrow, value or outcome was opened. Commit this immutable qualification before launching
both formal chain jobs together; no standalone chain result may drive whether the other chain runs.

The qualification was committed and pushed at `78cfc09e0`. The exact commit and three pinned source trees were
provisioned on both V100 hosts in isolated `ecophys-d0v2` Conda environments. Preflight reproduced the parent and
amendment hashes, qualification digest, source audit, worker identities, hidden CUDA setting and common batch ID
`e35adb81…6c59`. Base and Ethereum were then launched before either result was read.

The one formal full D0 is a transport FAIL. Base stopped after 199.80 s when Portal shard 5 raised a sanitized
`SqdPortalError`; Ethereum stopped after 243.06 s when the frozen Blockscout RPC endpoint exhausted connection
timeout retries. Both chain artifacts have `support: null`, so no candidate, edge, span, date, vault,
classification or receipt statistic exists. Canonical hashes are `bb330b79…c16ca` (Base),
`181d11c9…1b2c1` (Ethereum) and `cf97beb8…d8dab` (merged). The merged file hash is `6b261b78…a5c4`.

The merged artifact's pooled zero values are legacy unavailable-data sentinels, not observed zeros. Preserve that
formal file unchanged; future merger behavior emits `null` when any required chain lacks support. The frozen stop
rule closes the route before values, outcomes, D1, provider substitution, rerun, EcoMD, GPU or paid data. This
failure neither proves low support nor falsifies the mechanism, but it leaves no empirical result and therefore
no NMI/NCS claim. T0 survives only as accounting infrastructure.
