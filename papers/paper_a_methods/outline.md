# Paper A — EcoMD: A Differentiable Equivariant GNN for Financial Markets

**Working title** (revised 2026-04-25): *EcoMD: A Differentiable Typed Pair Potential for Financial Market Simulation, with a Quantitative Survey of Failed Microstructure-Inspired Symmetries*

**Earlier title (NOT used)**: "Equivariant Graph Neural Network ... Derived from Microstructure Symmetries"
**Why dropped**: a careful reading of v2.1 — the only working architecture
in our family — shows it carries only permutation-within-type
equivariance, which is **strictly weaker** than the full permutation
equivariance v0.x already has from any pair-sum. None of the additional
microstructure-derived symmetries we tried (Ilinski log-price gauge,
Kyle global mean-field potential, MACE-style SE(3) tensor products)
survive ablation. Calling v2.1 "equivariant" beyond v0.x is dishonest.

**Target venue (primary)**: ICAIF 2026 (Aug deadline) — realistic 65-85% accept
**Stretch target**: NeurIPS 2027 Main / ICLR 2027 Main if narrative tightens
**arXiv preprint**: aim Wk 28 (M3 milestone in plan_v3)

---

## Top-line claim (revised honest version)

We present **EcoMD**, a differentiable particle-based market simulator
trainable end-to-end via moment matching on Cont (2001) stylized facts.
The architecture is a **typed pair potential**: pair-MLP over per-agent
state plus a learnable K×K coupling matrix between persistent agent
type labels (Lux-Marchesi 1999 instantiation), combined with Hawkes
self-excitation in price formation.

We further perform an unusually thorough **architectural survey of
microstructure-theory-inspired symmetries** as inductive biases. Of six
symmetries we tried (SE(3) equivariance, Ilinski log-price gauge, Kyle
global mean-field, body-order ≥ 3 tensor products, full permutation,
T = identity initialization), **five fail under ablation** and the
sixth (permutation-within-type) is a strict weakening of permutation
equivariance that v0.x already has. We document each failure mode
quantitatively: force-magnitude probes (figure 1), ACF decay shape
(figure 2), and 41 stylized-fact runs (table 3).

