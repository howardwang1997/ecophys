# Exposure-routing exploratory result

**Analysis commit:** `7b297fd125b6b6590b9a973f2ecc9982b7544853`

**Status:** `POST_HOC_DESCRIPTION_NO_INFERENTIAL_GATE`

**U1R decision:** unchanged; `FAIL_FULL_PREPERIOD_EXPOSURE_SUPPORT_KEEP_UNISWAP_M2_ONLY`

## Concentration geometry

| Measure | Swap | Position actions | Combined |
|---|---:|---:|---:|
| Active pools | 89 | 25 | 91 |
| Active fraction | 0.089 | 0.025 | 0.091 |
| Top-1 share | 0.3010 | 0.2890 | 0.3005 |
| Top-5 share | 0.6039 | 0.7054 | 0.6014 |
| Top-10 share | 0.7303 | 0.8499 | 0.7296 |
| Top-20 share | 0.8852 | 0.9717 | 0.8824 |
| HHI | 0.1207 | 0.1494 | 0.1202 |
| Inverse-HHI effective pools | 8.28 | 6.69 | 8.32 |
| Entropy effective pools | 18.02 | 11.12 | 18.27 |
| Full-population Gini | 0.9843 | 0.9910 | 0.9840 |
| Active-only Gini | 0.8236 | 0.6393 | 0.8244 |
| Total variation from uniform contracts | 0.9382 | 0.9750 | 0.9368 |

The two-stage structure is descriptive but sharp: most contracts have no event in the window, and counts remain
highly unequal after conditioning on activity. A future router should therefore separate support from conditional
intensity instead of predicting one dense weight vector.

## Channel and partition geometry

Swap and position supports intersect on 23 pools. Position support is 92% covered by swap support, but only 25.84%
of swap-active pools have a position action; two pools are position-only. The support Jaccard is 0.2527. Normalized
swap and position weights have total variation 0.4153, normalized Jensen-Shannon divergence 0.2690 and cosine
similarity 0.8397. A shared latent router may be useful, but a single channel-independent exposure measure is not
supported by these counts.

The first 500-pool propagation batch contains 88.29% of swaps and 84.99% of position actions despite containing
half the contracts. Packed fee `0x44` contains 10.7% of pools but 22.98% of swaps and 30.03% of position actions,
representation ratios of 2.15 and 2.81 relative to contract share. These are pre-treatment event-count
associations. Propagation order and fee class may encode selection; neither contrast is causal or representative.

## Identity verification

For an independently generated bounded response vector, the direct difference `E_p[r]-E_u[r]` and
`Cov_u(Np,r)` agreed to `8.05e-16`. The independently recomputed swap HHI, effective count, top-10 share, total
variation, fee total and batch totals exactly reproduce the artifact. For swaps,
`Var_u(Np)=N*HHI-1=119.7107`, and the numerical Cauchy inequality holds.

The very large total variation is a geometric worst-case capacity for uniform-versus-event-weighted aggregation,
not an observed response bias. Its sign and realized size require a response and valid identification, both still
closed.

## Architecture consequence

The smallest model consistent with the evidence has four distinct components:

1. an exact, non-learned mechanism transition at event level;
2. a learned channel-specific support gate;
3. a learned conditional exposure intensity and normalization;
4. participant adaptation/entry-exit dynamics only after the first three are validated.

Fee and propagation order are candidate routing covariates, not causal features. They require a new domain/frame
with outcome-blind controls before model training. This result does not make the exposure router a validated
method and does not meet NMI or NCS evidence requirements.

Artifact SHA-256: `964b809c186894146961f0f2cbc64f8d0e77fdd91eec9cd79edba4b632adf5dc`.
The run made zero network requests and used zero paid data, remote workers or GPU-hours.
