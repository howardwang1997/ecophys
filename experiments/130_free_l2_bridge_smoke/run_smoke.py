"""Stream free LOBSTER samples and validate a message-to-L2 observation bridge."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import resource
import subprocess
import time
import zipfile
from collections import defaultdict
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SAMPLE_ROOT = ROOT / "data" / "sample" / "LOBSTER"
DEFAULT_OUT = ROOT / "experiments" / "130_free_l2_bridge_smoke" / "L2_SMOKE_RESULTS.json"
MSG_DTYPES = {
    0: np.float64,
    1: np.int8,
    2: np.int64,
    3: np.int64,
    4: np.int64,
    5: np.int8,
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _identity(path: Path) -> tuple[str, int]:
    match = re.fullmatch(r"LOBSTER_SampleFile_([A-Z]+)_\d{4}-\d{2}-\d{2}_(\d+)\.zip", path.name)
    if match is None:
        raise ValueError(f"unexpected LOBSTER sample filename: {path.name}")
    return match.group(1), int(match.group(2))


def _csv_names(archive: zipfile.ZipFile) -> tuple[str, str]:
    names = archive.namelist()
    message = next((name for name in names if "message" in name.lower() and name.endswith(".csv")), None)
    book = next((name for name in names if "orderbook" in name.lower() and name.endswith(".csv")), None)
    if message is None or book is None:
        raise ValueError(f"archive lacks message/orderbook CSV: {names}")
    return message, book


def _paired_chunks(
    archive: zipfile.ZipFile,
    message_name: str,
    book_name: str,
    *,
    max_rows: int,
    chunk_rows: int,
) -> Iterator[tuple[np.ndarray, np.ndarray]]:
    with archive.open(message_name) as message_stream, archive.open(book_name) as book_stream:
        messages = pd.read_csv(
            message_stream,
            header=None,
            dtype=MSG_DTYPES,
            nrows=max_rows,
            chunksize=chunk_rows,
        )
        books = pd.read_csv(
            book_stream,
            header=None,
            dtype=np.int64,
            nrows=max_rows,
            chunksize=chunk_rows,
        )
        message_iter = iter(messages)
        book_iter = iter(books)
        while True:
            try:
                message_chunk = next(message_iter)
            except StopIteration as message_end:
                try:
                    next(book_iter)
                except StopIteration:
                    return
                raise RuntimeError("orderbook has more chunks than messages") from message_end
            try:
                book_chunk = next(book_iter)
            except StopIteration as exc:
                raise RuntimeError("messages have more chunks than orderbook") from exc
            if len(message_chunk) != len(book_chunk):
                raise RuntimeError(
                    f"chunk row mismatch: messages={len(message_chunk)}, book={len(book_chunk)}"
                )
            yield message_chunk.to_numpy(), book_chunk.to_numpy(dtype=np.int64, copy=False)


def _online_add(acc: dict[str, float], x: np.ndarray, y: np.ndarray) -> None:
    finite = np.isfinite(x) & np.isfinite(y)
    x = x[finite].astype(np.float64, copy=False)
    y = y[finite].astype(np.float64, copy=False)
    acc["n"] += len(x)
    acc["sx"] += float(x.sum())
    acc["sy"] += float(y.sum())
    acc["sxx"] += float(np.dot(x, x))
    acc["syy"] += float(np.dot(y, y))
    acc["sxy"] += float(np.dot(x, y))


def _correlation(acc: dict[str, float]) -> float | None:
    n = acc["n"]
    if n < 2:
        return None
    cov = acc["sxy"] - acc["sx"] * acc["sy"] / n
    vx = acc["sxx"] - acc["sx"] ** 2 / n
    vy = acc["syy"] - acc["sy"] ** 2 / n
    if vx <= 0.0 or vy <= 0.0:
        return None
    return float(cov / np.sqrt(vx * vy))


def inspect_archive(path: Path, *, max_rows: int, chunk_rows: int) -> dict[str, Any]:
    symbol, level = _identity(path)
    started = time.perf_counter()
    counts: defaultdict[str, int] = defaultdict(int)
    recon: dict[int, defaultdict[str, float]] = {
        event_type: defaultdict(float) for event_type in (1, 2, 3, 4)
    }
    hidden_total = 0
    hidden_unchanged = 0
    ofi_message = defaultdict(float)
    ofi_mid = defaultdict(float)
    prev_book: np.ndarray | None = None
    prev_time: float | None = None

    with zipfile.ZipFile(path) as archive:
        bad_member = archive.testzip()
        if bad_member is not None:
            raise RuntimeError(f"ZIP CRC failure in {bad_member}")
        message_name, book_name = _csv_names(archive)
        for messages, books in _paired_chunks(
            archive, message_name, book_name, max_rows=max_rows, chunk_rows=chunk_rows
        ):
            n_rows = len(messages)
            counts["rows"] += n_rows
            if books.shape[1] != 4 * level:
                raise RuntimeError(
                    f"{path.name}: expected {4 * level} book columns, got {books.shape[1]}"
                )

            times = messages[:, 0].astype(np.float64)
            if prev_time is not None and times[0] < prev_time:
                counts["time_violations"] += 1
            counts["time_violations"] += int(np.count_nonzero(np.diff(times) < 0.0))
            prev_time = float(times[-1])

            ask_price = books[:, 0::4]
            ask_size = books[:, 1::4]
            bid_price = books[:, 2::4]
            bid_size = books[:, 3::4]
            counts["crossed_or_locked"] += int(np.count_nonzero(ask_price[:, 0] <= bid_price[:, 0]))
            counts["ask_order_violations"] += int(np.count_nonzero(np.diff(ask_price, axis=1) < 0))
            counts["bid_order_violations"] += int(np.count_nonzero(np.diff(bid_price, axis=1) > 0))
            counts["negative_size_violations"] += int(
                np.count_nonzero(ask_size < 0) + np.count_nonzero(bid_size < 0)
            )
            event_types, event_counts = np.unique(messages[:, 1].astype(np.int64), return_counts=True)
            for event_type, count in zip(event_types, event_counts, strict=True):
                counts[f"event_{event_type}"] += int(count)

            if prev_book is None:
                if n_rows < 2:
                    prev_book = books[-1].copy()
                    continue
                pre = books[:-1]
                post = books[1:]
                msg = messages[1:]
            else:
                pre = np.vstack([prev_book, books[:-1]])
                post = books
                msg = messages
            prev_book = books[-1].copy()
            counts["transitions"] += len(msg)

            pre_ask_price, pre_ask_size = pre[:, 0::4], pre[:, 1::4]
            pre_bid_price, pre_bid_size = pre[:, 2::4], pre[:, 3::4]
            post_ask_price, post_ask_size = post[:, 0::4], post[:, 1::4]
            post_bid_price, post_bid_size = post[:, 2::4], post[:, 3::4]

            event = msg[:, 1].astype(np.int64)
            size = msg[:, 3].astype(np.int64)
            price = msg[:, 4].astype(np.int64)
            direction = msg[:, 5].astype(np.int64)
            for event_type in (1, 2, 3, 4):
                for side, pre_price, pre_size, post_price, post_size in (
                    (1, pre_bid_price, pre_bid_size, post_bid_price, post_bid_size),
                    (-1, pre_ask_price, pre_ask_size, post_ask_price, post_ask_size),
                ):
                    mask = (event == event_type) & (direction == side)
                    if not np.any(mask):
                        continue
                    p = price[mask]
                    before = np.sum(pre_size[mask] * (pre_price[mask] == p[:, None]), axis=1)
                    after = np.sum(post_size[mask] * (post_price[mask] == p[:, None]), axis=1)
                    visible = np.any(pre_price[mask] == p[:, None], axis=1) | np.any(
                        post_price[mask] == p[:, None], axis=1
                    )
                    delta = after - before
                    expected = size[mask] if event_type == 1 else -size[mask]
                    error = delta[visible] - expected[visible]
                    recon[event_type]["all"] += int(np.count_nonzero(mask))
                    recon[event_type]["visible"] += int(np.count_nonzero(visible))
                    recon[event_type]["exact"] += int(np.count_nonzero(error == 0))
                    recon[event_type]["abs_error"] += float(np.abs(error).sum())

            hidden = event == 5
            hidden_total += int(np.count_nonzero(hidden))
            if np.any(hidden):
                hidden_unchanged += int(np.count_nonzero(np.all(pre[hidden] == post[hidden], axis=1)))

            pbp, pbq = pre_bid_price[:, 0], pre_bid_size[:, 0]
            pap, paq = pre_ask_price[:, 0], pre_ask_size[:, 0]
            nbp, nbq = post_bid_price[:, 0], post_bid_size[:, 0]
            nap, naq = post_ask_price[:, 0], post_ask_size[:, 0]
            ofi = (
                (nbp >= pbp) * nbq
                - (nbp <= pbp) * pbq
                - (nap <= pap) * naq
                + (nap >= pap) * paq
            ).astype(np.float64)
            action = np.where(event == 1, 1, np.where(np.isin(event, (2, 3, 4)), -1, 0))
            displayed_proxy = (direction * size * action).astype(np.float64)
            mid_delta = ((nap + nbp) - (pap + pbp)).astype(np.float64) / 2.0
            _online_add(ofi_message, ofi, displayed_proxy)
            _online_add(ofi_mid, ofi, mid_delta)

    recon_out: dict[str, dict[str, float | int | None]] = {}
    pooled_visible = pooled_exact = 0
    for event_type, values in recon.items():
        visible = int(values["visible"])
        exact = int(values["exact"])
        pooled_visible += visible
        pooled_exact += exact
        recon_out[str(event_type)] = {
            "all_events": int(values["all"]),
            "visible_events": visible,
            "visible_fraction": visible / values["all"] if values["all"] else None,
            "exact_events": exact,
            "exact_rate_visible": exact / visible if visible else None,
            "mean_absolute_error_visible": values["abs_error"] / visible if visible else None,
        }

    rows = counts["rows"]
    transitions = counts["transitions"]
    return {
        "archive": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
        "archive_bytes": path.stat().st_size,
        "symbol": symbol,
        "level": level,
        "rows_processed": rows,
        "reached_row_cap": rows == max_rows,
        "seconds": time.perf_counter() - started,
        "rows_per_second": rows / max(time.perf_counter() - started, 1e-9),
        "counts": dict(counts),
        "rates": {
            "time_violation": counts["time_violations"] / max(rows - 1, 1),
            "crossed_or_locked": counts["crossed_or_locked"] / max(rows, 1),
            "ask_order_violation_per_comparison": counts["ask_order_violations"] / max(rows * (level - 1), 1),
            "bid_order_violation_per_comparison": counts["bid_order_violations"] / max(rows * (level - 1), 1),
            "negative_size_violation_per_cell": counts["negative_size_violations"] / max(rows * 2 * level, 1),
            "visible_reconstruction_exact": pooled_exact / pooled_visible if pooled_visible else None,
            "hidden_display_unchanged": hidden_unchanged / hidden_total if hidden_total else None,
        },
        "reconstruction_by_event_type": recon_out,
        "hidden_execution": {"events": hidden_total, "display_unchanged": hidden_unchanged},
        "correlations": {
            "l1_ofi_vs_displayed_message_proxy": _correlation(ofi_message),
            "l1_ofi_vs_midprice_delta": _correlation(ofi_mid),
        },
        "transition_rows": transitions,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-root", type=Path, default=SAMPLE_ROOT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--max-rows", type=int, default=200_000)
    parser.add_argument("--chunk-rows", type=int, default=50_000)
    args = parser.parse_args()

    archives = sorted(args.sample_root.glob("*.zip"))
    if not archives:
        raise FileNotFoundError(f"no ZIP files under {args.sample_root}")
    started = time.perf_counter()
    samples = [
        inspect_archive(path, max_rows=args.max_rows, chunk_rows=args.chunk_rows)
        for path in archives
    ]
    pooled_visible = sum(
        int(item["rates"]["visible_reconstruction_exact"] is not None)
        for item in samples
    )
    hard_gate = {
        "all_archives_processed": len(samples) == len(archives),
        "crossed_or_locked_below_1e-4": all(item["rates"]["crossed_or_locked"] < 1e-4 for item in samples),
        "level_order_below_1e-6": all(
            item["rates"]["ask_order_violation_per_comparison"] < 1e-6
            and item["rates"]["bid_order_violation_per_comparison"] < 1e-6
            for item in samples
        ),
        "sizes_nonnegative_below_1e-6": all(
            item["rates"]["negative_size_violation_per_cell"] < 1e-6 for item in samples
        ),
        "visible_reconstruction_at_least_0_99": all(
            item["rates"]["visible_reconstruction_exact"] is not None
            and item["rates"]["visible_reconstruction_exact"] >= 0.99
            for item in samples
        ),
        "hidden_unchanged_at_least_0_99_when_present": all(
            item["rates"]["hidden_display_unchanged"] is None
            or item["rates"]["hidden_display_unchanged"] >= 0.99
            for item in samples
        ),
    }
    payload = {
        "experiment": "130_free_l2_bridge_smoke",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "platform": platform.platform(),
        "arguments": vars(args) | {"sample_root": str(args.sample_root), "out": str(args.out)},
        "wall_seconds": time.perf_counter() - started,
        "peak_rss_raw": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "n_archives": len(samples),
        "n_archives_with_visible_events": pooled_visible,
        "hard_gate": hard_gate,
        "all_hard_gates_pass": all(hard_gate.values()),
        "samples": samples,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "out": str(args.out),
        "n_archives": len(samples),
        "all_hard_gates_pass": payload["all_hard_gates_pass"],
        "hard_gate": hard_gate,
        "sample_rates": {
            f"{item['symbol']}:L{item['level']}": item["rates"] for item in samples
        },
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
