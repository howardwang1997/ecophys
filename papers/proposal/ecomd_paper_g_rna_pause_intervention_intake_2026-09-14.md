# Paper G RNA pause-intervention intake

PRIVATE / INTERNAL — 2026-09-14. Excluded from public evidence.

A concrete arrest-and-release experiment lineage was found. A distinct new ML contribution was not yet established. Retain the experimental lead without promoting it to a candidate or claiming pause-aware RNA prediction is new.

[TECprobe-LM (2025)](https://www.nature.com/articles/s41467-025-60425-w) uses a photoreversible roadblock followed by a downstream chase. It samples aliquots at different stages; individual RNA molecules are not tracked repeatedly. The paper validates known rearrangements and proposes variable-speed and time-resolved extensions. Those proposals do not establish an already executed pause-duration benchmark. This is a useful population-intervention asset; its transcript representation and restart behavior require their stated qualifications.

[Watters et al. (2016)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5497173/) explicitly distinguish length-resolved structural snapshots from direct pause measurements. Length should not be silently substituted for time, nor should this distinction be presented as a newly discovered defect of the assay.

[R2D2 (2021)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8061711/) selects structures using target-length experimental reactivity. Comparing that reconstruction against a sequence-only predictor without acknowledging this input would mix inference tasks. A downstream intervention prediction must withhold the target intervention's outcome from model input and selection.

[Wang et al. (2022)](https://www.sciencedirect.com/science/article/abs/pii/S0141813022020463), read at abstract/selected indexed excerpt depth, already model pausing and speed effects. [DrTransformer (2023)](https://academic.oup.com/bioinformatics/article/39/1/btad034/6992659) tracks evolving structural ensembles and supports specific pause sites. It is a kinetic heuristic, not a neural Transformer. These are stronger parents than a full-length equilibrium predictor alone.

[KinPFN, ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/hash/e3137c6e046fdf9f4af76fe08425f5cf-Abstract-Conference.html) already approximates folding-time distributions from a small context of first-passage-time examples. Its RNA reference examples come from simulation; the separate biological case study must not convert simulator-derived RNA times into wet-lab truth. Its input contract differs from predicting a new pause schedule with no target-condition samples. No empirical failure is demonstrated here, and generic few-sample distribution transfer is not opened as a new candidate.

One elementary control concerns the clock. With fixed length-specific state spaces and extension maps, let

\[
Q_n=k_0L_n,\qquad P_n=\exp(k_0L_n\tau_n).
\]

Changing \(k_0\) to \(\alpha k_0\) and every dwell \(\tau_n\) to \(\tau_n/\alpha\) preserves each propagator and hence the propagated distributions indexed by transcript length. This is standard kinetic scaling, consistent with the existing algorithm's discussion, not a new theorem. Independent physical dwell measurements remove this particular ambiguity. It is not an impossibility claim for known-clock interventions.

The desired future evidence would connect a specified pause intervention, calibrated timing and a downstream structural or functional response while holding the RNA sequence and relevant conditions fixed. That is a source-selection criterion, not a new question by itself. A learning method would still need a concrete benefit against kinetic parents with equal information. The missing piece is this supported contribution, not a mandatory complete final F3 truth contract at intake.

The next bounded source check is the single-molecule SRP refolding work cited as reference 18 in TECprobe-LM, including its force and timing controls. No experiment, payload access or implementation is authorized by this note. SRA/RMDB and code links remain locators. The 2026 memerna search hit is not counted as a primary methods review.

Six retained primary works at unequal depth and one standard control. No new question/cycle/status, F2/F3, forecast/card or family saturation. Paper G89/29/0; detailed36/173; inclusive45/229; graph333/279/1980; evidence1277; candidate0/parked14. Broad ICLR/ICML goal remains incomplete.
