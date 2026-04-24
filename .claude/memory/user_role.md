---
name: User role and research context (EcoPhys)
description: User is an independent full-time researcher (6-18 months) pursuing top-tier publication on physics-inspired financial market dynamics. Has **8×H20 NVLink long-term** (upgraded from 4×H20 on 2026-04-24). Prefers cheap/abundant data, budget $50k. Workflow: Mac dev + Cloudflare R2 + GitHub + H20 pull-and-train. No formal advisor/lab; Claude serves as critical research partner. As of 2026-04-24, committed to Nature Physics flagship path with explicit retreat plans.
type: user
originSessionId: c6748c05-53ac-462d-9535-154e95f91d9f
---
# User Profile — EcoPhys Project

- **Identity**: Independent researcher, full-time, 6–18 month horizon.
- **Goal**: Produce groundbreaking research on applying molecular-dynamics / statistical-mechanics methods to financial markets. **Plan v3 (2026-04-24)**: Paper B targets Nature Physics (flagship, 10–15% joint probability); Paper A (NeurIPS/ICML main) + companion PRL (TUR) as retreat paths; user explicitly willing to delay submission 4–6 weeks for flagship attempt.
- **Compute**: **8×H20 NVLink, single node, long-term access** (upgraded 2026-04-24 from 4×H20). Each H20 = 96GB HBM, ~148 TFLOPS FP16. NVLink enables tensor-parallel single-model training at N=5×10⁵ agents and shared-θ joint training across 8 markets — both required for Nature Physics universality claim. Machine **remote, inside user's company network**. Network: whitelist outbound (Cloudflare R2, AWS S3, GitHub confirmed reachable; other domains need IT whitelist). **Mac cannot mount the NFS directly** — all Mac↔H20 data transit must go via Cloudflare R2 (confirmed 2026-04-23).
- **H20 paths** (confirmed 2026-04-23):
  - Code: `/root/ecophys/`
  - Hot-cache data drive: `/root/data/ecophys/` (target budget 500 GB for active experiments)
  - NFS canonical store: `/AI4S/Users/howardwang/ecophys/`
- **Dev workflow**: Mac local dev → push processed data to Cloudflare R2 (bucket `ecophys-data`) → push code to GitHub → H20 pulls from R2 into NFS, then rsync subset into `/root/data/ecophys/` hot cache → training reads exclusively from hot cache.
- **Data preference**: Cheap and abundant. Free first (yfinance, Binance public, CryptoDataDownload, LOBSTER samples). **Data budget: up to $50k** (2026-04-23 revision). Plan spends ~$15k–30k on Tier 1+1.5 (FirstRate minute, LOBSTER full, CBOE EOD options, international equities, Tardis 3-mo). Reserve $20k+ for Phase 4/5 contingencies. User has personal contacts with data vendors who may offer below-retail prices.
- **Collaboration**: Solo independent research. No co-authors or advisor by default. Claude is key research partner; user can find endorsers/discussants when needed for backing or deep domain feedback.
- **Python env**: Always use conda (per global CLAUDE.md). Project env = `ecophys`, Python 3.11, conda path `/Users/howardwang/miniconda3/bin/python`.
- **Language**: Chinese primary in conversation; paper writing in English; code comments minimal.
