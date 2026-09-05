from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import zipfile
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import TextIO

Key = tuple[int, str, str, str]


@dataclass(frozen=True)
class ResultState:
    fully_processed: str
    processed_demand: int


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def open_single_csv(archive: zipfile.ZipFile) -> TextIO:
    members = [name for name in archive.namelist() if name.lower().endswith(".csv")]
    if len(members) != 1:
        raise ValueError("archive must contain exactly one CSV member")
    return io.TextIOWrapper(archive.open(members[0]), encoding="utf-8-sig", newline="")


def required_indices(header: list[str], fields: tuple[str, ...]) -> dict[str, int]:
    normalized = [value.lstrip("\ufeff") for value in header]
    missing = sorted(set(fields) - set(normalized))
    if missing:
        raise ValueError(f"required schema fields absent: {', '.join(missing)}")
    return {field_name: normalized.index(field_name) for field_name in fields}


def load_results(path: Path) -> tuple[dict[Key, ResultState], int]:
    fields = (
        "auction_id",
        "round",
        "frn",
        "market",
        "category",
        "processed_demand",
        "fully_processed_flag",
    )
    results: dict[Key, ResultState] = {}
    rows = 0
    with zipfile.ZipFile(path) as archive, open_single_csv(archive) as handle:
        reader = csv.reader(handle)
        indices = required_indices(next(reader), fields)
        for row in reader:
            rows += 1
            if row[indices["auction_id"]] != "108":
                raise ValueError("unexpected auction id in results")
            key = (
                int(row[indices["round"]]),
                row[indices["frn"]],
                row[indices["market"]],
                row[indices["category"]],
            )
            flag = row[indices["fully_processed_flag"]].strip()
            demand = int(row[indices["processed_demand"]])
            if flag not in {"Y", "N"} or demand not in {0, 1}:
                raise ValueError("invalid result state")
            if key in results:
                raise ValueError("duplicate result key")
            results[key] = ResultState(flag, demand)
    return results, rows


def classify_bid(row: list[str], indices: dict[str, int]) -> tuple[str, int, int | None]:
    round_number = int(row[indices["round"]])
    bid_type = row[indices["bid_type"]].strip()
    quantity = int(row[indices["quantity"]])
    if quantity not in {0, 1}:
        raise ValueError("invalid bid quantity")
    previous_raw = row[indices["previous_round_processed_demand"]].strip()
    previous = None if previous_raw == "" else int(previous_raw)
    if previous not in {None, 0, 1}:
        raise ValueError("invalid previous demand")

    switch_from = row[indices["switch_from_category"]].strip()
    switch_to = row[indices["switch_to_category"]].strip()
    if round_number == 1:
        if bid_type != "Simple" or previous is not None:
            raise ValueError("invalid round-one bid")
        return "round1_simple", quantity, previous
    if previous is None:
        raise ValueError("missing prior state after round one")
    if bid_type == "Switch":
        if bool(switch_from) == bool(switch_to):
            raise ValueError("invalid switch orientation")
        return ("switch_to" if switch_from else "switch_from"), quantity, previous
    if bid_type != "Simple" or switch_from or switch_to:
        raise ValueError("invalid simple bid")
    simple_classes = {
        (1, 1): "simple_maintain",
        (1, 0): "simple_reduce",
        (0, 1): "simple_increase",
        (0, 0): "simple_noop_zero",
    }
    return simple_classes[(previous, quantity)], quantity, previous


def transition_is_possible(
    bid_class: str,
    quantity: int,
    result: ResultState,
) -> bool:
    if bid_class == "round1_simple":
        return result.fully_processed == "Y" and result.processed_demand == quantity
    expected = {
        "simple_maintain": {"Y": 1},
        "simple_reduce": {"Y": 0, "N": 1},
        "simple_increase": {"Y": 1, "N": 0},
        "simple_noop_zero": {"Y": 0},
        "switch_from": {"Y": 0, "N": 1},
        "switch_to": {"Y": 1, "N": 0},
    }
    return result.fully_processed in expected[bid_class] and (
        result.processed_demand == expected[bid_class][result.fully_processed]
    )


