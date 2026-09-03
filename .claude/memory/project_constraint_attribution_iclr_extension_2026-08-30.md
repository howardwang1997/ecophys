# Constraint-attribution ICLR extension (2026-08-30)

## Canonical status

An ICLR 2027 extension is frozen and locally implementation-complete. Initial pilot, all triggered
expansions, the C learning-rate correction, and both clean provenance replacements are complete.
The final ID-only lock has 58 unique mechanism/cell jobs over ten systems and SHA-256
`5100ae5ca6f757a5166fba3692fd912e19e7a0c7a4da65980488e92a402c604e`. Pilot OOD remains unopened,
confirmation seeds 1000--1029 remain untouched, and no confirmation outcome exists. The verified
41,426-byte confirmation snapshot is deployed to both V100s; archive/file hashes, 25 tests, and
isolated seed-999 CUDA preflights pass. The PI registered a scoped ICLR current machine decision,
and both authorized production workers are running with first-record metadata/provenance/finiteness
gates passed. The authoritative protocol is
`papers/proposal/ecomd_constraint_attribution_iclr_extension_freeze_2026-08-30.md`.

Historical A/B/C/M/E results are discovery evidence only for the extension:

- five seeds do not meet the project claim standard;
- visual overlap/non-significance is not evidence that hard and free-residual arms are equivalent;
- the historical matched-ID analyzer did not establish simultaneous ID-and-compute overlap;
- historical family M did not implement its claimed FIFO/nonzero-fee engine and cannot support a
  market-domain claim;
- the family-E sign flip at `nu=10` followed an adaptive sweep and needs an independent holdout;
- historical JSON records with `git_sha=unknown` are not acceptable confirmation provenance.

Do not carry the paper skeleton's current `30/30`, `42/42`, "constraints never matter", or broad
market claims into an ICLR submission unless the new confirmation protocol supports them.

## Frozen extension

- Pilot seeds: 100--102, ID-only cell selection.
- Confirmation seeds: 1000--1029, paired across arms and untouched as of 2026-08-30. The
  compute-authority amendment prospectively increased the set from 20 to 30 before any
  confirmation run; there is no 20-seed interim.
- Simultaneous matching: mean ID RMSE within 5% and parameter-count × examples-seen proxy within
  5%. Non-overlap becomes fixed-compute wording; never widen the window.
- Hard versus free-residual: 90% paired-bootstrap practical-equivalence CI inside ±10% of the
  free-residual mean. Thirty seeds; 50,000 bootstrap draws; analysis seed 20260830.
- Parameterization: paired 95% interval; all seed SDs use `ddof=1`; Holm correction within primary
  claim families.
- Deterministic rollout horizons: 1, 4, 16, 64. Projection/free equality is an exact algebraic gate
  only at horizon one because later projected inputs diverge.
- Independent holdout: mean-preserving uniform contraction at gamma 0.5 versus 50, predicting
  residual versus absolute output respectively.
- Corrected M2: actual price-time FIFO queues, resting-order settlement, nonzero bilateral fees,
  and participant cash plus fee-account conservation. No M2 rollout because the observation is not
  queue-Markov-complete.
- GPU-hours are monitoring and scheduling quantities, not scientific stop conditions. The former
  25/120-hour caps were superseded by explicit PI direction on 2026-08-30.

## Implementation and tests

New independent extension files live under `scripts/*constraint_iclr*`,
`configs/constraint_iclr/`, and `tests/test_constraint_iclr.py`. Historical scripts remain
untouched. Records are append-only JSONL with resolved Hydra config, command, git head, dirty flag,
source/config SHA-256, host/software/GPU metadata, parameters, examples seen, runtime, peak memory,
and explicit null W&B URL.

Local A/B/C/H/M2 smoke runs succeeded. The targeted suite has 25 passing tests. Confirmation
records now fail closed unless the exact selected-cell lock exists and matches its declared hash;
the analyzer independently checks top-level, resolved-config, and source-hash lock binding. A 2D
sampler bug found by smoke was fixed before remote execution.

## Compute and blocker

Both initial pilots completed normally. V100a produced 1,620 records / 1,296 trained arms in 1.208
GPU-hours; V100b produced 480 records / 384 trained arms in 5.452 GPU-hours. All active records are
finite, use seeds 100--102, and passed local/remote hash checks after retrieval. The aborted B
full-grid partial remains intact under `runtime_only_aborted/` and is excluded.

