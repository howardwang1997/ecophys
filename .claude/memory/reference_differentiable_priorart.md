---
name: reference_differentiable_priorart
description: "Literature check (2026-06-03) on the C1 'first differentiable Langevin/MD market simulator' claim — three broad versions are FALSE (prior art exists); only a narrow qualifier-stacked version survives. Use before writing any novelty claim for Paper A's methods pillar."
metadata:
  type: reference
---

**Lit sweep 2026-06-03 (WebSearch) to test C1 = "first differentiable Langevin MD market simulator."
Verdict: do NOT claim "first differentiable / first Langevin." Every broad form is occupied; only a
narrow, qualifier-stacked intersection is plausibly novel. The paper's moat is the FINDING (concave-
impact tail solve), not the artifact.** See [[project_neural_sde_tournament]], [[project_overview]].

**Dead versions (prior art):**
- "first **Langevin** market model" — Bouchaud & Cont (1998), *A Langevin approach to stock market
  fluctuations and crashes* (arXiv cond-mat/9801279). Plus a whole Langevin/Fokker-Planck market
  subfield (physics/0511129, cond-mat/0103600).
- "first **differentiable agent-based** market model" — active INET-Oxford / Farmer-group line:
  Dyer, Quera-Bofarull et al., *Gradient-Assisted Calibration for Financial ABMs* (ICAIF '23,
  dl.acm.org/doi/10.1145/3604237.3626857); Quera-Bofarull, Bishop, Dyer et al., *Automatic
  Differentiation of Agent-Based Models* (arXiv 2509.03303, **2025**); *Some challenges of
  calibrating differentiable ABMs* (arXiv 2307.01085, 2023). NOTE many use SURROGATE gradients
  (params→stylized-facts) or relaxed discrete decisions, not full pathwise BPTT — a real but narrow
  differentiator for us. Chopra et al. (arXiv 2207.09714) — already in our cite list — is this line.
- "first **differentiable** market simulator" — neural-SDEs, GAN/RNN LOB simulators all differentiable.
- "first **interacting-particle** market model" — herding/particle models (arXiv 1712.01085; herd-
  behavior-and-crashes; 2014 colloid-in-fluid analogy). Classical/analytic, NOT learned.

**The one survivable (narrow) claim:** the INTERSECTION is empty — nobody combines (MD-style with
*learned equivariant* interaction potentials, MACE-lite) × (markets) × (end-to-end pathwise BPTT at
N=10⁴). Equivariant-learned-potential machinery (NequIP/Allegro/MACE, arXiv 2204.05249) is atomistic
chemistry only. Survivable phrasing: *"to our knowledge first to combine learned equivariant
interaction potentials with end-to-end pathwise differentiability for market simulation — distinct
from classical Langevin/particle models (Bouchaud-Cont 1998) and from differentiable financial ABMs
with parametric rules + surrogate gradients (Dyer & Quera-Bofarull 2023–25)."* Three caveats: (1)
qualifier-stacked = reads incremental; (2) the differentiators (learned equiv. potentials + pathwise
BPTT at scale) are SYSTEMS contributions, not the interesting science; (3) "to our knowledge" + a
2025 competitor = scoopable on the methods axis.

**Decision:** demote C1 to a SECONDARY methods contribution phrased as "a differentiable MD-style
simulator with learned equivariant potentials — which is what makes the diagnose + calibrated
√-impact fix possible," cite Bouchaud-Cont and Dyer/Quera-Bofarull explicitly as related work, and
LEAD with the finding. Same discipline as the "Pareto ceiling" overclaim catch (both were
non-公认 premises that our own evidence/lit undercut). [[feedback_critical_thinking]]
