#!/usr/bin/env python3
"""Mac-side ingest for the air-gapped G-D1b payload.

Usage:
  pbpaste > /tmp/gd1b_pasted.txt        # or however the text arrived
  conda run -n ecophys python scripts/gd1b_ingest_text.py /tmp/gd1b_pasted.txt

Extracts the FULL JSON between the markers, verifies the CRC32 the operator also
transcribed, and writes experiments/126_strengthen_workshops/noise_ablation_cost.json.
Fails loudly on CRC mismatch (transcription error) — fix and re-paste.
"""
from __future__ import annotations
import json, re, sys, zlib
from pathlib import Path

EXP = Path("experiments/126_strengthen_workshops")
OUT = EXP / "noise_ablation_cost.json"


def main(txt_path: str) -> int:
    raw = Path(txt_path).read_text()
    m = re.search(r"### FULL JSON:\n(.*?)\n### CRC32", raw, re.S)
    if not m:
        print("ERROR: could not find '### FULL JSON' ... '### CRC32' block in the pasted text.")
        return 1
    payload = m.group(1).strip()
    # tolerate transcription noise around the JSON by extracting the outermost braces
    start, end = payload.find("{"), payload.rfind("}")
    if start < 0 or end < 0:
        print("ERROR: no {...} JSON object found in the FULL JSON block.")
        return 1
    payload = payload[start : end + 1]

    try:
        data = json.loads(payload)
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON parse failed — {e}. Likely a transcription typo. Re-paste.")
        return 1

    crc_reported = None
    cm = re.search(r"### CRC32.*?:\s*([0-9a-fA-F]{8})", raw)
    if cm:
        crc_reported = cm.group(1).lower()
    crc_actual = format(zlib.crc32(payload.encode()) & 0xFFFFFFFF, "08x")

    n_points = len(data.get("G-D1b_pareto_curve_by_alpha", {}))
    print(f"Pareto points ingested: {n_points}  (incl. baseline_tdf5 anchor)")
    print(f"hill range: {min((v.get('hill_tail_index', 9) for v in data.get('G-D1b_pareto_curve_by_alpha',{}).values()), default=None)}")

    if crc_reported and crc_reported != crc_actual:
        print(f"!!! CRC MISMATCH: reported={crc_reported} actual={crc_actual}")
        print("    Payload written to a TEMP file for inspection, NOT into place.")
        tmp = OUT.with_suffix(".json.unverified")
        tmp.write_text(json.dumps(data, indent=2))
        print(f"    -> {tmp}")
        return 2

    print(f"CRC OK ({crc_actual})" if crc_reported else "no CRC in paste — wrote anyway, verify manually")
    OUT.write_text(json.dumps(data, indent=2))
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "/dev/stdin"))
