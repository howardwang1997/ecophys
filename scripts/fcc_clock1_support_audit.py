from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import TextIO


@dataclass(frozen=True)
class AuctionSchema:
    product_field: str
    result_flag_field: str
    has_switch_bids: bool


@dataclass
class Instruction:
    round_number: int
    frn: str
    price_point: Decimal | None = None
    products: set[tuple[str, str]] = field(default_factory=set)


SCHEMAS = {
    "108": AuctionSchema("category", "fully_processed_flag", True),
    "110": AuctionSchema("category", "fully_processed_flag", True),
    "113": AuctionSchema("channel_block", "fully_applied_flag", False),
}


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


def load_result_keys(
    path: Path,
    *,
    auction_id: str,
    schema: AuctionSchema,
) -> tuple[set[tuple[int, str, str, str]], set[tuple[int, str, str, str]], int]:
    fields = (
        "auction_id",
        "round",
        "frn",
        "market",
        schema.product_field,
        schema.result_flag_field,
    )
    all_keys: set[tuple[int, str, str, str]] = set()
    negative_keys: set[tuple[int, str, str, str]] = set()
    row_count = 0
    wrong_auction_rows = 0
    invalid_flag_rows = 0
    with zipfile.ZipFile(path) as archive, open_single_csv(archive) as handle:
        reader = csv.reader(handle)
        indices = required_indices(next(reader), fields)
        for row in reader:
            row_count += 1
            if row[indices["auction_id"]] != auction_id:
                wrong_auction_rows += 1
                continue
            flag = row[indices[schema.result_flag_field]].strip()
            if flag not in {"Y", "N"}:
                invalid_flag_rows += 1
                continue
            key = (
                int(row[indices["round"]]),
                row[indices["frn"]],
                row[indices["market"]],
                row[indices[schema.product_field]],
            )
            all_keys.add(key)
            if flag == "N":
                negative_keys.add(key)
    if wrong_auction_rows or invalid_flag_rows:
        raise ValueError(
            "result integrity failure: "
            f"wrong_auction_rows={wrong_auction_rows}, invalid_flag_rows={invalid_flag_rows}"
        )
    return all_keys, negative_keys, row_count


def load_instructions(
    path: Path,
    *,
    auction_id: str,
    schema: AuctionSchema,
) -> tuple[dict[tuple[int, str, str], Instruction], int, int]:
    common_fields = (
        "auction_id",
        "round",
        "frn",
        "market",
        schema.product_field,
        "price_point",
        "selection_number",
    )
    switch_fields = ("bid_type", "switch_from_category", "switch_to_category")
    fields = common_fields + switch_fields if schema.has_switch_bids else common_fields
    instructions: dict[tuple[int, str, str], Instruction] = {}
    row_count = 0
    wrong_auction_rows = 0
    invalid_rows = 0
    discarded_switch_to_rows = 0
    with zipfile.ZipFile(path) as archive, open_single_csv(archive) as handle:
        reader = csv.reader(handle)
        indices = required_indices(next(reader), fields)
        for row in reader:
            row_count += 1
            if row[indices["auction_id"]] != auction_id:
                wrong_auction_rows += 1
                continue
            try:
                round_number = int(row[indices["round"]])
                price_point = Decimal(row[indices["price_point"]])
            except (ValueError, InvalidOperation):
                invalid_rows += 1
                continue
            frn = row[indices["frn"]]
            selection_number = row[indices["selection_number"]]
            if not frn or not selection_number:
                invalid_rows += 1
                continue
            key = (round_number, frn, selection_number)
            market = row[indices["market"]]
            product = row[indices[schema.product_field]]
            touched_products = {(market, product)}
            if schema.has_switch_bids:
                bid_type = row[indices["bid_type"]]
                if bid_type == "Switch":
                    switch_from = row[indices["switch_from_category"]]
                    switch_to = row[indices["switch_to_category"]]
                    if bool(switch_from) == bool(switch_to):
                        invalid_rows += 1
                        continue
                    if switch_from:
                        discarded_switch_to_rows += 1
                        continue
                    touched_products.add((market, switch_to))
                elif bid_type != "Simple":
                    invalid_rows += 1
                    continue
            if key in instructions:
                invalid_rows += 1
                continue
            instructions[key] = Instruction(
                round_number=round_number,
                frn=frn,
                price_point=price_point,
                products=touched_products,
            )
    missing_price_points = sum(
        instruction.price_point is None for instruction in instructions.values()
    )
    if wrong_auction_rows or invalid_rows or missing_price_points:
        raise ValueError(
            "bid integrity failure: "
            f"wrong_auction_rows={wrong_auction_rows}, invalid_rows={invalid_rows}, "
            f"missing_price_points={missing_price_points}"
        )
    return instructions, row_count, discarded_switch_to_rows


