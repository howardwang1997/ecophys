# E2 — Post-training thermodynamic parameters (064 winner_50seed_repro)

## Hypothesis to test
Did the model 'cheat' by driving T → 0 to suppress stochasticity?
Init values: T=0.05, γ=1.0, dt=0.01
Init per-step noise std σ_init = sqrt(2·T·dt/γ) = **0.0316**

## Distribution across 50 seeds

| param | stats |
|---|---|
| T_eff | mean=0.0515  median=0.0515  min=0.0499  max=0.0539  sd=0.0011 |
| gamma_eff | mean=0.9804  median=0.9783  min=0.9641  max=1.0139  sd=0.0103 |
| noise_per_step | mean=0.0324  median=0.0323  min=0.0317  max=0.0334  sd=0.0004 |
| T_eff / T_init | mean=1.0291  median=1.0307  min=0.9977  max=1.0787  sd=0.0223 |
| gamma_eff / gamma_init | mean=0.9804  median=0.9783  min=0.9641  max=1.0139  sd=0.0103 |

**T_eff < 0.5·T_init**: 0/50 seeds (cheat indicator)
**γ_eff > 2·γ_init**: 0/50 seeds (alt cheat indicator)
**noise_per_step < 0.5·σ_init**: 0/50 seeds (composite)

## Score vs T_eff / γ_eff (does cheating correlate with high score?)

| score | n | mean_T | mean_γ | mean_noise |
|---:|---:|---:|---:|---:|
| 1/11 | 1 | 0.0502 | 0.9781 | 0.0320 |
| 2/11 | 1 | 0.0506 | 0.9682 | 0.0323 |
| 3/11 | 10 | 0.0513 | 0.9798 | 0.0324 |
| 4/11 | 11 | 0.0514 | 0.9817 | 0.0324 |
| 5/11 | 10 | 0.0515 | 0.9824 | 0.0324 |
| 6/11 | 5 | 0.0508 | 0.9832 | 0.0321 |
| 7/11 | 9 | 0.0521 | 0.9745 | 0.0327 |
| 8/11 | 1 | 0.0520 | 1.0139 | 0.0320 |
| 10/11 | 2 | 0.0522 | 0.9772 | 0.0327 |

## Per-seed (top 10 by score)

| seed | score | T_eff | γ_eff | noise/step | iter |
|---:|---:|---:|---:|---:|---:|
| 51 | 10/11 | 0.0518 | 0.9759 | 0.0326 | 200 |
| 70 | 10/11 | 0.0527 | 0.9784 | 0.0328 | 200 |
| 60 | 8/11 | 0.0520 | 1.0139 | 0.0320 | 200 |
| 39 | 7/11 | 0.0532 | 0.9752 | 0.0330 | 200 |
| 44 | 7/11 | 0.0527 | 0.9651 | 0.0331 | 200 |
| 46 | 7/11 | 0.0527 | 0.9692 | 0.0330 | 200 |
| 56 | 7/11 | 0.0539 | 0.9687 | 0.0334 | 200 |
| 57 | 7/11 | 0.0521 | 0.9782 | 0.0326 | 200 |
| 59 | 7/11 | 0.0523 | 0.9716 | 0.0328 | 200 |
| 61 | 7/11 | 0.0505 | 0.9828 | 0.0321 | 200 |

## Per-seed (bottom 10 by score)

| seed | score | T_eff | γ_eff | noise/step | iter |
|---:|---:|---:|---:|---:|---:|
| 38 | 1/11 | 0.0502 | 0.9781 | 0.0320 | 200 |
| 79 | 2/11 | 0.0506 | 0.9682 | 0.0323 | 200 |
| 36 | 3/11 | 0.0527 | 0.9732 | 0.0329 | 200 |
| 40 | 3/11 | 0.0506 | 0.9773 | 0.0322 | 200 |
| 49 | 3/11 | 0.0501 | 0.9903 | 0.0318 | 200 |
| 62 | 3/11 | 0.0502 | 1.0007 | 0.0317 | 200 |
| 63 | 3/11 | 0.0505 | 0.9765 | 0.0322 | 200 |
| 65 | 3/11 | 0.0523 | 0.9738 | 0.0328 | 200 |
| 66 | 3/11 | 0.0501 | 0.9780 | 0.0320 | 200 |
| 67 | 3/11 | 0.0536 | 0.9681 | 0.0333 | 200 |

## Verdict (auto)

**CHEAT REJECTED**: only 0/50 seeds reduced noise meaningfully. The autocorr problem is NOT due to T-suppression — it's structural (force field too smooth across one dt, or per-step relaxation γ·dt=0.01 too small to decorrelate velocity).
