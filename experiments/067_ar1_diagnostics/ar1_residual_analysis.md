# E3a — Analytical AR(1)-residual ACF analysis (064 winner_50seed_repro)

## What this measures
Sample raw return ACF was computed in 064 inference. Here we fit AR(1) per realization (rho = ACF[1]), analytically whiten the ACF, and recompute the autocorr_returns metric (mean |ACF| over lags 1..20).
- **pre_metric** = mean |ACF_raw|  (matches `autocorr_returns.estimate`)
- **post_metric** = mean |ACF_residual|  (after AR(1) whitening)
- **band** = (-0.1, 0.2) (pass = white-noise-like)

## Population summary

- realizations scanned: 200 (50 seeds × 4 rollouts each)
- rho_hat (AR(1) coef): mean=0.904  median=0.935  min=0.445  max=0.991
- pre_metric:  mean=0.580  pass=9/200 (4.5%)
- post_metric: mean=0.059  pass=188/200 (94.0%)

## Is the autocorr structure pure AR(1)?

If yes, ACF[k] should equal rho^k. We measure deviation from pure AR(1):

| lag | mean ACF observed | mean rho^lag (pure AR(1) expected) | excess |
|---:|---:|---:|---:|
| 1 | +0.904 | +0.904 | +0.000 |
| 5 | +0.696 | +0.680 | +0.016 |
| 10 | +0.559 | +0.513 | +0.046 |
| 20 | +0.390 | +0.319 | +0.071 |

## Per-seed (avg of 4 realizations)

| seed | rho_hat | pre_metric | post_metric | pre_pass | post_pass |
|---:|---:|---:|---:|---:|---:|
| 35 | 0.914 | 0.466 | 0.002 | 0/4 | 4/4 |
| 36 | 0.979 | 0.796 | 0.013 | 0/4 | 4/4 |
| 37 | 0.958 | 0.747 | 0.010 | 0/4 | 4/4 |
| 38 | 0.979 | 0.898 | 0.278 | 0/4 | 1/4 |
| 39 | 0.908 | 0.392 | 0.002 | 0/4 | 4/4 |
| 40 | 0.968 | 0.771 | 0.037 | 0/4 | 4/4 |
| 41 | 0.949 | 0.675 | 0.021 | 0/4 | 4/4 |
| 42 | 0.908 | 0.430 | 0.001 | 0/4 | 4/4 |
| 43 | 0.959 | 0.724 | 0.006 | 0/4 | 4/4 |
| 44 | 0.941 | 0.647 | 0.007 | 0/4 | 4/4 |
| 45 | 0.912 | 0.452 | 0.002 | 0/4 | 4/4 |
| 46 | 0.929 | 0.575 | 0.007 | 0/4 | 4/4 |
| 47 | 0.949 | 0.707 | 0.035 | 0/4 | 4/4 |
| 48 | 0.863 | 0.404 | 0.276 | 0/4 | 2/4 |
| 49 | 0.946 | 0.627 | 0.166 | 0/4 | 3/4 |
| 50 | 0.986 | 0.770 | 0.036 | 0/4 | 4/4 |
| 51 | 0.927 | 0.577 | 0.007 | 0/4 | 4/4 |
| 52 | 0.923 | 0.517 | 0.004 | 0/4 | 4/4 |
| 53 | 0.988 | 0.820 | 0.038 | 0/4 | 4/4 |
| 54 | 0.878 | 0.277 | 0.040 | 0/4 | 4/4 |
| 55 | 0.911 | 0.426 | 0.026 | 0/4 | 4/4 |
| 56 | 0.962 | 0.744 | 0.008 | 0/4 | 4/4 |
| 57 | 0.908 | 0.374 | 0.012 | 0/4 | 4/4 |
| 58 | 0.870 | 0.251 | 0.143 | 0/4 | 4/4 |
| 59 | 0.950 | 0.700 | 0.008 | 0/4 | 4/4 |
| 60 | 0.466 | 0.432 | 0.167 | 0/4 | 4/4 |
| 61 | 0.948 | 0.709 | 0.027 | 0/4 | 4/4 |
| 62 | 0.735 | 0.287 | 0.065 | 0/4 | 4/4 |
| 63 | 0.784 | 0.210 | 0.163 | 1/4 | 3/4 |
| 64 | 0.891 | 0.363 | 0.135 | 0/4 | 3/4 |
| 65 | 0.989 | 0.883 | 0.012 | 0/4 | 4/4 |
| 66 | 0.936 | 0.568 | 0.014 | 0/4 | 4/4 |
| 67 | 0.954 | 0.674 | 0.005 | 0/4 | 4/4 |
| 68 | 0.990 | 0.885 | 0.136 | 0/4 | 4/4 |
| 69 | 0.929 | 0.575 | 0.006 | 0/4 | 4/4 |
| 70 | 0.935 | 0.617 | 0.007 | 0/4 | 4/4 |
| 71 | 0.926 | 0.574 | 0.009 | 0/4 | 4/4 |
| 72 | 0.914 | 0.423 | 0.006 | 0/4 | 4/4 |
| 73 | 0.924 | 0.470 | 0.054 | 0/4 | 4/4 |
| 74 | 0.489 | 0.170 | 0.071 | 4/4 | 4/4 |
| 75 | 0.901 | 0.299 | 0.024 | 0/4 | 4/4 |
| 76 | 0.949 | 0.706 | 0.021 | 0/4 | 4/4 |
| 77 | 0.979 | 0.736 | 0.017 | 0/4 | 4/4 |
| 78 | 0.962 | 0.777 | 0.030 | 0/4 | 4/4 |
| 79 | 0.981 | 0.883 | 0.034 | 0/4 | 4/4 |
| 80 | 0.915 | 0.500 | 0.047 | 0/4 | 4/4 |
| 81 | 0.982 | 0.952 | 0.604 | 0/4 | 0/4 |
| 82 | 0.465 | 0.093 | 0.046 | 4/4 | 4/4 |
| 83 | 0.954 | 0.725 | 0.016 | 0/4 | 4/4 |
| 84 | 0.961 | 0.714 | 0.048 | 0/4 | 4/4 |

## Verdict

**AR(1) FULLY EXPLAINS THE DRIFT**: 188/200 (94%) realizations pass after whitening.
→ The autocorr_returns failure is essentially the lag-1 component alone.
→ Reviewer-2 verdict: 'this fact only fails because returns are AR(1); other facts may share the artifact'.
→ Action: must check whether vol-clustering (acf_sq²) and Hurst survive whitening (E3b).
