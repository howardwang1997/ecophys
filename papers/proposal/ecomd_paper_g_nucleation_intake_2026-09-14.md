# Paper G nucleation source intake

PRIVATE / INTERNAL — 2026-09-14. Selection reasoning, excluded from public evidence.

Three primary works and one author archive establish a narrower next step. Generic prediction of induction-time distributions and competitive polymorph selection have direct parents. A distinct source-defined mechanism question remains: does a laser-generated bubble trigger nuclei through interfacial concentration or through pressure waves at collapse? A discriminating observation/control and a concrete ML contribution are not yet specified well enough to count a raw question or candidate.

| Source and selected depth | Implication |
| --- | --- |
| [Sun and Ceder, 2017](https://escholarship.org/content/qt14w6449n/qt14w6449n.pdf), competitive-induction section, equations 5–7 | Exponential races already explain different polymorph outcomes under identical preparation and common conditional waiting times among winners. This does not establish every real system follows constant hazards or first-nucleation-wins. |
| [Yerdelen et al., 2023](https://strathprints.strath.ac.uk/83716/12/Yerdelen_etal_CGD_2023_Machine_learning_derived_correlations_for_scale_up.pdf), selected methods, equation 1, conclusion and availability | ML already predicts nucleation rates and growth lags, hence induction-time distributions, from hydrodynamic features. The study has 131 observations and repeats solution heating/cooling cycles. It names an open data deposit; no payload or full validation audit was performed. |
| [Ndukwe-Ajala et al., 2025](https://journals.aps.org/prresearch/pdf/10.1103/kr3g-67gz), selected pressure experiment, model and discussion | Pressure suppresses laser-triggered KCl crystal yield. The authors explicitly allow both interface concentration and collapse-wave pathways. Their model fit is not a unique identification of either pathway. Supporting data are available on request. |
| [Edinburgh CsCl imaging archive](https://datashare.ed.ac.uk/handle/10283/8952?show=full), metadata/file listing | Public CC BY4.0 raw images and montages are organized by paper figures, with frame-rate labels including 180–200 kfps. This is a plausible observation lead, not a qualified complete event/negative or timing-truth panel. No payload, preview, contents text or full imaging-paper methods were read. |

Two standard controls

Let latent nucleation times T_i be independent exponentials with rates lambda_i, and observe only the first event time T and winning polymorph I. With Lambda=sum_i lambda_i,

    f(T=t,I=i) = lambda_i exp(-Lambda t),
    P(I=i) = lambda_i/Lambda,
    T | I=i ~ Exp(Lambda).

Thus winner-conditioned mean times can coincide despite very different isolated rates. For lambda_1=1 and lambda_2=0.01, both winning classes have mean time 1/1.01; the second isolated clock has mean100. This is the classic competing-risk construction, not a new mechanism. Under these assumptions, winner proportions plus total survival identify the rates. Growth delays, transformations and nonstationary conditions require a different observation model.

For the bubble question, distinguish the first visible crystal from nucleus formation. Write T_visible=T_nucleus+G, with an unknown nonnegative growth/detection lag G. Suppose collapse occurs at20 microseconds and the first visible crystal at30. Nucleation at5 followed by lag25 and nucleation at25 followed by lag5 give the same observation. These are illustrative values, not measurements. A calibrated lag bound can resolve timing in suitable cases; establishing causality still requires an appropriate intervention.

What remains scientifically unresolved

In the pressure study, both candidate pathways can increase nucleation with bubble size. The shared pressure trend therefore cannot choose between them. The KCl pressure experiment and CsCl imaging are different chemical systems; they are not a matched causal contrast. The paper's nine sequential videos per pressure are not nine independently prepared experiments. Its high-pressure extrapolation is a proposed future test, not an established universal switch-off law.

The next bounded preflight will inspect the named imaging resource and primary methods for laser/camera synchronization, detection-lag calibration, complete event and negative selection, independent units, internal versus external bubbles, and a same-solute perturbation that separates the two pathways. At most two additional primary works are allocated. This is reading and metadata work only; no outcome access, implementation, training, experiment or outreach is authorized. Stop if only illustrative visible-event sequences are supported. Source availability alone does not establish a new ML topic.

No generic calibration-transfer re-entry, family-wide closure, F2/F3, forecast or machine card. Paper G remains89 formulations/29 cycles/0cards; detailed36 cycles/173raw; inclusive45cycles/229raw. Graph333nodes/279edges/1980locators unchanged; evidence1258; candidate0/parked14. Administrative validation follows separately. Broad goal incomplete.
