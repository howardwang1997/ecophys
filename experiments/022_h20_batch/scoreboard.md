# v3 batch scoreboard

Inference 11-fact (10 actually scored — conditional_kurtosis missing in
inference module) on the trained ckpt of each batch variant.

| Variant | n/10 | acf(r²) | hill | leverage | zumbach | aggr_g |
|---|---:|---:|---:|---:|---:|---:|
| A0_baseline_spx | **6/10** + | +0.367 | +1.676 | -4.545 | -0.012 | +44.658 |
| A1_multi_asset | **4/10**  | +0.205 | +7.148 | -3.647 | -0.022 | +511.368 |
| A2_+multiscale_hawkes | **2/10**  | +0.638 | +403.083 | -7.329 | -0.005 | +51.103 |
| A3_+regime_GRU | **4/10**  | +0.339 | +3544.595 | -3.936 | -0.016 | +1040.517 |
| A4_+twopop_γT | **6/10** + | +0.162 | +137.756 | +2.696 | -0.011 | +192.111 |
| A5_all_features | **0/10**  | +0.043 | +70.170 | +0.669 | -0.004 | -9.780 |
| B0_baseline_redo | **4/10**  | +0.154 | +5.297 | -2.785 | -0.005 | +452.515 |
| B1_multi_asset | **3/10**  | +0.143 | +11.330 | -2.358 | -0.008 | +466.495 |
| B2_+mshawkes_conservative | **4/10**  | +0.377 | +52.649 | -4.943 | -0.001 | +310.727 |
| B3_+regime_conservative | **6/10** + | +0.197 | +3.248 | -3.298 | -0.012 | +327.403 |
| B4_+twopop_conservative | **3/10**  | +0.083 | +42.518 | -1.724 | -0.001 | +349.772 |
| B5_all_conservative | **4/10**  | +0.092 | +27.137 | -1.263 | -0.002 | +58.725 |
| C0_baseline_+exploss | **6/10** + | +0.201 | +2.838 | -3.455 | -0.031 | +373.230 |
| C1_multi_asset_+exploss | **4/10**  | +0.161 | +5.170 | -3.070 | -0.056 | +563.511 |
| C2_+mshawkes_+exploss | **5/10** + | +0.151 | +6.207 | -2.949 | +0.036 | +539.748 |
| C3_+regime_+exploss | **4/10**  | +0.113 | +18.257 | -2.526 | +0.015 | +692.181 |
| C4_+twopop_+exploss | **7/10** ★ | +0.235 | +3.380 | -2.368 | -0.067 | +48.748 |
| C5_all_+exploss | **4/10**  | +0.292 | +3.356 | -1.881 | -0.063 | -7.858 |
| D0_a0_long | **2/10**  | +0.083 | +75.964 | -1.759 | -0.001 | +1228.197 |
| D1_b0_long | **2/10**  | +0.083 | +75.720 | -1.765 | -0.003 | +1226.371 |
| D2_b4_long | **3/10**  | +0.752 | +6.282 | -7.984 | -0.012 | +11.532 |
| D3_c0_long | **4/10**  | +0.594 | +60.365 | -6.647 | +0.002 | +93.192 |
| D4_c4_long | **4/10**  | +0.299 | +3.748 | -1.214 | -0.017 | -10.277 |

Real targets: acf=+0.342, hill=2.68, leverage=−0.79, zumbach>0, aggr 10-200

## A0_baseline_spx — 6/10 (n_realiz=8)

| fact | value | band | pass |
|---|---:|---|:-:|
| autocorr_returns | +0.807 | [-0.10, +0.20] | ✗ |
| hill_tail_index | +1.676 | [+2.00, +4.00] | ✗ |
| gain_loss_asymmetry | -5.905 | [-30.00, -3.00] | ✓ |
| aggregational_gaussianity | +44.658 | [+10.00, +200.00] | ✓ |
| intermittency_fano | +38.030 | [+5.00, +100.00] | ✓ |
| acf_squared_returns | +0.367 | [+0.15, +0.55] | ✓ |
| dfa_hurst_abs_r | +1.076 | [+0.60, +0.90] | ✗ |
| leverage_effect | -4.545 | [-6.00, -0.50] | ✓ |
| volume_volatility_corr | +0.661 | [+0.30, +0.80] | ✓ |
| zumbach_asymmetry | -0.012 | [+0.00, +0.50] | ✗ |

