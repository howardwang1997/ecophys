"""Lock-checkpoint variant + binding sidecar (D0 build item L1-5, code-only).

Spec: simulator contracts section 2.5 "(i) optimizer-stripped, CPU-offloaded
final 'lock' checkpoint variant (surgery cells read parameters only; ops
section 3 item 4) ... (ii) ``n_draws``, ``allocation_rule``, seed and
corpus-manifest binding inside the checkpoint payload or sidecar so G4/G10
checks are self-contained. Nothing here changes the existing loader contract."

The payload adopts the format_version-2 trainer checkpoint pattern of
:mod:`ecomd.training.train_fact_surrogate` (itself adopted verbatim from
``train_distributed``): same key vocabulary and atomic write,
``torch.load(..., map_location="cpu", weights_only=False)`` load, and the same
format-validation posture. Deltas, each pinned by a spec clause:

- ``optim_state_dict`` is STRIPPED (ops section 3 item 4: final locked
  checkpoints are optimizer-stripped; surgery cells read parameters only,
  C11/G5) and ``checkpoint_flavor = "lock"`` marks the variant.
- The rank runtime freezes the RNG runtime: named-substream generator states
  (the C1 seed tree), the torch/numpy/python global states (trainer-pattern
  runtime vocabulary), and the optional recurrent hidden state at the save
  boundary (simulator contracts section 3.5 slot shape).
- ``lock_binding`` carries ``n_draws``, ``allocation_rule`` (validated against
  the engine kernel set — pro_rata is exact-arithmetic only, C3/C16 item 12),
  ``seed_root``, substream names and the corpus/prestate/manifest hashes.
- A JSON BINDING SIDECAR (``<checkpoint>.lock.json``) records the same binding
  plus ``checkpoint_sha256`` and a hash chain (sha256 over the canonical JSON
  of the binding: model hash + config hash + corpus binding), so the lock is
  verifiable WITHOUT loading weights (``verify_lock(..., deep=False)`` never
  calls ``torch.load``). The sidecar is path-free: the (checkpoint, sidecar)
  pair stays verifiable after relocation; the D0 lock manifest (G4) is the
  external anchor against fully self-consistent forgeries.

The module has no stochastic consumer (rule: named substream or deterministic;
global-RNG states are captured, never consumed). CPU smoke only; nothing is
persisted by this module itself — callers choose the destination paths.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import random
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import numpy as np
import torch
from torch import Tensor, nn

from ..mechanisms.through_m import KERNEL_BY_RULE
from .train_fact_surrogate import K_INFERENCE_DRAWS, SUBSTREAM_NAMES

__all__ = [
    "LOCK_CHECKPOINT_FORMAT_VERSION",
    "LOCK_FLAVOR",
    "LOCK_SIDECAR_SCHEMA_VERSION",
    "LockCorpusBinding",
    "LockSidecar",
    "LockState",
    "LockVerification",
    "load_lock_checkpoint",
    "lock_sidecar_path",
    "model_state_sha256",
    "save_lock_checkpoint",
    "verify_lock",
]


LOCK_CHECKPOINT_FORMAT_VERSION = 2
"""Same format family as the trainer checkpoint (train_fact_surrogate)."""

LOCK_FLAVOR = "lock"
LOCK_SIDECAR_SCHEMA_VERSION = 1

_SIDECAR_KEYS = (
    "schema_version",
    "flavor",
    "format_version",
    "checkpoint_sha256",
    "lock_chain_sha256",
    "binding",
)


# ─────────────────────────────────────────────────────────────────────────────
# Canonical hashing (E-1 vocabulary: sha256 over sorted-key compact JSON)
# ─────────────────────────────────────────────────────────────────────────────


def _canonical_json(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _require_sha256(value: object, field: str, *, optional: bool = False) -> None:
    if optional and value is None:
        return
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{field} must be a 64-hex-character sha256 string, got {value!r}")


def _tensor_bytes(tensor: Tensor) -> bytes:
    try:
        return tensor.numpy().tobytes()
    except (TypeError, RuntimeError):  # dtypes numpy refuses (e.g. bfloat16)
        return tensor.reshape(-1).view(torch.uint8).numpy().tobytes()


def model_state_sha256(state: Mapping[str, Tensor]) -> str:
    """Deterministic sha256 over a state dict (name, dtype, shape, raw bytes)."""

    hasher = hashlib.sha256()
    for name, tensor in state.items():
        cpu = tensor.detach().to("cpu").contiguous()
        encoded_name = name.encode("utf-8")
        hasher.update(len(encoded_name).to_bytes(4, "big"))
        hasher.update(encoded_name)
        hasher.update(str(cpu.dtype).encode("ascii"))
        hasher.update(str(tuple(cpu.shape)).encode("ascii"))
        hasher.update(_tensor_bytes(cpu))
    return hasher.hexdigest()


# ─────────────────────────────────────────────────────────────────────────────
# Binding contracts
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class LockCorpusBinding:
    """Corpus/engine binding recorded inside the lock (contracts section 2.5(ii)).

    Hashes use the E-1 projector vocabulary (``corpus_hash`` /
    ``prestate_hash`` of ``ecomd.corpus.fexec_projector``; ``manifest_hash``
    binds the corpus/fixture manifest, e.g. the frozen lab-asset-v3 anchor).
    """

    seed_root: int
    corpus_hash: str
    prestate_hash: str
    allocation_rule: str
    n_draws: int = K_INFERENCE_DRAWS
    schema_version: str = "lab-asset-v3"
    tape_hash: str | None = None
    manifest_hash: str | None = None

    def __post_init__(self) -> None:
        if self.seed_root < 0:
            raise ValueError(f"seed_root must be >= 0, got {self.seed_root}")
        if self.allocation_rule not in KERNEL_BY_RULE:
            raise ValueError(
                f"allocation_rule {self.allocation_rule!r} is not an engine kernel "
                f"{sorted(KERNEL_BY_RULE)}; pro_rata is exact-arithmetic only "
                "(C3 / C16 item 12) and can never be locked"
            )
        if self.n_draws != K_INFERENCE_DRAWS:
            raise ValueError(
                f"n_draws must equal the frozen K = {K_INFERENCE_DRAWS} "
                f"(C16 item 11; G8/G10), got {self.n_draws}"
            )
        _require_sha256(self.corpus_hash, "corpus_hash")
        _require_sha256(self.prestate_hash, "prestate_hash")
        _require_sha256(self.tape_hash, "tape_hash", optional=True)
        _require_sha256(self.manifest_hash, "manifest_hash", optional=True)


@dataclass(frozen=True)
class LockSidecar:
    """The verifiable-without-weights record written next to the checkpoint."""

    checkpoint_sha256: str
    lock_chain_sha256: str
    binding: dict[str, Any]

    schema_version: int = LOCK_SIDECAR_SCHEMA_VERSION
    flavor: str = LOCK_FLAVOR
    format_version: int = LOCK_CHECKPOINT_FORMAT_VERSION

    def to_json(self) -> str:
        document = {
            "schema_version": self.schema_version,
            "flavor": self.flavor,
            "format_version": self.format_version,
            "checkpoint_sha256": self.checkpoint_sha256,
            "lock_chain_sha256": self.lock_chain_sha256,
            "binding": self.binding,
        }
        return _canonical_json(document)

    @classmethod
    def from_json(cls, raw: str) -> LockSidecar:
        document = cast(dict[str, Any], json.loads(raw))
        if set(document) != set(_SIDECAR_KEYS):
            raise ValueError(
                f"sidecar must carry exactly {sorted(_SIDECAR_KEYS)}, got {sorted(document)}"
            )
        if document["schema_version"] != LOCK_SIDECAR_SCHEMA_VERSION:
            raise ValueError(
                f"unsupported sidecar schema_version={document['schema_version']!r}"
            )
        if document["flavor"] != LOCK_FLAVOR:
            raise ValueError(f"sidecar flavor must be {LOCK_FLAVOR!r}")
        if document["format_version"] != LOCK_CHECKPOINT_FORMAT_VERSION:
            raise ValueError(
                f"sidecar format_version must be {LOCK_CHECKPOINT_FORMAT_VERSION}"
            )
        binding = document["binding"]
        if not isinstance(binding, dict):
            raise ValueError("sidecar binding must be a JSON object")
        for field in ("checkpoint_sha256", "lock_chain_sha256"):
            _require_sha256(document[field], f"sidecar.{field}")
        return cls(
            checkpoint_sha256=document["checkpoint_sha256"],
            lock_chain_sha256=document["lock_chain_sha256"],
            binding=binding,
            schema_version=int(document["schema_version"]),
            flavor=str(document["flavor"]),
            format_version=int(document["format_version"]),
        )


def lock_sidecar_path(checkpoint_path: Path | str) -> Path:
    """Sidecar convention: ``<checkpoint>.lock.json`` (same directory)."""

    return Path(str(checkpoint_path) + ".lock.json")


# ─────────────────────────────────────────────────────────────────────────────
# Atomic write (crash-leftover tolerant: pid-suffixed temp + os.replace)
# ─────────────────────────────────────────────────────────────────────────────


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        with open(temporary, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _numpy_rng_snapshot() -> tuple[Any, ...]:
    """``np.random.get_state`` with the keys array COPIED: numpy 2.4 returns a
    live-aliased array, so an uncopied tuple would not be a frozen snapshot."""

    state = cast(tuple[Any, ...], np.random.get_state())
    return (state[0], np.array(state[1], copy=True), state[2], state[3], state[4])


def _serialize_torch(payload: Mapping[str, Any]) -> bytes:
    """Canonical torch serialization via an in-memory buffer.

    ``torch.save`` to a PATH embeds the destination filename as the zip
    archive root, so path-based writes are not byte-reproducible across
    destinations or pids; the buffer form is (verified byte-identical and
    loadable under any filename), which is what the D0 cross-node byte-identity
    discipline and rule "same inputs -> byte-identical outputs" require.
    """

    buffer = io.BytesIO()
    torch.save(payload, buffer)
    return buffer.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# Save
# ─────────────────────────────────────────────────────────────────────────────


def save_lock_checkpoint(
    path: Path | str,
    *,
    model: nn.Module,
    config: Mapping[str, Any],
    corpus: LockCorpusBinding,
    substream_generators: Mapping[str, torch.Generator],
    execution_metadata: Mapping[str, Any],
    iter_idx: int,
    history: Sequence[Mapping[str, Any]] = (),
    recurrent_hidden: Tensor | None = None,
) -> LockSidecar:
    """Freeze model + RNG runtime + corpus binding into a lock checkpoint.

    Writes the optimizer-stripped CPU checkpoint to ``path`` and the binding
    sidecar to ``<path>.lock.json`` (both atomically), returning the sidecar.
    The checkpoint bytes are hashed AFTER the final ``os.replace`` so the
    sidecar's ``checkpoint_sha256`` always matches the on-disk file.
    """

    checkpoint_path = Path(path)
    names = sorted(substream_generators)
    if not names:
        raise ValueError("a lock must freeze at least one named-substream generator")
    unknown = [name for name in names if name not in SUBSTREAM_NAMES]
    if unknown:
        raise ValueError(
            f"unknown substream names {unknown}; expected subsets of {SUBSTREAM_NAMES}"
        )
    try:
        config_document: dict[str, Any] = dict(config)
        config_encoded = _canonical_json(config_document)
    except TypeError as error:
        raise ValueError(f"config payload must be JSON-serializable: {error}") from error

    cpu_state = {
        name: tensor.detach().to("cpu").clone() for name, tensor in model.state_dict().items()
    }
    config_sha256 = _sha256_hex(config_encoded.encode("utf-8"))
    binding: dict[str, Any] = {
        "schema_version": corpus.schema_version,
        "seed_root": int(corpus.seed_root),
        "substream_names": names,
        "model_sha256": model_state_sha256(cpu_state),
        "config_sha256": config_sha256,
        "corpus_hash": corpus.corpus_hash,
        "prestate_hash": corpus.prestate_hash,
        "tape_hash": corpus.tape_hash,
        "manifest_hash": corpus.manifest_hash,
        "allocation_rule": corpus.allocation_rule,
        "n_draws": int(corpus.n_draws),
        "iter_idx": int(iter_idx),
    }
    payload = {
        "format_version": LOCK_CHECKPOINT_FORMAT_VERSION,
        "checkpoint_flavor": LOCK_FLAVOR,
        "iter_idx": int(iter_idx),
        "world_size": 1,
        "state_complete": True,
        "sim_state_dict": cpu_state,
        "rank_runtimes": [
            {
                "rank": 0,
                "recurrent_hidden": (
                    recurrent_hidden.detach().to("cpu").clone()
                    if recurrent_hidden is not None
                    else None
                ),
                "substream_generator_states": {
                    name: substream_generators[name].get_state().detach().cpu().clone()
                    for name in names
                },
                "torch_cpu_rng_state": torch.get_rng_state().detach().cpu().clone(),
                "numpy_rng_state": _numpy_rng_snapshot(),
                "python_rng_state": random.getstate(),
                "history": [dict(record) for record in history],
            }
        ],
        "targets": {},
        "sim_config": config_document,
        "train_config": {"config_sha256": config_sha256},
        "execution_metadata": dict(execution_metadata),
        "lock_binding": binding,
    }
    _atomic_write_bytes(checkpoint_path, _serialize_torch(payload))
    sidecar = LockSidecar(
        checkpoint_sha256=_sha256_hex(checkpoint_path.read_bytes()),
        lock_chain_sha256=_sha256_hex(_canonical_json(binding).encode("utf-8")),
        binding=binding,
    )
    _atomic_write_bytes(lock_sidecar_path(checkpoint_path), sidecar.to_json().encode("utf-8"))
    return sidecar


# ─────────────────────────────────────────────────────────────────────────────
# Load
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class LockState:
    """Loaded lock: payload, restored substream generators, runtime snapshot."""

    payload: Mapping[str, Any]
    generators: dict[str, torch.Generator]
    recurrent_hidden: Tensor | None
    torch_rng_state: Tensor
    numpy_rng_state: tuple[Any, ...]
    python_rng_state: tuple[Any, ...]
    sidecar: LockSidecar


def _validate_lock_payload(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    version = int(payload.get("format_version", -1))
    if version != LOCK_CHECKPOINT_FORMAT_VERSION:
        raise ValueError(f"unsupported checkpoint format_version={version}")
    if payload.get("checkpoint_flavor") != LOCK_FLAVOR:
        raise ValueError(
            "not a lock checkpoint (checkpoint_flavor must be "
            f"{LOCK_FLAVOR!r}); the trainer state-complete format is a different flavor"
        )
    if "optim_state_dict" in payload:
        raise ValueError("lock checkpoints are optimizer-stripped (ops section 3 item 4)")
    if "lock_binding" not in payload or not isinstance(payload["lock_binding"], dict):
        raise ValueError("lock checkpoint is missing its lock_binding")
    if int(payload.get("world_size", -1)) != 1:
        raise ValueError("lock checkpoints are single-rank (world_size=1)")
    runtimes = payload.get("rank_runtimes")
    if not isinstance(runtimes, list) or len(runtimes) != 1:
        raise ValueError("lock checkpoint is missing its single rank runtime")
    runtime = runtimes[0]
    if not isinstance(runtime, dict):
        raise ValueError("rank runtime must be a mapping")
    for key in (
        "substream_generator_states",
        "torch_cpu_rng_state",
        "numpy_rng_state",
        "python_rng_state",
    ):
        if key not in runtime:
            raise ValueError(f"rank runtime is missing {key}")
    return runtime


def load_lock_checkpoint(
    path: Path | str,
    *,
    model: nn.Module | None = None,
    verify: bool = True,
    deep_verify: bool = True,
) -> LockState:
    """CPU-load a lock checkpoint (``map_location="cpu"``, pattern-posture
    format validation) and restore the named-substream generators.

    ``verify=True`` runs :func:`verify_lock` first and raises ``ValueError``
    listing every failure, so a surgery cell cannot start from an unverified
    lock. Restored generators continue their exact pre-lock streams; the
    torch/numpy/python global states are returned for callers that must also
    restore the ambient runtime.
    """

    checkpoint_path = Path(path)
    if verify:
        verification = verify_lock(checkpoint_path, deep=deep_verify)
        if not verification.ok:
            raise ValueError(f"lock verification failed: {list(verification.failures)}")

    payload = cast(
        dict[str, Any],
        torch.load(checkpoint_path, map_location="cpu", weights_only=False),
    )
    runtime = _validate_lock_payload(payload)
    if model is not None:
        model.load_state_dict(payload["sim_state_dict"])
    generators: dict[str, torch.Generator] = {}
    for name, state in runtime["substream_generator_states"].items():
        generator = torch.Generator(device="cpu")
        generator.set_state(state.detach().cpu().clone())
        generators[str(name)] = generator
    hidden = runtime.get("recurrent_hidden")
    sidecar = LockSidecar.from_json(lock_sidecar_path(checkpoint_path).read_text())
    return LockState(
        payload=payload,
        generators=generators,
        recurrent_hidden=hidden if isinstance(hidden, Tensor) else None,
        torch_rng_state=runtime["torch_cpu_rng_state"].detach().cpu().clone(),
        numpy_rng_state=tuple(runtime["numpy_rng_state"]),
        python_rng_state=tuple(runtime["python_rng_state"]),
        sidecar=sidecar,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Verify
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class LockVerification:
    """Non-raising verdict: ``failures`` empty iff every check passed."""

    ok: bool
    failures: tuple[str, ...]
    sidecar: LockSidecar | None = None


def _binding_failures(binding: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    for field in ("model_sha256", "config_sha256", "corpus_hash", "prestate_hash"):
        try:
            _require_sha256(binding.get(field), f"binding.{field}")
        except ValueError as error:
            failures.append(str(error))
    if binding.get("allocation_rule") not in KERNEL_BY_RULE:
        failures.append(
            f"binding.allocation_rule {binding.get('allocation_rule')!r} is not an "
            "engine kernel (pro_rata is exact-arithmetic only)"
        )
    if binding.get("n_draws") != K_INFERENCE_DRAWS:
        failures.append(
            f"binding.n_draws must equal the frozen K = {K_INFERENCE_DRAWS}, "
            f"got {binding.get('n_draws')!r}"
        )
    names = binding.get("substream_names")
    if not isinstance(names, list) or not names or any(
        name not in SUBSTREAM_NAMES for name in names
    ):
        failures.append(
            f"binding.substream_names must be a non-empty subset of {SUBSTREAM_NAMES}, "
            f"got {names!r}"
        )
    return failures


def verify_lock(path: Path | str, *, deep: bool = True) -> LockVerification:
    """Verify a lock checkpoint + sidecar.

    Shallow mode (``deep=False``) never calls ``torch.load``: it re-hashes the
    checkpoint file bytes against ``checkpoint_sha256`` and recomputes the
    binding hash chain — the contracts' "verifiable without loading weights"
    surface for G4 (checkpoint sha256 vs lock manifest) and G10
    (allocation_rule / n_draws field validity). Deep mode additionally loads
    the payload and proves the weights, config and runtime inside the file
    match the recorded binding (catches a checkpoint whose bytes were rewritten
    together with the sidecar's file hash but whose weights no longer match the
    locked model hash; only the D0 lock manifest anchors a fully self-consistent
    rewrite).
    """

    checkpoint_path = Path(path)
    failures: list[str] = []
    sidecar: LockSidecar | None = None

    sidecar_file = lock_sidecar_path(checkpoint_path)
    try:
        sidecar = LockSidecar.from_json(sidecar_file.read_text())
    except (OSError, ValueError) as error:
        return LockVerification(ok=False, failures=(f"sidecar unreadable: {error}",))
    assert sidecar is not None

    if not checkpoint_path.exists():
        failures.append(f"checkpoint file is missing: {checkpoint_path}")
    else:
        file_sha256 = _sha256_hex(checkpoint_path.read_bytes())
        if file_sha256 != sidecar.checkpoint_sha256:
            failures.append(
                f"checkpoint file sha256 {file_sha256} != sidecar {sidecar.checkpoint_sha256}"
            )
    recomputed_chain = _sha256_hex(_canonical_json(sidecar.binding).encode("utf-8"))
    if recomputed_chain != sidecar.lock_chain_sha256:
        failures.append(
            f"binding hash chain {recomputed_chain} != sidecar {sidecar.lock_chain_sha256}"
        )
    failures.extend(_binding_failures(sidecar.binding))
    if failures:
        return LockVerification(ok=False, failures=tuple(failures), sidecar=sidecar)

    if not deep:
        return LockVerification(ok=True, failures=(), sidecar=sidecar)

    try:
        payload = cast(
            dict[str, Any],
            torch.load(checkpoint_path, map_location="cpu", weights_only=False),
        )
        runtime = _validate_lock_payload(payload)
    except Exception as error:  # a validator reports, it does not raise
        return LockVerification(
            ok=False,
            failures=(f"checkpoint unreadable or malformed: {error}",),
            sidecar=sidecar,
        )

    binding = sidecar.binding
    if _canonical_json(payload["lock_binding"]) != _canonical_json(binding):
        failures.append("checkpoint lock_binding differs from the sidecar binding")
    weights_sha256 = model_state_sha256(payload["sim_state_dict"])
    if weights_sha256 != binding["model_sha256"]:
        failures.append(
            f"recomputed model sha256 {weights_sha256} != binding {binding['model_sha256']}"
        )
    config_sha256 = _sha256_hex(_canonical_json(payload["sim_config"]).encode("utf-8"))
    if config_sha256 != binding["config_sha256"]:
        failures.append(
            f"recomputed config sha256 {config_sha256} != binding {binding['config_sha256']}"
        )
    if payload["train_config"].get("config_sha256") != binding["config_sha256"]:
        failures.append("payload train_config.config_sha256 differs from the binding")
    if sorted(runtime["substream_generator_states"]) != sorted(binding["substream_names"]):
        failures.append("rank-runtime substream states differ from binding.substream_names")
    if payload.get("iter_idx") != binding.get("iter_idx"):
        failures.append("payload iter_idx differs from the binding")
    return LockVerification(ok=not failures, failures=tuple(failures), sidecar=sidecar)
