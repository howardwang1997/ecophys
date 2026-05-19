from __future__ import annotations

import json
from pathlib import Path

from ecomd.data.checkpoint_sync import (
    _database_url_kwargs,
    build_record,
    discover_checkpoints,
    make_r2_key,
    sha256_file,
)


def test_discover_checkpoints_and_key_generation(tmp_path: Path) -> None:
    ckpt = tmp_path / "experiments" / "001_demo" / "results_seed0" / "checkpoint.pt"
    ckpt.parent.mkdir(parents=True)
    ckpt.write_bytes(b"checkpoint")
    (ckpt.parent / "not_a_checkpoint.txt").write_text("x")

    found = discover_checkpoints(tmp_path / "experiments")

    assert found == [ckpt]
    assert make_r2_key(ckpt, tmp_path, "checkpoints/") == (
        "checkpoints/experiments/001_demo/results_seed0/checkpoint.pt"
    )


def test_build_record_extracts_metadata(tmp_path: Path) -> None:
    exp = tmp_path / "experiments" / "001_demo"
    result = exp / "results_seed0"
    result.mkdir(parents=True)
    ckpt = result / "checkpoint.pt"
    ckpt.write_bytes(b"abc")
    (exp / "config_seed0.yaml").write_text(
        "simulator:\n  n_agents: 10\ntraining:\n  seed: 0\n  target_dataset: spx\n"
    )
    (result / "training_log.json").write_text(
        json.dumps({"targets": {"acf": 1.0}, "history": [{"iter": 0}, {"iter": 1, "loss": 0.5}]})
    )

    record = build_record(
        ckpt,
        repo_root=tmp_path,
        r2_bucket="ecophys",
        r2_key=make_r2_key(ckpt, tmp_path),
    )

    assert record.local_path == "experiments/001_demo/results_seed0/checkpoint.pt"
    assert record.experiment_dir == "experiments/001_demo"
    assert record.result_dir == "experiments/001_demo/results_seed0"
    assert record.size_bytes == 3
    assert record.sha256 == sha256_file(ckpt)
    assert record.config is not None
    assert record.config["training"]["seed"] == 0
    assert record.seed == 0
    assert record.target_dataset == "spx"
    assert record.n_agents == 10
    assert record.training_summary is not None
    assert record.training_summary["history_len"] == 2
    assert record.training_summary["last"]["loss"] == 0.5


def test_database_url_parser_tolerates_special_password_chars() -> None:
    kwargs = _database_url_kwargs(
        "postgresql://postgres.ref:p@[ss]#word@aws-0-us-west-1.pooler.supabase.com:6543/postgres?sslmode=require"
    )

    assert kwargs["user"] == "postgres.ref"
    assert kwargs["password"] == "p@[ss]#word"
    assert kwargs["host"] == "aws-0-us-west-1.pooler.supabase.com"
    assert kwargs["port"] == 6543
    assert kwargs["dbname"] == "postgres"
    assert kwargs["sslmode"] == "require"


def test_database_url_parser_adds_pooler_project_ref() -> None:
    kwargs = _database_url_kwargs(
        "postgresql://postgres:secret@aws-0-us-west-1.pooler.supabase.com:6543/postgres?sslmode=require",
        supabase_url="https://rxesmcpahnpuuzfopubb.supabase.co",
    )

    assert kwargs["user"] == "postgres.rxesmcpahnpuuzfopubb"
