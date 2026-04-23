#!/usr/bin/env bash
# H20-side: pull data from Cloudflare R2 into the NFS canonical store, then
# optionally rsync a subset into the local NVMe hot cache.
#
# Prereqs on H20:
#   - conda env `ecophys` installed (pip install -e . from this repo)
#   - ~/.config/ecophys/r2.env with R2 credentials
#   - NFS mounted at /AI4S/Users/howardwang/ecophys/
#   - Data drive mounted at /data/ecophys/
#
# Usage:
#   bash scripts/h20_pull_from_r2.sh processed/sp500_minute
#   bash scripts/h20_pull_from_r2.sh processed/ --hot-cache-subset sp500_minute

set -euo pipefail

PREFIX="${1:-}"
HOT_CACHE_SUBSET=""
CONDA_ENV="${CONDA_ENV:-ecophys}"

shift || true
while [[ $# -gt 0 ]]; do
    case "$1" in
        --hot-cache-subset)
            HOT_CACHE_SUBSET="$2"; shift 2 ;;
        *)
            echo "unknown arg: $1" >&2; exit 2 ;;
    esac
done

if [[ -z "$PREFIX" ]]; then
    echo "usage: $0 <r2-prefix> [--hot-cache-subset <subpath>]" >&2
    exit 2
fi

NFS_ROOT="/AI4S/Users/howardwang/ecophys"
HOT_ROOT="/root/data/ecophys"

NFS_DST="${NFS_ROOT}/${PREFIX}"
mkdir -p "$NFS_DST"

echo "[$(date -u +%FT%TZ)] pulling r2://ecophys/${PREFIX} → ${NFS_DST}"
conda run -n "$CONDA_ENV" python -m ecomd.data.r2_sync download "$PREFIX" "$NFS_DST"

if [[ -n "$HOT_CACHE_SUBSET" ]]; then
    HOT_DST="${HOT_ROOT}/${PREFIX%/}/${HOT_CACHE_SUBSET}"
    NFS_SRC="${NFS_DST%/}/${HOT_CACHE_SUBSET}"
    mkdir -p "$HOT_DST"
    echo "[$(date -u +%FT%TZ)] rsync ${NFS_SRC} → ${HOT_DST}"
    rsync -avh --info=progress2 "${NFS_SRC}/" "${HOT_DST}/"
fi

echo "[$(date -u +%FT%TZ)] done"
