# V8 causal-memory-transplant audit

**Date:** 2026-08-13

**Frozen parent:** `observable-state-mechanism-search-v8@358cf9df3`

**Outcome/model access:** none

**Remote/GPU access:** none

**Final decision:** `V8_NO_SURVIVOR_PRIOR_ART`

## 1. Scope and decision

V8 asked whether an episode history, represented by an explicit external-memory capsule, carries a signed response
from a randomized source regime into an independently restarted computational economy. This is a materially cleaner
information source than the hidden-state targets retired in V6 and V7: the capsule can in principle be read,
randomized, erased and transplanted. The cleaner intervention fixes the earlier *identification* defect, but it does
not survive the prior-art gate as a Nature-level method or phenomenon.

| Candidate layer | N0 result | Final state | Binding reason |
|---|---|---|---|
| memory-transplant method | fails | `RETIRED_PRIOR_ART` | a 2026 memory-transplant protocol already separates architecture and content with a `2 x 2` factorial design, transplant conditions and preregistered validation controls |
| causal memory intervention | fails | `RETIRED_PRIOR_ART` | external memory is already treated as an editable intervention surface and compared under no-memory, with-memory and perturbed-memory conditions |
| cross-environment behavioral carry-over | fails | `RETIRED_PRIOR_ART` | Shachi explicitly transfers EconAgent/OASIS memory into a fresh cognitive task and lets agents carry state between stock and social environments, producing history-dependent behavior |
| behavioral/memory contagion | fails | `RETIRED_PRIOR_ART` | recent work directly studies cross-temporal bias propagation through memory and preference propagation across multi-agent networks |
| economy-level randomized interaction contrast | identified but standard | `RETIRED_PRIOR_ART` | the proposed contrast is the interaction coefficient of an ordinary cluster-randomized factorial experiment, not a new causal estimand or theorem |

The exact economic application and stronger semantic shams could produce a more rigorous specialist benchmark.
They do not restore Nature Machine Intelligence method novelty or Nature Computational Science phenomenon novelty.
The frozen N0 stop rule therefore fires before any transparent-agent fixture, model inference or generated outcome.

## 2. Primary-source attack matrix