## A1_multi_asset — 4/10 (n_realiz=8)

| fact | value | band | pass |
|---|---:|---|:-:|
| autocorr_returns | +0.332 | [-0.10, +0.20] | ✗ |
| hill_tail_index | +7.148 | [+2.00, +4.00] | ✗ |
| gain_loss_asymmetry | -21.855 | [-30.00, -3.00] | ✓ |
| aggregational_gaussianity | +511.368 | [+10.00, +200.00] | ✗ |
| intermittency_fano | +38.030 | [+5.00, +100.00] | ✓ |
| acf_squared_returns | +0.205 | [+0.15, +0.55] | ✓ |
| dfa_hurst_abs_r | +0.580 | [+0.60, +0.90] | ✗ |
| leverage_effect | -3.647 | [-6.00, -0.50] | ✓ |
| volume_volatility_corr | +0.872 | [+0.30, +0.80] | ✗ |
| zumbach_asymmetry | -0.022 | [+0.00, +0.50] | ✗ |

## A2_+multiscale_hawkes — 2/10 (n_realiz=8)

| fact | value | band | pass |
|---|---:|---|:-:|
| autocorr_returns | +0.654 | [-0.10, +0.20] | ✗ |
| hill_tail_index | +403.083 | [+2.00, +4.00] | ✗ |
| gain_loss_asymmetry | +6.023 | [-30.00, -3.00] | ✗ |
| aggregational_gaussianity | +51.103 | [+10.00, +200.00] | ✓ |
| intermittency_fano | +4.520 | [+5.00, +100.00] | ✗ |
| acf_squared_returns | +0.638 | [+0.15, +0.55] | ✗ |
| dfa_hurst_abs_r | +1.138 | [+0.60, +0.90] | ✗ |
| leverage_effect | -7.329 | [-6.00, -0.50] | ✗ |
| volume_volatility_corr | +0.585 | [+0.30, +0.80] | ✓ |
| zumbach_asymmetry | -0.005 | [+0.00, +0.50] | ✗ |

## A3_+regime_GRU — 4/10 (n_realiz=8)

| fact | value | band | pass |
|---|---:|---|:-:|
| autocorr_returns | +0.290 | [-0.10, +0.20] | ✗ |
| hill_tail_index | +3544.595 | [+2.00, +4.00] | ✗ |
| gain_loss_asymmetry | +29.238 | [-30.00, -3.00] | ✗ |
| aggregational_gaussianity | +1040.517 | [+10.00, +200.00] | ✗ |
| intermittency_fano | +2.144 | [+5.00, +100.00] | ✗ |
| acf_squared_returns | +0.339 | [+0.15, +0.55] | ✓ |
| dfa_hurst_abs_r | +0.723 | [+0.60, +0.90] | ✓ |
| leverage_effect | -3.936 | [-6.00, -0.50] | ✓ |
| volume_volatility_corr | +0.669 | [+0.30, +0.80] | ✓ |
| zumbach_asymmetry | -0.016 | [+0.00, +0.50] | ✗ |

## A4_+twopop_γT — 6/10 (n_realiz=8)

| fact | value | band | pass |
|---|---:|---|:-:|
| autocorr_returns | +0.338 | [-0.10, +0.20] | ✗ |
| hill_tail_index | +137.756 | [+2.00, +4.00] | ✗ |
| gain_loss_asymmetry | -10.512 | [-30.00, -3.00] | ✓ |
| aggregational_gaussianity | +192.111 | [+10.00, +200.00] | ✓ |
| intermittency_fano | +5.361 | [+5.00, +100.00] | ✓ |
| acf_squared_returns | +0.162 | [+0.15, +0.55] | ✓ |
| dfa_hurst_abs_r | +0.631 | [+0.60, +0.90] | ✓ |
| leverage_effect | +2.696 | [-6.00, -0.50] | ✗ |
| volume_volatility_corr | +0.497 | [+0.30, +0.80] | ✓ |
| zumbach_asymmetry | -0.011 | [+0.00, +0.50] | ✗ |

## A5_all_features — 0/10 (n_realiz=8)

