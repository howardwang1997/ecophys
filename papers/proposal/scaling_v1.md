# EcoMD Scaling Design v1 — Stochastic Pair Sampling for N ≥ 10⁴
**2026-04-24 evening, post-M2**

## Context

After M2 gate pass (v0.8 = 7/11 SPX daily, v0.6 = 7/11 BTC 1m), Paper A's main
weakness is **scale**: N=200 agents is "toy" by ABM standards (ABIDES runs
N=10⁴, LM99 typically N=10³). We tried v1 MACE-lite (k-NN sparse + body-order
2/3/4) to reach N=10⁴–10⁵ but it failed on vol clustering due to two
architectural properties:
1. **Biased sparsity**: k-NN locality loses long-range pair signal
2. **Per-node readout**: MLP on aggregated features smooths dynamics into
   steady-state regimes (no burst-and-decay)

We now propose a scaling path that **keeps v0.x's pair-sum physics** while
reducing memory cost by a factor ~100×: **stochastic pair sampling**.

This doc specifies the architecture, training protocol, expected memory /
wall-clock, and risks. Target: land at N=10⁴ on 4-card H20 within 1 week
of implementation.

## Design

### 1. Stochastic pair sampling (SPS)

Current v0.x `PairwisePotential`:
```
V(s) = Σ_{i<j} φ_θ(s_i, s_j)       # O(N²) pairs, complete graph
```

Proposed v0.9 `StochasticPairwisePotential`:
```
For each forward pass:
    For each agent i:
        Sample k indices J_i = {j_1, ..., j_k} uniformly from {0..N-1} \ {i}
    Build edge list E = { (i, j) : i ∈ [N], j ∈ J_i }           # |E| = N·k
    Compute:
        V_stoch(s) = (N-1)/(2k) · Σ_{(i,j) ∈ E} φ_θ(s_i, s_j)
```

**Properties**:
- `E[V_stoch] = V_full` (unbiased) — the scale (N-1)/(2k) corrects for the
  fraction of pairs sampled. Factor 1/2 accounts for (i,j) vs (j,i) redundancy.
- `Var[V_stoch] ∝ (P - E)/E · Var[φ]` where P = N(N-1)/2, E = N·k. At
  N=10⁴, k=50, P/E = 100 → std-to-signal ratio ~10%, comparable to minibatch
  SGD noise.
- Gradient `∇V_stoch` is an unbiased estimator of `∇V_full`, so training is
  stochastic-gradient MD — a direct analogue of SGD for particle systems.
- At **inference** (Paper A reported stylized facts), we can use **full pairs**
  for deterministic behavior. Training stochasticity costs nothing at eval.

### 2. Why this beats MACE-lite k-NN

| Property | v1 MACE-lite k-NN | v0.9 Stochastic pair |
|---|---|---|
| Sparsity source | structural (locality) | random |
| Force bias | **biased** (short-range only) | **unbiased** |
| Pair-sum scale | O(N·k) only | preserves O(N²) via (N-1)/k rescaling |
| Per-node readout | yes (smooths dynamics) | no (keeps φ(s_i, s_j) directly) |
| Preserves v0.x physics | no | **yes** |
| Training dynamics | steady-state attractor | burst-and-decay preserved |

The key is: we do NOT change the physics, only the Monte-Carlo estimator of
the force integral. Every analysis that works for v0.x transfers: convergence
properties, interpretability, paper B's T_eff derivation.

### 3. Memory and wall-clock estimates

For an H20 card (96 GB HBM), running `PairwisePotential` on CPU-tiled MLP:

**Per-step forward memory** (N=10⁴):

| k | Pairs/step | MLP input `(E, 3d)` | Forward activations | BPTT @ chunk=32 |
|---|---|---|---|---|
| 20 | 200K | 77 MB | ~400 MB | ~13 GB |
| 50 | 500K | 192 MB | ~1 GB | ~32 GB |
| 100 | 1M | 384 MB | ~2 GB | ~64 GB |
| 200 | 2M | 768 MB | ~4 GB | >80 GB |

At k=50, chunk=32 → 32 GB fits comfortably on a single H20 card. 4-card DDP
with independent seed rollouts gives effectively 4× seed diversity per iter.

Per-iter wall time (estimate from Mac per-step scaling):
- Current v0.6 at N=200: ~4s/iter (Mac CPU)
- Scaling: step cost ∝ N·k (MLP over E edges)
- v0.9 at N=10⁴, k=50 on H20 GPU: ~0.5-1s/iter expected (rough order-of-magnitude)
- 200 iter training ≈ 2-5 min on H20

### 4. Training protocol

