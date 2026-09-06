"""Lock-checkpoint variant + binding sidecar tests (D0 build item L1-5).

Core subject: ``ecomd/training/lock_checkpoint.py`` — the optimizer-stripped,
CPU-offloaded lock flavor of the format_version-2 trainer checkpoint pattern
(``ecomd/training/train_fact_surrogate.py``), its binding sidecar hash chain
(verifiable without loading weights), tamper detection, RNG-runtime round-trip
byte-identity (a restored generator continues the exact stream), atomic write
and crash-leftover tolerance, and the binding validations pinned by the spec
(engine kernel set without pro_rata; K = 16; C1 substream names).

CPU smoke only, ``tmp_path`` only: no GPU, no training, no batch batteries,
no market data, no outcome access, nothing persisted for reuse. The test seed
root 12345 is outside both training namespaces (11000--11029 / 12000--12029).
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

import numpy as np
import pytest
import torch
from torch import nn

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ecomd.models.fact_surrogate import (  # noqa: E402
    FactSurrogateConfig,
    RecurrentFactSurrogate,
)
from ecomd.training import lock_checkpoint as lc  # noqa: E402
from ecomd.training.lock_checkpoint import (  # noqa: E402
    LockCorpusBinding,
    lock_sidecar_path,
    model_state_sha256,
    save_lock_checkpoint,
    verify_lock,
)
from ecomd.training.train_fact_surrogate import substream_generator  # noqa: E402

TEST_SEED_ROOT = 12345
CONFIG: dict[str, object] = {
    "coordinate": "increment",
    "enforcement": "raw",
    "lr": 3e-4,
    "channel_scales": [1.0, 1.0],
}
EXECUTION_METADATA: dict[str, object] = {
    "schema_version": 1,
    "lineage": "test",
    "git_sha": "test-only",
    "config_sha256": hashlib.sha256(b"test").hexdigest(),
}


def _hex(label: bytes) -> str:
    return hashlib.sha256(label).hexdigest()


def _binding(kernel: str = "fifo") -> LockCorpusBinding:
    return LockCorpusBinding(
        seed_root=TEST_SEED_ROOT,
        corpus_hash=_hex(b"corpus"),
        prestate_hash=_hex(b"prestate"),
        allocation_rule=kernel,
    )


def _tiny_model(seed_root: int = TEST_SEED_ROOT) -> RecurrentFactSurrogate:
    return RecurrentFactSurrogate(
        FactSurrogateConfig(d_hidden=4, n_slots=2),
        generator=substream_generator(seed_root, "init"),
    )


def _generators() -> dict[str, torch.Generator]:
    return {
        name: substream_generator(TEST_SEED_ROOT, name)
        for name in ("train_kernel", "kernel:1")
    }


def _save(path: Path, **overrides: object) -> object:
    model = overrides.pop("model", None) or _tiny_model()
    kwargs: dict[str, object] = {
        "model": model,
        "config": CONFIG,
        "corpus": _binding(),
        "substream_generators": _generators(),
        "execution_metadata": EXECUTION_METADATA,
        "iter_idx": 7,
        "recurrent_hidden": torch.randn(2, 4, generator=substream_generator(1, "init")),
    }
    kwargs.update(overrides)
    return save_lock_checkpoint(path, **kwargs)


def _draw(generator: torch.Generator, count: int) -> list[int]:
    return [
        int(value)
        for value in torch.randint(0, 2**31, (count,), generator=generator).tolist()
    ]


def _stray_temp_files(directory: Path) -> list[str]:
    return sorted(
        name
        for name in (child.name for child in directory.iterdir())
        if ".tmp-" in name
    )


# ─────────────────────────────────────────────────────────────────────────────
# Format adoption + save surface
# ─────────────────────────────────────────────────────────────────────────────


def test_save_writes_checkpoint_and_sidecar_atomically(tmp_path: Path) -> None:
    checkpoint = tmp_path / "model.lock.ckpt"
    sidecar = _save(checkpoint)
    assert checkpoint.exists() and lock_sidecar_path(checkpoint).exists()
    assert _stray_temp_files(tmp_path) == []
    parsed = json.loads(lock_sidecar_path(checkpoint).read_text())
    assert parsed == json.loads(sidecar.to_json())
    assert parsed["flavor"] == "lock"
    assert parsed["format_version"] == 2


def test_payload_adopts_trainer_format_vocabulary(tmp_path: Path) -> None:
    checkpoint = tmp_path / "model.lock.ckpt"
    _save(checkpoint)
    payload = torch.load(checkpoint, map_location="cpu", weights_only=False)
    # trainer pattern keys minus the stripped optimizer, plus the two lock marks
    assert set(payload) == {
        "format_version",
        "iter_idx",
        "world_size",
        "state_complete",
        "sim_state_dict",
        "rank_runtimes",
        "targets",
        "sim_config",
        "train_config",
        "execution_metadata",
        "checkpoint_flavor",
        "lock_binding",
    }
    assert payload["format_version"] == 2
    assert payload["checkpoint_flavor"] == "lock"
    assert payload["world_size"] == 1
    assert payload["state_complete"] is True
    assert payload["iter_idx"] == 7
    assert payload["sim_config"] == CONFIG
    assert payload["targets"] == {}
    runtime = payload["rank_runtimes"][0]
    assert runtime["rank"] == 0
    for key in (
        "recurrent_hidden",
        "substream_generator_states",
        "torch_cpu_rng_state",
        "numpy_rng_state",
        "python_rng_state",
        "history",
    ):
        assert key in runtime
    assert sorted(runtime["substream_generator_states"]) == ["kernel:1", "train_kernel"]
    assert payload["execution_metadata"] == EXECUTION_METADATA


def test_lock_is_optimizer_stripped(tmp_path: Path) -> None:
    checkpoint = tmp_path / "model.lock.ckpt"
    _save(checkpoint)
    payload = torch.load(checkpoint, map_location="cpu", weights_only=False)
    assert "optim_state_dict" not in payload
    assert all(
        tensor.device.type == "cpu" for tensor in payload["sim_state_dict"].values()
    )


def test_sidecar_records_the_binding_the_spec_demands(tmp_path: Path) -> None:
    checkpoint = tmp_path / "model.lock.ckpt"
    _save(checkpoint, corpus=_binding("random_unit_within_price"))
    binding = json.loads(lock_sidecar_path(checkpoint).read_text())["binding"]
    assert binding["allocation_rule"] == "random_unit_within_price"
    assert binding["n_draws"] == 16
    assert binding["seed_root"] == TEST_SEED_ROOT
    assert binding["substream_names"] == ["kernel:1", "train_kernel"]
    assert binding["model_sha256"] == model_state_sha256(_tiny_model().state_dict())
    assert binding["config_sha256"] == hashlib.sha256(
        json.dumps(CONFIG, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    assert binding["corpus_hash"] == _hex(b"corpus")
    assert binding["prestate_hash"] == _hex(b"prestate")


def test_save_is_byte_deterministic(tmp_path: Path) -> None:
    first, second = tmp_path / "a.lock.ckpt", tmp_path / "b.lock.ckpt"
    _save(first)
    _save(second)
    assert first.read_bytes() == second.read_bytes()
    assert lock_sidecar_path(first).read_bytes() == lock_sidecar_path(second).read_bytes()


# ─────────────────────────────────────────────────────────────────────────────
# Round trips: parameters, RNG runtime, hidden state
# ─────────────────────────────────────────────────────────────────────────────


def test_round_trip_parameter_byte_identity(tmp_path: Path) -> None:
    checkpoint = tmp_path / "model.lock.ckpt"
    model = _tiny_model()
    _save(checkpoint, model=model)
    # a differently-initialized model differs before the load (precondition)
    restored = _tiny_model(TEST_SEED_ROOT + 1)
    assert any(
        not torch.equal(a, b)
        for a, b in zip(
            model.state_dict().values(), restored.state_dict().values(), strict=True
        )
    )
    state = lc.load_lock_checkpoint(checkpoint, model=restored)
    assert set(state.payload["sim_state_dict"]) == set(model.state_dict())
    assert all(
        torch.equal(model.state_dict()[name], restored.state_dict()[name])
        for name in model.state_dict()
    )


def test_restored_generator_continues_the_exact_stream(tmp_path: Path) -> None:
    checkpoint = tmp_path / "model.lock.ckpt"
    generators = _generators()
    before = {name: _draw(generator, 16) for name, generator in generators.items()}
    _save(checkpoint, substream_generators=generators)

    # uninterrupted reference: keep drawing on the originals
    after_reference = {name: _draw(generator, 32) for name, generator in generators.items()}

    state = lc.load_lock_checkpoint(checkpoint)
    for name in generators:
        resumed = _draw(state.generators[name], 32)
        assert resumed == after_reference[name]
        assert before[name] + resumed == _draw(
            substream_generator(TEST_SEED_ROOT, name), 48
        )
        assert torch.equal(
            state.generators[name].get_state(), generators[name].get_state()
        )


def test_global_runtime_and_hidden_round_trip(tmp_path: Path) -> None:
    checkpoint = tmp_path / "model.lock.ckpt"
    hidden = torch.randn(2, 4, generator=substream_generator(9, "init"))

    # uninterrupted reference: draws 1-4, then the continuation draws 5-8
    torch.manual_seed(11)
    np.random.seed(11)
    random.seed(11)
    torch.rand(4)
    np.random.random(4)
    [random.random() for _ in range(4)]
    next_torch = torch.rand(4)
    next_numpy = np.random.random(4)
    next_python = [random.random() for _ in range(4)]

    # locked branch: same first draws, then the lock (captured at position 4),
    # then the streams are destroyed before restoration
    torch.manual_seed(11)
    np.random.seed(11)
    random.seed(11)
    torch.rand(4)
    np.random.random(4)
    [random.random() for _ in range(4)]
    _save(checkpoint, recurrent_hidden=hidden)
    torch.manual_seed(99)
    np.random.seed(99)
    random.seed(99)
    state = lc.load_lock_checkpoint(checkpoint)
    torch.set_rng_state(state.torch_rng_state)
    np.random.set_state(state.numpy_rng_state)
    random.setstate(state.python_rng_state)
    assert torch.equal(torch.rand(4), next_torch)
    assert np.array_equal(np.random.random(4), next_numpy)
    assert [random.random() for _ in range(4)] == next_python
    assert torch.equal(state.recurrent_hidden, hidden)


def test_locks_any_lineage_module(tmp_path: Path) -> None:
    checkpoint = tmp_path / "plain.lock.ckpt"
    model = nn.Sequential(nn.Linear(3, 2), nn.Tanh(), nn.Linear(2, 1))
    _save(checkpoint, model=model, recurrent_hidden=None)
    restored = nn.Sequential(nn.Linear(3, 2), nn.Tanh(), nn.Linear(2, 1))
    state = lc.load_lock_checkpoint(checkpoint, model=restored)
    assert state.recurrent_hidden is None
    assert all(
        torch.equal(a, b)
        for a, b in zip(model.parameters(), restored.parameters(), strict=True)
    )
    assert verify_lock(checkpoint).ok


# ─────────────────────────────────────────────────────────────────────────────
# Verification: shallow (no weights load), deep, tamper detection
# ─────────────────────────────────────────────────────────────────────────────


def test_verify_ok_deep(tmp_path: Path) -> None:
    checkpoint = tmp_path / "model.lock.ckpt"
    _save(checkpoint)
    verification = verify_lock(checkpoint)
    assert verification.ok and verification.failures == ()
    assert verification.sidecar is not None


def test_verify_shallow_never_loads_weights(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    checkpoint = tmp_path / "model.lock.ckpt"
    _save(checkpoint)

    def explode(*args: object, **kwargs: object) -> None:
        raise AssertionError("shallow verification must not torch.load")

    monkeypatch.setattr(lc.torch, "load", explode)
    verification = verify_lock(checkpoint, deep=False)
    assert verification.ok and verification.failures == ()


def test_verify_detects_checkpoint_byte_tamper(tmp_path: Path) -> None:
    checkpoint = tmp_path / "model.lock.ckpt"
    _save(checkpoint)
    raw = bytearray(checkpoint.read_bytes())
    raw[-1] ^= 0xFF
    checkpoint.write_bytes(bytes(raw))
    verification = verify_lock(checkpoint, deep=False)
    assert not verification.ok
    assert any("checkpoint file sha256" in failure for failure in verification.failures)
    with pytest.raises(ValueError, match="lock verification failed"):
        lc.load_lock_checkpoint(checkpoint)


@pytest.mark.parametrize("field,value", [
    ("allocation_rule", "pro_rata"),
    ("n_draws", 8),
    ("corpus_hash", _hex(b"other-corpus")),
    ("model_sha256", _hex(b"other-model")),
    ("seed_root", 12001),
])
def test_verify_detects_sidecar_binding_tamper(
    tmp_path: Path, field: str, value: object
) -> None:
    checkpoint = tmp_path / "model.lock.ckpt"
    _save(checkpoint)
    sidecar_file = lock_sidecar_path(checkpoint)
    document = json.loads(sidecar_file.read_text())
    document["binding"][field] = value
    sidecar_file.write_text(json.dumps(document))
    verification = verify_lock(checkpoint, deep=False)
    assert not verification.ok
    assert any("hash chain" in failure for failure in verification.failures)


def test_verify_detects_weights_binding_mismatch_deep_only(tmp_path: Path) -> None:
    checkpoint = tmp_path / "model.lock.ckpt"
    _save(checkpoint)
    payload = torch.load(checkpoint, map_location="cpu", weights_only=False)
    payload["sim_state_dict"][next(iter(payload["sim_state_dict"]))] += 0.125
    torch.save(payload, checkpoint)
    # forger also repairs the sidecar's file hash, so shallow checks pass...
    sidecar_file = lock_sidecar_path(checkpoint)
    document = json.loads(sidecar_file.read_text())
    document["checkpoint_sha256"] = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    sidecar_file.write_text(json.dumps(document))
    assert verify_lock(checkpoint, deep=False).ok
    # ...but deep verification recomputes the model hash from the actual weights
    deep = verify_lock(checkpoint)
    assert not deep.ok
    assert any("model sha256" in failure for failure in deep.failures)


def test_verify_missing_sidecar_fails(tmp_path: Path) -> None:
    checkpoint = tmp_path / "model.lock.ckpt"
    _save(checkpoint)
    lock_sidecar_path(checkpoint).unlink()
    verification = verify_lock(checkpoint)
    assert not verification.ok
    assert any("sidecar" in failure for failure in verification.failures)


def test_verify_detects_lock_binding_drift_inside_payload(tmp_path: Path) -> None:
    checkpoint = tmp_path / "model.lock.ckpt"
    _save(checkpoint)
    payload = torch.load(checkpoint, map_location="cpu", weights_only=False)
    payload["lock_binding"]["iter_idx"] = 999
    torch.save(payload, checkpoint)
    sidecar_file = lock_sidecar_path(checkpoint)
    document = json.loads(sidecar_file.read_text())
    document["checkpoint_sha256"] = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    sidecar_file.write_text(json.dumps(document))
    deep = verify_lock(checkpoint)
    assert not deep.ok
    assert any("lock_binding differs" in failure for failure in deep.failures)


# ─────────────────────────────────────────────────────────────────────────────
# Loader format validation
# ─────────────────────────────────────────────────────────────────────────────


def test_load_rejects_non_lock_payloads(tmp_path: Path) -> None:
    # a trainer state-complete checkpoint (no lock marks) is a different flavor
    trainer_checkpoint = tmp_path / "trainer.ckpt"
    torch.save(
        {
            "format_version": 2,
            "iter_idx": 3,
            "world_size": 1,
            "state_complete": True,
            "sim_state_dict": {},
            "optim_state_dict": {},
            "rank_runtimes": [{}],
            "targets": {},
            "sim_config": {},
            "train_config": {},
            "execution_metadata": {},
        },
        trainer_checkpoint,
    )
    with pytest.raises(ValueError, match="checkpoint_flavor"):
        lc.load_lock_checkpoint(trainer_checkpoint, verify=False)

    # a lock-flavored payload that still carries optimizer state is rejected
    optimizer_checkpoint = tmp_path / "not-stripped.ckpt"
    torch.save(
        {
            "format_version": 2,
            "checkpoint_flavor": "lock",
            "lock_binding": {},
            "optim_state_dict": {},
        },
        optimizer_checkpoint,
    )
    with pytest.raises(ValueError, match="optimizer-stripped"):
        lc.load_lock_checkpoint(optimizer_checkpoint, verify=False)

    stale_checkpoint = tmp_path / "stale.ckpt"
    torch.save(
        {
            "format_version": 1,
            "checkpoint_flavor": "lock",
            "lock_binding": {},
        },
        stale_checkpoint,
    )
    with pytest.raises(ValueError, match="format_version"):
        lc.load_lock_checkpoint(stale_checkpoint, verify=False)


# ─────────────────────────────────────────────────────────────────────────────
# Binding validations pinned by the spec
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("kernel", ["fifo", "random_unit_within_price"])
def test_binding_accepts_both_engine_kernels(kernel: str) -> None:
    binding = _binding(kernel)
    assert binding.allocation_rule == kernel


@pytest.mark.parametrize("kernel", ["pro_rata", "PRO_RATA", "garbage", ""])
def test_binding_rejects_non_engine_kernels(kernel: str) -> None:
    with pytest.raises(ValueError, match="allocation_rule"):
        _binding(kernel)


def test_binding_rejects_wrong_n_draws() -> None:
    with pytest.raises(ValueError, match="n_draws"):
        LockCorpusBinding(
            seed_root=TEST_SEED_ROOT,
            corpus_hash=_hex(b"corpus"),
            prestate_hash=_hex(b"prestate"),
            allocation_rule="fifo",
            n_draws=8,
        )


def test_binding_rejects_malformed_hashes() -> None:
    with pytest.raises(ValueError, match="corpus_hash"):
        LockCorpusBinding(
            seed_root=TEST_SEED_ROOT,
            corpus_hash="not-a-hash",
            prestate_hash=_hex(b"prestate"),
            allocation_rule="fifo",
        )


def test_save_rejects_unknown_or_empty_substreams(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unknown substream"):
        _save(tmp_path / "a.ckpt", substream_generators={"not_a_substream": torch.Generator()})
    with pytest.raises(ValueError, match="at least one"):
        _save(tmp_path / "b.ckpt", substream_generators={})


# ─────────────────────────────────────────────────────────────────────────────
# Atomic write + crash-leftover tolerance
# ─────────────────────────────────────────────────────────────────────────────


def test_stale_crash_leftovers_do_not_break_save_load_verify(tmp_path: Path) -> None:
    checkpoint = tmp_path / "model.lock.ckpt"
    (tmp_path / ".model.lock.ckpt.tmp-999999").write_bytes(b"stale garbage")
    (tmp_path / ".model.lock.ckpt.lock.json.tmp-999999").write_bytes(b"stale garbage")
    _save(checkpoint)
    state = lc.load_lock_checkpoint(checkpoint)
    assert verify_lock(checkpoint).ok
    assert sorted(state.generators) == ["kernel:1", "train_kernel"]
    # stale leftovers from another (dead) pid are inert; only our own temps are managed
    assert ".model.lock.ckpt.tmp-999999" in _stray_temp_files(tmp_path)


def test_failed_save_leaves_no_artifacts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    checkpoint = tmp_path / "model.lock.ckpt"

    def exploding_save(payload: object, target: object, *args: object, **kwargs: object) -> None:
        if isinstance(target, (str, Path)):
            Path(target).write_bytes(b"partial garbage")
        raise RuntimeError("simulated crash mid-save")

    monkeypatch.setattr(lc.torch, "save", exploding_save)
    with pytest.raises(RuntimeError, match="simulated crash"):
        _save(checkpoint)
    assert not checkpoint.exists()
    assert not lock_sidecar_path(checkpoint).exists()
    assert _stray_temp_files(tmp_path) == []


def test_failed_resave_leaves_previous_lock_intact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    checkpoint = tmp_path / "model.lock.ckpt"
    _save(checkpoint)
    original_bytes = checkpoint.read_bytes()
    original_sidecar = lock_sidecar_path(checkpoint).read_bytes()

    def exploding_save(payload: object, target: object, *args: object, **kwargs: object) -> None:
        if isinstance(target, (str, Path)):
            Path(target).write_bytes(b"partial garbage")
        raise RuntimeError("simulated crash mid-resave")

    monkeypatch.setattr(lc.torch, "save", exploding_save)
    with pytest.raises(RuntimeError, match="simulated crash"):
        _save(checkpoint, iter_idx=8)
    assert checkpoint.read_bytes() == original_bytes
    assert lock_sidecar_path(checkpoint).read_bytes() == original_sidecar
    assert verify_lock(checkpoint).ok
    assert _stray_temp_files(tmp_path) == []


def test_sidecar_write_failure_is_never_silently_accepted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    checkpoint = tmp_path / "model.lock.ckpt"
    _save(checkpoint)

    real_write = lc._atomic_write_bytes

    def failing_write(path: Path, data: bytes) -> None:
        if path.name.endswith(".lock.json"):
            raise OSError("simulated sidecar write crash")
        real_write(path, data)

    monkeypatch.setattr(lc, "_atomic_write_bytes", failing_write)
    with pytest.raises(OSError, match="sidecar write crash"):
        _save(checkpoint, iter_idx=8)
    # new checkpoint bytes + old sidecar hash => loud verification failure
    verification = verify_lock(checkpoint)
    assert not verification.ok
    assert any("checkpoint file sha256" in failure for failure in verification.failures)
