"""Fit frozen dynamic-book observation-only baselines on free LOBSTER samples."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import re
import subprocess
import time
import zipfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
from omegaconf import OmegaConf

ROOT = Path(__file__).resolve().parents[2]
N_CLASSES = 10
MESSAGE_DTYPES = {0: np.float64, 1: np.int8, 2: np.int64, 3: np.int64, 4: np.int64, 5: np.int8}


def event_classes(messages: np.ndarray) -> np.ndarray:
    """Map visible/hidden LOBSTER event type and side to ten fixed classes."""

    event_type = messages[:, 1].astype(np.int64)
    direction = messages[:, 5].astype(np.int64)
    valid = np.isin(event_type, np.arange(1, 6)) & np.isin(direction, (-1, 1))
    result = np.full(len(messages), -1, dtype=np.int64)
    result[valid] = 2 * (event_type[valid] - 1) + (direction[valid] == -1).astype(np.int64)
    return result


def history_features(
    timestamps: np.ndarray, classes: np.ndarray, timescales: Sequence[float]
) -> np.ndarray:
    """Build causal exponentially decayed event-count features."""

    if any(value <= 0.0 for value in timescales):
        raise ValueError("history timescales must be positive")
    states = np.zeros((len(timescales), N_CLASSES), dtype=np.float64)
    output = np.zeros((len(classes), len(timescales) * N_CLASSES), dtype=np.float32)
    previous = float(timestamps[0])
    for index, (timestamp, event_class) in enumerate(zip(timestamps, classes, strict=True)):
        delta = max(float(timestamp) - previous, 0.0)
        states *= np.exp(-delta / np.asarray(timescales, dtype=np.float64))[:, None]
        if event_class >= 0:
            states[:, event_class] += 1.0
        output[index] = np.log1p(states).reshape(-1)
        previous = float(timestamp)
    return output


def queue_features(books: np.ndarray, timestamps: np.ndarray, depth: int) -> np.ndarray:
    """Build causal displayed-book features from post-event states."""

    if depth <= 0 or books.shape[1] < 4 * depth:
        raise ValueError("requested queue depth is unavailable")
    ask_price = books[:, 0 : 4 * depth : 4].astype(np.float64)
    ask_size = books[:, 1 : 4 * depth : 4].astype(np.float64)
    bid_price = books[:, 2 : 4 * depth : 4].astype(np.float64)
    bid_size = books[:, 3 : 4 * depth : 4].astype(np.float64)
    ask_total = ask_size.sum(axis=1)
    bid_total = bid_size.sum(axis=1)
    total = np.maximum(ask_total + bid_total, 1.0)
    top_total = np.maximum(ask_size[:, 0] + bid_size[:, 0], 1.0)
    spread = np.maximum(ask_price[:, 0] - bid_price[:, 0], 1.0)
    mid = 0.5 * (ask_price[:, 0] + bid_price[:, 0])
    mid_change = np.zeros(len(books), dtype=np.float64)
    mid_change[1:] = (mid[1:] - mid[:-1]) / spread[:-1]
    delta_time = np.empty(len(books), dtype=np.float64)
    delta_time[0] = np.nan
    delta_time[1:] = np.maximum(np.diff(timestamps.astype(np.float64)), 1e-6)
    finite_delta = delta_time[np.isfinite(delta_time)]
    delta_time[0] = float(np.median(finite_delta)) if len(finite_delta) else 1.0
    event_rate = np.log1p(np.minimum(1.0 / delta_time, 1e6))
    return np.column_stack(
        [
            np.log1p(spread),
            (bid_total - ask_total) / total,
            np.log1p(bid_total),
            np.log1p(ask_total),
            (bid_size[:, 0] - ask_size[:, 0]) / top_total,
            np.log1p(bid_size[:, 0]),
            np.log1p(ask_size[:, 0]),
            mid_change,
            event_rate,
        ]
    ).astype(np.float32)


def audit_dynamic_book(messages: np.ndarray, books: np.ndarray, depth: int) -> dict[str, Any]:
    """Audit book validity and exact message-induced queue changes."""

    ask_price = books[:, 0 : 4 * depth : 4]
    ask_size = books[:, 1 : 4 * depth : 4]
    bid_price = books[:, 2 : 4 * depth : 4]
    bid_size = books[:, 3 : 4 * depth : 4]
    checks = {
        "timestamps_nondecreasing": bool(np.all(np.diff(messages[:, 0].astype(np.float64)) >= 0.0)),
        "books_not_crossed_or_locked": bool(np.all(ask_price[:, 0] > bid_price[:, 0])),
        "ask_levels_ordered": bool(np.all(np.diff(ask_price, axis=1) >= 0)),
        "bid_levels_ordered": bool(np.all(np.diff(bid_price, axis=1) <= 0)),
        "sizes_nonnegative": bool(np.all(ask_size >= 0) and np.all(bid_size >= 0)),
    }
    visible = exact = 0
    for index in range(1, len(messages)):
        event_type = int(messages[index, 1])
        direction = int(messages[index, 5])
        if event_type not in (1, 2, 3, 4) or direction not in (-1, 1):
            continue
        price = int(messages[index, 4])
        size = int(messages[index, 3])
        if direction == 1:
            pre_price, pre_size = bid_price[index - 1], bid_size[index - 1]
            post_price, post_size = bid_price[index], bid_size[index]
        else:
            pre_price, pre_size = ask_price[index - 1], ask_size[index - 1]
            post_price, post_size = ask_price[index], ask_size[index]
        is_visible = bool(np.any(pre_price == price) or np.any(post_price == price))
        if not is_visible:
            continue
        before = int(pre_size[pre_price == price].sum())
        after = int(post_size[post_price == price].sum())
        expected = size if event_type == 1 else -size
        visible += 1
        exact += int(after - before == expected)
    rate = exact / visible if visible else math.nan
    return {
        "checks": checks,
        "book_checks_pass": all(checks.values()),
        "visible_type_1_to_4_events": visible,
        "exact_visible_events": exact,
        "visible_reconstruction_rate": rate,
        "distinct_message_prices": int(np.unique(messages[:, 4].astype(np.int64)).size),
        "midprice_changes": int(
            np.count_nonzero(
                np.diff(ask_price[:, 0].astype(np.float64) + bid_price[:, 0].astype(np.float64))
            )
        ),
    }


def _archive_identity(path: Path) -> str:
    match = re.search(r"SampleFile_([A-Z]+)_", path.name)
    if match is None:
        raise ValueError(f"cannot identify symbol from {path.name}")
    return match.group(1)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_archive(path: Path, *, max_rows: int, depth: int) -> tuple[np.ndarray, np.ndarray]:
    """Load only required columns from one immutable LOBSTER archive."""

    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise RuntimeError(f"CRC failure in {path}")
        message_name = next(name for name in archive.namelist() if "message" in name.lower())
        book_name = next(name for name in archive.namelist() if "orderbook" in name.lower())
        with archive.open(message_name) as stream:
            messages = pd.read_csv(
                stream, header=None, nrows=max_rows, usecols=range(6), dtype=MESSAGE_DTYPES
            ).to_numpy()
        with archive.open(book_name) as stream:
            books = pd.read_csv(
                stream, header=None, nrows=max_rows, usecols=range(4 * depth), dtype=np.int64
            ).to_numpy(dtype=np.int64, copy=False)
    if len(messages) != len(books):
        raise RuntimeError("message and order-book row counts differ")
    return messages, books


def _split_points(n_rows: int, train_fraction: float, validation_fraction: float) -> tuple[int, int]:
    train_end = int(train_fraction * n_rows)
    validation_end = int((train_fraction + validation_fraction) * n_rows)
    if train_end <= 0 or validation_end <= train_end or validation_end >= n_rows:
        raise ValueError("invalid chronological split")
    return train_end, validation_end


def unconditional_scores(
    labels: np.ndarray, train_end: int, validation_end: int
) -> dict[str, float]:
    """Score the Laplace-smoothed train class-frequency baseline."""

    counts = np.bincount(labels[:train_end], minlength=N_CLASSES).astype(np.float64) + 1.0
    probabilities = counts / counts.sum()
    test = labels[validation_end:]
    predictions = int(np.argmax(probabilities))
    return {
        "test_nll": float(-np.log(probabilities[test]).mean()),
        "test_accuracy": float(np.mean(test == predictions)),
    }


def markov_scores(
    previous_classes: np.ndarray, labels: np.ndarray, train_end: int, validation_end: int
) -> dict[str, float]:
    """Score a Laplace-smoothed first-order event transition table."""

    counts = np.ones((N_CLASSES, N_CLASSES), dtype=np.float64)
    np.add.at(counts, (previous_classes[:train_end], labels[:train_end]), 1.0)
    probabilities = counts / counts.sum(axis=1, keepdims=True)
    test_previous = previous_classes[validation_end:]
    test = labels[validation_end:]
    chosen = probabilities[test_previous, test]
    predicted = probabilities[test_previous].argmax(axis=1)
    return {
        "test_nll": float(-np.log(chosen).mean()),
        "test_accuracy": float(np.mean(predicted == test)),
    }


def fit_linear_baseline(
    features: np.ndarray,
    labels: np.ndarray,
    *,
    train_end: int,
    validation_end: int,
    steps: int,
    batch_size: int,
    learning_rate: float,
    weight_decay: float,
    seed: int,
    device: torch.device,
) -> dict[str, float | int | bool]:
    """Fit and score one fixed multinomial linear observation model."""

    mean = features[:train_end].mean(axis=0, dtype=np.float64)
    scale = features[:train_end].std(axis=0, dtype=np.float64)
    scale = np.where(scale > 1e-8, scale, 1.0)
    standardized = ((features - mean) / scale).astype(np.float32)
    x = torch.from_numpy(standardized).to(device)
    y = torch.from_numpy(labels.astype(np.int64, copy=False)).to(device)
    model = torch.nn.Linear(x.shape[1], N_CLASSES).to(device)
    torch.nn.init.zeros_(model.weight)
    torch.nn.init.zeros_(model.bias)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=learning_rate, weight_decay=weight_decay
    )
    generator = torch.Generator(device=device)
    generator.manual_seed(seed)
    actual_batch = min(batch_size, train_end)
    for _ in range(steps):
        indices = torch.randint(
            0, train_end, (actual_batch,), generator=generator, device=device
        )
        loss = torch.nn.functional.cross_entropy(model(x[indices]), y[indices])
        if not bool(torch.isfinite(loss)):
            raise RuntimeError("non-finite optimizer loss")
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()
    with torch.no_grad():
        validation_logits = model(x[train_end:validation_end])
        test_logits = model(x[validation_end:])
        validation_nll = torch.nn.functional.cross_entropy(
            validation_logits, y[train_end:validation_end]
        )
        test_nll = torch.nn.functional.cross_entropy(test_logits, y[validation_end:])
        accuracy = (test_logits.argmax(dim=1) == y[validation_end:]).float().mean()
        parameter_norm = torch.sqrt(
            sum(parameter.square().sum() for parameter in model.parameters())
        )
    values = (validation_nll, test_nll, accuracy, parameter_norm)
    finite = all(bool(torch.isfinite(value)) for value in values)
    return {
        "n_features": int(x.shape[1]),
        "optimizer_steps": steps,
        "validation_nll": float(validation_nll.cpu()),
        "test_nll": float(test_nll.cpu()),
        "test_accuracy": float(accuracy.cpu()),
        "parameter_norm": float(parameter_norm.cpu()),
        "all_finite": finite,
    }


def run_archive(path: Path, config: Mapping[str, Any], device: torch.device, seed: int) -> dict[str, Any]:
    """Run every frozen baseline and stress for one symbol path."""

    depth = int(config["retained_depth"])
    messages, books = load_archive(
        path, max_rows=int(config["max_rows"]), depth=depth
    )
    audit = audit_dynamic_book(messages, books, depth)
    classes = event_classes(messages)
    history = history_features(
        messages[:, 0].astype(np.float64),
        classes,
        [float(value) for value in config["history_timescales_seconds"]],
    )
    one_hot = np.eye(N_CLASSES, dtype=np.float32)[np.maximum(classes, 0)]
    queue_by_depth = {
        int(value): queue_features(books, messages[:, 0].astype(np.float64), int(value))
        for value in config["queue_depths"]
    }
    eligible = (classes[:-1] >= 0) & (classes[1:] >= 0)
    previous = classes[:-1][eligible]
    labels = classes[1:][eligible]
    history_x = history[:-1][eligible]
    one_hot_x = one_hot[:-1][eligible]
    queue_x = {key: value[:-1][eligible] for key, value in queue_by_depth.items()}
    train_end, validation_end = _split_points(
        len(labels), float(config["train_fraction"]), float(config["validation_fraction"])
    )
    baseline_kwargs = {
        "steps": int(config["optimizer_steps"]),
        "batch_size": int(config["batch_size"]),
        "learning_rate": float(config["learning_rate"]),
        "weight_decay": float(config["weight_decay"]),
        "device": device,
    }
    unconditional = unconditional_scores(labels, train_end, validation_end)
    models: dict[str, dict[str, Any]] = {
        "unconditional": unconditional,
        "markov": markov_scores(previous, labels, train_end, validation_end),
        "history": fit_linear_baseline(
            history_x,
            labels,
            train_end=train_end,
            validation_end=validation_end,
            seed=seed + 1,
            **baseline_kwargs,
        ),
    }
    for offset, (queue_depth, features) in enumerate(sorted(queue_x.items())):
        models[f"queue_l{queue_depth}"] = fit_linear_baseline(
            features,
            labels,
            train_end=train_end,
            validation_end=validation_end,
            seed=seed + 10 + offset,
            **baseline_kwargs,
        )
    combined = np.concatenate([one_hot_x, history_x, queue_x[depth]], axis=1)
    models["combined"] = fit_linear_baseline(
        combined,
        labels,
        train_end=train_end,
        validation_end=validation_end,
        seed=seed + 20,
        **baseline_kwargs,
    )
    for offset, delay in enumerate(config["latency_events"]):
        delay = int(delay)
        delayed_features = combined[:-delay]
        delayed_labels = labels[delay:]
        delayed_train, delayed_validation = _split_points(
            len(delayed_labels),
            float(config["train_fraction"]),
            float(config["validation_fraction"]),
        )
        delayed_null = unconditional_scores(delayed_labels, delayed_train, delayed_validation)
        result = fit_linear_baseline(
            delayed_features,
            delayed_labels,
            train_end=delayed_train,
            validation_end=delayed_validation,
            seed=seed + 30 + offset,
            **baseline_kwargs,
        )
        result["matching_unconditional_test_nll"] = delayed_null["test_nll"]
        result["gain_over_matching_unconditional"] = delayed_null["test_nll"] - float(
            result["test_nll"]
        )
        models[f"combined_delay_{delay}"] = result

    for name, result in models.items():
        if name != "unconditional" and "gain_over_matching_unconditional" not in result:
            result["gain_over_unconditional"] = unconditional["test_nll"] - float(result["test_nll"])
    non_null = [
        float(result["gain_over_unconditional"])
        for result in models.values()
        if "gain_over_unconditional" in result
    ]
    finite = all(
        math.isfinite(float(value))
        for result in models.values()
        for key, value in result.items()
        if key in {"test_nll", "test_accuracy", "validation_nll", "parameter_norm"}
    )
    checks = {
        "book_checks_pass": bool(audit["book_checks_pass"]),
        "reconstruction_gate_pass": float(audit["visible_reconstruction_rate"])
        >= float(config["minimum_visible_reconstruction_rate"]),
        "all_models_finite": finite,
        "declared_models_complete": set(models)
        == {
            "unconditional",
            "markov",
            "history",
            "queue_l1",
            "queue_l5",
            "queue_l10",
            "combined",
            "combined_delay_5",
            "combined_delay_20",
        },
        "baseline_gain_gate_pass": max(non_null)
        >= float(config["minimum_best_gain_nats_per_event"]),
    }
    return {
        "symbol": _archive_identity(path),
        "archive": str(path.relative_to(ROOT)),
        "archive_sha256": _sha256(path),
        "rows": len(messages),
        "eligible_transitions": len(labels),
        "train_end": train_end,
        "validation_end": validation_end,
        "audit": audit,
        "models": models,
        "best_gain_over_unconditional": max(non_null),
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--num-shards", type=int, default=1)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cuda")
    parser.add_argument("--git-sha")
    args = parser.parse_args()
    if args.num_shards <= 0 or not 0 <= args.shard_index < args.num_shards:
        raise ValueError("invalid shard assignment")
    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable")
    device = torch.device(args.device)
    raw_config = OmegaConf.to_container(OmegaConf.load(args.config), resolve=True)
    if not isinstance(raw_config, dict):
        raise ValueError("configuration must be a mapping")
    archives = [ROOT / str(value) for value in raw_config["archives"]]
    assigned = [path for index, path in enumerate(archives) if index % args.num_shards == args.shard_index]
    started = time.perf_counter()
    results = [
        run_archive(path, raw_config, device, int(raw_config["seed_root"]) + 1000 * index)
        for index, path in enumerate(assigned)
    ]
    gain_count = sum(item["checks"]["baseline_gain_gate_pass"] for item in results)
    local_required = math.ceil(
        len(results) * int(raw_config["minimum_symbols_with_gain"]) / len(archives)
    )
    checks = {
        "assigned_paths_complete": len(results) == len(assigned),
        "all_pipeline_checks_pass": all(
            all(value for key, value in item["checks"].items() if key != "baseline_gain_gate_pass")
            for item in results
        ),
        "shard_gain_count_provisional": gain_count >= local_required,
    }
    git_sha = args.git_sha or subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    payload = {
        "experiment": raw_config["experiment"],
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_sha": git_sha,
        "platform": platform.platform(),
        "torch_version": torch.__version__,
        "device": str(device),
        "device_name": torch.cuda.get_device_name(device) if device.type == "cuda" else "cpu",
        "shard_index": args.shard_index,
        "num_shards": args.num_shards,
        "wall_seconds": time.perf_counter() - started,
        "symbols": results,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": "one-day observation-baseline feasibility only; no EcoMD claim",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "shard": args.shard_index,
                "symbols": [item["symbol"] for item in results],
                "checks": checks,
                "wall_seconds": payload["wall_seconds"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
