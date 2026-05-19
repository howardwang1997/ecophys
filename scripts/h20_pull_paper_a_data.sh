#!/usr/bin/env bash
# H20-side: pull Paper A yfinance tickers from R2. These shards are cataloged
# in Supabase `data_assets` and stored under r2://ecophys/raw/yfinance/...
#
# Run on H20:
#   bash scripts/h20_pull_paper_a_data.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

TICKERS=('^GDAXI' '^STOXX50E' '^HSI' '^N225' QQQ IWM GLD 'EURUSD=X' '^NDX')

for sym in "${TICKERS[@]}"; do
    echo "═ pulling $sym from r2://ecophys/raw/yfinance/interval=1d/symbol=$sym"
    bash scripts/h20_pull_from_r2.sh "raw/yfinance/interval=1d/symbol=$sym"
done

echo ""
echo "── verify ──"
for sym in "${TICKERS[@]}"; do
    d="$REPO_ROOT/data/raw/yfinance/interval=1d/symbol=$sym"
    if [[ -d "$d" ]]; then
        n=$(ls "$d"/year=*.parquet 2>/dev/null | wc -l | tr -d ' ')
        echo "  $sym: $n shards"
    else
        echo "  $sym: MISSING"
    fi
done
