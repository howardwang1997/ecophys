"""090c — n=50 SOTA confirmations + AR(1)-clip × Zumbach combo.

Two purposes bundled:

(A) n=50 confirmation for the top-3 SOTA candidates from 089/090.
    Branch F taught us n=30 means inflate ~0.16 (asymdrag 5.10→4.94,
    b3_k3 5.21→4.94 at n=50). 090 has these cells at n=30; we add 20
    more seeds so the final n=50 results survive reviewer-2 scrutiny.

    - pair_zumdn_b3       : 090's projected new SOTA pair → seeds 30..49
    - pair_AB_reref       : Branch F's 5.18 SOTA pair (Zumbach `dn` removed) → seeds 30..49
    - zumdn_solo_n30      : 089's SOTA single → seeds 30..49

(B) AR(1)-clip × Zumbach `dn` composition — newly unlocked by the
    ar1_whiten_clip knob added in this session. Without clip, AR(1)
    s05 + anything composes unstably (089 s03 had 70% rej; s05 only
    1/50 rej but breaks ckur). With clip=1.0, the EMA-subtraction is
    bounded, so AR(1) becomes a safe patch to combine. Three
    strengths tested.

    - pair_ar1clip05_zumdn   : AR(1) s=0.5, clip=1.0 + Zumbach `dn`
    - pair_ar1clip03_zumdn   : AR(1) s=0.3, clip=1.0 + Zumbach `dn`
    - pair_ar1clip05_b3      : AR(1) s=0.5, clip=1.0 + B3 (control)

Total: 3 × 20 + 3 × 30 = 60 + 90 = 150 cfg ≈ ~2.5h H20.

Seeds for confirmation cells start at 30 (not 0), so they don't collide
with 090's seeds 0..29. score_phase merges them under the same cell tag
when the matching cells in 090 share the prefix.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_SPX = REPO / "experiments" / "069_gamma_damping_30seed" / "config_T05_g10_seed0.yaml"
OUT = REPO / "experiments" / "090c_n50_confirm_and_ar1clip_combo"
OUT.mkdir(parents=True, exist_ok=True)


def apply_asym(cfg, alpha=0.6):
    cfg["simulator"]["asym_drag_alpha"] = alpha


def apply_b3(cfg, k=3, tau=1.0):
    cfg["simulator"]["regime_enabled"] = True
    cfg["simulator"]["regime_discrete_enabled"] = True
    cfg["simulator"]["regime_n_states"] = k
    cfg["simulator"]["regime_gumbel_tau"] = tau


def apply_ar1_whiten_clip(cfg, lam=0.9, strength=0.5, clip=1.0):
    cfg["simulator"]["ar1_whiten_lambda"] = lam
    cfg["simulator"]["ar1_whiten_strength"] = strength
    cfg["simulator"]["ar1_whiten_clip"] = clip


def apply_zumbach_dn(cfg):
    cfg["simulator"]["zumbach_feedback_lambda"] = 0.95
    cfg["simulator"]["zumbach_feedback_strength"] = 1.0
    cfg["simulator"]["zumbach_feedback_mode"] = "downside"


# (tag, n_seeds, seed_start, mods)
CELLS = [
    # ── (A) n=50 confirmation extensions: seeds 30..49 only ────────────
    ("pair_zumdn_b3",  20, 30, [apply_zumbach_dn, lambda c: apply_b3(c)]),
    ("pair_AB_reref",  20, 30, [lambda c: apply_asym(c), lambda c: apply_b3(c)]),
    ("zumdn_solo_n30", 20, 30, [apply_zumbach_dn]),
    # ── (B) AR(1)-clip × Zumbach combos (new, full n=30) ───────────────
    ("pair_ar1clip05_zumdn", 30, 0,
        [lambda c: apply_ar1_whiten_clip(c, lam=0.9, strength=0.5, clip=1.0),
         apply_zumbach_dn]),
    ("pair_ar1clip03_zumdn", 30, 0,
        [lambda c: apply_ar1_whiten_clip(c, lam=0.9, strength=0.3, clip=1.0),
         apply_zumbach_dn]),
    ("pair_ar1clip05_b3", 30, 0,
        [lambda c: apply_ar1_whiten_clip(c, lam=0.9, strength=0.5, clip=1.0),
         lambda c: apply_b3(c)]),
]


def main() -> None:
    base_spx = yaml.safe_load(BASE_SPX.read_text())
    n = 0
    for tag, n_seeds, seed_start, mods in CELLS:
        for offset in range(n_seeds):
            seed = seed_start + offset
            cfg = copy.deepcopy(base_spx)
            for fn in mods:
                fn(cfg)
            cfg["training"]["seed"] = seed
            (OUT / f"config_{tag}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1
    print(f"wrote {n} configs across {len(CELLS)} cells to {OUT}")


if __name__ == "__main__":
    main()
