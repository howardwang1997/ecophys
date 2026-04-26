# T_eff(t) pilot — C4 N=1000 rollout (Mac, 4000 steps)

steps after warmup transient: 3900

## Equipartition T_eff(t)
- mean      : +481.3642
- std       : 2.6440
- relative  : std/mean = 0.0055
- min, max  : [473.1136, 495.0317]

## σ̇(t) entropy production rate
- mean      : -0.0013
- std       : 0.0000

## Cross-correlation T_eff(t) vs |r(t)|: +0.1276
## Cross-correlation T_eff(t) vs r²(t): +0.1377
## Peak cross-corr T_eff(t)→|r(t+τ)|: τ=0 cc=+0.1276
  (positive lag = T_eff precedes vol spike)

Lag scan:
  τ=-20  corr=+0.0415
  τ=-16  corr=+0.0564
  τ=-12  corr=+0.0538
  τ= -8  corr=+0.0434
  τ= -4  corr=+0.0432
  τ= +0  corr=+0.1276
  τ= +4  corr=+0.0404
  τ= +8  corr=+0.0559
  τ=+12  corr=+0.0293
  τ=+16  corr=+0.0670
  τ=+20  corr=+0.0559

## Interpretation
  T_eff is essentially constant (rel std < 5%).
  → Paper B Path A (PRL, TUR alone) only — no NP flagship from this sim.