The provisional ID-only lock SHA-256
`9ad88f746bc0fd8bb03d81720747cd7beafd588201ff394af54600e654054cb2` is retained only as an audit
artifact and must not launch confirmation. It triggered A-advection/diffusion/burgers,
B-advection/diffusion/burgers, H-near, and H-strong expansion before the configuration discrepancy
was found. All eight jobs remain active/queued behind one `flock` per V100.

The timing amendment froze B/C learning rates `{0.0003,0.001}`, but the thin manifest omitted the
override and executed `{0.001,0.003}`. The correction is frozen in
`ecomd_constraint_attribution_iclr_bc_lr_correction_2026-08-30.md`: preserve all records, exclude
B/C `lr=0.003` from selection, let the B expansion fill its correct grid, and append missing C
`lr=0.0003` cells. The PI authorized C, queued as PID 171506 on V100b. After completion, rerun the
corrected ID-only selector; expand C only if that corrected result triggers the existing rule.
OOD metrics remain unopened, confirmation seeds 1000--1029 remain untouched, and necessary
evidence runs are not stopped by superseded hour estimates.

All expansion/correction compute later completed: 5,040 raw records / 4,032 trained arms and 30.534
recorded V100-hours, with ten local/remote file hashes matching and no runtime error. The first
corrected selector invocation read no ID/OOD because provenance validation failed first. Exactly
510 records lack `git_head`: H-near expansion 450 and C correction 60. Frozen policy requires rerun,
not metadata patching. The PI authorized clean substitutes with Git HEAD
`86dd76ee0127c5eb7945a5806bdad74548c62459` and dirty flag: H-near PID 2281697 on V100a (720 target)
and C PID 182376 on V100b (120 target). First records passed. Local provenance capture now fails
before training if HEAD or dirty state is unavailable. After hash verification, substitute only
these two files and run the corrected ID-only selector; original defective records remain excluded.

Both clean replacements later completed and matched their remote SHA-256 values: H-near
`934a74662a480a8197775b2399e89f9a0dce7d9531c06ba6d6b8c51b8974215d`, C-ad2d
`d0bf4646a85e5c41cda8b170df5f21481b82e5705ecb88abc34b1e7ea6db0f11`. The clean selector input
contains 4,980 unique records / 4,800 eligible records, zero provenance failures, and explicitly
excludes the superseded H/C files and 180 B `lr=0.003` records. The final ID-only selector ran once;
C matched without expansion. The two production V100s are idle. The confirmation archive SHA-256
is `b70c000cdd1c70d676ce1846f74e66d147bcd8a03a0fc0a84564e8e0cbbb1305`. Both remote archive and
file-hash gates, 25 tests, and seed-999 CUDA preflights pass. A concurrent launch attempt exposed
the missing current-machine-decision registration: V100a never started; V100b was terminated by
exact process group before writing any record, with its command-only log retained. Both GPUs are
then returned idle. The PI subsequently authorized and registered decision SHA
`9d6e1e67cc0055b719c1b904f266123e29b9b31f1f24008a58bafbc8ea49dace`; V100a launcher PID
2568827 and V100b PID 190373 are now running. First-record gates passed on both hosts without
displaying metric values. At the first checkpoint V100a had 18 records and V100b two, with no log
error. Pilot OOD and confirmation analysis remain unopened until both workers complete.

At the 2026-08-31 16:39 NZST checkpoint, both launchers remain healthy. V100a has 456/1,440 records
(A-advection complete, A-diffusion 216/240) and V100b has 64/870 B-advection records. All 520
current records pass an outcome-blind full integrity scan over lock membership, seeds, unique IDs,
provenance, source hashes, and finite numbers. No metric value or early analysis was accessed.

Later the same day, V100a completed A-advection and A-diffusion (240 records each) but deterministically
failed before writing the first A-burgers record: locked free/c128/e400/lr0.001 seed 1000 produced a
nonfinite value rejected by strict JSON serialization. The one machine-decision-authorized
identical retry reproduced the failure with no parameter/seed change and no metric inspection.
A-burgers is failed/incomplete; no third retry or repair is allowed. V100a is idle with 480 valid
records. V100b continues normally (195 records at checkpoint). H-near, H-strong, and M2 require a
PI-approved failure-continuation amendment that does not alter their locked jobs.