Reuse the v0.6 / v0.8 recipe verbatim:
- `persistent_state: true`
- `warmup_steps: 16`, `chunk_steps: 32` (or 64 if memory allows)
- `noise_dist: t`, `noise_df: 5`
- `grad_clip_max_norm: 100` (H20 diagnostic lesson: clip=1 kills signal at scale)
- `lr: 1e-3` with `lr_warmup_iters: 10` + cosine decay
- Loss: moment matching on (acf_sq, leverage_sum, hill_alpha) + planned
  shape-constraint addition (see §5)

Seeds for random pair sampling should be **resampled every chunk step** (not
every iteration), so that the stochastic gradient has independent noise each
BPTT step. For deterministic ablation we can fix the seed.

### 5. Loss improvements co-shipped with v0.9

Today's v1 H hybrid showed: single-number `acf_sq_mean` target can be
satisfied by a **constant-variance regime** rather than real clustering. To
prevent this Goodhart failure at scale:

**Add shape constraint to ACF loss**:
```
loss_acf_shape = λ · | acf_sim[1] - acf_sim[10] |    # must be a decaying curve
```
(Reference SPX: acf(r²)[1]=0.45, acf(r²)[10]=0.22 — real data has ~half-life
at lag 10. We penalize deviation from this ratio.)

This is a **~5 line addition** to `ecomd/training/losses.py` — add per-lag
ACF computation already used in eval, then penalize the ratio.

### 6. Test plan

**Mac validation (30 min)**:
1. Implement `StochasticPairwisePotential(n_agents, k_random, rescale=True)`
2. Verify: at N=200, k=199 (complete), produces identical V as current
3. Verify: at N=200, k=50, V within 10% of full V on random s (unbiased check)
4. Run v0.6 recipe with StochasticPairwise on SPX → should match v0.6 baseline
   at 6/11 (within realization noise)

**H20 scale-up (1 day)**:
1. N=1000, k=50 → expect matching or better than Mac v0.6
2. N=10000, k=50 → Paper A headline result
3. Compare full-pairs eval at each N to demonstrate scaling preserves physics

**Cross-asset at scale**:
4. Rerun BTC 1m + (potentially) ETH 1m at N=10⁴ — full universality scoreboard

## Risks

**R1: Stochastic gradient noise destabilizes training at large N.**
Mitigation: already have Student-t noise + gradient clipping. If unstable, can
accumulate gradient over 4 stochastic forward passes before step.

**R2: Vol clustering weakens at N=10⁴ due to CLT averaging.**
This is a real physics concern: aggregate demand from 10⁴ agents may be too
Gaussian even with heterogeneous agents. Mitigation: inject extra heterogeneity
via per-agent init_state_scale varied across population (a Beta distribution
over N agents, not a single scalar).

**R3: H20 environment (NCCL broken, gloo slow for >4 cards).**
Known issue from today's diagnostics. Mitigation: stay on 4-card gloo for
v0.9; tackle NCCL ordinal issue separately.

**R4: Paper A reviewers reject "stochastic pair sampling" as mere SGD
rebranding.**
Response: the novelty is applying SGD-style estimation to *particle
interaction sums* (not data batches), and showing it preserves pair-force
statistics that smoother message-passing architectures (MACE) destroy. We
have quantitative evidence (force magnitude, ACF shape) from today's v1
ablation to back this up.

## Milestones

Target delivery (aggressive, 1-2 week horizon):

| Deliverable | Owner | When |
|---|---|---|
| `StochasticPairwisePotential` in `ecomd/models/potentials.py` | code | +1 day |
| Mac verification (N=200 k=50 matches v0.6) | experiments/013 | +1 day |
| H20 N=10000 training w/ v0.6 recipe | scripts/h20_launch_v0p9.sh | +3 days |
| Cross-asset at N=10⁴ (SPX + BTC + ETH) | experiments/014 | +4 days |
| Shape-constraint loss | `training/losses.py` | +5 days |
| N=10⁴ + shape-loss final results | → Paper A Table 1 | +7 days |

## Paper A impact

If v0.9 scaling works at N=10⁴ with ≥7/11 on SPX daily and matches on BTC 1m,
Paper A gets three strong upgrades:

1. **Claim**: "EcoMD scales to N=10⁴ agents on a single H20 GPU, matching the
   state-of-the-art ABIDES sim scale without requiring scripted agent rules."
2. **Distinction from v1 failure**: quantitative comparison of random pair
   sampling (v0.9) vs biased k-NN (v1) — the scaling ablation is itself a
   Paper-A contribution.
3. **Fair comparison possible**: at N=10⁴ we can meaningfully contrast to
   ABIDES, TimeGAN, and other baselines at comparable scale.

This is the missing link between "toy methodology paper" and "credible market
simulator contribution at NeurIPS / ICLR main tracks."