| fact | value | band | pass |
|---|---:|---|:-:|
| autocorr_returns | +0.824 | [-0.10, +0.20] | ✗ |
| hill_tail_index | +70.170 | [+2.00, +4.00] | ✗ |
| gain_loss_asymmetry | -1.287 | [-30.00, -3.00] | ✗ |
| aggregational_gaussianity | -9.780 | [+10.00, +200.00] | ✗ |
| intermittency_fano | +3.383 | [+5.00, +100.00] | ✗ |
| acf_squared_returns | +0.043 | [+0.15, +0.55] | ✗ |
| dfa_hurst_abs_r | +0.564 | [+0.60, +0.90] | ✗ |
| leverage_effect | +0.669 | [-6.00, -0.50] | ✗ |
| volume_volatility_corr | +0.209 | [+0.30, +0.80] | ✗ |
| zumbach_asymmetry | -0.004 | [+0.00, +0.50] | ✗ |

## B0_baseline_redo — 4/10 (n_realiz=8)

| fact | value | band | pass |
|---|---:|---|:-:|
| autocorr_returns | +0.341 | [-0.10, +0.20] | ✗ |
| hill_tail_index | +5.297 | [+2.00, +4.00] | ✗ |
| gain_loss_asymmetry | -20.851 | [-30.00, -3.00] | ✓ |
| aggregational_gaussianity | +452.515 | [+10.00, +200.00] | ✗ |
| intermittency_fano | +13.641 | [+5.00, +100.00] | ✓ |
| acf_squared_returns | +0.154 | [+0.15, +0.55] | ✓ |
| dfa_hurst_abs_r | +0.403 | [+0.60, +0.90] | ✗ |
| leverage_effect | -2.785 | [-6.00, -0.50] | ✓ |
| volume_volatility_corr | -0.561 | [+0.30, +0.80] | ✗ |
| zumbach_asymmetry | -0.005 | [+0.00, +0.50] | ✗ |

## B1_multi_asset — 3/10 (n_realiz=8)

| fact | value | band | pass |
|---|---:|---|:-:|
| autocorr_returns | +0.225 | [-0.10, +0.20] | ✗ |
| hill_tail_index | +11.330 | [+2.00, +4.00] | ✗ |
| gain_loss_asymmetry | -20.555 | [-30.00, -3.00] | ✓ |
| aggregational_gaussianity | +466.495 | [+10.00, +200.00] | ✗ |
| intermittency_fano | +14.684 | [+5.00, +100.00] | ✓ |
| acf_squared_returns | +0.143 | [+0.15, +0.55] | ✗ |
| dfa_hurst_abs_r | +0.460 | [+0.60, +0.90] | ✗ |
| leverage_effect | -2.358 | [-6.00, -0.50] | ✓ |
| volume_volatility_corr | -0.018 | [+0.30, +0.80] | ✗ |
| zumbach_asymmetry | -0.008 | [+0.00, +0.50] | ✗ |

## B2_+mshawkes_conservative — 4/10 (n_realiz=8)

| fact | value | band | pass |
|---|---:|---|:-:|
| autocorr_returns | +0.499 | [-0.10, +0.20] | ✗ |
| hill_tail_index | +52.649 | [+2.00, +4.00] | ✗ |
| gain_loss_asymmetry | -13.432 | [-30.00, -3.00] | ✓ |
| aggregational_gaussianity | +310.727 | [+10.00, +200.00] | ✗ |
| intermittency_fano | +20.284 | [+5.00, +100.00] | ✓ |
| acf_squared_returns | +0.377 | [+0.15, +0.55] | ✓ |
| dfa_hurst_abs_r | +0.362 | [+0.60, +0.90] | ✗ |
| leverage_effect | -4.943 | [-6.00, -0.50] | ✓ |
| volume_volatility_corr | -0.460 | [+0.30, +0.80] | ✗ |
| zumbach_asymmetry | -0.001 | [+0.00, +0.50] | ✗ |

## B3_+regime_conservative — 6/10 (n_realiz=8)

| fact | value | band | pass |
|---|---:|---|:-:|
| autocorr_returns | +0.478 | [-0.10, +0.20] | ✗ |
| hill_tail_index | +3.248 | [+2.00, +4.00] | ✓ |
| gain_loss_asymmetry | -16.210 | [-30.00, -3.00] | ✓ |
| aggregational_gaussianity | +327.403 | [+10.00, +200.00] | ✗ |
| intermittency_fano | +36.862 | [+5.00, +100.00] | ✓ |
| acf_squared_returns | +0.197 | [+0.15, +0.55] | ✓ |
| dfa_hurst_abs_r | +0.756 | [+0.60, +0.90] | ✓ |
| leverage_effect | -3.298 | [-6.00, -0.50] | ✓ |
| volume_volatility_corr | -0.685 | [+0.30, +0.80] | ✗ |
| zumbach_asymmetry | -0.012 | [+0.00, +0.50] | ✗ |

