---
name: User role and research context (EcoPhys)
description: User is an independent full-time researcher pursuing top-tier work on physics-inspired financial market dynamics. Current compute is 2×V100 32 GB and may expand to more GPU/CPU nodes, with H20 explicitly excluded from future plans as of 2026-08-09. Data scope may also expand beyond current holdings behind scientific gates. No formal advisor/lab; Claude serves as critical research partner.
type: user
originSessionId: c6748c05-53ac-462d-9535-154e95f91d9f
---
# User Profile — EcoPhys Project

- **Identity**: Independent researcher, full-time, 6–18 month horizon.
- **Goal**: Produce a complete, influential archival work rather than publish EcoMD by existence. **Plan v4 (2026-08-09)** targets a conditional Nature Computational Science Article centered on a novel invariant-measure/long-horizon calibration method, cross-system validation, a repaired EcoMD, a validated model-to-L2 observation bridge, and a frozen method-dependent real-data prediction. The earlier Nature Physics Plan v3 remains historical/parallel context.
- **Compute**: Current verified production floor is **2×V100 32 GB on two independent nodes**. The user may expand to more GPU and CPU nodes as gates pass; future capacity is not limited to those two cards. **H20 is explicitly excluded from future plans.** Express budgets in measured V100-equivalent GPU-hours, keep heterogeneous devices in separate pools, and never reduce seeds/horizons/baselines merely to fit two GPUs.
- **Dev workflow**: Mac local development and analysis → GitHub for code → Cloudflare R2 for canonical bulk data and transit → non-H20 compute workers stage immutable shards locally, run resumable jobs, and upload manifests/results.
- **Data preference**: Current holdings are only the starting tier. The user is willing to expand data across vendors, markets, exchanges, periods, and modalities when a pre-registered scientific gate justifies it. Treat historical $8–12k quotes as stale planning context; obtain current quotes and sample audits before purchase. The earlier $50k envelope is not permission to make ungated purchases.
- **Collaboration**: Solo independent research. No co-authors or advisor by default. Claude is key research partner; user can find endorsers/discussants when needed for backing or deep domain feedback.
- **Python env**: Always use conda (per global CLAUDE.md). Project env = `ecophys`, Python 3.11, conda path `/Users/howardwang/miniconda3/bin/python`.
- **Language**: Chinese primary in conversation; paper writing in English; code comments minimal.
