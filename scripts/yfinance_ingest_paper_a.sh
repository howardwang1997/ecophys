#!/usr/bin/env bash
# Download new daily tickers for Paper A solidify M (multi-asset universality)
# and N (crash OOS) series.
#
# 7 new tickers: DAX (^GDAXI), EuroSTOXX 50 (^STOXX50E), Hang Seng (^HSI),
# Nikkei 225 (^N225), QQQ, IWM, GLD daily 2015-2026. Uses existing
# ecomd.data.yfinance_ingest pipeline; writes parquet shards to
# data/raw/yfinance/interval=1d/symbol={SYM}/year={YYYY}.parquet.
#
# Run on Mac:
#   bash scripts/yfinance_ingest_paper_a.sh
#
# Existing tickers (^GSPC, SPY) are skipped if shards exist; pass
# FORCE_DOWNLOAD=1 to re-download.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Comma-separated; ^... need single-quoting in shell to avoid expansion
NEW_TICKERS='^GDAXI,^STOXX50E,^HSI,^N225,QQQ,IWM,GLD'

START_DATE="${START_DATE:-2015-01-01}"
END_DATE="${END_DATE:-2026-04-26}"

echo "[ingest] symbols: $NEW_TICKERS"
echo "[ingest] period:  $START_DATE → $END_DATE"
echo ""

# Check existing shards (skip already-downloaded unless FORCE)
ROOT="$REPO_ROOT/data/raw/yfinance/interval=1d"
NEEDED=()
IFS=',' read -ra TICKERS <<< "$NEW_TICKERS"
for sym in "${TICKERS[@]}"; do
    d="$ROOT/symbol=$sym"
    if [[ -d "$d" ]] && compgen -G "$d/year=*.parquet" > /dev/null && \
       [[ -z "${FORCE_DOWNLOAD:-}" ]]; then
        n=$(ls "$d"/year=*.parquet 2>/dev/null | wc -l | tr -d ' ')
        echo "  [skip] $sym already has $n shard(s)"
    else
        NEEDED+=("$sym")
    fi
done

if [[ ${#NEEDED[@]} -eq 0 ]]; then
    echo "[ingest] all tickers already present — skipping (use FORCE_DOWNLOAD=1 to redo)"
    exit 0
fi

JOIN=$(IFS=','; echo "${NEEDED[*]}")
echo "[ingest] downloading: $JOIN"

conda run -n ecophys python -m ecomd.data.yfinance_ingest \
    --symbols "$JOIN" \
    --start "$START_DATE" --end "$END_DATE" \
    --interval 1d

echo ""
echo "[ingest] done. Verify:"
for sym in "${NEEDED[@]}"; do
    d="$ROOT/symbol=$sym"
    n=$(ls "$d"/year=*.parquet 2>/dev/null | wc -l | tr -d ' ')
    echo "  $sym: $n shard(s) in $d"
done
