# Paper G battery diagnostic intake

PRIVATE / INTERNAL — 2026-09-14. Excluded from public evidence.

No distinct new question was formed within four retained primary works. Rapid health prediction, constrained diagnostic reconstruction and the inadequacy of capacity-only mechanism validation have existing parents. The useful outcome is a sharper baseline and interpretation contract.

[Gasper et al. (2025)](https://research-hub.nlr.gov/en/publications/searching-for-a-pulse-evaluating-the-use-of-rapid-dc-pulses-for-d/) report different outcomes for rapid capacity and safety-target prediction. Retained evidence is institutional abstract/publisher excerpt depth; detailed target construction is not independently qualified here. Their results do not prove universal information absence.

[Che et al. (2025)](https://doi.org/10.1016/j.joule.2025.102010) already reconstruct diagnostic curves from operational fragments with DVA-constrained latent states. Selected methods describe low-rate tests and harvested-electrode OCP curves. Their 94-cell rate-test cohort is a subset of the 236-cell cohort: cohort entries must not be counted as distinct independent cells. A reconstructed voltage curve does not by itself establish unique latent mechanism recovery.

[Li et al.](https://arxiv.org/abs/2311.05482), read at abstract depth, already compare degradation models with similar capacity/resistance fits and different degradation-mode fits. No full-model verification was performed.

[Jamil and Kapadia (2026)](https://arxiv.org/pdf/2605.15351), a preprint, use a positive diagonal generator for battery relaxation. Their discussion explicitly acknowledges the multi-exponential objective and effective, window-conditioned modes. The Nyquist reconstruction includes a supervised cross-cell map. These qualifications must accompany any comparison; they are not new empirical findings from this intake.

For that diagonal model, the following algebra is exact:

\[
A=-\operatorname{diag}(d_i),\quad d_i=\operatorname{softplus}(\theta_i)>0,\qquad
\mathbf 1^\top e^{At}v_0=\sum_i v_{0,i}e^{-d_it}.
\]

The sampled least-squares objective is joint exponential fitting under matching constraints. This establishes function-class equality, not equal optimizer performance. Initialization, warm starts, amplitude and offset restrictions, observation window, weighting and computational budget must all be matched. General non-diagonal generator models are outside this reduction.

Stability alone does not remove poor parameter sensitivity. With \(d>\epsilon>0\), consider two positive-amplitude decays:

\[
f_\epsilon(t)=\tfrac12e^{-(d-\epsilon)t}+\tfrac12e^{-(d+\epsilon)t}
=e^{-dt}\cosh(\epsilon t).
\]

For \(0\le t\le T\),

\[
0\le f_\epsilon(t)-f_0(t)
\le \tfrac12e^{-dt}(\epsilon t)^2\cosh(\epsilon T).
\]

The rates remain strictly positive. Near coincidence, separating the modes changes the waveform only quadratically. At coincidence, the separation derivative vanishes and amplitude allocation between identical modes is unidentifiable. This is a standard exponential-mixture control, not a new theorem, measured noise result, or demonstration that every distinct exponential mixture is unidentifiable. It does not invalidate reported diagnostic performance.

A useful new method would have to change the available information or achieve a defensible cost/error improvement against those baselines. A useful empirical study could instead resolve a specific mechanism or measurement-policy question. Neither was established here. No full final truth contract was demanded merely for F1; the missing piece is a distinct supported contribution.

The paired KIT resource and the large pulse archive are locators for future work, not qualified raw-data or execution contracts. Diagnostic scheduling was not established as a matched intervention. Stop this bounded generic chain; no broad closure of battery research, no claim of universal asset absence.

Four primary readings at unequal depth, two elementary controls. Paper G89/29/0; detailed36/173; inclusive45/229; graph333/279/1980; evidence1267. No question/cycle/status, F2/F3, forecast/card, outcome payload, scientific implementation, simulation/training, hardware, outreach, delegation or publication. Broad goal incomplete.
