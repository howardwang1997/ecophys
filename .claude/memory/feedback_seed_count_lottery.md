---
name: 5-seed sample is lottery, never report mean from n<20
description: Lesson from 048→052 regression — twice now a 5-seed mean has been ~30% inflated by upper-tail lottery; 30+ seeds needed for honest CI
type: feedback
---

**Rule: never report the mean of a stylized-fact pass count from fewer than 20 seeds, and treat anything below 30 as a preliminary signal.**

**Why:** Four confirmed instances of small-n mean being upper-tail lottery:
1. `t42_dyngraph_no_u` (047): 5-seed mean = 6.10/11 → 30-seed mean (049) = 5.40/11. **+13% inflation.**
2. `p_4_2__2_1` (048): 5-seed mean = 7.20/11 → 35-seed mean (048+052) = 5.40/11. **+33% inflation.**
3. `pair_AB_reref` (090): seeds 0-29 mean = 5.21 → 090c continuation seeds 30-48 mean = 4.05. Combined n=49 ≈ 4.7. **First "30-seed underflow" hit** — 30 seeds isn't always enough either when the seed distribution has heavy upper outliers.
4. `zumdn_s075_lam095` (098): 3 stable seeds (after rejections) → mean 6.67. **n=3 is meaningless** — 098b at n=30 will confirm or kill.

The EcoMD architecture under moment-matching loss has a heavy-upper-tail outcome distribution (std ~1.75 on a 0-11 scale, bimodal between 3-5 and 7-10 basins). 5 random samples will frequently land in the upper basin and produce a biased mean.

**How to apply:**
- For ANY new architecture or hyperparameter cell, run ≥20 seeds before claiming improvement
- Treat 5-seed sweeps as **direction-finding only**, not as evidence
- Treat ≤3-seed sweeps as "this config doesn't immediately crash"
- For the Paper-A and Paper-B reported numbers, use n ≥ 30
- When budget is tight, prefer 30 seeds × 1 cell over 5 seeds × 6 cells — the latter just generates noise
- Bootstrap CI on the seed distribution; report 95% CI, not just point estimate
- Do NOT use min/max as the headline number — use mean and median

**Honesty trigger**: if a 5-seed result excites you, the next batch must be 30 seeds before discussing. Don't update plans/papers/memory based on 5-seed signals.
