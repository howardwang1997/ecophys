# Theory-exploration topology v5

**Canonical machine state:** `knowledge_graph.yaml`  
**As of:** 2026-08-13
**Current decision:** NCS `NCS_FEASIBILITY_CANDIDATE`; NMI `NO_SURVIVOR`

The graph is an append-only research-control artifact. It preserves v1/v2, exp144/145 and every retirement, then
adds the v3 state-closure/operator attacks, v4 phenomenon-first audit and v5 annual-rule-feedback gate. Graph proximity is not evidence of
novelty; each `covers`, `falsified_by` or `retired_by` edge records an equation-level judgement with a source or
exact counterexample.

```mermaid
flowchart TB
    ROOT["EcoMD separated mechanism + adaptive state"]

    subgraph V1["v1 immutable layer"]
        S15["S1--S5 all retired"]
        NMI1["mechanism excitation retired"]
        NCS1["relaxation exceedance under attack"]
        E144["exp144: stacked rank + fixed order effect"]
        S15 --> NMI1
        E144 -. "negative control" .-> NMI1
        E144 -. "raw order effect fails" .-> NCS1
    end

    ROOT --> V1

    subgraph NMI2["v2 NMI: target-conditioned primitives"]
        T1["T1 target completeness"]
        T2["T2 horizon threshold"]
        T3["T3 complementary targets"]
        T4["T4 target order"]
        MASK["masked-prediction identifiability"]
        CAUSAL["minimal causal/predictive states"]
        BLACK["Blackwell experiment order"]
        PART["task-family partition intersection"]
        MASK -->|covers| T1
        MASK -->|matrix-power attack| T2
        MASK -->|tensor-target coverage| T3
        CAUSAL -->|covers| T1
        PART -->|reduces| T3
        BLACK -->|covers| T4
    end

    subgraph NCS2["v2 NCS: attribution boundary"]
        ENV["prospective relaxation envelope"]
        DYN["dynamic event-study response"]
        DISC["simulator discrepancy / causal-twin limits"]
        SLOW["fixed hidden slow mode"]
        CLOCK["fixed Markov clock"]
        E145["exp145: both non-adaptive witnesses confirmed"]
        REG["registry: 2 development / 0 sealed / 8 reject"]
        ENV -->|rejects only class B| CLASS["model-class incompleteness"]
        DYN -->|identifies treatment path, not label| CLASS
        DISC -->|blocks residual attribution| CLASS
        SLOW --> E145
        CLOCK --> E145
        E145 -->|retires adaptation claim| CLASS
        REG -->|no C1 pair| CLASS
    end

    subgraph V3["v3: closure, memory and long horizon"]
        C1["C1 controlled state closure"]
        C2["C2 semigroup-memory repair"]
        C3["C3 Poisson operator calibration"]
        PSR["PSR + operational Markov + PSR-f"]
        MZ["process recovery + Mori-Zwanzig"]
        POIS["Poisson/Stein + Koopman + invariant loss"]
        XOR["noisy XOR: one-step/stationary alias"]
        PSR -->|covers| C1
        MZ -->|covers| C2
        POIS -->|covers| C3
        XOR -. "missing-state blind spot" .-> C3
    end

    NMI1 --> NMI2
    NCS1 --> NCS2
    NMI2 --> DNMI["NMI_NO_SURVIVOR"]
    NCS2 --> DNCS["NCS_C0_FAIL_IDENTIFICATION"]
    DNMI --> V3
    DNCS --> V3
    V3 --> DV3["V3_NO_SURVIVOR"]

    subgraph V4["v4: phenomenon-first human / algorithm / agent audit"]
        P1["P1 population response spectrum"]
        P2["P2 aggregate-to-micro loss"]
        P3["P3 strategic memory breaks"]
        POP["dynamic markets + institutional response + effect surrogacy"]
        MICRO["same-protocol macro--micro dissociation"]
        RESET["no randomized erase/replay witness"]
        POP -->|covers| P1
        MICRO -->|covers| P2
        RESET -->|no witness| P3
    end

    DV3 --> V4
    V4 --> DV4["V4_NO_SURVIVOR"]

    subgraph V5["v5: annual endogenous market-rule feedback"]
        RULE["RTS 11: ADNT_y -> band/tick_(y+1)"]
        MIX["ADNT_(y+1): about 9 treated months"]
        AMF["AMF: circularity already known"]
        FCA["FCA: one-step effects already known"]
        DATA["ESMA 2017--2025 + sealed FCA 2021--2026"]
        RD["robust multi-cutoff + discrete RD"]
        CAND["repeated next-input discontinuity"]
        RULE --> MIX --> CAND
        AMF -->|narrows novelty| CAND
        FCA -->|mandatory baseline| CAND
        DATA -->|conditional contract| CAND
        RD -->|retires NMI method| CAND
    end

    DV4 --> V5
    V5 --> DV5["NCS feasibility only / NMI no survivor"]
    DV5 --> CPU["separately frozen generated Mac-CPU preflight"]
    DV5 --> LOCK["real values / workers / GPUs locked"]
```

## Exact reductions retained

