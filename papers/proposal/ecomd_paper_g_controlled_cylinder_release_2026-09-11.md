# Paper G — Controlled Cylinder release preflight

PRIVATE / INTERNAL. Infrastructure record; not a scientific result or public evidence.
Session 20, 2026-09-11, started 06:33 NZST. Decision: **not_trigger**.

The bounded question was whether the calibration lead retained on September 10
now supplies a traceable executed-control and measurement-reference asset. The
audit pins a usable release identity and declared schema, but does not qualify
that capability or remove a contribution blocker. No new candidate cycle opens.

## What was established

The official Hugging Face dataset revision is
`5e6309f6e4de745b1ae3d3a0eefd6ea785803df9`, last modified
2026-08-14T20:09:01Z according to repository metadata. It predates the earlier
route closure; newly inspecting it is not a post-closure release event.
The pinned dataset card declares CC-BY-NC-4.0. This is the dataset-card rights
statement, separate from article and code licenses; no legal sufficiency review
or redistribution is performed here.

The complete outer `controlled_cylinder/` tree has 165 files and three
directories. Its file paths exactly match the same prefix in the repository
siblings listing; the tree response contains no continuation link. There are
51 real and 96 numerical Arrow shards, plus 18 metadata/index/statistics files.
Shards are not trajectories: both machine schemas declare 96 trajectory rows.
The remote file-size total is 175,791,576,954 bytes (about 175.8 decimal GB),
including metadata. This is an inventory sum, not measured RAM or training cost.
No shard contents or source-provided payload hashes were locally verified.

The real `dataset_info.json` declares `sim_id`, binary `u,v,vo,x,y,t`, and shape
fields. The numerical schema additionally declares `p`. `channels.json` says
Reynolds number and control frequency are encoded in trajectory filenames and
parameter JSON files. These are operating-condition labels; they do not by
themselves establish a synchronized realized cylinder-position trace.

The pinned README describes dataset version 2.0.0, with 76/10/10 real
remain/in-distribution-test/out-of-distribution-test trajectories. These counts
are documentation claims, not an independently inspected split assignment.
The serialized `train` container in `dataset_info.json` is a storage group;
the benchmark's scientific partitions are separately indexed. Its name alone
does not demonstrate leakage or a contradiction in the evaluation design.

## What remains unqualified

Neither the declared columns nor the enumerated outer file names identifies a
separate synchronized actuator trace, raw-image calibration package, or
target-matched uncertainty budget for this HF scenario. This is a statement
about this inspected release surface. It does **not** prove that such resources
are absent from unopened binary contents, another host, or the authors' records.
The article's calibration-resource statement is therefore not contradicted.

Nominally paired experimental and numerical parameter regimes do not establish
identical hidden initial states, executed interventions, or zero-error physical
targets. Likewise, benchmark held-out parameter regimes are not automatically
an untouched confirmation partition for a newly chosen response estimand.
No outcomes have been used to decide either issue.

The supported immediate use remains the benchmark's documented prediction
setting. A mean-response study need not have joint force/PIV or exact hidden-state
replay if an appropriate assignment and measurement design identifies its target.
This audit qualifies neither that design nor a same-state impulse-response target;
it does not impose unnecessary sensors on every possible question.

## Allocation decision

Preserve the immutable release, rights declaration, schemas and inventory as
reusable infrastructure. Stop this exact source audit pending an identifiable
executed-control/calibration manifest tied to run IDs, clock, measurement support,
and a specified estimand, or another qualified trigger removing a named blocker.
Do not download large payloads merely to continue searching for a topic.

Even a complete calibration asset would not itself supply a new learning or
measurement contribution. The existing physical-history route remains closed
under `necessary_memory_control_changes_observation_regime` and
`generic_statistical_accuracy_and_forced_response_have_direct_prior`.
No original theorem, practical model failure, matched primary disagreement,
candidate-harvest permission, experiment, or publication claim is established.
The broader Paper G objective remains unresolved.

Sources: [pinned dataset card](https://huggingface.co/datasets/AI4Science-WestlakeU/RealPDEBench/blob/5e6309f6e4de745b1ae3d3a0eefd6ea785803df9/README.md),
[immutable scenario tree](https://huggingface.co/api/datasets/AI4Science-WestlakeU/RealPDEBench/tree/5e6309f6e4de745b1ae3d3a0eefd6ea785803df9/controlled_cylinder?recursive=true&expand=false),
[real schema](https://huggingface.co/datasets/AI4Science-WestlakeU/RealPDEBench/resolve/5e6309f6e4de745b1ae3d3a0eefd6ea785803df9/controlled_cylinder/hf_dataset/real/dataset_info.json),
[official documentation](https://realpdebench.github.io/datasets/controlled-cylinder/).
Full metadata provenance and scope exclusions are in the private manifest.