The minimal architecture that matches v0.x baseline 7/11 stylized
facts on SPX daily *and* extends naturally to typed agent populations
(Paper B's universality target) is the typed pair potential of v2.1.

## What we are NOT claiming (negative space, important)

- We are **not** claiming a novel equivariant GNN. v2.1's equivariance
  group (permutation-within-type) is strictly smaller than v0.x's
  (full permutation). Adding type labels *breaks* a symmetry, not
  adds one.
- We are **not** claiming microstructure theory uniquely determines
  the architecture. Five of six theory-derived symmetries hurt.
- We are **not** claiming Ilinski gauge applies to particle market
  simulators (it does not — agent positions are not log-prices).
- We are **not** claiming the materials-physics GNN literature
  (MACE / NequIP / TorchMD-Net) transfers to markets (it does not —
  documented quantitatively in §4).

---

## Section structure

### 1. Introduction (~1 page)

- Market simulation as a generative modeling problem.
- Why differentiable: gradient calibration is sample-efficient (80 iter)
  vs Simulation-Based Inference (10⁴+ rollouts in ABIDES literature).
- Why GNN: agents = particles, pair interactions = market microstructure.
- Why our specific GNN: market has its own symmetry group, distinct from SE(3).
- Three contributions:
    1. **EcoMD v2.1 architecture** with persistent type embedding + learnable
       K×K coupling matrix (Lux-Marchesi 1999 NN-ization)
    2. **Quantitative ablation of 4 architectures**: shows 33+8 configs needed
       to find what works; 5 negative results documented as findings
    3. **Cross-asset universality**: same training recipe transfers daily
       equity ↔ minute crypto

### 2. Related work (~0.75 page)

- Market simulators: ABIDES (Byrd 2020), ABIDES-Gym (Amrouni 2021)
- Differentiable ABMs: GradABM (Chopra 2022 AAMAS), Andelfinger SIGSIM 2021,
  Dyer ICAIF 2023, JAX-LOB (Frey ICAIF 2023)
- Generative time-series: TimeGAN (Yoon 2019), QuantGAN (Wiese 2020),
  Cont-Cucuringu LOB GAN 2023
- Materials GNNs as templates: MACE (Batatia NeurIPS 2022), TorchMD-Net
  (Thölke NeurIPS 2022) — we explicitly compare and show why they fail
  on markets
- Microstructure theory: Kyle 1985, Glosten-Milgrom 1985, Lux-Marchesi 1999,
  Cont-Bouchaud 2000, Bornholdt 2001, Hawkes 1971 / Bacry-Muzy 2015

### 3. Method: EcoMD architecture (~2 pages)

#### 3.1 Agent dynamics

Overdamped Langevin in latent feature space:
$$
s_i(t+\\Delta t) = s_i(t) - \\Delta t \\cdot \\gamma \\cdot \\nabla_{s_i} V_\\theta(s) + \\sqrt{2\\gamma T \\Delta t} \\, \\xi_i
$$
with γ, T learnable; ξ ~ Student-t(ν=5) for fat tails.

#### 3.2 Price formation

ExcessDemandPrice (Lux-Marchesi-style market maker) with optional
Hawkes self-excitation memory.

#### 3.3 Pair potential — v2.1 design (the "winning" architecture)

Derived from market symmetries:
- **Permutation-within-type** (Lux-Marchesi 1999): agents have persistent
  type labels τ_i ∈ {0,...,K-1}; pair kernel allowed to differ across types.
- **Pair-sum structure** (Kyle 1985 microstructure): V = Σ_pairs φ, NOT per-node
  readout (negative result vs MACE).
- **Hawkes self-excitation** for vol clustering (Bacry-Muzy 2015).

Formula:
$$
V_{\\text{rel}}(s, \\tau) = \\frac{N-1}{2k} \\sum_{(i,j) \\in E_{\\text{rand}}}
T_\\theta[\\tau_i, \\tau_j] \\cdot \\phi_\\theta(s_i, s_j, |\\Delta s|, e_{\\tau_i}, e_{\\tau_j})
$$

with random k-pair sampling for unbiased estimation at large N (v0.9 SPS),
**T initialized to all-ones** (critical, see ablation).

#### 3.4 Training recipe

- Persistent state across iterations + warmup detach
- Truncated BPTT with chunk_steps=32
- Cosine LR schedule
- Loss: Σ |stylized_fact - target| with optional ACF-shape penalty

### 4. Negative results from architecture exploration (~1.5 pages)

#### 4.1 v1 MACE-lite: SE(3)-equivariant GNN does not transfer

5 ablation variants (k-NN graph, body-order 2/3/4, LayerNorm).
**Result**: 0–4/11 stylized facts. Force magnitude 60-190× weaker than
v0.x baseline (figure: force_magnitude_table).

**Diagnosis**: per-node readout sum is O(N) vs pair-sum O(N²); markets
need pair-wise Kyle-style coupling. MACE's body-order tensor products
don't help — they SMOOTH dynamics rather than create burst-decay.

#### 4.2 v2.0 with Ilinski gauge invariance: 33 configs all stuck at 4/11

Tested phi_init_gain × kyle_λ × shape_loss × Kyle on/off × gauge × k.

**Diagnosis 1** (gauge): Ilinski (2001) gauge theory of finance applies
to log-prices. Our agent state s[0] is *position* (inventory), not
log-price. Position has absolute meaning (inventory risk). Forcing
gauge invariance discards information needed for vol clustering.

**Diagnosis 2** (T initialization): Default T = I + 0.1·randn kept only
diagonal entries near 1 (intra-type coupling); inter-type entries near 0.1.
At K=4 types randomly assigned, P(τ_i=τ_j) = 25%, so 75% of pair forces
were 10× damped. T=ones recovers full coupling.

#### 4.3 Force-magnitude analysis (figure 1)

Quantitative table showing |F|/σ ratio at init across all architectures:
- v0.x baseline: 26× (trains)
- v1 MACE default: 1.2× (drowned)
- v2.0 default: 1.5× (drowned)
- v2.0 phi=3.0: 1400× (clip-saturated)
- **v2.1: 183× (Goldilocks)**

### 5. Results (~2 pages)

#### 5.1 Stylized facts on SPX daily (Mac, N=200)

Scoreboard: GARCH 7/11, LM99 5/11, v0.6 6/11, v0.8 7/11, v0.9 SPS pending,
v1 MACE 0-4/11, v2.0 4/11, **v2.1 7/11 (with shape loss)**.

#### 5.2 Cross-asset universality (BTC 1m + ETH 1m)

Same recipe → 7/11 on BTC 1m for v0.6 (already shown in experiments/012).
Pending: v2.1 cross-asset replication.

#### 5.3 Scaling: H20 N=10⁴

v0.9 SPS production run + v2.1 H20 ablation grid. Pending H20 results.

#### 5.4 Ablations

- Architecture: v0.x / v0.9 / v1 / v2.0 / v2.1 (table 4.1)
- Training recipe: noise_dist (normal vs t), persistent_state, learnable_β,
  chunk_steps × warmup_steps (Mac data already collected)

#### 5.5 Out-of-sample crash validation

Train SPX 2015-2019, eval 2020 H1 crash window (experiments/015 pending H20).

### 6. Discussion (~0.75 page)

- What worked: persistent type embedding + uniform initial coupling +
  Hawkes + Student-t.
- What didn't: SE(3) equivariance, log-price gauge, body-order ≥ 3, Kyle global
  potential. Each documented with quantitative diagnosis.
- Limitation: tested at N=200-10⁴; aspirational N=10⁵ requires further work.
- Reproducibility: full code + grids + 100+ result JSONs at github.com/...

### 7. Future work

- Paper B: T_eff and entropy production using EcoMD as measurement tool.
- Larger N via tensor-parallel.
- Sparse-attention pair selection (vs random SPS).

---

## Figures (planned)

1. **Force magnitude ratio across architectures** — `experiments/018_force_probe/`
2. **ACF(r²) decay shape across architectures** — `experiments/019_acf_shape/`
3. **Stylized facts scoreboard matrix** — heatmap of 11 facts × N architectures
4. **Cross-asset universality** — radar charts SPX/BTC × architectures
5. **Training dynamics**: loss + grad norm + acf_sim trajectories
6. **Sweet-spot diagram**: |F|/σ ratio vs passing count (scatter)

## Tables (planned)

1. **Architecture lineage and which symmetries each enforces**
2. **Hyperparameter sweet spots from ablation**
3. **Stylized facts per architecture, full 11 columns**
4. **Failure modes of attempted architectures + diagnosis**

## Status as of 2026-04-25

| Section | Data ready? | Draft? |
|---|---|---|
| 1. Introduction | – | ✗ |
| 2. Related work | partial (in plan + memory) | ✗ |
| 3. Method | ✓ (code + Section 9 of plan_v3) | ✗ |
| 4.1 v1 MACE failure | ✓ (experiments 008, 009, 018) | ✗ |
| 4.2 v2.0 stuck | ✓ (experiments 017) | ✗ |
| 4.3 Force probe | ✓ (experiments 018 force_magnitude_table.md) | ✗ |
| 5.1 SPX stylized facts | ✓ (experiments 011, 017) | ✗ |
| 5.2 Cross-asset | partial (v0.6/v0.8 done, v2.1 pending) | ✗ |
| 5.3 H20 scaling | pending H20 runs | ✗ |
| 5.4 Ablations | ✓ (experiments 003-008, 011, 012, 017) | ✗ |
| 5.5 OOS crash | code ready, awaiting H20 | ✗ |
| 6. Discussion | ✓ (logs/2026-04-{24,25}.md, plan §9) | ✗ |
| Fig 1 force | ✓ (experiments 018) | ✗ |
| Fig 2 ACF shape | ✓ (experiments 019) | ✗ |
| Fig 3 scoreboard | half (need to render) | ✗ |
| Fig 4 cross-asset | half | ✗ |
