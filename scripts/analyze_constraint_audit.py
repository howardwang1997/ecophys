"""Apply the D0-frozen decision rules to the constraint-attribution audit records.

Rules are read from papers/proposal/ecomd_constraint_attribution_audit_d0_freeze_2026-08-27.md
and implemented exactly: matched-ID (+/-5%) cell selection against the free_res reference,
seed mean +/- sd, attribution ratio, laundering, and the projection decoupling control.
"""
from __future__ import annotations

import argparse
import itertools
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


def load_records(directory: Path) -> list[dict]:
    records: list[dict] = []
    for path in sorted(directory.glob("*.json")):
        payload = json.loads(path.read_text())
        if "records" not in payload:
            continue
        for rec in payload["records"]:
            rec = dict(rec)
            rec["source_file"] = path.name
            records.append(rec)
    return records


def cell_key(rec: dict) -> tuple[int, int]:
    return int(rec["hidden"]), int(rec["epochs"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records-dir", type=Path, required=True)
    parser.add_argument("--case", default="ood_flat")
    parser.add_argument("--id-tolerance", type=float, default=0.05)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    records = load_records(args.records_dir)
    systems = sorted({r["system"] for r in records})
    sigmas = sorted({r["sigma_flat"] for r in records}, reverse=True)

    output_lines: list[str] = []
    verdicts: dict[str, dict] = {}

    for system, sigma in itertools.product(systems, sigmas):
        subset = [r for r in records if r["system"] == system and r["sigma_flat"] == sigma]
        by_mech_cell: dict[tuple[str, tuple[int, int]], list[dict]] = defaultdict(list)
        for rec in subset:
            by_mech_cell[(rec["mechanism"], cell_key(rec))].append(rec)

        free_res_cells = {
            cell: np.mean([r["id_rmse"] for r in recs])
            for (mech, cell), recs in by_mech_cell.items()
            if mech == "free_res"
        }
        if not free_res_cells:
            continue
        ref_cell = min(free_res_cells, key=free_res_cells.get)
        ref_id = free_res_cells[ref_cell]
        tol = args.id_tolerance * ref_id

        def matched(
            mech: str,
            by_mech_cell: dict = by_mech_cell,
            ref_id: float = ref_id,
            tol: float = tol,
        ) -> tuple[tuple[int, int] | None, list[dict]]:
            candidates = {
                cell: recs
                for (m, cell), recs in by_mech_cell.items()
                if m == mech and abs(np.mean([r["id_rmse"] for r in recs]) - ref_id) <= tol
            }
            if not candidates:
                return None, []
            best = min(candidates, key=lambda c, ref=ref_id: abs(np.mean([r["id_rmse"] for r in candidates[c]]) - ref))
            return best, candidates[best]

        header = (
            f"== {system} sigma_f={sigma} | ref free_res cell={ref_cell} id={ref_id:.4f} "
            f"tol=±{tol:.4f} | case={args.case}"
        )
        output_lines.append(header)
        table: dict[str, dict[str, float]] = {}
        for mech in ("free", "projection", "free_res", "hard", "soft@3.0", "soft@30.0",
                     "soft_res@3.0", "soft_res@30.0"):
            cell, recs = matched(mech)
            if not recs:
                output_lines.append(f"  {mech:>13} : NO MATCHED CELL (non-overlap reported)")
                continue
            cons = [r["cases"][args.case]["conserving_err"] for r in recs]
            drift = [r["cases"][args.case]["mass_drift"] for r in recs]
            idm = [r["id_rmse"] for r in recs]
            row = {
                "cell": f"{cell[0]}x{cell[1]}",
                "id": float(np.mean(idm)),
                "cons_mean": float(np.mean(cons)),
                "cons_sd": float(np.std(cons)),
                "drift_mean": float(np.mean(drift)),
                "drift_sd": float(np.std(drift)),
                "n_seeds": len(recs),
            }
            table[mech] = row
            output_lines.append(
                f"  {mech:>13} cell={row['cell']:>7} id={row['id']:.4f} "
                f"cons={row['cons_mean']:.3f}±{row['cons_sd']:.3f} "
                f"drift={row['drift_mean']:.4f}±{row['drift_sd']:.4f} n={row['n_seeds']}"
            )

        verdict: dict[str, object] = {"table": table}
        if {"free", "free_res", "hard"} <= table.keys():
            d_param = abs(table["free"]["cons_mean"] - table["free_res"]["cons_mean"])
            d_cons = abs(table["free_res"]["cons_mean"] - table["hard"]["cons_mean"])
            sep_param = d_param > 2 * (table["free"]["cons_sd"] + table["free_res"]["cons_sd"])
            verdict["attribution_ratio"] = d_param / d_cons if d_cons > 0 else float("inf")
            verdict["attribution_2sd_rule"] = bool(sep_param)
        if {"free", "soft@30.0"} <= table.keys():
            verdict["laundering_30"] = bool(
                table["soft@30.0"]["cons_mean"] > table["free"]["cons_mean"]
                and table["soft@30.0"]["drift_mean"] < table["free"]["drift_mean"]
            )
        if {"free", "projection"} <= table.keys():
            base = max(table["free"]["cons_mean"], 1e-9)
            verdict["decoupling_ok"] = bool(
                abs(table["projection"]["cons_mean"] - base) / base <= 0.01
            )
        verdicts[f"{system}@{sigma}"] = verdict
        output_lines.append(f"  verdicts: { {k: v for k, v in verdict.items() if k != 'table'} }")

    report = "\n".join(output_lines)
    print(report)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(verdicts, indent=2))
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
