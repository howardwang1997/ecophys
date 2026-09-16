# Paper G protein stability curve intake

PRIVATE / INTERNAL — 2026-09-14. Excluded from public evidence.

The bounded intake does not establish a distinct new ML question. The generic full-curve target and the proposed heat-capacity mechanism have direct parents. This does not settle the accuracy achievable by future methods or close protein-stability research.

[SCooP (2017)](https://academic.oup.com/bioinformatics/article/33/21/3415/3892394) already predicts a protein's temperature-dependent free-energy curve through melting temperature, enthalpy and heat capacity. Its scope assumes monomeric, two-state folding and temperature-independent heat capacity. Selected equations, dataset construction and validation sections were read; its protein-level validation is not treated as proof of mutant transfer.

[HoTMuSiC (2016)](https://www.nature.com/articles/srep23257) predicts mutation-induced melting-temperature changes. The indexed thermodynamic discussion explicitly qualifies their relationship to reference-temperature stability when enthalpy or heat capacity changes. Only the abstract and selected indexed discussion were retained; full validation was not audited.

[Robic et al. (2003)](https://pmc.ncbi.nlm.nih.gov/articles/PMC208759/) already use comparative RNase H mutations to separate stability and heat-capacity effects and support an unfolded-state contribution. Similar native CD/activity does not establish exact structural identity. Aggregation restricted complete calorimetric comparison, and the residual structure itself was not resolved. The source supplies a useful intervention lineage, not a new discovery or a qualified cross-family ML corpus.

[Ito et al. (2024)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11129621/) describe high-throughput mutant screening with dye fluorescence during heating. Their selected method extracts an operational melting temperature from a curve derivative. This does not by itself qualify each mutant's equilibrium free-energy curve or heat capacity. The full DSC comparison and reversibility coverage were not audited. No blanket failure of DSF, or absence of suitable data elsewhere, is asserted.

Two elementary controls sharpen the target. Use unfolding free energy, absolute temperature, fixed pressure and solution conditions, and the constant-heat-capacity approximation. For mutant-minus-wild-type free energy,

\[
D(T)=a+b(T-T_0)+c\,q(T),\qquad
q(T)=(T-T_0)-T\log(T/T_0),\qquad
D''(T)=-c/T,
\]

where \(c=\Delta\Delta C_p\). Even at \(c=0\), an entropy difference permits an affine, nonconstant effect. Rejecting a constant offset therefore does not establish heat-capacity change. A curvature claim must compare against the affine null. Curvature alone still does not identify its microscopic origin.

Nor do one free-energy value and one melting point determine the full curve. For \(T_m\ne T_0\), set

\[
r(T)=q(T)-q(T_m)\frac{T-T_0}{T_m-T_0}.
\]

Then \(r(T_0)=r(T_m)=0\) and \(r''(T)=-1/T\). Adding \(\epsilon r\) to a curve preserves its reference free energy and its zero at \(T_m\), while changing its heat capacity. Restrict sufficiently small perturbations to an interior admissible family; the construction does not promise preservation of all roots or physical constraints for arbitrary perturbations. It says nothing about identifiability from complete, correctly modeled thermograms.

These are standard thermodynamic consequences, not new theorems, experimental findings or demonstrated failures of a learned model. They make future controls more precise but do not themselves meet the target contribution.

Stop the generic intake. A future attempt needs a concrete learning advantage or a genuinely unresolved intervention question against these parents. A final F3 truth contract was not demanded at this stage; the missing element is the contribution itself. Database descriptions remain metadata-only locators. No source payload, predictor execution, scientific implementation or experiment was accessed.

Four retained primaries, two controls, no new question/cycle/status/forecast/card. Paper G89/29/0; detailed36/173; inclusive45/229; graph333/279/1980; evidence1271. Broad ICLR/ICML topic goal remains incomplete.
