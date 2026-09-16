# Paper G: cis-regulatory intervention asset scope

PRIVATE / INTERNAL. 2026-09-14 NZ. Source/design preflight; no new topic, cycle or route status.

The bounded audit identifies usable experimental capabilities, but does not qualify a common bidirectional enhancer-response panel for independent mechanism prediction. Keep the exact designs separate. The missing contribution is not supplied by a larger guide count or a generic nonlinear interaction model.

## Allocation and supported evidence

The [allocation](../../../research/paper_g/cis_intervention_scope_start_20260914.yaml) freezes three primary works and at most two metadata sources. It follows initial design excerpts and precedes this final comparison. No candidate harvesting, F2/F3, forecast, scientific implementation, outcome payload, laboratory work or outreach is authorized. The previous turn made progress by adjudicating the knot candidate. The broader ICLR/ICML objective remains incomplete.

[Pacalin et al., CRISPRai](https://www.nature.com/articles/s41587-024-02213-3), published online in 2024 and in the 2025 Nature Biotechnology volume, provides simultaneous activation and repression at distinct loci. Selected design, readout and deposition sections distinguish a K562 Perturb-seq panel from Jurkat cytokine screens. The former uses a selected 19-gene panel with 82 single and 22 double guide constructs, not an exhaustive directional interaction matrix. The latter includes IL2 and IFNG regulatory-element libraries, FACS cytokine gates and guide enrichment; the IFNG library includes 625 bidirectional guide pairs. The paper also uses validation guides, epigenomic observations and primary-cell experiments. Do not reduce its hierarchy evidence to a single rescue score or claim this audit refutes it. Hundreds of guide pairs are not hundreds of independent loci or mechanisms.

[Chardon, McDiarmid et al., multiplex single-cell CRISPRa](https://www.nature.com/articles/s41467-024-52490-4), 2024, was read through indexed primary design/analysis/deposition excerpts. Random multiplex activation and scRNA-seq are used in K562 and iPSC-derived neurons with a 493-guide library. A main analysis partitions cells by presence or absence of each guide and tests neighboring gene expression. This supports activation-associated response mapping, but does not add simultaneous CRISPRi or automatically supply balanced pairwise contrasts. Joint guide/cell measurements may support further combination analysis; adequate coverage and joins have not been inspected. The paper names PRJNA1157910 and IGVFDS9078ZWQH / IGVFDS4021XJLW. A previous CRISPRi study using related guides is not automatically a matched bidirectional experiment.

[NAIAD, ICML2025](https://proceedings.mlr.press/v267/qin25g.html) supplies a direct small-data combinatorial prediction and acquisition parent. Selected model/design sections of its [December2024 v2 preprint](https://arxiv.org/html/2411.12010) use measured single-gene effects, learned embeddings and a nonlinear interaction component; the target can be a scalar phenotype. Its historical experiments are bulk combination screens, and its acquisition objective emphasizes high-effect combinations. It is not merely an additive baseline or a method for identifying enhancer causal order. Do not equate its sampled-combination evaluations with held-out-locus or bidirectional mechanism validation. The final conference methods were not fully reconciled with this preprint reading.

## Metadata-only findings

The indexed official [GEO GSE220976 record](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE220976) identifies a public SuperSeries with 66 sample entries and directs design details to SubSeries. That count is an archive count, not the number of independent experiments or a complete paired data matrix. No matrices, sequencing reads or outcome files were opened. A file-level guide/assay/replicate join remains unqualified.

The public [multiplex CRISPRa repository](https://github.com/shendurelab/multiplex_scCRISPRa_screening) contains README and directory metadata for guide design, preprocessing, differential-expression testing and visualization. The read is limited to the landing page and file listing; no scripts were executed or implementations audited. Presence of an analysis repository does not establish data licensing, frozen input manifests, experimental exchangeability or exact sample coverage. No general code/data reuse right was inferred.

## Two standard controls for any later truth contract

**C1: gated abundance does not identify a continuous expression distribution.** Let one population put probability 1/2 at expression0 and 1/2 at expression2; another puts 1/2 at0 and 1/2 at10. Both have the same fraction above threshold1, but means1 and5. A partition-based readout cannot distinguish their within-bin values. The same limitation applies to any guide-enrichment statistic computed from otherwise identical gated counts. This is a toy about information discarded by measurement, not a claim about actual CRISPRai distributions. More bins, quantitative fluorescence or transcript measurements can add information; the relevant observation model must be frozen.

**C2: a multiplex marginal contrast is not a specific pair contrast.** For independently balanced binary guide indicators A,B, compare response-probability tables, ordered as (00,10,01,11):

\[
p=(0.2,0.4,0.4,0.6),\qquad
p'=(0.1,0.5,0.5,0.5).
\]

Both have P(Y=1|A=0)=0.3, P(Y=1|A=1)=0.5, and identical B marginals. Yet p11-p10-p01+p00 equals0 versus-0.4. Thus guide-presence marginals alone do not determine the pair interaction. The full joint guide/outcome table distinguishes these examples immediately. This is not an intrinsic impossibility for multiplex single-cell data: it specifies why retaining joint assignments and sufficient combination coverage matters. Real guide co-occurrence need not be balanced, so its assignment model is an additional requirement.

Neither control is a new theorem or an empirical finding. Generic latent-phenotype/readout separation remains covered by the closed `g33_protein_assay_epistasis` formulation and its MAVE-NN parent. These controls are reusable contract checks, not a renamed candidate or a qualified re-entry trigger.

## Frozen preflight contract and stop decision

- **Estimands:** expression or sorted-population enrichment for the exact published guide pair, perturbation direction, cell context and observation window. Continuous expression, cytokine-gate probability, viability and molecular hierarchy remain distinct targets.
- **Assignment/interference:** retain both guide identities, orthogonal a/i machinery, co-occurring guides, biological replicate, cell line/donor and stimulation. Within-cell interactions are intentional; guide combinations and batches define the conditioning set. Guide identity is not a calibrated common molecular dose.
- **Lifecycle/replay:** require construct-to-guide mapping, delivery/selection, induction and stimulation timing, collection window, FACS gates and sampled fractions, transcript/guide capture and all relevant exclusions. A joined cross-study manifest is unqualified.
- **Rights/ethics/release:** public literature and metadata were read. Exact payload licenses, donor/use restrictions and distributable derivatives remain to be qualified before any access decision; no participants or materials are involved in this audit.
- **Untouched confirmation:** no data partition selected or accessed. Future splits must separate the intended units of transfer—loci, biological batches and contexts as appropriate—not random correlated cells alone. Published validation experiments are part of prior evidence, not newly untouched confirmation.
- **Independent replication:** activation-only K562/neuron data cannot independently confirm the same Jurkat a/i hierarchy by declaration. Shared intervention/readout support, dose calibration and independent paired coverage remain unqualified. This is not a claim that such assets do not exist elsewhere.
- **Cost/stop:** three primary and two metadata readings complete the allocation. Processing, matched reference acquisition and independent confirmation costs are unqualified. Stop this source chain; return only for an exact matched control/observation asset or a concrete contribution-changing mechanism. No automatic source expansion or generic calibration candidate.

Counts remain Paper G86 formulations /26 cycles /0 cards; detailed33 cycles /170 raw questions; inclusive42 /226. Graph330 /279 /1,946 is unchanged. Five source records bring the registry to1,218. Candidate0 /parked12; forecasts9 and re-entry audits176 /qualified0 unchanged. This is infrastructure progress: a concrete design map and two safeguards, not a qualified ICLR/ICML topic.
