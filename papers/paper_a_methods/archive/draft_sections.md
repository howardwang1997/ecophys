# Paper A — Section drafts (skeleton, ~3000 words)

Working title: *EcoMD: A Calibrated Differentiable Particle Simulator
for Non-Equilibrium Analysis of Financial Markets*

Target: ICAIF 2026 primary; arXiv preprint Wk 28 stretch goal NeurIPS
2027 / ICLR 2027 if weekend pushes to ≥9/11.

---

## §1 Introduction (target 1 page)

> The non-equilibrium thermodynamics of financial markets is a 25-year-old
> open question. Tóth, Lux & Sornette (2018) derived a Boltzmann equation
> for high-frequency limit-order books; Maskawa (2025) showed an
> empirical integral fluctuation theorem holds for multi-scale realized
> volatility cascades to ~5% accuracy; Bouchaud
> (2001) and Mantegna-Stanley (2000) raised the founding questions on
> universality and critical scaling. Progress on these questions requires
> measurement infrastructure that existing market simulators do not provide.

**Specifically, the next round of physics-of-markets results demand**:

1. **Per-particle entropy production** — needed for σ̇(t) = ⟨F_diss · v⟩/T
   measurements that decompose the non-equilibrium dissipation across
   agent populations. Generative time-series models (TimeGAN, QuantGAN)
   produce return distributions but lack agent-level state.

2. **Gradient-trained calibration** — needed because Jarzynski work
   protocols (Crooks, 1999; Jarzynski, 1997) over event windows like
   FOMC announcements require recalibrating the simulator on tens of
   minutes of data. Simulation-based inference (SBI) on agent-based
   models like ABIDES (Byrd et al., 2020) typically requires 10⁴+
   forward rollouts per recalibration; gradient-based calibration in
   ~10² steps makes event-driven physics protocols feasible.

3. **Microstructure realism** — needed because the thermodynamic
   uncertainty relation (TUR; Barato-Seifert, 2015) requires accurate
   second-moment statistics of order-flow currents, which mean-field
   SDEs cannot capture.

These requirements rule out three classes of existing tools:
agent-based simulators (ABIDES, JAX-LOB) are forward-only or only
gradient-trainable on selected layers; generative models (Cont-Cucuringu
LOB GAN, 2023) lack the agent axis; molecular-dynamics-style learned
potentials in materials science (MACE; Batatia et al., NeurIPS 2022) are
SE(3)-equivariant and don't transfer to markets (we show in §4).

**Our contribution**: **EcoMD**, a differentiable particle-based market
simulator with three properties:

1. **Calibrated**: matches 8/11 Cont (2001) stylized facts under a single
   shared θ trained jointly across SPX daily, BTC and ETH 1-minute returns.
