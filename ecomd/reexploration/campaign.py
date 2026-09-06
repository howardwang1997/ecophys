"""E-5 frozen campaign enumeration + seed/stream manifest (ALPHA market cube).

Declarative single source of truth for two things the D0 freeze pins:

1. The C14-restated campaign arithmetic (prereg v2 section 3.4): 450
   trainings and 299,520 confirmatory evaluation records, reproduced here by
   explicit enumeration over the frozen grids — never by restating the
   published totals. ``validate_counts`` refuses (raises) if the enumeration
   and the preregistered targets disagree.
2. The C1 RNG-tree seed namespaces (11000-11029 / 12000-12029) and every
   disjoint instrument/preflight namespace, with the frozen
   ``numpy.random.SeedSequence.spawn`` substream derivation recorded per seed
   root and asserted collision-free (gate G2 namespace sub-check).

The module also validates the Hydra tree under ``configs/reexploration``
against the frozen sibling build surfaces (E-2 ``DGPConfig``, L1-2 /
fact-surrogate trainer configs, through-M estimator constants), so the tree
records but cannot drift from the code. It is outcome-blind: nothing here
runs cells, evaluations, endpoints or training.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import sys
from collections.abc import Iterator
from dataclasses import dataclass, fields, replace
from pathlib import Path
from typing import Any, cast

from ecomd.mechanisms.through_m import (
    PINNED_PERTURB_AND_MAP_SEED,
    PINNED_PERTURB_AND_MAP_SIGMA,
    PINNED_STRAIGHT_THROUGH_SCALE,
)
from ecomd.models.fact_surrogate import FactSurrogateConfig
from ecomd.models.l1_coordinate_heads import L1CoordinateHeadsConfig
from ecomd.training.l1_supervised import L1SupervisedTrainConfig
from ecomd.training.train_fact_surrogate import (
    K_INFERENCE_DRAWS,
    SUBSTREAM_NAMES,
    FactSurrogateTrainConfig,
    MechanismBackend,
    derive_substream_seeds,
)

REPO_ROOT: Path = Path(__file__).resolve().parents[2]
CONFIG_DIR: Path = REPO_ROOT / "configs" / "reexploration"
MANIFEST_PATH: Path = (
    REPO_ROOT
    / "experiments"
    / "reexploration"
    / "seed_stream_manifest_20260907"
    / "seeds_manifest.json"
)
MANIFEST_VERSION: int = 1
SCHEMA_VERSION: str = "ecomd-reexploration-e5-v1"
CAMPAIGN_ID: str = "alpha_cube_d0_20260919"


class CampaignError(RuntimeError):
    """Base class for E-5 validation failures (fail loudly, never coerce)."""


class CampaignArithmeticError(CampaignError):
    """The enumeration disagrees with the preregistered C14 targets."""


class SeedCollisionError(CampaignError):
    """A seed/stream disjointness assertion failed (gate G2 sub-check)."""


class ConfigTreeError(CampaignError):
    """The Hydra tree disagrees with the frozen sibling build surfaces."""


# ─────────────────────────────────────────────────────────────────────────────
# C1 seed namespaces and instrument/preflight namespaces
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class SeedNamespace:
    """A training seed-root namespace (prereg v2 C1; PI decision D1_10)."""

    namespace_id: str
    label: str
    seed_start: int
    seed_stop_inclusive: int
    stage2_subset_size: int  # C16 item (13): pinned first-15 Stage-2 subset
    reflexive_subset_size: int  # Annex B(d): first-10 reflexive/telemetry subset

    @property
    def seeds(self) -> tuple[int, ...]:
        return tuple(range(self.seed_start, self.seed_stop_inclusive + 1))

    @property
    def stage2_subset(self) -> tuple[int, ...]:
        return self.seeds[: self.stage2_subset_size]

    @property
    def reflexive_subset(self) -> tuple[int, ...]:
        return self.seeds[: self.reflexive_subset_size]


L1_TRAINING: SeedNamespace = SeedNamespace(
    namespace_id="l1_training",
    label="L1 lineage / B1-B2 seed roots 11000-11029",
    seed_start=11000,
    seed_stop_inclusive=11029,
    stage2_subset_size=15,
    reflexive_subset_size=10,
)
L2_TRAINING: SeedNamespace = SeedNamespace(
    namespace_id="l2_training",
    label="L2 lineage / B3-B4 seed roots 12000-12029",
    seed_start=12000,
    seed_stop_inclusive=12029,
    stage2_subset_size=15,
    reflexive_subset_size=10,
)
TRAINING_NAMESPACES: tuple[SeedNamespace, ...] = (L1_TRAINING, L2_TRAINING)

ENRICHMENT_MASTER_SEED: int = 20260972  # reserved 2026097x instrument block
RESAMPLER_MASTER_SEED: int = 20260973
S3_ROBUSTNESS_MASTER_SEEDS: tuple[int, ...] = (20260974, 20260975, 20260976)
PAM_FIXTURE_SEED: int = 20260906  # through_m fixture/replay default (not production noise)
K_PREFLIGHT_RESERVED_RANGE: tuple[int, int] = (31000, 31099)
K_PREFLIGHT_MASTER_SEEDS: tuple[int, ...] = tuple(range(31000, 31032))
INSTRUMENT_NAMESPACE_SEEDS: tuple[int, ...] = (
    ENRICHMENT_MASTER_SEED,
    RESAMPLER_MASTER_SEED,
    *S3_ROBUSTNESS_MASTER_SEEDS,
    PAM_FIXTURE_SEED,
)

# C8 / Annex B(a) bootstrap derivation: 5 blocks x 3 Holm families.
BOOTSTRAP_SALT: str = "ecomd_reexploration_v2_bootstrap"
BOOTSTRAP_MODULUS: int = 2**63
BOOTSTRAP_FAMILIES: tuple[str, ...] = (
    "signflip_mandatory",
    "axis_contrast",
    "truncation",
)


def bootstrap_seed(block_id: str, family_id: str) -> int:
    """Annex B(a): int(sha256(salt || block_id || family_id), 16) mod 2^63."""

    payload = f"{BOOTSTRAP_SALT}{block_id}{family_id}"
    return int(hashlib.sha256(payload.encode("utf-8")).hexdigest(), 16) % BOOTSTRAP_MODULUS


# ─────────────────────────────────────────────────────────────────────────────
# C3/C4 evaluation grid (eval-time parameters; training configs ignore them)
# ─────────────────────────────────────────────────────────────────────────────

AXES: tuple[str, ...] = ("id", "pop_2x", "tick_2x", "kswap")
DGP_AXES: tuple[str, ...] = ("id", "pop_2x", "tick_2x")  # E-2 config_for_axis vocabulary
HORIZONS: tuple[int, ...] = (1, 4, 16, 31)
HORIZON_DESCRIPTIVE_ONLY: int = 64
INFERENCE_ENFORCEMENTS: tuple[str, ...] = ("raw", "through_m")
KERNELS: tuple[str, ...] = ("fifo", "random_unit_within_price")  # pro_rata never executes (C3)
TRUNCATION_CONDITIONS: tuple[str, ...] = ("trunc_lag", "trunc_cap")
TRAINING_KERNEL: str = "fifo"  # C4: training kernel is FIFO in every stratum

# Preregistered C14-restated targets (prereg v2 section 3.4 tables). The
# enumeration below must reproduce these exactly or refuse to run.
C14_TARGETS: dict[str, int] = {
    "per_seed_mandatory": 2048,
    "trainings_stage1": 240,
    "trainings_stage2": 180,
    "trainings_audit": 30,
    "trainings_total": 450,
    "mandatory_stage1": 122880,
    "mandatory_stage2": 92160,
    "mandatory_total": 215040,
    "truncation_total": 76800,
    "audit_records": 7680,
    "confirmatory_total": 299520,
    "horizon_one_probes": 420,
}


# ─────────────────────────────────────────────────────────────────────────────
# Campaign specs (what the Hydra option files must say, verbatim)
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class BlockSpec:
    block_id: str
    option_name: str
    stage: int
    lineage_id: str
    dgp_id: str
    seed_namespace: str
    seed_start: int
    seed_stop_inclusive: int
    n_seeds: int
    stage2_subset: tuple[int, int] | None  # inclusive (start, stop)
    truncation_conditions: tuple[str, ...]

    @property
    def seeds(self) -> tuple[int, ...]:
        if self.stage2_subset is None:
            return tuple(range(self.seed_start, self.seed_stop_inclusive + 1))
        return tuple(range(self.stage2_subset[0], self.stage2_subset[1] + 1))

    @property
    def namespace(self) -> SeedNamespace:
        found = [ns for ns in TRAINING_NAMESPACES if ns.namespace_id == self.seed_namespace]
        if not found:
            raise CampaignError(f"unknown namespace {self.seed_namespace!r}")
        return found[0]


@dataclass(frozen=True)
class ArmSpec:
    arm_id: str
    coordinate: str
    enforcement: str
    estimator: str | None
    training_kernel: str


@dataclass(frozen=True)
class AxisSpec:
    axis_id: str
    dgp_axis: str
    inference_kernel_through_m: str
    raw_infer_duplicate_of: str | None


@dataclass(frozen=True)
class AuditSpec:
    audit_id: str
    lineage_id: str
    dgp_id: str
    coordinate: str
    enforcement: str
    inference_enforcement: str
    estimator: str
    seed_namespace: str
    seed_start: int
    seed_stop_inclusive: int
    n_seeds: int
    parent_block: str
    shares_substreams_with_parent: tuple[str, ...]


BLOCKS: tuple[BlockSpec, ...] = (
    BlockSpec(
        block_id="B1",
        option_name="b1",
        stage=1,
        lineage_id="l1",
        dgp_id="lab_asset",
        seed_namespace="l1_training",
        seed_start=11000,
        seed_stop_inclusive=11029,
        n_seeds=30,
        stage2_subset=None,
        truncation_conditions=("trunc_lag", "trunc_cap"),
    ),
    BlockSpec(
        block_id="B2",
        option_name="b2",
        stage=2,
        lineage_id="l1",
        dgp_id="garch_student_t5",
        seed_namespace="l1_training",
        seed_start=11000,
        seed_stop_inclusive=11029,
        n_seeds=15,
        stage2_subset=(11000, 11014),
        truncation_conditions=("trunc_lag", "trunc_cap"),
    ),
    BlockSpec(
        block_id="B3",
        option_name="b3",
        stage=1,
        lineage_id="l2",
        dgp_id="lab_asset",
        seed_namespace="l2_training",
        seed_start=12000,
        seed_stop_inclusive=12029,
        n_seeds=30,
        stage2_subset=None,
        truncation_conditions=("trunc_lag",),
    ),
    BlockSpec(
        block_id="B4-variantA",
        option_name="b4_variant_a",
        stage=2,
        lineage_id="l2",
        dgp_id="garch_student_t5",
        seed_namespace="l2_training",
        seed_start=12000,
        seed_stop_inclusive=12029,
        n_seeds=15,
        stage2_subset=(12000, 12014),
        truncation_conditions=("trunc_lag",),
    ),
    BlockSpec(
        block_id="B4-variantB",
        option_name="b4_variant_b",
        stage=2,
        lineage_id="l2",
        dgp_id="multiscale_logvol",
        seed_namespace="l2_training",
        seed_start=12000,
        seed_stop_inclusive=12029,
        n_seeds=15,
        stage2_subset=(12000, 12014),
        truncation_conditions=("trunc_lag",),
    ),
)
BLOCKS_BY_ID: dict[str, BlockSpec] = {block.block_id: block for block in BLOCKS}

ARMS: tuple[ArmSpec, ...] = (
    ArmSpec(
        arm_id="absolute_raw",
        coordinate="absolute",
        enforcement="raw",
        estimator=None,
        training_kernel=TRAINING_KERNEL,
    ),
    ArmSpec(
        arm_id="absolute_through_m",
        coordinate="absolute",
        enforcement="through_m",
        estimator="straight_through",
        training_kernel=TRAINING_KERNEL,
    ),
    ArmSpec(
        arm_id="increment_raw",
        coordinate="increment",
        enforcement="raw",
        estimator=None,
        training_kernel=TRAINING_KERNEL,
    ),
    ArmSpec(
        arm_id="increment_through_m",
        coordinate="increment",
        enforcement="through_m",
        estimator="straight_through",
        training_kernel=TRAINING_KERNEL,
    ),
)
ARMS_BY_ID: dict[str, ArmSpec] = {arm.arm_id: arm for arm in ARMS}

AXIS_SPECS: tuple[AxisSpec, ...] = (
    AxisSpec(
        axis_id="id",
        dgp_axis="id",
        inference_kernel_through_m=TRAINING_KERNEL,
        raw_infer_duplicate_of=None,
    ),
    AxisSpec(
        axis_id="pop_2x",
        dgp_axis="pop_2x",
        inference_kernel_through_m=TRAINING_KERNEL,
        raw_infer_duplicate_of=None,
    ),
    AxisSpec(
        axis_id="tick_2x",
        dgp_axis="tick_2x",
        inference_kernel_through_m=TRAINING_KERNEL,
        raw_infer_duplicate_of=None,
    ),
    AxisSpec(
        axis_id="kswap",
        dgp_axis="id",
        inference_kernel_through_m="random_unit_within_price",
        raw_infer_duplicate_of="id",
    ),
)
AXIS_SPECS_BY_ID: dict[str, AxisSpec] = {axis.axis_id: axis for axis in AXIS_SPECS}

AUDIT_A10: AuditSpec = AuditSpec(
    audit_id="A10",
    lineage_id="l1",
    dgp_id="lab_asset",
    coordinate="increment",
    enforcement="through_m",
    inference_enforcement="raw",
    estimator="perturb_and_map",
    seed_namespace="l1_training",
    seed_start=11000,
    seed_stop_inclusive=11029,
    n_seeds=30,
    parent_block="B1",
    shares_substreams_with_parent=("data", "init", "train_kernel"),
)

DGP_OPTION_NAMES: tuple[str, ...] = ("lab_asset", "garch_student_t5", "multiscale_logvol")
L2_ONLY_DGP_OPTIONS: tuple[str, ...] = ("multiscale_logvol",)
NAMED_NOT_RUN_DGP_FAMILIES: tuple[str, ...] = ("negative_jump_iid",)


# ─────────────────────────────────────────────────────────────────────────────
# C14 enumeration (explicit grid walks, not restated totals)
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class TrainingRun:
    """One sha256-locked training unit (gate G4 counts these)."""

    block_id: str
    stage: int
    lineage_id: str
    dgp_id: str
    arm_id: str
    seed: int
    seed_namespace: str
    audit_id: str | None = None
    estimator_override: str | None = None


def enumerate_trainings() -> tuple[TrainingRun, ...]:
    """All 450 training units: 5 blocks x 4 arms x seeds, plus the A10 audit."""

    audit_arm = ARMS_BY_ID["increment_through_m"].arm_id
    runs: list[TrainingRun] = []
    for block in BLOCKS:
        for arm in ARMS:
            for seed in block.seeds:
                runs.append(
                    TrainingRun(
                        block_id=block.block_id,
                        stage=block.stage,
                        lineage_id=block.lineage_id,
                        dgp_id=block.dgp_id,
                        arm_id=arm.arm_id,
                        seed=seed,
                        seed_namespace=block.seed_namespace,
                    )
                )
    parent = BLOCKS_BY_ID[AUDIT_A10.parent_block]
    for seed in range(AUDIT_A10.seed_start, AUDIT_A10.seed_stop_inclusive + 1):
        runs.append(
            TrainingRun(
                block_id=parent.block_id,
                stage=parent.stage,
                lineage_id=AUDIT_A10.lineage_id,
                dgp_id=AUDIT_A10.dgp_id,
                arm_id=audit_arm,
                seed=seed,
                seed_namespace=AUDIT_A10.seed_namespace,
                audit_id=AUDIT_A10.audit_id,
                estimator_override=AUDIT_A10.estimator,
            )
        )
    return tuple(runs)


def _cells() -> tuple[tuple[str, str], ...]:
    """The 8 evaluation cells: 4 trained arms x 2 inference enforcements."""

    return tuple(
        (arm.arm_id, infer) for arm in ARMS for infer in INFERENCE_ENFORCEMENTS
    )


def _mandatory_records(block: BlockSpec) -> int:
    """Walk the per-seed mandatory grid: 8 cells x 4 axes x 4 horizons x K."""

    per_seed = 0
    for _cell in _cells():
        for _axis in AXES:
            for _horizon in HORIZONS:
                for _draw in range(K_INFERENCE_DRAWS):
                    per_seed += 1
    return per_seed * len(block.seeds)


def _truncation_records(block: BlockSpec) -> int:
    """Section 3.4: per condition, ID axis, all 8 cells, all 4 horizons, K=16."""

    per_seed_per_condition = 0
    for _cell in _cells():
        for _horizon in HORIZONS:
            for _draw in range(K_INFERENCE_DRAWS):
                per_seed_per_condition += 1
    return len(block.truncation_conditions) * len(block.seeds) * per_seed_per_condition


def _audit_records() -> int:
    """A10: 1 cell x 30 seeds x 4 axes x 4 horizons x 16 draws."""

    total = 0
    for _seed in range(AUDIT_A10.seed_start, AUDIT_A10.seed_stop_inclusive + 1):
        for _axis in AXES:
            for _horizon in HORIZONS:
                for _draw in range(K_INFERENCE_DRAWS):
                    total += 1
    return total


@dataclass(frozen=True)
class CampaignCounts:
    trainings_stage1: int
    trainings_stage2: int
    trainings_audit: int
    trainings_total: int
    per_seed_mandatory: int
    mandatory_stage1: int
    mandatory_stage2: int
    mandatory_total: int
    truncation_total: int
    audit_records: int
    confirmatory_total: int
    horizon_one_probes: int
    per_block_mandatory: dict[str, int]
    per_block_truncation: dict[str, int]
    per_block_probes: dict[str, int]


def campaign_counts() -> CampaignCounts:
    """Enumerate the campaign grids and total them (never reads C14_TARGETS)."""

    runs = enumerate_trainings()
    per_block_mandatory = {block.block_id: _mandatory_records(block) for block in BLOCKS}
    per_block_truncation = {block.block_id: _truncation_records(block) for block in BLOCKS}
    # Horizon-one probes: 4 axes per block-unit (block x seed), K-independent.
    per_block_probes = {
        block.block_id: sum(1 for _seed in block.seeds for _axis in AXES)
        for block in BLOCKS
    }
    mandatory_stage1 = sum(per_block_mandatory[b.block_id] for b in BLOCKS if b.stage == 1)
    mandatory_stage2 = sum(per_block_mandatory[b.block_id] for b in BLOCKS if b.stage == 2)
    mandatory_total = mandatory_stage1 + mandatory_stage2
    truncation_total = sum(per_block_truncation.values())
    audit_records = _audit_records()
    return CampaignCounts(
        trainings_stage1=sum(1 for r in runs if r.stage == 1 and r.audit_id is None),
        trainings_stage2=sum(1 for r in runs if r.stage == 2 and r.audit_id is None),
        trainings_audit=sum(1 for r in runs if r.audit_id is not None),
        trainings_total=len(runs),
        per_seed_mandatory=per_block_mandatory[BLOCKS[0].block_id] // len(BLOCKS[0].seeds),
        mandatory_stage1=mandatory_stage1,
        mandatory_stage2=mandatory_stage2,
        mandatory_total=mandatory_total,
        truncation_total=truncation_total,
        audit_records=audit_records,
        confirmatory_total=mandatory_total + truncation_total + audit_records,
        horizon_one_probes=sum(per_block_probes.values()),
        per_block_mandatory=per_block_mandatory,
        per_block_truncation=per_block_truncation,
        per_block_probes=per_block_probes,
    )


def validate_counts() -> CampaignCounts:
    """Self-check: the enumeration must reproduce the section-3.4 targets.

    If it cannot, the discrepancy is raised (and must be recorded), never
    forced — the manifest refuses to build on a mismatch.
    """

    counts = campaign_counts()
    pairs: dict[str, int] = {
        "trainings_stage1": counts.trainings_stage1,
        "trainings_stage2": counts.trainings_stage2,
        "trainings_audit": counts.trainings_audit,
        "trainings_total": counts.trainings_total,
        "per_seed_mandatory": counts.per_seed_mandatory,
        "mandatory_stage1": counts.mandatory_stage1,
        "mandatory_stage2": counts.mandatory_stage2,
        "mandatory_total": counts.mandatory_total,
        "truncation_total": counts.truncation_total,
        "audit_records": counts.audit_records,
        "confirmatory_total": counts.confirmatory_total,
        "horizon_one_probes": counts.horizon_one_probes,
    }
    mismatches = [
        f"{key}: enumerated {value} != target {C14_TARGETS[key]}"
        for key, value in pairs.items()
        if value != C14_TARGETS[key]
    ]
    if mismatches:
        raise CampaignArithmeticError("C14 enumeration mismatch: " + "; ".join(mismatches))
    return counts


# ─────────────────────────────────────────────────────────────────────────────
# Rank-seed posture (simulator contracts section 6, flag 5)
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class RankSeedPosture:
    world_size: int
    rank_seed_formula: str
    rule_source: str
    overlap_note: str
    latent_overlap_example: str


RANK_SEED_POSTURE: RankSeedPosture = RankSeedPosture(
    world_size=1,
    rank_seed_formula="rank_seed(seed, rank) = seed + 10000 * rank",
    rule_source="ecomd/training/train_distributed.py rank-seed derivation",
    overlap_note=(
        "The campaign is pinned to single-worker training posture "
        "(world_size = 1, rank 0), where rank_seed == seed and the training "
        "roots 11000-11029 / 12000-12029 are consumed verbatim. The "
        "auxiliary rank streams at seed + 5,000,000 (61000-61029 / "
        "62000-62029) lie outside every reserved namespace."
    ),
    latent_overlap_example=(
        "At world_size >= 3 the L1 rank-2 seeds 11000 + 2*10000 = 31000-31029 "
        "would numerically equal the K-preflight master seeds 31000-31031 "
        "inside the reserved 31000-31099 block; that posture is forbidden "
        "for this campaign (flag 5 requires the check)."
    ),
)


# ─────────────────────────────────────────────────────────────────────────────
# Disjointness assertions (gate G2 namespace sub-check; fail loudly)
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class DisjointnessCheck:
    name: str
    ok: bool
    detail: str


def disjointness_checks() -> tuple[DisjointnessCheck, ...]:
    """Every namespace/substream disjointness assertion the freeze pins."""

    checks: list[DisjointnessCheck] = []
    l1, l2 = L1_TRAINING.seeds, L2_TRAINING.seeds
    training_roots = set(l1) | set(l2)
    reserved = set(range(K_PREFLIGHT_RESERVED_RANGE[0], K_PREFLIGHT_RESERVED_RANGE[1] + 1))
    instruments = set(INSTRUMENT_NAMESPACE_SEEDS)

    checks.append(
        DisjointnessCheck(
            name="training_namespaces_pairwise_disjoint",
            ok=not (set(l1) & set(l2)),
            detail=(
                f"l1_training [{L1_TRAINING.seed_start},{L1_TRAINING.seed_stop_inclusive}] "
                f"vs l2_training [{L2_TRAINING.seed_start},{L2_TRAINING.seed_stop_inclusive}]"
            ),
        )
    )
    checks.append(
        DisjointnessCheck(
            name="training_vs_k_preflight_reserved_disjoint",
            ok=not (training_roots & reserved),
            detail=(
                "training roots vs reserved [31000,31099] "
                f"(posture world_size={RANK_SEED_POSTURE.world_size})"
            ),
        )
    )
    checks.append(
        DisjointnessCheck(
            name="training_vs_instruments_disjoint",
            ok=not (training_roots & instruments),
            detail=f"training roots vs {sorted(instruments)}",
        )
    )
    checks.append(
        DisjointnessCheck(
            name="instruments_pairwise_distinct",
            ok=len(instruments) == len(INSTRUMENT_NAMESPACE_SEEDS),
            detail=f"instrument seeds {sorted(instruments)}",
        )
    )
    checks.append(
        DisjointnessCheck(
            name="instruments_vs_k_preflight_reserved_disjoint",
            ok=not (instruments & reserved),
            detail="2026097x block + PAM fixture vs [31000,31099]",
        )
    )
    for ns in TRAINING_NAMESPACES:
        checks.append(
            DisjointnessCheck(
                name=f"{ns.namespace_id}_stage2_subset_is_first15_ascending",
                ok=ns.stage2_subset == ns.seeds[:15],
                detail=(
                    f"[{ns.stage2_subset[0]},{ns.stage2_subset[-1]}] "
                    "(C16 item (13))"
                ),
            )
        )
        checks.append(
            DisjointnessCheck(
                name=f"{ns.namespace_id}_reflexive_subset_is_first10_ascending",
                ok=ns.reflexive_subset == ns.seeds[:10],
                detail=(
                    f"[{ns.reflexive_subset[0]},{ns.reflexive_subset[-1]}] "
                    "(Annex B(d))"
                ),
            )
        )
    for block in BLOCKS:
        ns = block.namespace
        if block.stage2_subset is None:
            ok = set(block.seeds) == set(ns.seeds)
            name = f"block_{block.block_id}_covers_namespace"
            detail = "Stage-1 block trains the full namespace"
        else:
            ok = set(block.seeds) == set(ns.stage2_subset)
            name = f"block_{block.block_id}_is_pinned_first15"
            detail = (
                "Stage-2 block trains exactly the pinned first-15 subset of "
                "its namespace (same-namespace Stage-1/Stage-2 seed overlap "
                "is by design; the subset pin is the contract)"
            )
        checks.append(DisjointnessCheck(name=name, ok=ok, detail=detail))
    checks.append(
        DisjointnessCheck(
            name="audit_A10_seeds_equal_parent_namespace",
            ok=set(range(AUDIT_A10.seed_start, AUDIT_A10.seed_stop_inclusive + 1))
            == set(L1_TRAINING.seeds),
            detail="audit reuses B1's fixture streams on all 30 paired seeds",
        )
    )
    bootstrap = {
        f"{block.block_id}|{family}": bootstrap_seed(block.block_id, family)
        for block in BLOCKS
        for family in BOOTSTRAP_FAMILIES
    }
    checks.append(
        DisjointnessCheck(
            name="bootstrap_seeds_pairwise_distinct",
            ok=len(set(bootstrap.values())) == len(bootstrap),
            detail=f"{len(bootstrap)} (block, family) bootstrap seeds",
        )
    )
    checks.append(
        DisjointnessCheck(
            name="bootstrap_seeds_outside_reserved_namespaces",
            ok=not (set(bootstrap.values()) & (training_roots | instruments | reserved)),
            detail=(
                "Annex B(a) seeds vs all reserved integer ranges (they are "
                "63-bit hashes, so disjoint by construction; asserted)"
            ),
        )
    )
    derived: dict[int, tuple[int, str]] = {}
    derived_ok = True
    collision_detail = "no collisions"
    reserved_ints = training_roots | instruments | reserved
    for ns in TRAINING_NAMESPACES:
        for root in ns.seeds:
            for name, value in derive_substream_seeds(root).items():
                if value in derived:
                    derived_ok = False
                    collision_detail = (
                        f"substream {name} of root {root} collides with "
                        f"{derived[value][1]} of root {derived[value][0]}"
                    )
                derived[value] = (root, name)
                if value in reserved_ints:
                    derived_ok = False
                    collision_detail = (
                        f"substream {name} of root {root} equals reserved integer {value}"
                    )
    checks.append(
        DisjointnessCheck(
            name="derived_substreams_distinct_and_outside_reserved",
            ok=derived_ok,
            detail=(
                f"{len(derived)} derived substream integers across "
                f"{len(training_roots)} roots; {collision_detail}"
            ),
        )
    )
    return tuple(checks)


def assert_disjointness() -> tuple[DisjointnessCheck, ...]:
    """Run all checks and raise SeedCollisionError on any failure."""

    checks = disjointness_checks()
    failed = [check for check in checks if not check.ok]
    if failed:
        raise SeedCollisionError(
            "seed/stream disjointness failed: "
            + "; ".join(f"{c.name} ({c.detail})" for c in failed)
        )
    return checks


# ─────────────────────────────────────────────────────────────────────────────
# Hydra composition (configs/reexploration tree)
# ─────────────────────────────────────────────────────────────────────────────


def _hydra_compose_batch(override_lists: list[list[str]]) -> list[dict[str, Any]]:
    from hydra import compose as hydra_compose
    from hydra import initialize_config_dir
    from omegaconf import OmegaConf

    if not CONFIG_DIR.is_dir():
        raise ConfigTreeError(f"missing config dir {CONFIG_DIR}")
    payloads: list[dict[str, Any]] = []
    with initialize_config_dir(config_dir=str(CONFIG_DIR), version_base="1.2"):
        for overrides in override_lists:
            cfg = hydra_compose(config_name="config", overrides=overrides)
            container = OmegaConf.to_container(cfg, resolve=False)
            if not isinstance(container, dict):
                raise ConfigTreeError("composed config is not a mapping")
            payloads.append(cast("dict[str, Any]", container))
    return payloads


def _overrides_for(block_id: str, arm_id: str, axis_id: str) -> list[str]:
    if block_id not in BLOCKS_BY_ID:
        raise CampaignError(f"unknown block {block_id!r}")
    if arm_id not in ARMS_BY_ID:
        raise CampaignError(f"unknown arm {arm_id!r}")
    if axis_id not in AXIS_SPECS_BY_ID:
        raise CampaignError(f"unknown axis {axis_id!r}")
    return [
        f"block={BLOCKS_BY_ID[block_id].option_name}",
        f"arm={arm_id}",
        f"axis={axis_id}",
    ]


def load_composed_config(block_id: str, arm_id: str, axis_id: str | None = None) -> dict[str, Any]:
    """Compose one run config from the frozen option groups."""

    return _hydra_compose_batch(
        [_overrides_for(block_id, arm_id, axis_id if axis_id is not None else "id")]
    )[0]


def training_compositions() -> tuple[tuple[str, str, dict[str, Any]], ...]:
    """The 20 (block, arm) training compositions.

    Axis is pinned to id and ignored at training time; eval-time parameters
    are composed in for provenance only.
    """

    override_lists = [
        _overrides_for(block.block_id, arm.arm_id, "id")
        for block in BLOCKS
        for arm in ARMS
    ]
    payloads = _hydra_compose_batch(override_lists)
    return tuple(
        (BLOCKS[i // len(ARMS)].block_id, ARMS[i % len(ARMS)].arm_id, payload)
        for i, payload in enumerate(payloads)
    )


def deployment_compositions() -> tuple[tuple[str, str, str, dict[str, Any]], ...]:
    """The 80 (block, arm, axis) deployment compositions."""

    grid = [
        (block.block_id, arm.arm_id, axis.axis_id)
        for block in BLOCKS
        for arm in ARMS
        for axis in AXIS_SPECS
    ]
    payloads = _hydra_compose_batch(
        [_overrides_for(*triple) for triple in grid]
    )
    return tuple((*triple, payload) for triple, payload in zip(grid, payloads, strict=True))


def canonical_json_bytes(obj: Any) -> bytes:
    """Byte-stable serialization (sorted keys, tight separators, newline)."""

    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def composed_fingerprint(payload: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json_bytes(payload))


def _read_yaml(path: Path) -> dict[str, Any]:
    import yaml

    with path.open("rb") as handle:
        loaded = yaml.safe_load(handle)
    if not isinstance(loaded, dict):
        raise ConfigTreeError(f"{path} is not a mapping")
    return cast("dict[str, Any]", loaded)


def load_audit_config() -> dict[str, Any]:
    """The A10 audit cell config (a plain YAML document, no Hydra groups)."""

    return _read_yaml(CONFIG_DIR / "audit" / "a10.yaml")


# ─────────────────────────────────────────────────────────────────────────────
# Config-tree validation against the frozen sibling build surfaces
# ─────────────────────────────────────────────────────────────────────────────


def _e2_module() -> Any:
    """Lazily import the E-2 generator (scripts/ is not an installed package)."""

    scripts_dir = str(REPO_ROOT / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    return importlib.import_module("lab_asset.dgp_request_generator")


def _iter_strings(obj: Any) -> Iterator[str]:
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for key, value in obj.items():
            yield from _iter_strings(key)
            yield from _iter_strings(value)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            yield from _iter_strings(item)


def _check_dataclass_binding(
    label: str,
    yaml_block: dict[str, Any],
    defaults: Any,
    excluded: set[str],
    failures: list[str],
) -> None:
    """A YAML hyperparameter block must equal frozen dataclass defaults.

    Required = every field with a non-None default that is not arm-level or
    sealed; optional (None-defaulted) fields may be absent (= None).
    """

    field_names = {f.name for f in fields(defaults)}
    unknown = sorted(set(yaml_block) - field_names)
    if unknown:
        failures.append(f"{label}: unknown keys {unknown}")
    required = {
        f.name
        for f in fields(defaults)
        if f.name not in excluded and getattr(defaults, f.name) is not None
    }
    missing = sorted(required - set(yaml_block))
    if missing:
        failures.append(f"{label}: missing required keys {missing}")
    for key, value in yaml_block.items():
        if key not in field_names:
            continue
        frozen_value = getattr(defaults, key)
        equal = frozen_value == value or (
            isinstance(frozen_value, float)
            and isinstance(value, (int, float))
            and float(value) == frozen_value
        )
        if not equal:
            failures.append(f"{label}: {key}={value!r} != frozen default {frozen_value!r}")


def validate_config_tree() -> tuple[str, ...]:
    """Validate the whole configs/reexploration tree. Returns failures."""

    failures: list[str] = []
    gen = _e2_module()
    if tuple(gen.D2_NAMED_NOT_RUN) != NAMED_NOT_RUN_DGP_FAMILIES:
        failures.append(
            f"E-2 D2_NAMED_NOT_RUN {tuple(gen.D2_NAMED_NOT_RUN)} != "
            f"{NAMED_NOT_RUN_DGP_FAMILIES}"
        )
    dgp_defaults = {
        family: replace(gen.DGPConfig(), dgp_family=gen.DgpFamily(family))
        for family in DGP_OPTION_NAMES
    }

    def check_block_payload(payload: dict[str, Any], block: BlockSpec) -> None:
        group = payload.get("block")
        if not isinstance(group, dict):
            failures.append(f"block {block.block_id}: group missing")
            return
        expected = {
            "block_id": block.block_id,
            "stage": block.stage,
            "lineage_id": block.lineage_id,
            "dgp_id": block.dgp_id,
            "seed_namespace": block.seed_namespace,
            "seed_start": block.seed_start,
            "seed_stop_inclusive": block.seed_stop_inclusive,
            "n_seeds": block.n_seeds,
        }
        for key, value in expected.items():
            if group.get(key) != value:
                failures.append(
                    f"block {block.block_id}: {key}={group.get(key)!r} != {value!r}"
                )
        yaml_subset = group.get("stage2_subset")
        if block.stage2_subset is None:
            if yaml_subset is not None:
                failures.append(f"block {block.block_id}: stage2_subset should be null")
        elif not isinstance(yaml_subset, dict):
            failures.append(f"block {block.block_id}: stage2_subset missing")
        elif (
            yaml_subset.get("seed_start") != block.stage2_subset[0]
            or yaml_subset.get("seed_stop_inclusive") != block.stage2_subset[1]
        ):
            failures.append(
                f"block {block.block_id}: stage2_subset {yaml_subset} != {block.stage2_subset}"
            )
        if tuple(group.get("truncation_conditions") or ()) != block.truncation_conditions:
            failures.append(
                f"block {block.block_id}: truncation_conditions "
                f"{group.get('truncation_conditions')} != {block.truncation_conditions}"
            )

    def check_lineage_payload(payload: dict[str, Any], lineage_id: str) -> None:
        block_group = payload.get("block")
        lineage = block_group.get("lineage") if isinstance(block_group, dict) else None
        if not isinstance(lineage, dict):
            failures.append("compose: missing lineage group")
            return
        if lineage.get("lineage_id") != lineage_id:
            failures.append(f"lineage group: lineage_id mismatch for {lineage_id}")
        model = lineage.get("model")
        train = lineage.get("train")
        if not isinstance(model, dict) or not isinstance(train, dict):
            failures.append(f"lineage {lineage_id}: model/train blocks missing")
            return
        if lineage_id == "l1":
            _check_dataclass_binding(
                f"lineage {lineage_id}.model", model, L1CoordinateHeadsConfig(), set(), failures
            )
            _check_dataclass_binding(
                f"lineage {lineage_id}.train",
                train,
                L1SupervisedTrainConfig(),
                {"coordinate", "channel_scales"},
                failures,
            )
        else:
            _check_dataclass_binding(
                f"lineage {lineage_id}.model", model, FactSurrogateConfig(), set(), failures
            )
            _check_dataclass_binding(
                f"lineage {lineage_id}.train",
                train,
                FactSurrogateTrainConfig(),
                {
                    "coordinate",
                    "enforcement",
                    "estimator",
                    "kernel",
                    "mechanism_backend",
                    "channel_scales",
                },
                failures,
            )

    def check_dgp_payload(payload: dict[str, Any], dgp_id: str) -> str:
        """Validate the dgp group; return its parsed-config fingerprint."""

        block_group = payload.get("block")
        dgp = block_group.get("dgp") if isinstance(block_group, dict) else None
        if not isinstance(dgp, dict):
            failures.append(f"dgp {dgp_id}: group missing")
            return ""
        if dgp.get("dgp_id") != dgp_id:
            failures.append(f"dgp group: dgp_id {dgp.get('dgp_id')!r} != {dgp_id!r}")
        mapping = dgp.get("config")
        if not isinstance(mapping, dict):
            failures.append(f"dgp {dgp_id}: config mapping missing")
            return ""
        try:
            parsed = gen.config_from_mapping(mapping)
        except ValueError as exc:
            failures.append(f"dgp {dgp_id}: config_from_mapping rejected: {exc}")
            return ""
        if parsed != dgp_defaults[dgp_id]:
            failures.append(
                f"dgp {dgp_id}: parsed config differs from frozen DGPConfig "
                f"defaults ({gen.config_fingerprint(parsed)} vs "
                f"{gen.config_fingerprint(dgp_defaults[dgp_id])})"
            )
        series_law = dgp.get("series_law")
        if dgp_id == "lab_asset":
            if series_law is not None:
                failures.append("dgp lab_asset: series_law must be null")
        elif not isinstance(series_law, dict):
            failures.append(f"dgp {dgp_id}: series_law registry entry missing")
        elif series_law.get("registry_key") != dgp_id:
            failures.append(f"dgp {dgp_id}: series_law.registry_key mismatch")
        elif dgp_id not in gen.D2_SERIES_REGISTRY:
            failures.append(f"dgp {dgp_id}: not in E-2 D2_SERIES_REGISTRY")
        if dgp_id in L2_ONLY_DGP_OPTIONS and "l2_only" not in dgp:
            failures.append(f"dgp {dgp_id}: missing l2_only marker")
        return str(gen.config_fingerprint(parsed))

    def check_arm_payload(payload: dict[str, Any], arm: ArmSpec) -> None:
        group = payload.get("arm")
        if not isinstance(group, dict):
            failures.append(f"arm {arm.arm_id}: group missing")
            return
        expected = {
            "arm_id": arm.arm_id,
            "coordinate": arm.coordinate,
            "enforcement": arm.enforcement,
            "estimator": arm.estimator,
            "training_kernel": arm.training_kernel,
        }
        for key, value in expected.items():
            if group.get(key) != value:
                failures.append(f"arm {arm.arm_id}: {key}={group.get(key)!r} != {value!r}")

    def check_axis_payload(payload: dict[str, Any], axis: AxisSpec) -> None:
        group = payload.get("axis")
        if not isinstance(group, dict):
            failures.append(f"axis {axis.axis_id}: group missing")
            return
        expected = {
            "axis_id": axis.axis_id,
            "dgp_axis": axis.dgp_axis,
            "inference_kernel_through_m": axis.inference_kernel_through_m,
            "raw_infer_duplicate_of": axis.raw_infer_duplicate_of,
        }
        for key, value in expected.items():
            if group.get(key) != value:
                failures.append(f"axis {axis.axis_id}: {key}={group.get(key)!r} != {value!r}")

    def check_root_payload(payload: dict[str, Any], label: str) -> None:
        if payload.get("schema_version") != SCHEMA_VERSION:
            failures.append(f"{label}: schema_version mismatch")
        if payload.get("mechanism_backend") != MechanismBackend.ENGINE_BRIDGE.value:
            failures.append(f"{label}: mechanism_backend is not engine_bridge")
        eval_block = payload.get("eval")
        if not isinstance(eval_block, dict):
            failures.append("root: eval block missing")
            return
        expected_eval: dict[str, Any] = {
            "axes": list(AXES),
            "horizons": list(HORIZONS),
            "horizon_descriptive_only": HORIZON_DESCRIPTIVE_ONLY,
            "inference_enforcements": list(INFERENCE_ENFORCEMENTS),
            "cells_per_seed": 8,
            "k_inference_draws": K_INFERENCE_DRAWS,
        }
        for key, value in expected_eval.items():
            if eval_block.get(key) != value:
                failures.append(f"root: eval.{key}={eval_block.get(key)!r} != {value!r}")
        estimators = payload.get("estimators")
        if not isinstance(estimators, dict):
            failures.append("root: estimators block missing")
            return
        expected_estimators = {
            "straight_through_scale": PINNED_STRAIGHT_THROUGH_SCALE,
            "perturb_and_map_sigma": PINNED_PERTURB_AND_MAP_SIGMA,
            "pam_fixture_default_seed": PINNED_PERTURB_AND_MAP_SEED,
        }
        for key, value in expected_estimators.items():
            if estimators.get(key) != value:
                failures.append(f"root: estimators.{key} != through_m pinned constant")

    for block_id, arm_id, payload in training_compositions():
        check_block_payload(payload, BLOCKS_BY_ID[block_id])
        check_arm_payload(payload, ARMS_BY_ID[arm_id])
        check_lineage_payload(payload, BLOCKS_BY_ID[block_id].lineage_id)
        check_dgp_payload(payload, BLOCKS_BY_ID[block_id].dgp_id)
        check_root_payload(payload, f"{block_id}/{arm_id}")

    id_fingerprints: dict[str, str] = {}
    for block_id, arm_id, axis_id, payload in deployment_compositions():
        axis = AXIS_SPECS_BY_ID[axis_id]
        check_axis_payload(payload, axis)
        fingerprint = check_dgp_payload(payload, BLOCKS_BY_ID[block_id].dgp_id)
        key = f"{block_id}|{arm_id}"
        if axis_id == "id":
            id_fingerprints[key] = fingerprint
        else:
            reference = id_fingerprints.get(key)
            if reference is not None and fingerprint != reference:
                failures.append(
                    f"axis {axis_id} changed DGP truth for {key}: "
                    f"{fingerprint} != {reference}"
                )
        try:
            gen.config_for_axis(dgp_defaults[BLOCKS_BY_ID[block_id].dgp_id], axis.dgp_axis)
        except ValueError as exc:
            failures.append(f"E-2 config_for_axis rejected {axis.dgp_axis!r}: {exc}")

    audit = load_audit_config()
    expected_audit = {
        "audit_id": AUDIT_A10.audit_id,
        "lineage_id": AUDIT_A10.lineage_id,
        "dgp_id": AUDIT_A10.dgp_id,
        "coordinate": AUDIT_A10.coordinate,
        "enforcement": AUDIT_A10.enforcement,
        "inference_enforcement": AUDIT_A10.inference_enforcement,
        "estimator": AUDIT_A10.estimator,
        "seed_namespace": AUDIT_A10.seed_namespace,
        "seed_start": AUDIT_A10.seed_start,
        "seed_stop_inclusive": AUDIT_A10.seed_stop_inclusive,
        "n_seeds": AUDIT_A10.n_seeds,
        "parent_block": AUDIT_A10.parent_block,
    }
    for key, value in expected_audit.items():
        if audit.get(key) != value:
            failures.append(f"audit A10: {key}={audit.get(key)!r} != {value!r}")
    if tuple(audit.get("shares_substreams_with_parent") or ()) != (
        AUDIT_A10.shares_substreams_with_parent
    ):
        failures.append("audit A10: shares_substreams_with_parent mismatch")

    dgp_options = sorted(path.stem for path in (CONFIG_DIR / "dgp").glob("*.yaml"))
    if dgp_options != sorted(DGP_OPTION_NAMES):
        failures.append(f"dgp option files {dgp_options} != {sorted(DGP_OPTION_NAMES)}")
    if tuple(gen.D2_RUN_VARIANTS) != ("garch_student_t5", "multiscale_logvol"):
        failures.append("E-2 D2_RUN_VARIANTS changed unexpectedly")

    root_doc = _read_yaml(CONFIG_DIR / "config.yaml")
    named_not_run = root_doc.get("named_not_run")
    if not isinstance(named_not_run, dict):
        failures.append("root: named_not_run block missing")
    elif tuple(named_not_run.get("dgp_families") or ()) != NAMED_NOT_RUN_DGP_FAMILIES:
        failures.append("root: named_not_run.dgp_families mismatch")

    # pro_rata must never appear as a VALUE anywhere in the tree (C3 ruling:
    # comments may name it, selections never do).
    for yaml_path in sorted(CONFIG_DIR.rglob("*.yaml")):
        for value in _iter_strings(_read_yaml(yaml_path)):
            if value == "pro_rata":
                failures.append(f"{yaml_path.name}: selects pro_rata")

    return tuple(failures)


# ─────────────────────────────────────────────────────────────────────────────
# Seed/stream manifest
# ─────────────────────────────────────────────────────────────────────────────


def build_seed_manifest() -> dict[str, Any]:
    """The complete frozen seed/stream manifest (validated; refuses on error)."""

    counts = validate_counts()
    checks = assert_disjointness()
    blocks_by_namespace: dict[str, list[str]] = {}
    for block in BLOCKS:
        blocks_by_namespace.setdefault(block.seed_namespace, []).append(block.block_id)

    seed_roots: list[dict[str, Any]] = []
    for ns in TRAINING_NAMESPACES:
        for root in ns.seeds:
            seed_roots.append(
                {
                    "seed": root,
                    "namespace": ns.namespace_id,
                    "blocks": blocks_by_namespace[ns.namespace_id],
                    "stage2_included": root in ns.stage2_subset,
                    "substreams": derive_substream_seeds(root),
                }
            )

    bootstrap = {
        f"{block.block_id}|{family}": bootstrap_seed(block.block_id, family)
        for block in BLOCKS
        for family in BOOTSTRAP_FAMILIES
    }

    return {
        "manifest_version": MANIFEST_VERSION,
        "campaign_id": CAMPAIGN_ID,
        "schema_version": SCHEMA_VERSION,
        "spec_sources": [
            "papers/proposal/ecomd_reexploration_prereg_v2_2026-09-06.md "
            "(C1-C4, C8/Annex B, C14 section 3.4, C16 items (11)-(16))",
            "papers/proposal/ecomd_reexploration_simulator_contracts_2026-09-06.md "
            "(section 4 item E-5, section 6 flag 5)",
        ],
        "derivation": {
            "substream_library": "numpy.random.SeedSequence.spawn",
            "substream_name_order": list(SUBSTREAM_NAMES),
            "substream_rule": (
                "SeedSequence(root).spawn(20) in exactly the recorded name "
                "order; the integer seed of substream i is the first uint32 "
                "of generate_state(1)"
            ),
            "episode_rule": (
                "episode nodes: SeedSequence(entropy=root, "
                "spawn_key=(data_index, episode_index)) — E-2 "
                "episode_seed_sequence, spawn-equivalent to the data child"
            ),
            "preflight_draw_rule": (
                "derive_seed(*parts) = int(sha256('|'.join(str(part) for "
                "part in parts).encode())[:8], big) — E-2 derive_seed, "
                "K-preflight byte-compatible"
            ),
            "bootstrap_salt": BOOTSTRAP_SALT,
            "bootstrap_rule": (
                "int(sha256(salt || block_id || family_id), 16) mod 2^63 — "
                "Annex B(a); recorded in the analyzer manifest"
            ),
            "bootstrap_block_ids": [block.block_id for block in BLOCKS],
            "bootstrap_family_ids": list(BOOTSTRAP_FAMILIES),
            "bootstrap_seeds": bootstrap,
        },
        "namespaces": [
            {
                "namespace_id": ns.namespace_id,
                "label": ns.label,
                "seed_start": ns.seed_start,
                "seed_stop_inclusive": ns.seed_stop_inclusive,
                "n_seeds": len(ns.seeds),
                "stage2_subset": {
                    "seed_start": ns.stage2_subset[0],
                    "seed_stop_inclusive": ns.stage2_subset[-1],
                    "n_seeds": ns.stage2_subset_size,
                    "pin": "C16 item (13): pinned first-15 ascending",
                },
                "reflexive_subset": {
                    "seed_start": ns.reflexive_subset[0],
                    "seed_stop_inclusive": ns.reflexive_subset[-1],
                    "n_seeds": ns.reflexive_subset_size,
                    "pin": "Annex B(d): first-10 reflexive/T4-telemetry",
                },
                "blocks": blocks_by_namespace[ns.namespace_id],
            }
            for ns in TRAINING_NAMESPACES
        ],
        "instrument_namespaces": [
            {
                "namespace_id": "enrichment",
                "master_seed": ENRICHMENT_MASTER_SEED,
                "reserved_block": "2026097x",
            },
            {
                "namespace_id": "resampler",
                "master_seed": RESAMPLER_MASTER_SEED,
                "reserved_block": "2026097x",
            },
            {
                "namespace_id": "s3_robustness",
                "master_seeds": list(S3_ROBUSTNESS_MASTER_SEEDS),
                "reserved_block": "2026097x",
                "pin": "Annex B(c): rung-order allocation",
            },
            {
                "namespace_id": "k_preflight",
                "reserved_range": list(K_PREFLIGHT_RESERVED_RANGE),
                "master_seeds": list(K_PREFLIGHT_MASTER_SEEDS),
            },
            {
                "namespace_id": "pam_fixture",
                "master_seed": PAM_FIXTURE_SEED,
                "note": (
                    "through_m fixture/replay default only; production PAM "
                    "noise derives from the train_kernel substream"
                ),
            },
        ],
        "seed_roots": seed_roots,
        "disjointness": {
            "checks": [{"name": c.name, "ok": c.ok, "detail": c.detail} for c in checks],
            "all_ok": all(c.ok for c in checks),
        },
        "campaign_enumeration": {
            "counts": {
                "trainings_stage1": counts.trainings_stage1,
                "trainings_stage2": counts.trainings_stage2,
                "trainings_audit": counts.trainings_audit,
                "trainings_total": counts.trainings_total,
                "per_seed_mandatory": counts.per_seed_mandatory,
                "mandatory_stage1": counts.mandatory_stage1,
                "mandatory_stage2": counts.mandatory_stage2,
                "mandatory_total": counts.mandatory_total,
                "truncation_total": counts.truncation_total,
                "audit_records": counts.audit_records,
                "confirmatory_total": counts.confirmatory_total,
                "horizon_one_probes": counts.horizon_one_probes,
                "per_block_mandatory": counts.per_block_mandatory,
                "per_block_truncation": counts.per_block_truncation,
                "per_block_probes": counts.per_block_probes,
            },
            "targets": C14_TARGETS,
            "matches_targets": True,
            "note": (
                "counts enumerated from the frozen grids (prereg v2 section "
                "3.4); validate_counts() refuses on any mismatch"
            ),
        },
        "rank_seed_posture": {
            "world_size": RANK_SEED_POSTURE.world_size,
            "rank_seed_formula": RANK_SEED_POSTURE.rank_seed_formula,
            "rule_source": RANK_SEED_POSTURE.rule_source,
            "overlap_note": RANK_SEED_POSTURE.overlap_note,
            "latent_overlap_example": RANK_SEED_POSTURE.latent_overlap_example,
        },
    }


def write_seed_manifest(path: Path | None = None) -> str:
    """Build, validate and write the manifest; returns its sha256."""

    target = path if path is not None else MANIFEST_PATH
    manifest = build_seed_manifest()
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = canonical_json_bytes(manifest)
    target.write_bytes(payload)
    return sha256_bytes(payload)


def manifest_sha256_on_disk(path: Path | None = None) -> str:
    target = path if path is not None else MANIFEST_PATH
    return sha256_bytes(target.read_bytes())
