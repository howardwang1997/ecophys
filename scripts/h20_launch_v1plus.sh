#!/usr/bin/env bash
# H20 launch script for EcoMD v1+ distributed training.
# Same as h20_launch_v1.sh but points at the v1+ config (MACE-lite +
# Student-t noise + learnable β, inheriting v0.6 training additions).

export CONFIG="${CONFIG:-experiments/007_ecomd_v1plus/config_h20.yaml}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "$SCRIPT_DIR/h20_launch_v1.sh" "$@"
