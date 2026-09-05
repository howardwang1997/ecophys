# Family C results: 2D U-Net — the parameterization effect inverts under contractive dynamics

Date: 2026-08-29

Status: **confirmatory outcome under the D0 freeze; 2 jobs (ad2d × σ_f ∈ {1.0, 0.1}),
channels {16,32} × epochs {400,800}, 5 seeds; pulled and pre-adjudicated automatically by the
local watcher. The result contradicts the toy/A/B attribution pattern and therefore triggers
the freeze-and-review clause of the D0; the review (mechanism test below) is recorded as an
exploratory branch under the same freeze.**

## Frozen-rule outcomes (best free_res cell; the inversion is visible at every cell)

| Probe | free | free_res | hard | attribution ratio | decoupling |
|---|---:|---:|---:|---:|---:|
| ood_flat@1.0 | **0.389±0.042** | 1.780±0.152 | 1.862±0.154 | 17× (inverted) | exact 0.00% |
| ood_flat@0.1 | **0.404±0.034** | 1.777±0.159 | 1.861±0.168 | 16× (inverted) | exact |
| ood_rich@1.0 | **0.247±0.059** | 1.559±0.159 | 1.828±0.158 | 5× (inverted) | exact |
| ood_mass | no separation (seed sd ±1.6–2.9 across arms) | | | ratio ≈ 0 | exact |

**The residual parameterization — the winner in families A, B, M — is 4.6× worse here; the
hard constraint tracks its residual family (hard ≡ free_res), and post-hoc projection remains
exactly decoupled.** Laundering: soft@30 inflates (+15%) without drift benefit (dominated,
as in A/B).

## Review finding (freeze-and-review clause): contraction predicts the sign

The 2D advection–diffusion operator at the frozen parameters is **strongly contractive**
(high-wavenumber modes decay by e^{−40} in one step): the true one-step map is far from the
identity. Mechanism: a residual head must represent `−(I−K)u` — cancelling most of the input —
and its off-support extrapolation is poor when `K` is contractive; an absolute head directly
represents the smooth `Ku`. In near-identity families (A: dt=0.1 mild PDE steps; B: same at
n=128; M: per-step trades change agent state marginally) the residual form wins for the
symmetric reason. **The constraint's verdict is sign-invariant: hard ≡ free_res in every
family and every direction.**

## Boundary prediction (exploratory mechanism test, authorized as the D0 review branch)

Vary family-A diffusion from near-identity to contractive via `ν ∈ {0.02 (frozen baseline),
2.0}`: the parameterization winner must flip from free_res to free. Runs are launched on the
idle V100 pool as explicitly-exploratory cells; they do not enter the confirmatory tables.

## Revised cross-family scoreboard

| Family | Attribution | Winner | Laundering | Decoupling |
|---|---|---|---|---|
| A (MLP, 3 PDE, near-identity) | PASS 6/6 | free_res (260–5225×) | 2/6; dominated | exact |
| B (1D U-Net, near-identity) | PASS 18/18 | free_res (12.7–6710×) | fail; dominated | exact |
| C (2D U-Net, contractive) | **inverted** | **free (4.6–6.3×)** | fail; dominated | exact |
| M (CDA market, near-identity) | PASS | free_res (140×) | **PASS (4.7×)** | exact |
