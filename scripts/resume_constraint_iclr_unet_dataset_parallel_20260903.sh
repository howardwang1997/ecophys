#!/usr/bin/env bash
set -euo pipefail

DATA=/data/ecophys_pdebench_v2/1D_Advection_Sols_beta0.4.hdf5
URL=https://darus.uni-stuttgart.de/api/access/datafile/255674
EXPECTED_BYTES=8232966952
EXPECTED_SHA=d973ff2bb3c2a5edf42957ff029b78672451532ebd6bf475848ff23cfd3ee3b6
WORKERS=24
CHUNK_DIR=/data/ecophys_pdebench_v2/.unet_ranges_20260903
ASSEMBLED=/data/ecophys_pdebench_v2/.1D_Advection_Sols_beta0.4.hdf5.assembled_20260903

if [[ ! -f "$DATA" ]]; then
  printf 'blocked missing_partial_file\n'
  exit 20
fi
START_BYTES=$(stat -c %s "$DATA")
if (( START_BYTES > EXPECTED_BYTES )); then
  printf 'blocked oversized_partial bytes=%s\n' "$START_BYTES"
  exit 21
fi
if (( START_BYTES == EXPECTED_BYTES )); then
  printf '%s  %s\n' "$EXPECTED_SHA" "$DATA" | sha256sum -c -
  printf 'already_complete bytes=%s\n' "$START_BYTES"
  exit 0
fi
if [[ -e "$CHUNK_DIR" ]] || [[ -e "$ASSEMBLED" ]]; then
  printf 'blocked prior_parallel_transfer_artifact\n'
  exit 22
fi

mkdir "$CHUNK_DIR"
MISSING=$((EXPECTED_BYTES - START_BYTES))
CHUNK_SIZE=$(((MISSING + WORKERS - 1) / WORKERS))
printf 'start_bytes=%s missing=%s workers=%s chunk_size=%s\n' \
  "$START_BYTES" "$MISSING" "$WORKERS" "$CHUNK_SIZE"

PIDS=()
CHUNKS=()
EXPECTED_SIZES=()
for ((INDEX = 0; INDEX < WORKERS; INDEX++)); do
  RANGE_START=$((START_BYTES + INDEX * CHUNK_SIZE))
  if (( RANGE_START >= EXPECTED_BYTES )); then
    break
  fi
  RANGE_END=$((RANGE_START + CHUNK_SIZE - 1))
  if (( RANGE_END >= EXPECTED_BYTES )); then
    RANGE_END=$((EXPECTED_BYTES - 1))
  fi
  CHUNK=$(printf '%s/chunk.%03d' "$CHUNK_DIR" "$INDEX")
  CHUNKS+=("$CHUNK")
  EXPECTED_SIZES+=("$((RANGE_END - RANGE_START + 1))")
  (
    curl --fail --silent --show-error --location \
      --retry 100 --retry-all-errors --retry-delay 2 \
      --range "${RANGE_START}-${RANGE_END}" \
      --output "${CHUNK}.tmp" "$URL"
    mv "${CHUNK}.tmp" "$CHUNK"
  ) > "${CHUNK}.log" 2>&1 &
  PIDS+=("$!")
done

STATUS=0
for PID in "${PIDS[@]}"; do
  if ! wait "$PID"; then
    STATUS=1
  fi
done
if (( STATUS != 0 )); then
  printf 'blocked one_or_more_range_downloads_failed\n'
  exit 23
fi

for ((INDEX = 0; INDEX < ${#CHUNKS[@]}; INDEX++)); do
  OBSERVED=$(stat -c %s "${CHUNKS[$INDEX]}")
  if [[ "$OBSERVED" != "${EXPECTED_SIZES[$INDEX]}" ]]; then
    printf 'blocked chunk_size_mismatch index=%s expected=%s observed=%s\n' \
      "$INDEX" "${EXPECTED_SIZES[$INDEX]}" "$OBSERVED"
    exit 24
  fi
done

cp --reflink=auto "$DATA" "$ASSEMBLED"
for CHUNK in "${CHUNKS[@]}"; do
  cat "$CHUNK" >> "$ASSEMBLED"
done
if [[ "$(stat -c %s "$ASSEMBLED")" != "$EXPECTED_BYTES" ]]; then
  printf 'blocked assembled_byte_count_mismatch\n'
  exit 25
fi
printf '%s  %s\n' "$EXPECTED_SHA" "$ASSEMBLED" | sha256sum -c -
mv "$ASSEMBLED" "$DATA"
printf 'parallel_transfer_complete bytes=%s sha256=%s\n' \
  "$EXPECTED_BYTES" "$EXPECTED_SHA"
