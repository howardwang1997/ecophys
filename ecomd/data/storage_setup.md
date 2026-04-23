# Storage Architecture — EcoPhys (v3, final)

**Updated 2026-04-23** — confirmed: R2 registered, H20 NFS path `/AI4S/Users/howardwang/ecophys/`, **Mac cannot mount NFS**, all Mac↔H20 data transit must go through R2.

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

### Rule 4: Checkpoints/results flow H20 → NFS → R2 → Mac (for inspection)

```bash
# H20: after training, write artifacts to NFS
rsync -avh /root/data/ecophys/experiments/<exp-id>/ /AI4S/Users/howardwang/ecophys/experiments/<exp-id>/

# H20: also upload to R2 for Mac-side inspection
python -m ecomd.data.r2_sync upload /AI4S/Users/howardwang/ecophys/experiments/<exp-id>/ experiments/<exp-id>/

# Mac: pull when needed
python -m ecomd.data.r2_sync download experiments/<exp-id>/ ./data/experiments/<exp-id>/
```

## R2 bucket layout

```
r2://ecophys/
├── raw/                              # unmodified vendor/source downloads
│   ├── yfinance/{symbol}/interval={iv}/year={yyyy}.parquet
│   ├── binance/market={m}/interval={iv}/{symbol}/{yyyy}/{mm}.parquet
│   ├── lobster/{symbol}/{yyyy-mm-dd}/messages.parquet
│   └── vendor/{vendor-slug}/...      # e.g. vendor/firstrate/sp500_minute/...
├── processed/                        # normalized schema ready for models
│   ├── returns/{frequency}/{symbol}/{yyyy-mm}.parquet
│   └── lob_features/{symbol}/{yyyy-mm-dd}.parquet
├── splits/                           # train/val/test manifests with explicit time ranges
│   └── v1/{train,val,test}.parquet
├── reference_values/                 # stylized-facts reference JSON per dataset slice
│   └── {dataset}/{period}/stylized_facts.json
├── experiments/                      # trained checkpoints, evaluation results
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

## Confirmed pending items

- [ ] User to share R2 credentials (account ID, API key pair, bucket name) → I'll add to our `~/.config/ecophys/r2.env` on Mac; you'll set the same on H20
- [ ] User to verify H20 can actually reach `<account>.r2.cloudflarestorage.com` (whitelist covers R2, should work)
- [ ] When vendor data arrives (~2026-04-26): process through `ecomd.data.vendor_ingest.*` → upload to R2 → pull on H20