## B4_+twopop_conservative — 3/10 (n_realiz=8)

| fact | value | band | pass |
|---|---:|---|:-:|
| autocorr_returns | +0.368 | [-0.10, +0.20] | ✗ |
| hill_tail_index | +42.518 | [+2.00, +4.00] | ✗ |
| gain_loss_asymmetry | -13.952 | [-30.00, -3.00] | ✓ |
| aggregational_gaussianity | +349.772 | [+10.00, +200.00] | ✗ |
| intermittency_fano | +6.818 | [+5.00, +100.00] | ✓ |
| acf_squared_returns | +0.083 | [+0.15, +0.55] | ✗ |
| dfa_hurst_abs_r | +0.216 | [+0.60, +0.90] | ✗ |
| leverage_effect | -1.724 | [-6.00, -0.50] | ✓ |
| volume_volatility_corr | -0.649 | [+0.30, +0.80] | ✗ |
| zumbach_asymmetry | -0.001 | [+0.00, +0.50] | ✗ |

## B5_all_conservative — 4/10 (n_realiz=8)

| fact | value | band | pass |
|---|---:|---|:-:|
| autocorr_returns | +0.654 | [-0.10, +0.20] | ✗ |
| hill_tail_index | +27.137 | [+2.00, +4.00] | ✗ |
| gain_loss_asymmetry | -5.426 | [-30.00, -3.00] | ✓ |
| aggregational_gaussianity | +58.725 | [+10.00, +200.00] | ✓ |
| intermittency_fano | +5.444 | [+5.00, +100.00] | ✓ |
| acf_squared_returns | +0.092 | [+0.15, +0.55] | ✗ |
| dfa_hurst_abs_r | +0.313 | [+0.60, +0.90] | ✗ |
| leverage_effect | -1.263 | [-6.00, -0.50] | ✓ |
| volume_volatility_corr | -0.679 | [+0.30, +0.80] | ✗ |
| zumbach_asymmetry | -0.002 | [+0.00, +0.50] | ✗ |

## C0_baseline_+exploss — 6/10 (n_realiz=8)

| fact | value | band | pass |
|---|---:|---|:-:|
| autocorr_returns | +0.424 | [-0.10, +0.20] | ✗ |
| hill_tail_index | +2.838 | [+2.00, +4.00] | ✓ |
| gain_loss_asymmetry | -18.193 | [-30.00, -3.00] | ✓ |
| aggregational_gaussianity | +373.230 | [+10.00, +200.00] | ✗ |
| intermittency_fano | +38.030 | [+5.00, +100.00] | ✓ |
| acf_squared_returns | +0.201 | [+0.15, +0.55] | ✓ |
| dfa_hurst_abs_r | +0.661 | [+0.60, +0.90] | ✓ |
| leverage_effect | -3.455 | [-6.00, -0.50] | ✓ |
| volume_volatility_corr | -0.891 | [+0.30, +0.80] | ✗ |
| zumbach_asymmetry | -0.031 | [+0.00, +0.50] | ✗ |

## C1_multi_asset_+exploss — 4/10 (n_realiz=8)

| fact | value | band | pass |
|---|---:|---|:-:|
| autocorr_returns | +0.280 | [-0.10, +0.20] | ✗ |
| hill_tail_index | +5.170 | [+2.00, +4.00] | ✗ |
| gain_loss_asymmetry | -23.238 | [-30.00, -3.00] | ✓ |
| aggregational_gaussianity | +563.511 | [+10.00, +200.00] | ✗ |
| intermittency_fano | +37.797 | [+5.00, +100.00] | ✓ |
| acf_squared_returns | +0.161 | [+0.15, +0.55] | ✓ |
| dfa_hurst_abs_r | +0.534 | [+0.60, +0.90] | ✗ |
| leverage_effect | -3.070 | [-6.00, -0.50] | ✓ |
| volume_volatility_corr | -0.701 | [+0.30, +0.80] | ✗ |
| zumbach_asymmetry | -0.056 | [+0.00, +0.50] | ✗ |

## C2_+mshawkes_+exploss — 5/10 (n_realiz=8)

