---
name: Reexploration regression receipt audit
description: Private engineering correction to the pre-D0 regression tally; remote receipts govern.
type: project
---

# Private/internal: pre-D0 test receipt audit

## Latest continuation (13:37 NZST)

PI asked to continue testing on V100. Completed seven targeted files CPU-only,
with 903 matching local/remote input hashes and unchanged assertions/protocols.
102 tests: 57 passed, 45 failed, zero errors/skips. Four previously red files
now pass: exp127 worker (3), Sim2Science artifact builder (5), GitHub contract
(3), route graph (16). Authentic required Git objects/ancestry and real fixture
bytes suffice; the mirror need not carry all bulk artifacts or fabricated history.

Three files remain non-green: dynamic_graph (7 pass/1 fail), research_discovery
(19 pass/43 failures caused by the missing route reference), and the full BPTT
checkpoint file (4 pass/1 fail). The formerly excluded 200-agent/64-step case
ran and failed CPU allocation under a 24 GiB address-space cap in 186 seconds.
Do not generalize that bounded failure to all CPU/GPU hardware.

The old numerical constant is not yet explained: current sum 0.0758228749;
restoring legacy global-RNG sampling in a private diagnostic gives 0.2714456916,
not 0.263843. Do not re-pin the constant merely to green the test. No source,
test, graph status or freeze-date edits were made. Receipts are durable under
logs/private/regression_continue_20260908/ (README, summary, XMLs, hashes).

## Earlier audit (superseded operational state)

On 2026-09-08 at 13:12 NZST, read-only inspection of v100ts contradicted the
recorded 142/146 remote-green tally. Merge the three existing summary.tsv files
under /tmp/regv2 (base, rerun1, rerun2), keeping the last exit code per filename:
146 files, 140 passing, six nonzero. Besides the four documented failures,
test_exp127_v100_worker.py and test_sim2science_artifact_builder.py still fail
for missing legacy fixtures. Local success does not certify the remote mirror.
One slow checkpoint test was excluded; do not call this full-suite green.

Six forecast entries reference reexploration_merged_gamma_led_paper, absent from
the canonical route graph at this inspection. Repair must preserve the current
D-minus-1 authorization bounds; do not infer full scientific activation.

Evidence: logs/2026-09-08.md Session 5 and the correction banner in
papers/proposal/ecomd_reexploration_d0_regression_battery_2026-09-08.md.
This is private operational provenance, never scientific evidence.
