# Storage Architecture — EcoPhys (v4, checkpoint offload)

**Updated 2026-05-19** — confirmed: R2 registered, H20 NFS path `/AI4S/Users/howardwang/ecophys/`, **Mac cannot mount NFS**, all Mac↔H20 data transit must go through R2. Binary model checkpoints are no longer kept in Git or on Mac after verification; they live in Cloudflare R2 and are cataloged in Supabase.

## Architecture

```
                 ┌─────────────────────────┐
                 │ Mac (Howard's laptop)   │
                 │ - ingestion scripts      │
                 │ - preprocessing          │
                 │ - paper writing          │
                 └──────────┬──────────────┘
                            │  (rclone / boto3, HTTPS)
                            ▼
                   ┌──────────────────┐
                   │ Cloudflare R2    │   ← sole Mac↔H20 bridge
                   │ ecophys          │      + offsite backup
                   │ (S3-API, $0 egress) │
                   └──────────┬───────┘
                              │  (HTTPS pull, H20 whitelist allows)
                              ▼
                 ┌──────────────────────────────────┐
                 │ H20 machine (inside company net) │
                 │                                  │
                 │  /AI4S/Users/howardwang/ecophys/ │ ← NFS = canonical on-prem store
                 │                                  │
                 │  rsync as needed ▼               │
                 │                                  │
                 │  /root/data/ecophys/                  │ ← local NVMe hot cache
                 │  (training reads from here)      │
                 └──────────────────────────────────┘
```

## Canonical locations

| Role | Location | Notes |
|---|---|---|
| **Canonical for checkpoint binaries** | `r2://ecophys/checkpoints/...` | Authoritative for `checkpoint*.pt`, `.ckpt`, `.pth`; local copies can be deleted after verification |
| **Checkpoint catalog** | Supabase `public.checkpoints` | Metadata index: local path, R2 bucket/key, size, SHA-256, status, config/training summaries |
| **Canonical for sharing between Mac ↔ H20** | `r2://ecophys/` | Authoritative during transit; kept as offsite backup afterward |
| **Canonical on H20 / for long-term storage** | `/AI4S/Users/howardwang/ecophys/` (NFS) | On-prem, fast within company net, persists across H20 reboots |
| **H20 hot cache** | `/root/data/ecophys/` (local data drive; target budget 500 GB) | Training reads here; rsynced from NFS before each big run |
| **H20 code** | `/root/ecophys/` (local code drive) | `git clone` target; conda env `ecophys` lives here |
| **Mac working copy** | `~/Desktop/playground/ecophys/data/` (gitignored) | Dev / prototype only |

## Data flow rules

### Rule 1: Mac → H20 always transits R2

Mac cannot mount NFS. Therefore every file that needs to reach H20 gets uploaded to R2 first.

```bash
# Mac side:
python -m ecomd.data.r2_sync upload ./data/processed/sp500_minute/ processed/sp500_minute/
```

### Rule 2: H20 pulls from R2 into NFS

```bash
# H20 side:
python -m ecomd.data.r2_sync download processed/sp500_minute/ /AI4S/Users/howardwang/ecophys/processed/sp500_minute/
```

### Rule 3: Training reads from local NVMe, not NFS

NFS is persistent but its IOPS can be a bottleneck under heavy random-access training loops. Before a big run:

```bash
# H20 side, pre-training:
rsync -avh --info=progress2 /AI4S/Users/howardwang/ecophys/processed/sp500_minute/ /root/data/ecophys/processed/sp500_minute/
```

Training code reads exclusively from `/root/data/ecophys/`. The `$ECOPHYS_DATA_DIR` env var points at this path on H20 and at `~/Desktop/playground/ecophys/data` on Mac.

### Rule 4: Checkpoints flow H20 → R2 + Supabase, then local cleanup

Every H20 production task must offload checkpoints through `ecomd.data.checkpoint_sync` before the run is considered archived. This keeps the Mac working copy and GitHub history small while preserving reproducible checkpoint lookup.

Required credentials on both Mac and H20:

```bash
cp .env.r2.example .env.r2
cp .env.supabase.example .env.supabase
chmod 600 .env.r2 .env.supabase
```

`.env.r2` provides Cloudflare R2 object storage credentials. `.env.supabase` provides `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_CHECKPOINT_TABLE`, and `DATABASE_URL` for table migration when needed. Both files are gitignored and must never be committed.

One-time Supabase table setup:

```bash
python -m ecomd.data.checkpoint_sync migrate
```

After each H20 training job:

```bash
# H20: inspect what will be uploaded
python -m ecomd.data.checkpoint_sync scan

# H20: upload checkpoint binaries to R2 and upsert metadata into Supabase
python -m ecomd.data.checkpoint_sync sync

# H20: delete only local checkpoints that are verified in R2 by size + SHA-256
python -m ecomd.data.checkpoint_sync cleanup
```

For a single-command H20 archive pass:

```bash
python -m ecomd.data.checkpoint_sync sync --delete-local
```

If a checkpoint path was accidentally added to Git, remove it from the index without deleting the local file:

```bash
python -m ecomd.data.checkpoint_sync git-rm-cached
```

The cleanup command performs an R2 HEAD check and compares the stored SHA-256/size metadata before deleting local files. If the R2 object is missing or mismatched, the local checkpoint is kept.

### Rule 5: Open/reference data flows Mac → R2 + Supabase → H20

Open data shards are not committed to Git. They live in R2 under their repo-relative `data/raw/...` layout and are cataloged in Supabase `public.data_assets`.

```bash
# Mac: one-time table setup
python -m ecomd.data.data_asset_sync migrate

# Mac: upload missing yfinance shards and upsert data_assets metadata
python -m ecomd.data.data_asset_sync sync data/raw/yfinance/interval=1d/symbol=EURUSD=X
python -m ecomd.data.data_asset_sync sync 'data/raw/yfinance/interval=1d/symbol=^NDX'

# H20: pull missing shards before eval/training
bash scripts/h20_pull_paper_a_data.sh
```

As of 2026-05-19, `EURUSD=X` and `^NDX` daily 2015-2026 shards are archived in R2 and registered in Supabase because eval for EUR/USD and NDX configs depends on them.

### Rule 6: Lightweight results flow H20 → NFS → R2 → Mac (for inspection)

```bash
# H20: after training, write artifacts to NFS
rsync -avh /root/data/ecophys/experiments/<exp-id>/ /AI4S/Users/howardwang/ecophys/experiments/<exp-id>/

# H20: upload lightweight results to R2 for Mac-side inspection
python -m ecomd.data.r2_sync upload /AI4S/Users/howardwang/ecophys/experiments/<exp-id>/ experiments/<exp-id>/

# Mac: pull when needed
python -m ecomd.data.r2_sync download experiments/<exp-id>/ ./data/experiments/<exp-id>/
```

## R2 bucket layout

```
r2://ecophys/
├── raw/                              # unmodified vendor/source downloads
│   ├── yfinance/interval={iv}/symbol={symbol}/year={yyyy}.parquet
│   ├── binance/market={m}/interval={iv}/symbol={symbol}/year={yyyy}/month={mm}.parquet
│   ├── lobster/{symbol}/{yyyy-mm-dd}/messages.parquet
│   └── vendor/{vendor-slug}/...      # e.g. vendor/firstrate/sp500_minute/...
├── processed/                        # normalized schema ready for models
│   ├── returns/{frequency}/{symbol}/{yyyy-mm}.parquet
│   └── lob_features/{symbol}/{yyyy-mm-dd}.parquet
├── splits/                           # train/val/test manifests with explicit time ranges
│   └── v1/{train,val,test}.parquet
├── reference_values/                 # stylized-facts reference JSON per dataset slice
│   └── {dataset}/{period}/stylized_facts.json
├── checkpoints/                      # checkpoint binaries managed by checkpoint_sync + Supabase
│   └── experiments/{experiment_id}/.../checkpoint.pt
├── experiments/                      # lightweight evaluation results, logs, scoreboards
│   └── {experiment_id}/
└── papers/                           # figures + large source data
    └── paper_a/figures/...
```

## Credentials configuration

Mac and H20 each need R2 credentials. Stored **project-local** at `<repo>/.env.r2`:

```bash
# one-time, on each machine
cp .env.r2.example .env.r2
chmod 600 .env.r2
# then edit .env.r2 and fill in:
#   R2_ACCOUNT_ID, R2_BUCKET, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY
```

`r2_sync` locates the project root by walking up until it finds `pyproject.toml`, so the tool works from any CWD. `.env.r2` is gitignored; **never commit**. The committed template is `.env.r2.example`.

## Cost estimate

- Storage: $0.015/GB-mo.
  - Raw crypto tick + LOB full from vendor ≈ 300 GB → $4.5/mo
  - Plus 200 GB processed/ = extra $3/mo
  - **Total steady-state: $5–10/mo**
- Egress: $0 (R2 selling point)
- Requests: $4.50 / million Class-A (PUT) + $0.36 / million Class-B (GET). Our access pattern ≈ 10³–10⁴ reqs/day → < $1/mo
- **All-in R2 spend: < $15/mo**

## Checkpoint operating policy

- Do not commit `checkpoint*.pt`, `.ckpt`, or `.pth` files.
- H20 jobs are complete only after checkpoint sync succeeds and Supabase has an `uploaded` row.
- Mac should pull checkpoint binaries only when local analysis requires model weights; otherwise use Supabase metadata plus lightweight result JSON/scoreboards.
- If Git history accidentally accumulates checkpoint blobs again, rewrite history with `git-filter-repo` before pushing.

## Confirmed pending items

- [ ] User to share R2 credentials (account ID, API key pair, bucket name) → I'll add to our `~/.config/ecophys/r2.env` on Mac; you'll set the same on H20
- [ ] User to verify H20 can actually reach `<account>.r2.cloudflarestorage.com` (whitelist covers R2, should work)
- [ ] When vendor data arrives (~2026-04-26): process through `ecomd.data.vendor_ingest.*` → upload to R2 → pull on H20