| fact | value | band | pass |
|---|---:|---|:-:|
| autocorr_returns | +0.234 | [-0.10, +0.20] | ✗ |
| hill_tail_index | +6.207 | [+2.00, +4.00] | ✗ |
| gain_loss_asymmetry | -22.914 | [-30.00, -3.00] | ✓ |
| aggregational_gaussianity | +539.748 | [+10.00, +200.00] | ✗ |
| intermittency_fano | +13.366 | [+5.00, +100.00] | ✓ |
| acf_squared_returns | +0.151 | [+0.15, +0.55] | ✓ |
| dfa_hurst_abs_r | +0.313 | [+0.60, +0.90] | ✗ |
| leverage_effect | -2.949 | [-6.00, -0.50] | ✓ |
| volume_volatility_corr | -0.356 | [+0.30, +0.80] | ✗ |
| zumbach_asymmetry | +0.036 | [+0.00, +0.50] | ✓ |

## C3_+regime_+exploss — 4/10 (n_realiz=8)

| fact | value | band | pass |
|---|---:|---|:-:|
| autocorr_returns | +0.173 | [-0.10, +0.20] | ✓ |
| hill_tail_index | +18.257 | [+2.00, +4.00] | ✗ |
| gain_loss_asymmetry | -25.159 | [-30.00, -3.00] | ✓ |
| aggregational_gaussianity | +692.181 | [+10.00, +200.00] | ✗ |
| intermittency_fano | +4.566 | [+5.00, +100.00] | ✗ |
| acf_squared_returns | +0.113 | [+0.15, +0.55] | ✗ |
| dfa_hurst_abs_r | +0.145 | [+0.60, +0.90] | ✗ |
| leverage_effect | -2.526 | [-6.00, -0.50] | ✓ |
| volume_volatility_corr | -0.397 | [+0.30, +0.80] | ✗ |
| zumbach_asymmetry | +0.015 | [+0.00, +0.50] | ✓ |

## C4_+twopop_+exploss — 7/10 (n_realiz=8)

| fact | value | band | pass |
|---|---:|---|:-:|
| autocorr_returns | +0.272 | [-0.10, +0.20] | ✗ |
| hill_tail_index | +3.380 | [+2.00, +4.00] | ✓ |
| gain_loss_asymmetry | -5.711 | [-30.00, -3.00] | ✓ |
| aggregational_gaussianity | +48.748 | [+10.00, +200.00] | ✓ |
| intermittency_fano | +24.665 | [+5.00, +100.00] | ✓ |
| acf_squared_returns | +0.235 | [+0.15, +0.55] | ✓ |
| dfa_hurst_abs_r | +0.900 | [+0.60, +0.90] | ✓ |
| leverage_effect | -2.368 | [-6.00, -0.50] | ✓ |
| volume_volatility_corr | -0.381 | [+0.30, +0.80] | ✗ |
| zumbach_asymmetry | -0.067 | [+0.00, +0.50] | ✗ |

## C5_all_+exploss — 4/10 (n_realiz=8)

| fact | value | band | pass |
|---|---:|---|:-:|
| autocorr_returns | +0.267 | [-0.10, +0.20] | ✗ |
| hill_tail_index | +3.356 | [+2.00, +4.00] | ✓ |
| gain_loss_asymmetry | -2.362 | [-30.00, -3.00] | ✗ |
| aggregational_gaussianity | -7.858 | [+10.00, +200.00] | ✗ |
| intermittency_fano | +22.134 | [+5.00, +100.00] | ✓ |
| acf_squared_returns | +0.292 | [+0.15, +0.55] | ✓ |
| dfa_hurst_abs_r | +0.911 | [+0.60, +0.90] | ✗ |
| leverage_effect | -1.881 | [-6.00, -0.50] | ✓ |
| volume_volatility_corr | -0.231 | [+0.30, +0.80] | ✗ |
| zumbach_asymmetry | -0.063 | [+0.00, +0.50] | ✗ |

## D0_a0_long — 2/10 (n_realiz=8)

| fact | value | band | pass |
|---|---:|---|:-:|
| autocorr_returns | +0.099 | [-0.10, +0.20] | ✓ |
| hill_tail_index | +75.964 | [+2.00, +4.00] | ✗ |
| gain_loss_asymmetry | -33.807 | [-30.00, -3.00] | ✗ |
| aggregational_gaussianity | +1228.197 | [+10.00, +200.00] | ✗ |
| intermittency_fano | +4.079 | [+5.00, +100.00] | ✗ |
| acf_squared_returns | +0.083 | [+0.15, +0.55] | ✗ |
| dfa_hurst_abs_r | +0.162 | [+0.60, +0.90] | ✗ |
| leverage_effect | -1.759 | [-6.00, -0.50] | ✓ |
| volume_volatility_corr | -0.029 | [+0.30, +0.80] | ✗ |
| zumbach_asymmetry | -0.001 | [+0.00, +0.50] | ✗ |

