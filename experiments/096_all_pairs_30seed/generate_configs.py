"""096 — All-pairs mechanism interaction matrix (Pareto-impossibility evidence).

The single biggest reviewer attack predictable from 090: "you only tried
5 hand-picked pairs; maybe a better pair exists." 096 answers by
enumerating ALL non-redundant pairs over the 8 best base mechanisms.

Base mechanisms (each at the headline strength from 089 attribution):
  zumdn  — zumbach_dn_s10 (089 SOTA single, mean 5.12)
  b3     — b3_k3                (Branch F stable winner)
  asym   — asymdrag_a06         (Branch D best)
  ar1c   — ar1_s05 + clip=1.0   (newly stable per 090b clip knob)
  levy   — levy_a17
  memk   — memk_l095_s10
  pl     — powerlaw_a15
  ms     — microstructure_r03   (weakest of 089 but included for completeness)

C(8,2) = 28 pairs. Already covered (in 090 + 090c, skip in 096):
  zumdn × b3       (090: pair_zumdn_b3)
  zumdn × asym     (090: pair_zumdn_asym)
  zumdn × ar1c     (090c: pair_ar1clip05_zumdn)
  ar1c  × b3       (090c: pair_ar1clip05_b3 — partial; 090 has pair_ar1_b3 no clip)
  ar1c  × asym     (090: pair_ar1_asym no clip — re-run with clip in 096)
  asym  × b3       (090: pair_AB_reref)

So 28 - 5 = 23 new pairs × 30 seeds = 690 cfg ≈ ~12h H20.

Note we exclude `inner_3` and `jump_l01` from the all-pairs enumeration
because both had ≥9/50 rejection rates in 089 (numerically unstable as
solos); pairing them would inflate the rej count further. We document
the exclusion explicitly in the paper.

Output: 8×8 mechanism-pair-mean heatmap → §5 Figure 2 (Pareto envelope).
"""

from __future__ import annotations

import copy
from pathlib import Path
from itertools import combinations

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BASE_SPX = REPO / "experiments" / "069_gamma_damping_30seed" / "config_T05_g10_seed0.yaml"
OUT = REPO / "experiments" / "096_all_pairs_30seed"
OUT.mkdir(parents=True, exist_ok=True)


# Base mechanisms — (short_tag, apply_fn) pairs
def apply_levy(cfg):
    cfg["simulator"]["noise_dist"] = "levy"
    cfg["simulator"]["noise_levy_alpha"] = 1.7
    cfg["simulator"]["noise_levy_clip"] = 50.0


def apply_asym(cfg):
    cfg["simulator"]["asym_drag_alpha"] = 0.6


def apply_memk(cfg):
    cfg["simulator"]["memory_kernel_lambda"] = 0.95
    cfg["simulator"]["memory_kernel_strength"] = 1.0


def apply_pl(cfg):
    cfg["simulator"]["power_law_external"] = True
    cfg["simulator"]["power_law_alpha"] = 1.5
    cfg["simulator"]["power_law_w_pow"] = 0.5
    cfg["simulator"]["power_law_w_mlp"] = 1.0


def apply_b3(cfg):
    cfg["simulator"]["regime_enabled"] = True
    cfg["simulator"]["regime_discrete_enabled"] = True
    cfg["simulator"]["regime_n_states"] = 3
    cfg["simulator"]["regime_gumbel_tau"] = 1.0


def apply_ms(cfg):
    cfg["simulator"]["microstructure_rho"] = 0.3


def apply_ar1c(cfg):
    cfg["simulator"]["ar1_whiten_lambda"] = 0.9
    cfg["simulator"]["ar1_whiten_strength"] = 0.5
    cfg["simulator"]["ar1_whiten_clip"] = 1.0


def apply_zumdn(cfg):
    cfg["simulator"]["zumbach_feedback_lambda"] = 0.95
    cfg["simulator"]["zumbach_feedback_strength"] = 1.0
    cfg["simulator"]["zumbach_feedback_mode"] = "downside"


BASE_MECHS = [
    ("zumdn", apply_zumdn),
    ("b3",    apply_b3),
    ("asym",  apply_asym),
    ("ar1c",  apply_ar1c),
    ("levy",  apply_levy),
    ("memk",  apply_memk),
    ("pl",    apply_pl),
    ("ms",    apply_ms),
]

# Pairs already covered in 090 / 090c — skip
ALREADY_COVERED = {
    frozenset(["zumdn", "b3"]),
    frozenset(["zumdn", "asym"]),
    frozenset(["zumdn", "ar1c"]),     # 090c pair_ar1clip05_zumdn
    frozenset(["ar1c", "b3"]),        # 090c pair_ar1clip05_b3
    frozenset(["ar1c", "asym"]),      # 090 pair_ar1_asym (no clip) — re-run is fine
    frozenset(["asym", "b3"]),        # 090 pair_AB_reref
}
# Reconsider: ar1c × asym in 090 is no-clip; we DO want clip variant in 096.
# So remove it from ALREADY_COVERED so it's regenerated here.
ALREADY_COVERED.discard(frozenset(["ar1c", "asym"]))


def main() -> None:
    base_spx = yaml.safe_load(BASE_SPX.read_text())
    n = 0
    n_cells = 0
    for (tag1, fn1), (tag2, fn2) in combinations(BASE_MECHS, 2):
        key = frozenset([tag1, tag2])
        if key in ALREADY_COVERED:
            continue
        # Canonical lex order in tag (zumdn comes before b3 because z>b but
        # we use the constructor order which already prioritises zumdn)
        tag = f"pair_{tag1}_{tag2}"
        n_cells += 1
        for seed in range(30):
            cfg = copy.deepcopy(base_spx)
            fn1(cfg)
            fn2(cfg)
            cfg["training"]["seed"] = seed
            (OUT / f"config_{tag}_seed{seed}.yaml").write_text(yaml.safe_dump(cfg))
            n += 1
    print(f"wrote {n} configs across {n_cells} pairs to {OUT}")


if __name__ == "__main__":
    main()
