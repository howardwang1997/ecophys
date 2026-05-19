---
name: Dev-to-training workflow (EcoPhys)
description: Mac local development → AWS S3 for data → GitHub for code → H20 remote machine pulls both and trains. User chose this split on 2026-04-23.
type: feedback
originSessionId: c6748c05-53ac-462d-9535-154e95f91d9f
---
# Workflow

**Rule** (v3 — revised for checkpoint offload 2026-05-19):
- **Mac**: code editing, data ingestion + preprocessing (raw → Parquet+zstd), small smoke tests (≤10⁴ agents, <1h), paper writing.
- **Cloud storage**: canonical processed data store. **Cloudflare R2 preferred** (zero egress, S3-API compatible, $0.015/GB-mo); AWS S3 as fallback if R2 is blocked by company firewall.
- **Checkpoint storage**: binary checkpoints live in Cloudflare R2 under `checkpoints/...`; Supabase `public.checkpoints` stores the catalog metadata. After every H20 training run, run `python -m ecomd.data.checkpoint_sync sync --delete-local` so H20/Mac/GitHub do not retain bulky checkpoint binaries.
- **GitHub**: canonical code store. Main always runnable. Experiments on feature branches.
- **H20 (remote, inside company network with whitelist outbound — R2/S3/GitHub OK)**:
  - Code at `/root/ecophys/` (separate code drive)
  - Hot cache at `/root/data/ecophys/` (separate data drive; target budget **500 GB**)
  - NFS canonical store at `/AI4S/Users/howardwang/ecophys/` (company shared)
  - Flow: R2 → NFS via `scripts/h20_pull_from_r2.sh`, then NFS → hot cache via rsync before training
  - Subsequent training reads exclusively from hot cache — no cloud/NFS round-trips per step
  - Mac cannot mount NFS directly; all Mac→H20 data transit goes via R2

**Why**: User chose Mac+cloud+GitHub+H20 split on 2026-04-23, then revised same day after flagging H20 is inside company network with poor connectivity. Rationale: avoids file-sync weirdness; keeps Mac productive when H20 network is down; minimizes slow-network data movement.

**Network gotcha (2026-04-23)**: H20 is inside company network. Assume H20's external connectivity is unreliable / bandwidth-constrained. Design experiments to NOT require mid-training cloud fetches. Every experiment must be runnable entirely from H20 local disk (`/data/ecophys/`) after a single pre-experiment bulk sync. Do NOT set up workflows where H20 hits `wandb.ai`, arXiv, pip mirrors, or S3 during the hot path of a training run — queue these outside the training loop or batch them.

**How to apply**:
- When writing training scripts, assume they run on H20. Make them parameterized (CLI args or Hydra config), not hardcoded for Mac paths.
- Data paths: always reference via `s3://` URIs or env-var-driven local cache (`$ECOPHYS_DATA_DIR`). Never hardcode `/Users/howardwang/...` in repo code.
- Before starting a long training, verify: (a) code is committed + pushed, (b) data shards are uploaded to S3, (c) the H20 machine has latest git + S3 sync.
- After a long training, verify: (a) `checkpoint_sync sync` uploaded all checkpoints to R2, (b) Supabase rows are `uploaded`, (c) `checkpoint_sync cleanup` removed verified local binaries, (d) Git does not track `checkpoint*.pt`, `.ckpt`, or `.pth`.
- Long experiments run under `tmux` + `wandb` with `resume` enabled; checkpoint every 1h or 1000 steps, whichever first.
- When user says "开始训练" / "start training", default to preparing the H20 remote run (unless the experiment is explicitly tiny).
- Mac-side dev tooling: PyTorch with MPS backend for smoke tests (not production); conda env `ecophys`.
- **H20 is remote** — not accessible from this Claude session. All instructions to run on H20 must be produced as runnable scripts user can SSH and execute, or handed back as suggested commands.

## Framework choice (decided 2026-04-23 revisit)

- **Default: PyTorch 2.3+ end-to-end**. Use `torchsde` for stochastic differential equation solving in Phase 4 (Jarzynski / Crooks fluctuation-theorem analysis), not JAX/diffrax.
- **Why**: avoids cognitive overhead of two frameworks in one repo; `torchsde` covers the needed SDE + adjoint sensitivity functionality even if it's less polished than diffrax.
- **Only introduce JAX/diffrax if** a specific Phase 4 experiment shows a concrete performance or API blocker with `torchsde` (e.g., batched reverse-time SDE integration > 10⁵ trajectories with adjoint, which is where diffrax/vmap shines).
- Original plan v1 labeled JAX as "optional physics extra" — this is still accurate but the default has shifted from "use if convenient" to "do not use unless needed".
- The `pyproject.toml` keeps `[physics]` extra with JAX/diffrax for future opt-in, but baseline installs should use `.[dev]` not `.[dev,physics]`.
