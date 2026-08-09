---
name: Dev-to-training workflow (EcoPhys)
description: Mac local development + GitHub code + Cloudflare R2 canonical data + scalable non-H20 compute pools. Current production floor is 2×V100 32 GB; future GPU/CPU capacity may expand, but H20 is excluded as of 2026-08-09.
type: feedback
originSessionId: c6748c05-53ac-462d-9535-154e95f91d9f
---
# Workflow

**Rule** (v3 — revised for scalable non-H20 compute 2026-08-09):
- **Mac**: code editing, data ingestion + preprocessing (raw → Parquet+zstd), small smoke tests (≤10⁴ agents, <1h), paper writing.
- **Cloud storage**: canonical processed data store. **Cloudflare R2 preferred** (zero egress, S3-API compatible, $0.015/GB-mo); AWS S3 as fallback if R2 is blocked by company firewall.
- **GitHub**: canonical code store. Main always runnable. Experiments on feature branches.
- **Compute workers**:
  - Current production pool: two independent V100 32 GB nodes.
  - Future pools may add more compatible CUDA GPUs and separate CPU/RAM data nodes; **do not plan around H20**.
  - Flow: GitHub → worker-local code; R2 → worker-local immutable input shards; local run → R2 manifests/results.
  - Training and reconstruction read local hot data only; no cloud round-trips in the hot path.
  - Keep different GPU types in separate worker pools and calibrate throughput using canonical V100 jobs.

**Why**: The original 2026-04-23 H20-specific workflow became unavailable. On 2026-08-09 the user explicitly chose a hardware-agnostic plan starting from 2×V100, expandable to more non-H20 resources. R2/GitHub separation still avoids file-sync ambiguity and makes workers replaceable.

**Network rule**: Treat every compute worker as replaceable and potentially bandwidth-constrained. After one bulk sync, an experiment must run from local disk and write a local canonical manifest. W&B is optional; no worker may require W&B, package mirrors, or R2/S3 access inside the training hot path.

**How to apply**:
- When writing training scripts, assume they run on a generic CUDA worker. Make them parameterized (CLI args or Hydra config), not hardcoded for Mac or a particular remote path.
- Data paths: reference canonical R2/S3-compatible object keys or an env-var-driven local cache (`$ECOPHYS_DATA_DIR`). Never hardcode `/Users/howardwang/...` in repo code.
- Before starting a long training, verify: (a) code is committed + pushed, (b) immutable data shards and hashes are on R2, (c) the assigned worker has the exact git SHA and complete local shards.
- Long experiments run under `tmux` or a supervised service with exact resume; checkpoint at least every 30 minutes for the NCS program. Local manifests are canonical and W&B is optional.
- When user says "开始训练" / "start training", use the available V100/non-H20 worker pool after a resource probe; do not infer H20 availability.
- Mac-side dev tooling: PyTorch with MPS backend for smoke tests (not production); conda env `ecophys`.
- Remote accessibility is checked per worker. Do not encode addresses or credentials in tracked files; inventory belongs in a gitignored machine manifest.

## Framework choice (decided 2026-04-23 revisit)

- **Default: PyTorch 2.3+ end-to-end**. Use `torchsde` for stochastic differential equation solving in Phase 4 (Jarzynski / Crooks fluctuation-theorem analysis), not JAX/diffrax.
- **Why**: avoids cognitive overhead of two frameworks in one repo; `torchsde` covers the needed SDE + adjoint sensitivity functionality even if it's less polished than diffrax.
- **Only introduce JAX/diffrax if** a specific Phase 4 experiment shows a concrete performance or API blocker with `torchsde` (e.g., batched reverse-time SDE integration > 10⁵ trajectories with adjoint, which is where diffrax/vmap shines).
- Original plan v1 labeled JAX as "optional physics extra" — this is still accurate but the default has shifted from "use if convenient" to "do not use unless needed".
- The `pyproject.toml` keeps `[physics]` extra with JAX/diffrax for future opt-in, but baseline installs should use `.[dev]` not `.[dev,physics]`.
