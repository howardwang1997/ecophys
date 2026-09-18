---
name: gamma-activation-2026-09-19
description: Merged GAMMA-led paper ACTIVATED 2026-09-19 (D0 pre-hash amendment to 2026-10-09, Annex C-12); no MacBook experiments of any size; pre-freeze build window and campaign calendar
metadata:
  type: project
---

PI decision `pi_gamma_activation_d0_amendment_20260919` (authorization text: "激活，但是不要在 MacBook 上面做任何实验，都在远程的服务器上面做"), recorded 2026-09-18T14:30Z / 2026-09-19 local:

- **Activation**: route `reexploration_merged_gamma_led_paper` un-parked to **active**; the 2026-09-12 withhold lifted; the D1 authorization chain (pi_reexploration_d1_authorization_20260906) resumes. Venue per the PI 2026-09-18 directive: **ICML 2027 main track**, market-physics framing ("training identification through a discrete mechanism layer"). Paper D reported submitted to ICLR 2027 by the PI on 2026-09-18.
- **D0 amendment**: outcome-blind freeze date 2026-09-19 → **2026-10-09**, pre-hash (no freeze sha256 existed, no [TO BE PINNED AT D0] field filled, no outcome accessed). Prereg v2 edited at all eight pin sites + errata entry **C-12** (C-11-lawful; mechanism named by the 2026-09-08 calendar proposal). R2 archive path → `r2://ecophys/alpha_cube_d0_20261009/`. Annex B(a)–(d) convention constants **ratified as pinned**. Campaign-anchored forecast resolve_by dates re-based +20 days in the decision record + C-12 (ledger file untouched — existing entries are validator prefix-protected and outcomes are strictly boolean); merged gate → 2026-11-20, gamma-theorem gate → 2026-10-09.
- **Compute-location rule (binding, supersedes ops-plan Mac-legal classifications for items 9–10)**: NO experiment of any size on the MacBook — including CPU smokes and dry-runs. All execution on remote workers via ssh. Mac keeps document authoring (analyzer contract doc itself is Mac-legal), governance, git, seconds-scale checks.
- **Calendar**: pre-freeze builds 09-19 → 10-09 (item 8 analyzer contract = the long pole, derive from frozen C1–C16/G1–G12/Annex B + adversarial audit; item 9 cleanup scripts, dry-runs remote; item 10 reflexive policy, smokes remote, not freeze-blocking before D0+12; re-verify the 2026-09-08 regression battery remotely). D0 freeze session 10-09 per prereg §1.3. Stage 1 ~650 V100-h (19–20 wall days), conditional Stage 2 ~410 V100-h; 4-week hard ceiling **2026-11-06**; shrink ladder unchanged. Forecast `d1_merged_gammas_led_paper_gate` (0.18/0.34/0.55) resolves at the outcome-blind D-1 exit gates, resolve_by re-based to 2026-11-20.
- **Compute environment at activation**: V100 cold-data migration done 2026-09-19 (see [[v100-disk-migration-2026-09-19]]): v100bts `/data` 153G free (~32%); v100ts `/data` 70G free (~14%). Prereg §8.3 makes ≥40% free a **STOP-class launch prerequisite** — both nodes are currently BELOW it, so the physics-bulk decision (phonon trees, `/data/results` 107G, graphene_physical_fd_dfpt 84G, phonon_offload) is REQUIRED before campaign launch, executing at D0-S1. Nodes are shared (phonon monitors, aletheia, atomistic fleet worker on v100bts GPU 0, cognition) — schedule GAMMA around them.

Related: [[v100-disk-migration-2026-09-19]], [[sandbox-launcher-hardening-2026-09-16]]