For task family `F`, define parameter equivalence by equality of every optimal predictor. Then

\[
\sim_{\mathcal F_1\cup\mathcal F_2}
=\sim_{\mathcal F_1}\cap\sim_{\mathcal F_2}.
\]

This explains complementary targets as ordinary partition refinement. It is not a new theorem.

For any bounded finite path `r_0,...,r_L`, the fixed chain

\[
P(i,i+1)=1\;(i<L),\qquad P(L,L)=1,\qquad f(i)=r_i
\]

satisfies `delta_0 P^ell f=r_ell`. Thus a finite response path, including one outside a stricter baseline envelope,
does not identify adaptation without a state-completeness or structural restriction. Exp145 verifies this exact
construction and the simpler fixed slow-mode exceedance.

For the v3 noisy-XOR warning,

\[
X_{t+1}=X_t\oplus X_{t-1}\oplus E_t,
\qquad E_t\sim\operatorname{Bernoulli}(\varepsilon),
\quad 0<\varepsilon<\tfrac12.
\]

The pair state has a uniform invariant law, so the observed marginal and one-step kernel exactly match an iid
Bernoulli chain. The three-time parity law is nevertheless correct with probability `1-epsilon`, not one-half.
Thus one-step and invariant-measure calibration can both be perfect while the observed multi-time process is
wrong. This elementary counterexample is a scope control, not a new theorem.

## Current cut through the graph

| Object | State | Decisive evidence | Permitted reuse |
|---|---|---|---|
| v1 S1--S5 | retired | SCM/OPE, CRL, PSR/bisimulation, response/averaging and composition coverage | negative history and baselines |
| v1 NMI mechanism excitation | `RETIRED_PRIOR_ART` | stacked observability, switching ID, active design and event-layer information conservation | none as a method claim |
| v2 NMI T1/T3 | `RETIRED_PRIOR_ART` | masked-prediction task-family theorems, minimal predictive states and partition intersection | task-design background only |
| v2 NMI T2 | `RETIRED_PRIOR_ART` | matrix-power ambiguity; horizon is not monotonically identifying | model-specific diagnostic only |
| v2 NMI T4 | `RETIRED_PRIOR_ART` | Blackwell comparison/garbling | correct terminology and oracle |
| NCS relaxation exceedance | `RETIRED_IDENTIFIABILITY` | exp145 plus discrepancy and causal-twin identification limits | prospective model-checking diagnostic |
| intervention metadata | `NO_DATA_CONTRACT` | 10 cases, no untouched replication | two development cases only |
| v3 C1 state closure | `RETIRED_PRIOR_ART` | controlled PSR, operational Markov condition and PSR-f completion | probe-relative model check only |
| v3 C2 memory repair | `RETIRED_PRIOR_ART` | process-recovery task bound and data-driven Mori--Zwanzig | reduced-dynamics baseline only |
| v3 C3 operator calibration | `RETIRED_PRIOR_ART` | Poisson/Stein identities, long-term Koopman and invariant-measure training | baseline after state closure only |
| v4 P1 population response | `RETIRED_PRIOR_ART` | dynamic human/LLM markets, institutional comparisons and effect-surrogacy work; no signed law/sealed pair | lower-claim benchmark only |
| v4 P2 aggregation loss | `RETIRED_PRIOR_ART` | direct same-protocol macro--micro dissociation | mandatory warning/baseline only |
| v4 P3 strategic memory | `RETIRED_NO_WITNESS` | no randomized erase/replay market dataset with independent replication | none until a true causal break exists |
| v5 NMI threshold-feedback method | `RETIRED_PRIOR_ART` | robust bias-corrected, multi-cutoff and discrete-running-variable RD | estimation oracle only |
| v5 NCS annual feedback | `ATTACKING` | exact statutory clock and blind support survive; exp147 failed before task dispatch on sandbox semaphore access, so no statistical evidence exists | exp148 serial CPU repair only |
| v5 cutoff pool | restricted | 80/2,000 share RTS 28 boundaries; 600/9,000 have low-price zero first stages | cutoff 10 plus price-qualified 600 primary |
| v5 data state | conditional | ESMA reusable; FCA documented API/OGL path; price/corporate actions unfrozen | no instrument pairs yet |

The graph has 188 nodes after recording the exp147 pre-task execution failure. NMI has no theorem or estimator
ready for human novelty audit. NCS has a
specific real mechanism and a conditional data route, but no empirical effect. One schema query disclosed a single
2021 value for `ROROCEACNOR1`; it is permanently excluded. No FITRS ZIP, outcome pair, remote worker or GPU was
opened, and both V100 workers and the RTX2060 remain outside the queue.

## Validation

```bash
conda run -n ecophys python -m ecomd.research.theory_graph \
  research/theory_exploration/knowledge_graph.yaml
conda run -n ecophys python -m ecomd.research.intervention_registry \
  research/theory_exploration/intervention_registry_v2.yaml
```

The validators enforce typed endpoints, candidate histories, attack/retirement edges, metadata-only intervention
cases, zero opened records and the prohibition on automated novelty `PASS` states.