The PI then approved that minimal amendment. Current decision
`constraint_attribution_iclr_failure_continuation_20260831` has SHA-256
`52619d431b5671205a1a4976c6174b49e7b63c5debd7cdd955d5481f4c80b324`. A-burgers stays
permanently failed/incomplete and excluded from inference; it cannot be retried, repaired, or
assigned a replacement seed. V100a now runs only H-near, H-strong, and M2 via a three-system
allowlist (18 unchanged lock jobs / 720 expected records), launcher PID 2918091. The amendment
archive SHA-256 is `f3e3ca94f84166e779b64bc54d30156a7e04d1eba2fb6eb7dbad14c7df3f49a3`;
all remote hashes and 26 focused tests passed. First continuation records passed outcome-blind
scope/provenance/lock/V100/finiteness gates. V100b remains the original healthy PID 190373; an
empty `pgrep` sample was a monitoring false negative, and no V100b restart occurred. Both V100s
are active, and analysis remains locked until amended completeness and integrity gates pass.

## Public PDEBench external block (2026-09-01)

The PI authorized a separate public linear-invariant PDE benchmark. PDEBench 1D Advection
beta=0.4 (DaRUS v8, file ID 255674, CC BY 4.0) was chosen before data access; the intended FNO
block is never pooled with or used to repair the synthetic confirmation. New formal seeds are
2000--2029. The exact downloaded file has SHA-256
`d973ff2bb3c2a5edf42957ff029b78672451532ebd6bf475848ff23cfd3ee3b6`; its released MD5 and byte
count pass. Fourteen focused tests and a complete synthetic-HDF5 runner smoke pass.

Version 1 stopped prospectively at data admission before any model run. Native-resolution mean
drift passes (`4.4541e-7` maximum), but direct stride-2/4 point decimation produces target mean
drift (`1.7501e-4` / `1.2178e-3`) above the frozen `1e-5` gate. No data lock or model record exists.
The official file also uses cell-centered x and has one unused trailing t-coordinate; this was
handled by a recorded schema-only amendment before tensor values were read. Re-entry requires
explicit approval of a new v2 using conservative block-average restriction, with every other
scientific and compute setting unchanged. The v1 gate must never be loosened or rewritten.

## PDEBench formal result and manuscript reframe (2026-09-01)

PDEBench v2 later completed under the conservative block-average amendment with exactly 150
records (30 seeds x four trained arms plus projection) and 120 checkpoints. The immutable local
formal artifacts are `experiments/constraint_attribution_iclr/pdebench/formal_20260901/`:

- `confirmation_v2.jsonl` SHA-256
  `09e69b4e50bd39c152bef0e22e07d86a8b513f31ed119d887ed3077fb72d2fc3`;
- `analysis.json` SHA-256
  `e1619126f46eb081ace19000d44771559029c49f22f0057812183fc7e2efb41a`.

The primary OOD-512/horizon-16 means are 0.0346601 (`free`), 0.0320406 (`free_res`), and
0.0307403 (`hard`). The path-specific parameterization effect is 0.0026195, 95% CI
[0.0011544, 0.0042624]; the hard effect is -0.0013002, 90% CI
[-0.0017886, -0.0007969]. Hard is practically equivalent under the frozen 10% SESOI, but it has a
small reproducible accuracy benefit. The absolute effect ratio is 2.015, only narrowly above the
frozen 2:1 gate. Across 12 cells, residual parameterization is favorable in all point estimates,
Holm-significant in 9, hard/free-res is equivalent in 8, and the full attribution rule passes in 4.

The durable scientific conclusion is conditional: matched parameterization controls are necessary
for credit assignment, but neither universal "all credit" nor "no credit" is supported. The old
absolute title/thesis was retired. Paper D now uses the title *Who Gets Credit for Conservation?
Disentangling Output Parameterization from Exact Enforcement in Neural PDE Surrogates* and lives at
`papers/paper_d_constraints/main.tex`; the verified 8-page PDF is `output/pdf/main.pdf`. The current
paper is not submission-ready on evidence breadth alone: it covers one public PDE, one FNO, and one
linear invariant.

Synthetic confirmation remains outcome-locked and absent from the paper. Seven systems are
complete; A-burgers and B-burgers have zero records after non-finite first locked configurations;
C-ad2d is unstarted. Both V100s were idle at the 2026-09-01 paper audit. B-burgers needs an
outcome-blind failure disposition before unchanged C continuation and a one-shot amended analysis
over eight complete systems plus two disclosed failures.

## Fully crossed attribution extension and synthetic closure (2026-09-01)

The missing absolute-output/hard-enforcement cell is now prospectively addressed by a fresh-seed
PDEBench advection 2 x 2 factorial. Cells are absolute/residual crossed with free/hard, seeds
3000--3029, and the primary remains OOD-512 horizon 16. The frozen interaction is
`I = Y_A0 - Y_R0 - Y_A1 + Y_R1`; path-averaged intervention credits are
`phi_P=(P0+P1)/2` and `phi_E=(E_A+E_R)/2`. Exact coverage is 150 records. Outcomes must remain
unread until 150/150 and integrity gates pass, followed by exactly one analyzer run. V100a formal
PID is 3852717; the snapshot and decision SHA-256 values are respectively
`8a88df5528f8e0d823fdad7d09c6e763aa1883671be279eff83aac4520376df2` and
`3043bede659df33e9dee44ed39ac3e3eb57175e83021d9d97516203797d8f8b0`.