| Neighborhood | Primary result checked | Exact collision with V8 | Residual role only |
|---|---|---|---|
| memory transplantation | [Memory Transplants for LLM Agents](https://openreview.net/pdf?id=AIJsjIqfsp), ICLR 2026 MemAgents workshop, introduces a protocol that independently varies memory architecture and content across a domain shift using a `2 x 2` factorial design, seven transplant conditions and six preregistered validation gates | V8 cannot claim the transplant protocol, factorial decomposition, frozen prompts, standardized export/import or basic negative-control idea as new | direct method oracle; V8's economy-level randomization and semantic sham would be stricter implementation details |
| economic LLM-ABM memory transfer | [Shachi](https://arxiv.org/abs/2509.21862) makes Config, Memory, Tools and LLM separately controllable; transfers OASIS/EconAgent memories into CognitiveBiases and carries agent state between StockAgent and OASIS | V8's broad phenomenon—history carried by explicit memory changes later behavior, including in economic agents and stock environments—is already demonstrated | direct economic-domain comparator; its small trial counts and exploratory validation leave room for replication quality, not first-phenomenon priority |
| causal memory manipulation | [Causal Intervention-Based Memory Selection](https://arxiv.org/abs/2605.17641) defines external memory as an editable intervention surface and scores each candidate under no-memory, with-memory and perturbed-memory conditions | adding `do(M=S)` notation or perturbed/sham capsules is not a distinct causal-memory primitive | baseline for memory perturbation and robustness controls |
| experience transfer | [ExpeTrans](https://aclanthology.org/2025.acl-long.520/) transfers textual experience from source to target tasks; [Echo](https://arxiv.org/abs/2604.05533) transfers structured experience between Minecraft tasks | source-history-to-target behavior transfer through explicit memory is occupied beyond economics | cross-task baselines |
| cross-temporal memory contagion | [Memory Contagion](https://arxiv.org/abs/2606.23195) constructs biased and clean memory stores, exposes future agents to them, uses controlled memory/retrieval manipulations and measures cross-temporal behavioral propagation | the narrowed claim that a source-induced response propagates to a new recipient through memory is directly occupied | bias-specific comparator; its model-specific and partly weak results are a warning against a universal law |
| cross-agent propagation | [Contagion Networks](https://arxiv.org/abs/2606.20493) defines a propagation matrix and studies preference propagation and topology-dependent regimes in multi-agent LLM systems | renaming the capsule effect behavioral contagion or proposing a propagation matrix does not recover phenomenon novelty | network-propagation baseline; its claims require independent replication |
| general multi-agent memory | [G-Memory](https://proceedings.neurips.cc/paper_files/paper/2025/hash/136a45cd9b841bf785625709a19c6508-Abstract-Conference.html) uses cross-trial, agent-specific hierarchical memory, and [Rememberer](https://proceedings.neurips.cc/paper_files/paper/2023/hash/f6b22ac37beb5da61efd4882082c9ecd-Abstract-Conference.html) reuses episode experience across different goals | persistent experience changing later agent behavior is established infrastructure | architecture and performance baselines |
| dynamic pricing with learning agents | [Tampubolon and Boche](https://arxiv.org/abs/1910.09314), [Bistritz and Bambos](https://proceedings.mlr.press/v139/bistritz21a.html) and [Turan et al.](https://proceedings.mlr.press/v242/turan24a.html) already couple online-learning users with adaptive pricing under resource constraints and evolving response | the rejected controller-gain by learning-rate phase-boundary idea is direct prior art and never enters candidacy | control baseline only |

The Shachi, causal-memory-intervention, Memory Contagion and Contagion Networks PDFs were downloaded, rendered
and visually inspected at their method and result pages. The OpenReview PDF endpoint was protected by a browser
challenge; its official indexed PDF text and workshop submission record were checked instead. The latter limitation
does not weaken the collision: the title, abstract and first method page explicitly state the factorial transplant
protocol and controls needed for the decision.

## 3. Formal reduction of the V8 estimand

Let `Z in {-1,+1}` be the randomized source regime, and restrict the capsule arm to
`C in {-1,+1}`, where `+1` is intact and `-1` is semantic scramble. Write

\[
\mu_{zc}=\mathbb E[Y\mid Z=z,C=c].
\]

The frozen V8 contrast is

\[
\tau_{mem}=\mu_{+,+}-\mu_{-,+}-\mu_{+,-}+\mu_{-,-}.
\]

Under the saturated effects-coded factorial model

\[
\mathbb E[Y\mid Z=z,C=c]
=\beta_0+\beta_Zz+\beta_Cc+\beta_{ZC}zc,
\]

direct substitution gives

\[
\tau_{mem}=4\beta_{ZC}.
\]

Thus V8's headline scalar is the standard source-regime by capsule-semantics interaction. If source economies,
donor capsules and recipient economies are randomized according to the frozen protocol, it identifies the effect
of the *compound assigned treatment* at the economy level. It is not automatically a natural indirect effect:
the realized capsule is a post-source-treatment object and its content differs with `Z`. Donor reuse also induces
clustering and must be reflected in randomization inference.

This is good experimental hygiene, but no new causal calculus follows. Semantic scrambling can help reject length,
serialization and position shortcuts; it still changes retrieval geometry and information content, so it cannot by
itself prove a unique semantic mechanism. Retrieval logs, shortest-sufficient-state oracles and explicit-label
controls remain mandatory if the design is ever reused.

## 4. Why the residual economic claim does not survive

The only residual after the direct method collisions is narrower:

> a signed donor-regime effect crosses a process boundary through memory and then changes an aggregate economic
> outcome under an exact mechanism.

This is a defensible application hypothesis, not yet a Nature-level scientific phenomenon:

1. Shachi already places memory carry-over inside EconAgent, StockAgent and cross-world economic/social
   simulations and reports downstream behavioral and market changes.
2. Memory Contagion already constructs source-biased versus clean stores and measures their effect on future
   agents; changing the recipient task to an economy changes the application, not the causal object.
3. The economic aggregation step is the known executable map from primitive actions to prices, allocation or
   congestion. Without a new signed law, scaling relation or invariant that survives model and mechanism changes,
   it adds a downstream readout rather than a new mechanism.
4. Existing evidence warns that the effect can be model- and content-specific. In Memory Contagion, the reported
   length effect appears in one older model while newer models show zero, and its authority-bias result fails in
   controlled multi-seed runs. That is incompatible with predeclaring a broad universal carrier law.
5. A result that disappears against an explicit source label or a shortest sufficient statistic is simply
   information transfer through a verbose representation. A result that survives those oracles may be interesting,
   but the current literature supplies no theoretical sign prediction that makes it a new computational-science law.

Improved power, more models, an order book and two exact mechanisms would make a stronger replication or benchmark.
They would not remove these conceptual collisions. Compute cannot turn stricter execution of an occupied design
into a new NMI method or NCS phenomenon.

## 5. Venue and resource consequence

- **Nature Machine Intelligence:** `NO_SURVIVOR`. The transplant, external-memory intervention, factorial contrast
  and propagation formalism are occupied. No non-equivalent method or theorem remains.
- **Nature Computational Science:** `NO_SURVIVOR_PRIOR_ART`. The economic recipient is an application extension;
  the plan has no new signed cross-mechanism law and no real scientific anchor.
- **Specialist route:** a preregistered, economy-level replication with semantic shams, transparent sufficient-state
  oracles and independent implementations could be publishable, but it is outside the unchanged Nature-level target.
- **Experiments:** none. The N0 gate fails before F0, so a toy CPU fixture would illustrate a standard factorial
  interaction and cannot alter the venue decision.
- **Data:** primary papers only; no generated agent actions, API calls, human data, market outcomes or paid data.
- **Compute:** local document/PDF work only; zero remote-host contact, zero V100/RTX2060 use and zero GPU-hours.

## 6. Re-entry condition

Do not reopen V8 by adding models, prompts, markets or capsule arms. Re-entry requires at least one of:

1. a formal causal estimand or guarantee provably unavailable from standard factorial intervention, mediation and
   memory-perturbation analyses under the same observations;
2. a prospectively signed cross-mechanism law with a theoretical reason for its sign and a falsifier that separates
   it from generic context transfer;
3. an independently measured scientific system in which the transferred state has external validity beyond
   generated computational-agent behavior.

Until then, the explicit state/reset protocol is retained as good experimental infrastructure, not as the next
archival headline.
