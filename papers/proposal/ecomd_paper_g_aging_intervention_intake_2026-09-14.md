# Paper G alloy-aging intervention intake

PRIVATE / INTERNAL — 2026-09-14. Bounded source-selection analysis, not public scientific evidence.

No distinct raw question emerged from three selected primary works. In particular, vacancy trapping and vacancy preservation are compatible effects, not mutually exclusive explanations. No new cycle or route is counted. The allocation ceiling was four raw questions, two quick screens and six primary works; the source chain stops early rather than filling these limits.

| Work and reading depth | What it contributes to selection |
| --- | --- |
| [Madanat et al., 2020](https://doi.org/10.1103/PhysRevMaterials.4.063608): publisher abstract and indexed author-manuscript methods | Heating-rate and pre-ageing experiments combine positron lifetime, hardness and resistivity. The authors already discuss competition between vacancy loss and precipitation. Post-treatment spectroscopy is distinct from direct in-situ vacancy counts. |
| [Jain et al., 2023](https://doi.org/10.1557/s43578-023-01245-w): selected mechanism, methods and availability | Neural-potential kinetic Monte Carlo already studies cluster-mediated vacancy trapping. Its fixed-vacancy periodic cell, approximate migration barriers and rescaled clock define its scope. Configurational accuracy alone does not certify every kinetic rate. The stated data route is author request. |
| [Sahoo et al., 2025](https://www.sciencedirect.com/science/article/pii/S1359645425002198): indexed primary introduction/model scope/summary | Pre-ageing and two-step quenching have an existing experimental comparison of storage stability and formability, with vacancy and work-hardening models. This is a direct parent for the proposed broad trade-off; model-derived vacancy equivalence is not full experimental state matching. |

Full supplements and raw measurement archives were not reviewed. Unrelated recommended-article text was excluded from the third work. Other initial search hits, including tabular alloy-property datasets and DSC prediction, were not developed into questions or a generic calibration-transfer revisit.

A minimal coexistence control

Let f, b and L be normalized free, trapped and lost vacancy populations. At fixed low temperature, suppose trapping occurs at rate a, free vacancies are lost to sinks at rate lambda, traps are unsaturated, and release is negligible. With f(0)=1 and b(0)=L(0)=0,

    df/dt = -(a + lambda) f
    db/dt = a f
    dL/dt = lambda f
    f + b + L = 1.

Then f=exp[-(a+lambda)t] and b=a/(a+lambda) * (1-exp[-(a+lambda)t]). The no-trapping reference has f0=exp(-lambda*t). At a=lambda=t=1, the trapped case has less immediate mobile population, exp(-2)<exp(-1), but more retained population:

    f+b = (1+exp(-2))/2 > exp(-1),
    (f+b)-f0 = (1-exp(-1))^2/2 > 0.

Thus trapping can suppress present diffusion and preserve vacancies simultaneously. In the separately specified limit of rapid subsequent release before appreciable sink loss, the retained population becomes available again. This standard rate-model calculation does not predict real alloy strength, prove an optimal heating protocol, or identify which mechanism dominates a particular experiment. No numerical simulation was performed.

The decision is narrower than a topic-family closure. Generic thermal-path dependence and ML-assisted aging have direct parents, and the apparent trapping/protection contrast lacks exclusive predictions. A future empirical question needs a particular controlled response for which refittable coupled trapping/release/loss models actually disagree. It does not need a new theorem or architecture. A history-blind property regressor is too weak a comparator for such a question.

Stop this bounded chain and move to another unsaturated native intervention. No family saturation or new re-entry gate is imposed. Complete matched-control and public-payload support remains unqualified; this is not a claim that no such resource exists.

Paper G remains 88 formulations / 28 cycles / 0 cards; detailed ledger 35 cycles / 172 raw; inclusive history 44 cycles / 228 raw. Graph 332 nodes / 279 edges / 1965 locators is unchanged. Three evidence records bring source accounting to 1239. No outcomes, scientific implementation, experiments, delegation, forecast or machine card. Completion validation is recorded separately.