The synthetic block is no longer outcome-locked. C-ad2d completed at 240 records; exact amended
coverage is 1,830 records across eight complete systems, with both Burgers failures preserved and
excluded. The amended analyzer ran once and produced SHA-256
`d537b97591845c37326012f4ecd4e86775d3ca7b895a6881b06290fe397cac99`. Parameterization is nonzero
in all eight primary cells but favors residual coordinates only 6/8; hard/free-res equivalence
holds in 6/8 and the full legacy rule passes only M2 (1/8). Do not promote this to a universal main
claim; retain it as appendix boundary evidence and disclose the two failed systems.

A second public replication is frozen on PDEBench periodic 1D Burgers at nu=0.01, seeds
4000--4029, with the same factorial and primary case. The official v8 file is file ID 281363,
8,232,968,312 bytes, MD5 `e6d9a4f62baf9a29121a816b919e2770`. No model may start before the
full data gate passes and a new lock/model decision is frozen. The initial data command failed
before downloading a byte because V100b lacked h5py; a recorded runtime-only amendment installed
the reference version `h5py==3.16.0`, and the sole retry is downloading the unchanged DaRUS file.

Before Advection factorial reveal, a separate mechanism diagnostic was frozen to test whether
conserving/violating parameter-gradient coupling explains the coordinate-by-enforcement interaction.
It reconstructs each seed's exact first minibatch, records channel-gradient geometry, executes the
exact matched first Adam step, and prospectively correlates the local coordinate interaction with
the final primary interaction. Protocol SHA is
`e99e6925cbb744ec4ac129e2a05b54fde27a862556963dc40b2954bfed8def78`; verified snapshot SHA is
`3d989bd9ac41b0d58a4e11f2d792e51d8e5881bae1131584b452cff46adaed9b`; machine decision SHA is
`1f314ff38dbc3a3a7ac1976186b62f08576f65f209f2fcbd22841a5d2edbc1cd`. All 63 focused tests pass.
The paper now includes a channel-separable null and a one-step gradient-coupling bound, explicitly
positioned against established PINN gradient-conflict work rather than claiming gradient alignment.

The Burgers DaRUS HTTP/2 retry regressed its partial size after curl error 92. A registered Wget
HTTP/1.1 fallback remains active. In parallel, a pre-outcome verified-mirror amendment permits the
official `pdebench/Burgers` Hugging Face candidate only if exact bytes, DaRUS MD5, and reported
SHA-256 `646f5907...ce7b` all agree; no model may start before the unchanged full data gate.

Before any gradient-diagnostic record existed, a code audit found that the initial Spearman
bootstrap resampled full-sample ranks rather than re-ranking within each paired bootstrap sample.
The frozen protocol permits implementation repair before diagnostic output. Runtime amendment
SHA is `cd46fd016b1264ae00348175fa7afc700fc77a8e8622ffd09764325c16863bc3`;
corrected analyzer SHA is `3ce291bd38eaf51266b68ed5419b1fb453dc0ae36261e43e5526b9863f696d28`.
Use only `pdebench_gradient_coupling_snapshot_v2_20260901.tar.gz`, SHA
`a0508565e30e5ad2a46146ea8297d7f76724d20308023a2ebf46435dc3385590`, under runtime decision SHA
`92b859499fa7cc8ffc2d3541032437f16809d9f71d9af2c1092e4c339f8a5ab0`; the v1 snapshot is
preserved but superseded. Full focused tests pass 64/64 and clean-room hashes 21/21.

The manuscript's three-cell non-identification theorem was also corrected to respect nonnegative
RMSE outcomes: for fixed observed cells, feasible interactions contain an infinite half-line, not
all real numbers. Non-identification and Shapley non-identification remain valid without an
additivity/structural restriction. The submission plan now has an explicit no-spin gate: an
unresolved factorial plus unsupported mechanism plus absent/uninformative Burgers evidence is not
ICLR-ready and cannot be rescued by robustness rhetoric.

