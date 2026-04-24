#!/usr/bin/env bash
# After H20 training / inference finishes, push the lightweight results
# (JSON + logs) to Cloudflare R2 so Mac can pull them back and generate
# the final comparison table.
#
# NOT included in upload:
#   checkpoint.pt — can be 200 KB (small v0/v0.5) up to several GB (v1 @ N=10⁴);
#                   set INCLUDE_CKPT=1 to include. Otherwise left on H20 NFS.
#
# Uses ecomd.data.r2_sync which reads .env.r2 from repo root.
#
# Usage:
#   bash scripts/h20_push_results_to_r2.sh                  # all experiments
#   bash scripts/h20_push_results_to_r2.sh 006 007           # specific experiment IDs
#   INCLUDE_CKPT=1 bash scripts/h20_push_results_to_r2.sh 006

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

INCLUDE_CKPT="${INCLUDE_CKPT:-0}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"

# If args given, map each ID to its experiments/NNN_... directory.
if [[ $# -gt 0 ]]; then
    TARGETS=()
    for id in "$@"; do
        match=$(find experiments -maxdepth 1 -type d -name "${id}_*" | head -1)
        if [[ -z "$match" ]]; then
            echo "WARNING: no experiment directory found for id '$id'"
        else
            TARGETS+=("$match")
        fi
    done
else
    # Default: all experiments/NNN_*/
    mapfile -t TARGETS < <(find experiments -maxdepth 1 -type d -name "[0-9][0-9][0-9]_*" | sort)
fi

if [[ ${#TARGETS[@]} -eq 0 ]]; then
    echo "No experiment directories to sync. Exiting."
    exit 0
fi

echo "─────────────────────────────────────────────────────────────"
echo " Pushing H20 results → R2 (results_${TIMESTAMP}/)"
echo " INCLUDE_CKPT=$INCLUDE_CKPT"
for t in "${TARGETS[@]}"; do echo "   $t"; done
echo "─────────────────────────────────────────────────────────────"

for exp in "${TARGETS[@]}"; do
    results="$exp/results"
    if [[ ! -d "$results" ]]; then
        echo "[skip] $results does not exist"
        continue
    fi
    exp_name="$(basename "$exp")"
    remote_prefix="h20_results/${TIMESTAMP}/${exp_name}/"
    echo ""
    echo "[upload] $results → r2://$remote_prefix"

    # Optionally exclude checkpoints (temporary dir approach)
    staging="$(mktemp -d)"
    trap 'rm -rf "$staging"' EXIT
    mkdir -p "$staging/$exp_name"
    # copy everything except checkpoint.pt (unless INCLUDE_CKPT=1)
    if [[ "$INCLUDE_CKPT" == "1" ]]; then
        cp -r "$results/." "$staging/$exp_name/"
    else
        (cd "$results" && find . -type f ! -name "checkpoint.pt" -exec cp --parents {} "$staging/$exp_name/" \;) 2>/dev/null || \
        # macOS-safe fallback (no --parents in BSD cp)
        (cd "$results" && find . -type f ! -name "checkpoint.pt" | while read -r f; do
            dest="$staging/$exp_name/$f"
            mkdir -p "$(dirname "$dest")"
            cp "$f" "$dest"
         done)
    fi

    python -m ecomd.data.r2_sync upload "$staging/$exp_name/" "$remote_prefix"
done

echo ""
echo "Done. On Mac, pull with:"
echo "   python -m ecomd.data.r2_sync download h20_results/${TIMESTAMP}/ ./h20_results_${TIMESTAMP}/"