def summarize_support(
    *,
    auction_id: str,
    instructions: dict[tuple[int, str, str], Instruction],
    result_keys: set[tuple[int, str, str, str]],
    negative_result_keys: set[tuple[int, str, str, str]],
    bid_rows: int,
    result_rows: int,
    discarded_switch_to_rows: int,
    minimum_tie_blocks: int,
) -> dict[str, int | bool | str]:
    blocks: dict[tuple[int, Decimal], list[Instruction]] = defaultdict(list)
    unmatched_touched_products = 0
    instructions_with_negative_flag = 0
    negative_by_instruction: dict[int, bool] = {}
    for instruction in instructions.values():
        assert instruction.price_point is not None
        blocks[(instruction.round_number, instruction.price_point)].append(instruction)
        touched_keys = {
            (instruction.round_number, instruction.frn, market, product)
            for market, product in instruction.products
        }
        unmatched_touched_products += len(touched_keys - result_keys)
        has_negative = bool(touched_keys & negative_result_keys)
        negative_by_instruction[id(instruction)] = has_negative
        instructions_with_negative_flag += int(has_negative)

    multi_instruction_blocks = 0
    structurally_coupled_blocks = 0
    upper_bound_blocks = 0
    for block in blocks.values():
        if len(block) < 2:
            continue
        multi_instruction_blocks += 1
        frn_counts = Counter(instruction.frn for instruction in block)
        product_counts = Counter(
            product for instruction in block for product in instruction.products
        )
        coupled_instruction_ids = {
            id(instruction)
            for instruction in block
            if frn_counts[instruction.frn] > 1
            or any(product_counts[product] > 1 for product in instruction.products)
        }
        if coupled_instruction_ids:
            structurally_coupled_blocks += 1
        if any(
            negative_by_instruction[id(instruction)]
            and id(instruction) in coupled_instruction_ids
            for instruction in block
        ):
            upper_bound_blocks += 1

    return {
        "auction_id": auction_id,
        "bid_rows": bid_rows,
        "result_rows": result_rows,
        "discarded_switch_to_rows": discarded_switch_to_rows,
        "instructions": len(instructions),
        "unmatched_touched_products": unmatched_touched_products,
        "tie_blocks": len(blocks),
        "multi_instruction_tie_blocks": multi_instruction_blocks,
        "structurally_coupled_tie_blocks": structurally_coupled_blocks,
        "instructions_with_any_n_flag": instructions_with_negative_flag,
        "order_sensitive_support_upper_bound": upper_bound_blocks,
        "provisional_minimum": minimum_tie_blocks,
        "upper_bound_prefilter_pass": upper_bound_blocks >= minimum_tie_blocks,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--auction", choices=sorted(SCHEMAS), required=True)
    parser.add_argument("--bids-zip", type=Path, required=True)
    parser.add_argument("--results-zip", type=Path, required=True)
    parser.add_argument("--bids-sha256", required=True)
    parser.add_argument("--results-sha256", required=True)
    parser.add_argument("--minimum-tie-blocks", type=int, default=30)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    observed_bids_hash = sha256_file(args.bids_zip)
    observed_results_hash = sha256_file(args.results_zip)
    if observed_bids_hash != args.bids_sha256:
        raise SystemExit("bids SHA-256 mismatch")
    if observed_results_hash != args.results_sha256:
        raise SystemExit("results SHA-256 mismatch")
    schema = SCHEMAS[args.auction]
    result_keys, negative_result_keys, result_rows = load_result_keys(
        args.results_zip,
        auction_id=args.auction,
        schema=schema,
    )
    instructions, bid_rows, discarded_switch_to_rows = load_instructions(
        args.bids_zip,
        auction_id=args.auction,
        schema=schema,
    )
    summary = summarize_support(
        auction_id=args.auction,
        instructions=instructions,
        result_keys=result_keys,
        negative_result_keys=negative_result_keys,
        bid_rows=bid_rows,
        result_rows=result_rows,
        discarded_switch_to_rows=discarded_switch_to_rows,
        minimum_tie_blocks=args.minimum_tie_blocks,
    )
    output = {
        "schema_version": 1,
        "bids_sha256": observed_bids_hash,
        "results_sha256": observed_results_hash,
        **summary,
    }
    print(json.dumps(output, sort_keys=True))


if __name__ == "__main__":
    main()
