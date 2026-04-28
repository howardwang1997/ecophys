# PLAN — Tier 4.2: Gated Stochastic Pairwise (dynamic graph)

**Date**: 2026-04-29
**Branch**: extend `feature/megnet-global-state` in place
(commits land on top of Tier 4.1's `9a41983 + …`).

## Why this tier

The orthogonal-basin ceiling has a **topology** explanation that
Tier 4.1's u doesn't fully address:

- `autocorr_returns ≈ 0` ⟹ ergodic mixing, many independent paths
- `zumbach_asymmetry > 0` ⟹ time-asymmetric edges
- `hill_tail_index` ⟹ occasional concentration / cascade events
- `volume_volatility_corr` ⟹ edges weighted by trading-volume proxy

Different facts live in different graphs. All current pairwise kinds
(SPS uniform random, MACE-lite Euclidean k-NN, ISAB) use a **fixed
sampling distribution** independent of (s_t, u_t). One model cannot
flip between topologies without retraining → the same orthogonal-basin
mechanism we see in fact coverage.

**Hypothesis**: a learnable, soft, regime-conditioned edge weight
``w_ij = σ(g(s_i, s_j, u))`` lets one network express different active
topologies at different times. Combined with Tier 4.1 u, this is a
**state-conditional dynamic graph**.

## Why **soft gating** specifically

| approach | differentiable | gradient quality | implementation cost |
|---|:-:|:-:|:-:|
| **Soft gate** (this plan) | ✓ | clean (sigmoid) | low (~80 LOC) |
| Top-k routing (Switch) | ✗ → STE | high variance, compounds in physics | medium |
| Discrete Gumbel sampling | ✓ (relaxed) | tricky temperature schedule | medium |
| Hard k-NN by learned metric | ✗ | needs soft top-k | medium |
| Persistent edges + gating | ✓ | clean | high (per-edge state through Sprint 2) |

Soft gating is the lowest-risk first step that exposes the topology
axis. Discrete sparsification (compute savings) is a follow-on if the
soft version proves the mechanism works.

## Implementation

### Files

**Edit (one file only)**:
- `ecomd/models/potentials.py` — extend `StochasticPairwisePotential`
  with `edge_gating: bool` + small gate MLP.

**Edit (config plumbing)**:
- `ecomd/models/ecomd.py` — add 3 config flags + pass through to
  `StochasticPairwisePotential`.

**New tests**:
- `tests/test_dynamic_graph.py` — ~120 LOC; default-off equivalence,
  forward+backward under both BPTT paths, gate-rescale preserves
  unbiasedness at init, composability with Tier 4.1 u.

**New experiments**:
- `experiments/047_arch_tier_4_2_dyngraph/` — 2 cells × 10 seeds
  - `t42_dyngraph` — gating on, no Tier 4.1 (gate sees s_i, s_j only)
  - `t42_dyngraph_with_u` — gating on, Tier 4.1 u also enabled (gate
    sees u; pair kernel also sees u). The "full thing".
- `experiments/048_arch_dyngraph_pairs/` — 3 hand-picked combos × 5 seeds
  - `4_2 + 1_1` (memory + dynamic graph)
  - `4_2 + 4_1` redundant with 047 cell 2; **drop**
  - `4_2 + 2_1` (jumps + dynamic graph — does selective topology help heavy tails?)
  - `4_2 + 1_3` (extra pair features + dynamic graph)

  Total: 3 × 5 = 15 configs.

### `EcoMDConfig` additions

```python
# Tier 4.2 — dynamic graph via learned soft edge gating on the SPS pool.
#   When enabled, each random edge (i, j) is weighted by
#   ``w_ij = σ(gate_mlp(s_i, s_j, u_global))`` and rescaled so the
#   estimator stays unbiased at init (mean(w) ≈ gate_init_p).
edge_gating_enabled: bool = False
edge_gating_init_p: float = 0.7      # initial open probability
edge_gating_input_u: bool = True     # if True and global_state_enabled, gate sees u
```

### `StochasticPairwisePotential` patch

```python
def __init__(self, ..., edge_gating=False, gate_init_p=0.7, gate_input_u=True):
    ...
    self.edge_gating = edge_gating
    self.gate_init_p = float(gate_init_p)
    self.gate_input_u = bool(gate_input_u)
    if edge_gating:
        # gate input: [s_i, s_j, |Δs|] (always) + u (when gate_input_u and d_global_in>0)
        gate_in_dim = 3 * d
        if self.gate_input_u and self.d_global_in > 0:
            gate_in_dim += self.d_global_in
        self.gate_mlp = nn.Sequential(
            nn.Linear(gate_in_dim, hidden),
            nn.SiLU(),
            nn.Linear(hidden, 1),
        )
        # init MLP near zero, then bias the OUTPUT layer so initial
        # σ(b) = gate_init_p → flag-on is approximately baseline at step 0.
        for m in self.gate_mlp.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight, gain=0.1)
                nn.init.zeros_(m.bias)
        # logit(p) = log(p / (1-p))
        from math import log
        b0 = log(gate_init_p / (1.0 - gate_init_p))
        self.gate_mlp[-1].bias.data.fill_(b0)
```

In `forward()`, after computing `phi = self._eval_kernel(...)`:

```python
if self.edge_gating:
    gate_inp = torch.cat([s_i, s_j, (s_i - s_j).abs()], dim=-1)
    if self.gate_input_u and self.d_global_in > 0 and u is not None:
        gate_inp = torch.cat([gate_inp, u.unsqueeze(0).expand(E, -1)], dim=-1)
    w = torch.sigmoid(self.gate_mlp(gate_inp)).squeeze(-1)         # (E,)
    # Rescale so E[w·phi] ≈ E[phi] at init (gate_init_p multiplier).
    phi = phi * w / self.gate_init_p
return scale * phi.sum()
```

**No change to ConservativePotential, conservative_forces, or
bptt_step_function** — the gate adds learnable params that are
already covered by `sim.parameters()` threading via Tier 4.1's
infrastructure.

## Risks + mitigations

| Risk | Mitigation |
|---|---|
| Gate collapses to all-0 (no edges) | Init bias = logit(0.7) → starts mostly open. If we see collapse in early experiments, add `-λ · H(w)` entropy regularizer (~10 LOC in `ecomd/training/losses.py`). |
| Gate collapses to all-1 (no selectivity) | Acceptable null — model just ignores the gate; falls back to baseline. |
| Sigmoid saturates → vanishing gradients | Init MLP weights at gain=0.1 so |output| ≪ 1 initially → σ stays in linear regime. |
| Variance inflation in V (random gates × random edges) | Increase k_random from 50 → 80 in experiments **only if** we see noisy training curves. First runs use k=50 to keep the experiment comparable to baseline. |
| Sprint 2 BPTT breaks | The gate adds only a feed-forward MLP — no new state to thread. Sprint 2 already covers all `sim.parameters()` automatically. |

## Tests

`tests/test_dynamic_graph.py` (~120 LOC):

1. `test_default_off_equivalence` — `edge_gating=False` → output bit-identical to
   pre-Tier-4.2 baseline.
2. `test_init_close_to_baseline` — flag-on at gate_init_p=0.7, with frozen
   weights, V differs from gate-off by < 5% (rescale factor 1/0.7
   compensates the σ ≈ 0.7 mean).
3. `test_forward_backward_default_bptt` — flag-on, default BPTT path,
   finite loss + gradient flowing into gate_mlp params.
4. `test_forward_backward_sprint2` — same under `bptt_custom_function=True`.
5. `test_composes_with_tier_4_1` — `edge_gating_enabled=True +
   global_state_enabled=True + edge_gating_input_u=True` works end-to-end.
6. `test_gate_input_u_false_flag` — flag-on, but gate ignores u even when u is
   present. Useful for ablation.

## Experiment plan

```
experiments/047_arch_tier_4_2_dyngraph/        # 20 configs (2 cells × 10 seeds)
experiments/048_arch_dyngraph_pairs/           # 15 configs (3 cells × 5 seeds)
```

Add `_arch_base.py` overrides:

```python
"tier_4_2_dyngraph_no_u": {
    "simulator": {
        "edge_gating_enabled": True,
        "edge_gating_init_p": 0.7,
        "edge_gating_input_u": False,
    },
},
"tier_4_2_dyngraph": {
    # The "full thing": gate sees u; u also feeds pair via Tier 4.1.
    "simulator": {
        "edge_gating_enabled": True,
        "edge_gating_init_p": 0.7,
        "edge_gating_input_u": True,
        "global_state_enabled": True,
        "global_state_d": 16,
        "global_state_into_pair": True,
    },
},
```

Pair combos (`048`):
- `p_4_2__1_1` — dynamic graph + per-agent memory
- `p_4_2__2_1` — dynamic graph + jumps
- `p_4_2__1_3` — dynamic graph + extra pair features

Add to `scripts/h20_arch_overnight.sh` DIRS list, between 045 and 044
(stack):

```bash
"experiments/047_arch_tier_4_2_dyngraph"
"experiments/048_arch_dyngraph_pairs"
```

Total H20 batch: 135 → **170 configs**.

## Time estimate (Mac)

| Task | Time |
|---|---|
| `StochasticPairwisePotential` patch | 30 min |
| Config flags + constructor wiring | 10 min |
| `tests/test_dynamic_graph.py` | 30 min |
| Generators + 35 configs (047 + 048) | 20 min |
| Master launcher + dry-run check | 5 min |
| Mac smoke (forward+backward + 1 mini-train) | 15 min |
| Commit + push | 10 min |
| **Total** | **~2h** |

## Decision criteria (next morning, after H20 batch)

For Tier 4.2 from the per-tier analysis:

- **mean ≥ 5.0 AND CI-low ≥ 4.0** → dynamic graph breaks the basin
  ceiling. Add entropy regularizer + temperature anneal in next sprint
  to push further.
- **3.5 ≤ mean < 5.0** → mild improvement. Pair with Tier 4.1 (u) cell
  in 047 to see if the combined gain is real.
- **mean < 3.5 AND no_u cell ≥ full cell** → gate is null without u
  context (i.e., the gate is just adding noise). Conclude: u alone
  was the active ingredient; topology dynamics didn't matter.
- **mean < 3.5 AND no_u cell ≈ full cell** → gate collapsed or vanished.
  Add entropy regularizer next sprint.

Cross-reference with `scripts/perfact_analysis.py` to see whether the
gated runs cover **different** facts than the ungated runs (would
confirm topology shifts the basin).

## Out of scope (next sprint if 4.2 wins)

- Discrete top-k routing (Switch-style) for compute savings
- Per-edge persistent state (edges that "remember" being active)
- Learned soft k-NN (replace random sampling with feature-distance bias)
- Hierarchical clustering with learnable cluster assignment

These are bigger architectural shifts. Soft gating tells us if the
dynamic-graph axis matters at all; if it does, these are the obvious
next levers.

## Verification before push

1. `pytest tests/test_dynamic_graph.py tests/test_global_state.py
   tests/test_arch_extensions.py` — all green.
2. Default-off equivalence — `edge_gating_enabled=False` flag run
   produces identical `log_returns` sum as the pre-4.2 commit.
3. End-to-end mini-train (Mac, N=80, 3 iters, Tier 4.2 + Tier 4.1
   both on) → finite loss, gradient flows into gate_mlp params,
   `training_log.json` written.
4. 35 new configs parse cleanly via `EcoMDConfig + LossWeights`.
5. `bash scripts/h20_arch_overnight.sh --dry-run` lists 170 configs.

## Branch + push

```bash
git checkout feature/megnet-global-state
# (work)
git commit -m "Tier 4.2: Gated SPS dynamic graph + 35 H20 configs"
git push
```

Stays on `feature/megnet-global-state` — Tier 4.1 + 4.2 ship as one
overnight batch under one branch. If 4.2 turns out to be a no-op we
still keep it behind a flag (default off), so no clean-up needed.
