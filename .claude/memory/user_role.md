---
name: User role and research context (EcoPhys)
description: User is an independent full-time researcher (6-18 months) pursuing top-tier publication on physics-inspired financial market dynamics. Has **8×H20 NVLink long-term** (upgraded from 4×H20 on 2026-04-24). Prefers cheap/abundant data, budget $50k. Workflow: Mac dev + Cloudflare R2 + GitHub + H20 pull-and-train. No formal advisor/lab; Claude serves as critical research partner. As of 2026-04-24, committed to Nature Physics flagship path with explicit retreat plans.
type: user
originSessionId: c6748c05-53ac-462d-9535-154e95f91d9f
---
# User Profile — EcoPhys Project

- **Identity**: Independent researcher, full-time, 6–18 month horizon.
- **Goal**: Produce groundbreaking research on applying molecular-dynamics / statistical-mechanics methods to financial markets. **Plan v3 + Path C (2026-04-24 evening)**: Paper B targets Nature Physics (flagship, **15–22% joint probability** after Path C commitment), backed by $8–12k high-frequency data (Tardis L2 6mo + FirstRate minute 3y + LOBSTER 3y). User reviewed daily-only feasibility and explicitly rejected it because it wouldn't answer the three main NP reviewer attacks (Jarzynski work protocol, TUR stationarity, T_eff novelty). Paper A (NeurIPS/ICML main) + companion PRL (TUR) + QF (applications) as retreat paths. Total timeline 58 weeks.
- **Compute**: **8×H20 NVLink, single node, long-term access** (upgraded 2026-04-24 from 4×H20). Each H20 = 96GB HBM, ~148 TFLOPS FP16. NVLink enables tensor-parallel single-model training at N=5×10⁵ agents and shared-θ joint training across 8 markets — both required for Nature Physics universality claim. Machine **remote, inside user's company network**. Network: whitelist outbound (Cloudflare R2, AWS S3, GitHub confirmed reachable; other domains need IT whitelist). **Mac cannot mount the NFS directly** — all Mac↔H20 data transit must go via Cloudflare R2 (confirmed 2026-04-23).
- **H20 paths** (confirmed 2026-04-23):
  - Code: `/root/ecophys/`
  - Hot-cache data drive: `/root/data/ecophys/` (target budget 500 GB for active experiments)
  - NFS canonical store: `/AI4S/Users/howardwang/ecophys/`
- **Dev workflow**: Mac local dev → push processed data to Cloudflare R2 (bucket `ecophys-data`) → push code to GitHub → H20 pulls from R2 into NFS, then rsync subset into `/root/data/ecophys/` hot cache → training reads exclusively from hot cache.
- **Data preference**: Cheap-first, but willing to pay for data that directly unlocks Nature Physics feasibility. **Data budget: $50k** approved. **Path C commitment (2026-04-24 evening): $8–12k up-front** on Tardis L2 crypto 6mo + FirstRate US equity minute 3y + LOBSTER 2-3y (detailed in `ecomd/data/buy_order_v2_{en,zh}.md`). Reserve $38–42k for Phase 4/5 contingencies. User has personal contacts with data vendors who may offer below-retail prices. User can be trusted to push back hard when data strategy glosses over physics-validity concerns.
- **Collaboration**: Solo independent research. No co-authors or advisor by default. Claude is key research partner; user can find endorsers/discussants when needed for backing or deep domain feedback.
- **Python env**: Always use conda (per global CLAUDE.md). Project env = `ecophys`, Python 3.11, conda path `/Users/howardwang/miniconda3/bin/python`.
- **Language**: Chinese primary in conversation; paper writing in English; code comments minimal.