def audit_row_contract(bids_path: Path, results_path: Path) -> dict[str, object]:
    results, result_rows = load_results(results_path)
    bid_fields = (
        "auction_id",
        "round",
        "frn",
        "market",
        "category",
        "bid_type",
        "quantity",
        "switch_from_category",
        "switch_to_category",
        "previous_round_processed_demand",
        "price_point",
        "price",
        "start_of_round_price",
    )
    class_status: Counter[tuple[str, str]] = Counter()
    round1_quantity_status: Counter[tuple[int, str]] = Counter()
    unmatched_round1_zero_price_point: Counter[str] = Counter()
    unmatched_round1_zero_price_equality: Counter[str] = Counter()
    transitions: Counter[tuple[str, str, int]] = Counter()
    bid_keys: set[Key] = set()
    impossible_transitions = 0
    bid_rows = 0
    with zipfile.ZipFile(bids_path) as archive, open_single_csv(archive) as handle:
        reader = csv.reader(handle)
        indices = required_indices(next(reader), bid_fields)
        for row in reader:
            bid_rows += 1
            if row[indices["auction_id"]] != "108":
                raise ValueError("unexpected auction id in bids")
            round_number = int(row[indices["round"]])
            key = (
                round_number,
                row[indices["frn"]],
                row[indices["market"]],
                row[indices["category"]],
            )
            if key in bid_keys:
                raise ValueError("duplicate bid-product key")
            bid_keys.add(key)
            bid_class, quantity, _ = classify_bid(row, indices)
            result = results.get(key)
            status = "matched" if result is not None else "unmatched"
            class_status[(bid_class, status)] += 1
            if bid_class == "round1_simple":
                round1_quantity_status[(quantity, status)] += 1
            if bid_class == "round1_simple" and quantity == 0 and result is None:
                try:
                    price_point = Decimal(row[indices["price_point"]])
                except InvalidOperation as error:
                    raise ValueError("invalid price point") from error
                price_class = "zero" if price_point == 0 else "nonzero"
                unmatched_round1_zero_price_point[price_class] += 1
                price_equal = (
                    row[indices["price"]].strip()
                    == row[indices["start_of_round_price"]].strip()
                )
                equality_class = "equal" if price_equal else "unequal"
                unmatched_round1_zero_price_equality[equality_class] += 1
            if result is not None:
                transitions[(bid_class, result.fully_processed, result.processed_demand)] += 1
                impossible_transitions += int(
                    not transition_is_possible(bid_class, quantity, result)
                )

    result_only_keys = len(set(results) - bid_keys)
    matched_rows = sum(count for (__, status), count in class_status.items() if status == "matched")
    unmatched_rows = sum(
        count for (__, status), count in class_status.items() if status == "unmatched"
    )
    action_changing_classes = {
        "simple_reduce",
        "simple_increase",
        "switch_from",
    }
    unmatched_action_changing = sum(
        count
        for (bid_class, status), count in class_status.items()
        if status == "unmatched" and bid_class in action_changing_classes
    )
    visible_transitions = {
        f"{bid_class}|{flag}|{demand}": count
        for (bid_class, flag, demand), count in sorted(transitions.items())
        if count >= 10
    }
    return {
        "schema_version": 1,
        "bid_rows": bid_rows,
        "result_rows": result_rows,
        "matched_rows": matched_rows,
        "unmatched_rows": unmatched_rows,
        "result_only_keys": result_only_keys,
        "unmatched_action_changing_rows": unmatched_action_changing,
        "impossible_matched_transitions": impossible_transitions,
        "class_by_match_status": {
            f"{bid_class}|{status}": count
            for (bid_class, status), count in sorted(class_status.items())
        },
        "round1_quantity_by_match_status_ge_10": {
            f"{quantity}|{status}": count
            for (quantity, status), count in sorted(round1_quantity_status.items())
            if count >= 10
        },
        "unmatched_round1_zero_by_price_point_class": {
            price_class: unmatched_round1_zero_price_point.get(price_class, 0)
            for price_class in ("zero", "nonzero")
        },
        "unmatched_round1_zero_by_price_start_equality": {
            equality_class: unmatched_round1_zero_price_equality.get(equality_class, 0)
            for equality_class in ("equal", "unequal")
        },
        "matched_transition_cells_ge_10": visible_transitions,
        "bid_accounting_closes": bid_rows == matched_rows + unmatched_rows,
        "result_accounting_closes": result_rows == matched_rows + result_only_keys,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bids-zip", type=Path, required=True)
    parser.add_argument("--results-zip", type=Path, required=True)
    parser.add_argument("--bids-sha256", required=True)
    parser.add_argument("--results-sha256", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    bids_hash = sha256_file(args.bids_zip)
    results_hash = sha256_file(args.results_zip)
    if bids_hash != args.bids_sha256:
        raise SystemExit("bids SHA-256 mismatch")
    if results_hash != args.results_sha256:
        raise SystemExit("results SHA-256 mismatch")
    output = {
        "bids_sha256": bids_hash,
        "results_sha256": results_hash,
        **audit_row_contract(args.bids_zip, args.results_zip),
    }
    print(json.dumps(output, sort_keys=True))


if __name__ == "__main__":
    main()