## D1_b0_long — 2/10 (n_realiz=8)

| fact | value | band | pass |
|---|---:|---|:-:|
| autocorr_returns | +0.100 | [-0.10, +0.20] | ✓ |
| hill_tail_index | +75.720 | [+2.00, +4.00] | ✗ |
| gain_loss_asymmetry | -33.769 | [-30.00, -3.00] | ✗ |
| aggregational_gaussianity | +1226.371 | [+10.00, +200.00] | ✗ |
| intermittency_fano | +4.485 | [+5.00, +100.00] | ✗ |
| acf_squared_returns | +0.083 | [+0.15, +0.55] | ✗ |
| dfa_hurst_abs_r | +0.167 | [+0.60, +0.90] | ✗ |
| leverage_effect | -1.765 | [-6.00, -0.50] | ✓ |
| volume_volatility_corr | -0.031 | [+0.30, +0.80] | ✗ |
| zumbach_asymmetry | -0.003 | [+0.00, +0.50] | ✗ |

## D2_b4_long — 3/10 (n_realiz=8)

| fact | value | band | pass |
|---|---:|---|:-:|
| autocorr_returns | +0.817 | [-0.10, +0.20] | ✗ |
| hill_tail_index | +6.282 | [+2.00, +4.00] | ✗ |
| gain_loss_asymmetry | -3.611 | [-30.00, -3.00] | ✓ |
| aggregational_gaussianity | +11.532 | [+10.00, +200.00] | ✓ |
| intermittency_fano | +37.096 | [+5.00, +100.00] | ✓ |
| acf_squared_returns | +0.752 | [+0.15, +0.55] | ✗ |
| dfa_hurst_abs_r | +1.443 | [+0.60, +0.90] | ✗ |
| leverage_effect | -7.984 | [-6.00, -0.50] | ✗ |
| volume_volatility_corr | -0.521 | [+0.30, +0.80] | ✗ |
| zumbach_asymmetry | -0.012 | [+0.00, +0.50] | ✗ |

## D3_c0_long — 4/10 (n_realiz=8)

| fact | value | band | pass |
|---|---:|---|:-:|
| autocorr_returns | +0.597 | [-0.10, +0.20] | ✗ |
| hill_tail_index | +60.365 | [+2.00, +4.00] | ✗ |
| gain_loss_asymmetry | -1.228 | [-30.00, -3.00] | ✗ |
| aggregational_gaussianity | +93.192 | [+10.00, +200.00] | ✓ |
| intermittency_fano | +20.833 | [+5.00, +100.00] | ✓ |
| acf_squared_returns | +0.594 | [+0.15, +0.55] | ✗ |
| dfa_hurst_abs_r | +0.794 | [+0.60, +0.90] | ✓ |
| leverage_effect | -6.647 | [-6.00, -0.50] | ✗ |
| volume_volatility_corr | +0.016 | [+0.30, +0.80] | ✗ |
| zumbach_asymmetry | +0.002 | [+0.00, +0.50] | ✓ |

## D4_c4_long — 4/10 (n_realiz=8)

| fact | value | band | pass |
|---|---:|---|:-:|
| autocorr_returns | +0.891 | [-0.10, +0.20] | ✗ |
| hill_tail_index | +3.748 | [+2.00, +4.00] | ✓ |
| gain_loss_asymmetry | -1.217 | [-30.00, -3.00] | ✗ |
| aggregational_gaussianity | -10.277 | [+10.00, +200.00] | ✗ |
| intermittency_fano | +17.942 | [+5.00, +100.00] | ✓ |
| acf_squared_returns | +0.299 | [+0.15, +0.55] | ✓ |
| dfa_hurst_abs_r | +1.136 | [+0.60, +0.90] | ✗ |
| leverage_effect | -1.214 | [-6.00, -0.50] | ✓ |
| volume_volatility_corr | -0.491 | [+0.30, +0.80] | ✗ |
| zumbach_asymmetry | -0.017 | [+0.00, +0.50] | ✗ |