Latest mechanism deployment correction: v2 was never deployed. The final join must additionally
match each diagnostic seed's training-index and initialization hashes to the completed factorial
records and require one common source manifest. Use only
`pdebench_gradient_coupling_snapshot_v3_20260901.tar.gz`, SHA
`ef91504bf90cde9e57219be928e961855e1e266642f62f021ff47183cd3a66c7`, under decision SHA
`5f2e87a5486a855cfc66a7fd93f97aa38f3b605bfd591d94f349a21ba03d8bbc`. Analyzer SHA is
`549c0382b4466e7eea8447ccc401625696b7216f02990233100d2d76b8cefbd2`; 64/64 tests and 23/23
clean-room hashes pass. Versions 1 and 2 remain preserved but are forbidden for deployment.

## Current audit update (2026-09-03)

The main FNO evidence chain is complete and passes every registered integrity gate. Fresh
Advection has 150 core records, 120 locked checkpoints, and 90 zero-training cube records; its
primary three-way interaction is material (`J=0.22974`, 95% CI `[0.19644, 0.26345]`) in 9/12
mandatory cells. The first-minibatch gradient association is not supported. The direct 60-record
same-checkpoint gauge intervention is material at all three resolutions (primary ratio `8.68398`,
95% CI `[7.91007, 9.50538]`), but its seed-level association with final harm is not supported.

The independently frozen 2D shallow-water block is also complete: 150 core records, 120 locked
checkpoints, and 90 cube records. Its primary interaction is material (`J=-86.69343`, 95% CI
`[-107.65055, -66.68345]`) in 6/8 mandatory cells, and the horizon-31 projection contrast is a
resolved conservation--positivity synergy. Burgers and compressible Navier--Stokes remain terminal
data/runtime failures with zero admissible model records. The rewritten Paper D manuscript passes
the internal contribution gate, but still has a narrow two-PDE/one-operator-family boundary.

The prospectively frozen U-Net architecture replication is the only incomplete scientific
experiment. V100-A completed its registered seeds 7000--7014 with exactly 75 unique records and 60
formal checkpoints; shard SHA-256 is
`c64e4d41497659c699ec370c55012bebac1e6948f576b059535aa60575817718`. No metric was inspected.
V100-B has zero records because its public-data transfer stopped at 634,521,600 of 8,232,966,952
bytes; its watcher is alive but waits silently for exact byte coverage and cannot self-recover the
missing transfer. The V100-A shard has not been retrieved to the Mac workspace, and R2 backup was
not verified in this audit.

The 2026-09-03 outcome-blind completion repair supersedes that last operational paragraph without
changing the frozen experiment. V100-A's 75-record shard and 60 checkpoints were validated and
preserved on the Mac, V100-B, and R2. A parallel range transfer atomically reconstructed V100-B's
exact 8,232,966,952-byte file only after SHA-256 `d973ff2b...e3b6` passed; the original watcher then
independently verified it and started only registered seeds 7015--7029. Metrics remain sealed until
75+75 completion and the registered core/cube analyzers exit. Use branch
`paper-d-iclr-2027-completion` and recovery commit `02e79498d`; the completion snapshot itself is
bound by `experiments/constraint_attribution_iclr/deployment/unet_completion_snapshot_20260903.sha256s`.

The previously missing shallow-water core JSONL, cube JSONL, and checkpoint lock are now recovered
locally with exact canonical hashes `5e486167...cef5bc`, `69dfa936...723fa`, and
`772c52f9...1037b5`. Reanalysis must use the distributed configs
`pdebench_swe_rdb_factorial_distributed_20260902.yaml` and
`pdebench_swe_rdb_enforcement_cube_distributed_20260902.yaml`; the analyzers' defaults name the
single-worker parents and correctly fail source-manifest validation on the formal distributed
records. `scripts/build_paper_d_supplement.py` now encodes these exact runtime identities and fails
closed on coverage, primary-cell, hash-binding, integrity, or deterministic-rebuild drift.

The U-Net scientific freeze requires a 150-record core, one-shot core analysis, 120-checkpoint
lock, and 90-record inference-toggle cube. The deployed snapshot implements only core production
and generic core analysis. It contains no U-Net-specific shard merger, cube configuration, cube
runner, or cube analyzer; the existing Advection cube runner rejects every formal seed universe
except 3000--3029. Freeze and verify this completion path while U-Net outcomes remain sealed.

Repository durability is currently below the project standard: HEAD and its remote tracking branch
remain at `86dd76ee0` (2026-08-27), while 384 files are currently untracked (383 before this
session's mandatory log was created), including 313 constraint-ICLR
source/config/decision/result/paper files. The current experiments bind honest dirty-worktree and
per-file hashes, but GitHub is not yet the canonical recovery source for this work.