2. **Differentiable**: trained by 200 gradient iterations of moment-matching
   (vs SBI's 10⁴+ rollouts).
3. **Particle-based**: each agent has individual state in a 32-d latent
   space; per-particle force decomposition supports Paper B's entropy
   production analysis.

The simulator combines four ingredients chosen empirically (each ablation
in §4):

- Overdamped Langevin dynamics with Student-t noise (heavy tails)
- Persistent K=4 agent type embedding with per-type γ, T scaling (Lux-Marchesi
  inspired; we call it *two-population Langevin* though K is general)
- Stochastic Pair Sampling (SPS): unbiased random k-pair Monte Carlo for
  O(N²) → O(Nk) potential evaluation
- Hawkes-augmented price formation (Hawkes, 1971; Bacry-Muzy, 2015)

We add an **expanded loss function** that penalises return autocorrelation
and clip pathological tail-index estimates, preventing a Goodhart failure
mode where the simulator over-optimises 3 of 11 facts at the expense of
the other 8.

**Empirically**, the chosen architecture (which we call *C4*) reaches
**8/11 stylized facts on a single θ trained jointly on equity + crypto** at
N=10⁴ agents on H20 hardware. Our exhaustive 23-config + 54-config ablation
demonstrates that this combination is a Pareto compromise: simpler designs
(GARCH baseline, plain Langevin) miss vol clustering; more elaborate
designs (SE(3)-equivariant GNN, log-price gauge invariance, Kyle global
mean-field, multi-scale Hawkes with default hyperparams) cause over-fitting
or training instability.

**Reproducibility**: full code, 80+ trained checkpoints, and the
configuration generator at https://github.com/howardwang1997/ecophys.

---

## §3 Method (target 2 pages)

We describe the C4 architecture, the chosen instantiation after the
ablation studies in §4. The key functional components are:

### §3.1 Agent dynamics — Overdamped Langevin

Each of N agents has state $s_i(t) \in \mathbb{R}^d$ with $d=32$. State
evolves under overdamped Langevin dynamics:
$$
s_i(t+\Delta t) = s_i(t) - \frac{\Delta t}{\gamma_i}\nabla_{s_i} V_\theta(s, h_t) + \sqrt{\frac{2 T_i \Delta t}{\gamma_i}}\, \xi_i(t)
$$
with $\xi_i \sim \mathcal{T}(\nu=5)$ (Student-t, unit variance,
fat-tailed); $\gamma$ and $T$ learnable scalars times per-type
multiplier (described below). The dimension $d=32$ is empirical
(ablation in §4 shows $d=16,64$ negligibly different).

### §3.2 Per-type heterogeneity (K=4 two-population Langevin)

At simulator initialisation, each agent receives a persistent type
label $\tau_i \in \{0,1,2,3\}$ sampled IID uniform with seed 42.
Per-type multipliers scale γ and T:
$$
\gamma_i = \bar{\gamma} \cdot a_{\tau_i}, \qquad T_i = \bar{T} \cdot b_{\tau_i}
$$
with multipliers $a, b$ chosen to span 0.5×–1.5× (Lux-Marchesi 1999
heterogeneous-agent inspired but parametrised differently). The
multipliers are fixed at simulation start; only $\bar{\gamma}, \bar{T}$
are trained. The sampling seed and multiplier values are fixed across
all training runs; ablations (§4) show a 0.9× to 1.1× spread is too
narrow to help while 0.7× to 1.5× spreads divergeunder unmodified
loss but converge under the expanded loss function (§3.5).

### §3.3 Pair potential — Stochastic Pair Sampling MLP

The pair-interaction potential is:
$$
V_\text{pair}(s) = \frac{N-1}{2k} \sum_{(i,j) \in E_t} \phi_\theta(s_i, s_j, |s_i - s_j|)
$$
where $E_t$ is a fresh random sample of $k=50$ partners per agent at
each time step $t$ (sampled without replacement from $\{1, \ldots, N\}
\setminus \{i\}$). The prefactor $(N-1)/(2k)$ is the unbiased estimator
correction so that $\mathbb{E}[V_\text{pair}]$ equals the full
$O(N^2)$ pair sum. This Stochastic Pair Sampling (SPS) reduces
per-step cost from $O(N^2 d)$ to $O(N k d)$, enabling training at
$N=10^4$ on a single H20 within ≈3 minutes.

The MLP $\phi_\theta : \mathbb{R}^{3d} \to \mathbb{R}$ has hidden 48,
SiLU activations, two hidden layers, Xavier-uniform initialisation
with gain 0.5.

### §3.4 Hawkes-augmented price formation

Price evolves under an excess-demand market-maker mechanism (Lux,
Marchesi, 1999) augmented with Hawkes self-excitation (Hawkes, 1971;
Bacry, Muzy, 2015). Let $p_t$ be log-price, $\text{ED}_t = \sum_i
\Delta s_{i,0}(t)$ excess demand from changes in agents' first state
component (interpreted as inventory):
$$
p_{t+1} - p_t = \beta \cdot \text{ED}_t - \tfrac{1}{2}\sigma^2 + \sigma \eta_t + \kappa \cdot M_t \cdot \text{sign}(\beta \text{ED}_t),
$$
where $\eta_t \sim \mathcal{N}(0,1)$ is microstructure noise, and $M_t$
is a Hawkes EMA memory:
$$
M_{t+1} = (1 - \alpha) M_t + \alpha |p_{t+1} - p_t - \kappa M_t \text{sign}(\cdot)|.
$$
Default $\beta = 0.02, \alpha=0.1, \kappa=0.3, \sigma=0.005$. The
Hawkes term provides volatility clustering (Cont, 2001 fact #6) without
discrete jumps, preserving differentiability.

The simulator also exposes optional multi-scale Hawkes (a slower second
EMA with $\alpha_\text{long}=0.005, \kappa_\text{long}$ tunable) and
optional regime-GRU latent state; both are off in the C4 architecture
(ablations in §4 show they cause over-fitting at N=10⁴ unless
hyperparams are very conservative).

### §3.5 Multi-asset joint training

Given a list of assets $\{A_1, \ldots, A_M\}$ each with target moments
$T_m = \{ACF_m, \text{Hill}_m, \text{Lev}_m, \ldots\}$, each training
iteration performs **one** rollout of length chunk_steps=24 from the
shared simulator $\theta$ and computes a weighted-sum loss:
$$
\mathcal{L}(\theta) = \sum_m w_m \cdot \mathcal{L}_m(\theta, T_m), \qquad \sum_m w_m = 1
$$
Each $\mathcal{L}_m$ is the moment-matching loss against asset $m$'s
target. With $M=3$ (SPX + BTC + ETH) and uniform weights, the trained
$\theta$ produces the Pareto-compromise distribution best matching
all three.

### §3.6 Expanded loss function

The 3-moment loss (ACF², leverage, Hill) is augmented with two terms
that prevent Goodhart failure modes:

$$
\mathcal{L} = \mathcal{L}_3 + w_\text{ar} \cdot |\rho_1(r)| + w_\text{hm} \cdot \text{ReLU}(\hat\alpha_\text{Hill} - \alpha_\text{cap})
$$

where $\rho_1(r)$ is lag-1 autocorrelation of raw returns (Cont fact
#1: should be near 0), and $\alpha_\text{cap} = 10$ caps the soft Hill
estimator (preventing tails from collapsing to numerical infinity
during ablation runaway). Coefficients $w_\text{ar}=0.5, w_\text{hm}
=0.3$ in C4. We ablate these in §4.

### §3.7 Training pipeline

200 iterations of Adam at lr=10⁻³ with linear warmup over 10 iterations
and cosine decay. chunk_steps=24, warmup_steps=16 (the first 17
returns are discarded). Persistent simulator state across iterations
detached at iteration boundaries (truncated BPTT). gradient clipping at
norm 100. Single-checkpoint save at training end.

For inference, 4-card data-parallel DDP with gloo backend produces 8
realizations of 4000-step rollouts; stylized facts are computed per
realization and aggregated.

---

## §6 Discussion (target 0.75 page)

### What this paper does (and does not) claim

**Does claim**: a differentiable particle-based market simulator
calibrated via gradient descent in O(10²) iterations to match 8/11
stylized facts under a single shared θ trained jointly on three
markets (S&P 500 daily, BTC/USDT 1-minute, ETH/USDT 1-minute).

**Does not claim**: novelty in the Langevin dynamics, the Hawkes
excitation mechanism, or the Lux-Marchesi-style heterogeneous-agent
formulation. Each is borrowed from prior work; our contribution is the
combination, the gradient-based calibration, the loss-function design
preventing Goodhart, and the empirical demonstration on real
multi-asset data.

### Connection to Paper B (forward-looking)

The simulator's per-particle force decomposition supports Paper B's
non-equilibrium thermodynamic measurements: T_eff(t) =
$\bar\gamma \langle |v|^2\rangle / d$ at each step, σ̇(t) =
$\langle F_\text{diss} \cdot v \rangle / T_\text{eff}$. A pilot
measurement (experiments/024_paper_b_pilot) on the trained C4
checkpoint at N=1000 finds T_eff variation of 0.55% (effectively
constant), suggesting the trained simulator runs near a Langevin
equilibrium. Paper B will accordingly target either a TUR
saturation-rate claim (PRL retreat) or driven-protocol Jarzynski work
identity (Nature Physics flagship), depending on whether driven
protocols at H20 N=10⁴ scale produce visible non-equilibrium structure.

### Limitations

**Particle scale**: tested up to $N=10^4$ on H20 NVLink. Larger scales
($N=10^5$) require tensor-parallelism not yet implemented.

**Data scale**: SPX daily (3024 returns) and BTC/ETH 1-minute (~130k
returns each) cover limited regime variation. Crash-period out-of-sample
validation (2020 H1, 2022 LUNA) is ongoing. High-frequency event-level
data (Path C purchases pending) will support Paper B's TUR analysis.

**Theoretical guarantees**: we do not prove identifiability of the
learned potential, convergence of the gradient calibration, or
approximation properties of the SPS estimator. These are open
problems for follow-up theoretical work.

**Comparison to existing market neural simulators**: a head-to-head
benchmark against Shi et al.'s 2024 Neural Hawkes (claimed 10+ stylized
facts) on the same SPX daily dataset is a direct task for follow-up
(or revision response).

### Negative results documented

§4 records five attempted architectural ideas that were ablated and
discarded: (a) SE(3)-equivariant GNN (MACE-lite), (b) Ilinski log-price
gauge invariance applied to agent state, (c) Kyle global mean-field
$V \propto (\sum \pi_i)^2$, (d) high body-order tensor products,
(e) multi-scale Hawkes at default hyperparams. Each is documented with
quantitative diagnosis. We believe this transparency is more valuable
to the community than concealing the failures.

### Future work (selected)

- Cross-asset universality at 5+ markets (extend joint training to
  DAX, EuroSTOXX, HSI via yfinance).
- Tensor-parallel scaling to $N=10^5$.
- Theoretical analysis of identifiability under SPS.
- Paper B physics protocols (separate paper).
- Crash early-warning system (Paper C, separate paper).
