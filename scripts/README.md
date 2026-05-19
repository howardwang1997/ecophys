# `scripts/` — H20 deployment scripts

All scripts in this directory are designed to run **on the H20 machine** via
SSH. From a Mac Claude session, the code is prepared here; the user
executes it remotely.

## Pre-requisites (run ONCE per H20)

```bash
# After fresh git clone on H20:
bash scripts/h20_setup_once.sh          # install conda env + pyproject
conda activate ecophys
# Data: data/sample/ (SPX daily 2015-2026) ships in git — enough for v1 training.
# Additional data from R2 only needed for multi-market work (M3.5+):
# bash scripts/h20_pull_from_r2.sh data/
wandb login                              # or set WANDB_API_KEY

# Required for checkpoint offload after training:
cp .env.r2.example .env.r2
cp .env.supabase.example .env.supabase
chmod 600 .env.r2 .env.supabase
# Fill both env files with the project R2 and Supabase credentials.
```

## Data you need at each phase

| Phase | Data | Source |
|---|---|---|
| **v1 / v1+ training** (now) | SPX daily 12 yr | ✓ in `data/sample/` (git) |
| M3 Paper A final | SPX full + BTC + LOBSTER | R2 pull (Tier 1 LOBSTER) |
| M3.5 A1 pilot | SPX + BTC + EUR/USD | yfinance + Binance + extra EUR/USD |
| M4 A1 full 8-market | + 5 more markets | yfinance + Tardis ~$3k |

## Training (v1 and v1+)

```bash
# Default: 4 cards
bash scripts/h20_launch_v1.sh            # EcoMD v1 (MACE-lite on v0.5 base)
bash scripts/h20_launch_v1plus.sh        # EcoMD v1+ (v0.6 + MACE-lite)

# Override to 8 cards (after 4-card run verified stable):
NPROC=8 bash scripts/h20_launch_v1.sh

# Dry-run (print command, don't execute):
DRY_RUN=1 bash scripts/h20_launch_v1.sh

# Resume from last checkpoint:
RESUME=1 bash scripts/h20_launch_v1.sh
```

Training writes checkpoint + wandb log to
`experiments/006_ecomd_v1/results/checkpoint.pt` (v1) or
`experiments/007_ecomd_v1plus/results/checkpoint.pt` (v1+).
Checkpoints are saved every 30 min on rank 0.

After every H20 training run, immediately archive checkpoints to Cloudflare R2
and register them in Supabase:

```bash
python -m ecomd.data.checkpoint_sync scan
python -m ecomd.data.checkpoint_sync sync
python -m ecomd.data.checkpoint_sync cleanup
```

Use the one-step form when the run is finished and local checkpoint retention
is not needed:

```bash
python -m ecomd.data.checkpoint_sync sync --delete-local
```

This is now the required checkpoint path for H20 work. Checkpoint binaries live
in R2 under `checkpoints/...`; Supabase `checkpoints` stores the searchable
catalog metadata. Git and Mac working copies should contain configs, logs,
scoreboards, and JSON outputs, not checkpoint binaries.

## Inference / evaluation

After training completes, run inference to produce long-rollout stylized
facts:

```bash
bash scripts/h20_inference.sh v1                # 4 cards × 2 rollouts = 8 realizations
bash scripts/h20_inference.sh v1plus            # same for v1+
NPROC=8 bash scripts/h20_inference.sh v1        # 8 cards × 2 = 16 realizations

# Extra args pass through to the Python script:
bash scripts/h20_inference.sh v1 --n-steps 8000 --n-realizations-per-rank 4
```

Outputs:
- `experiments/.../results/inference_rank_{0..N-1}.json` — per-rank realizations
- `experiments/.../results/inference_merged.json` — aggregated across all ranks

## Distributed architecture

The code uses **data-parallel DDP** (each rank independent rollout, gradients
all-reduced at the end of each training iteration). This avoids the
complexity of tensor-parallel while still achieving near-linear scaling on
NVLink. Tensor-parallel is reserved for v2 at N≥5×10⁵.

Backend: NCCL when CUDA available, GLOO otherwise. torchrun handles the
rendezvous.

## Monitoring

```bash
# In another SSH session:
tail -f experiments/006_ecomd_v1/results/run_*.log           # live stdout
nvidia-smi                                                   # GPU utilization
nvidia-smi topo -m                                           # NVLink topology
wandb                                                        # live at wandb.ai
```

## Capturing results for retrieval on Mac

Training + inference both **automatically** write:

```
experiments/<exp>/results/
├── training_log.json            # per-iter loss trace, wall time
├── checkpoint.pt                # model weights; offload to R2 + Supabase after training
├── inference_merged.json        # stylized facts from N rollouts
├── inference_rank_*.json        # per-rank raw outputs
├── run_YYYYMMDD-HHMMSS.log      # full stdout/stderr from this invocation
├── inference_YYYYMMDD-HHMMSS.log  # inference stdout
└── run_info.json                # git SHA, hostname, GPU count, timestamp
```

Retrieve lightweight artifacts to Mac after H20 run completes:

```bash
# On H20 — push lightweight artifacts; keep checkpoint binaries in R2 via checkpoint_sync
bash scripts/h20_push_results_to_r2.sh

# On Mac
python -m ecomd.data.r2_sync download h20_results/ ./h20_results/
# Then hand me the path and I'll generate the 8-way comparison table.
```

Need the checkpoint back for local analysis? Prefer querying Supabase for the
R2 key and downloading that object explicitly. Avoid bulk checkpoint downloads
to Mac.

```bash
python -m ecomd.data.r2_sync ls checkpoints/
python -m ecomd.data.r2_sync download checkpoints/<key-prefix>/ ./data/checkpoints/<key-prefix>/
```

## Troubleshooting

- **torchrun hangs on Mac (local dev)**: known macOS rendezvous issue.
  Test on Mac via manual env vars instead:
  ```bash
  RANK=0 LOCAL_RANK=0 WORLD_SIZE=1 MASTER_ADDR=localhost MASTER_PORT=29500 \
      python -m ecomd.training.train_distributed --config <cfg> --smoke
  ```
  On Linux H20 with NCCL, torchrun works normally.

- **NCCL all-reduce hang**: usually a firewall or NIC issue. Verify with:
  ```bash
  NCCL_DEBUG=INFO NPROC=2 bash scripts/h20_launch_v1.sh
  ```
  Look for "NCCL INFO" log lines in output.

- **Out of memory**: reduce `simulator.n_agents` in the config or lower
  `training.chunk_steps`. For N=10⁴, peak memory is ~20 GB per card.
