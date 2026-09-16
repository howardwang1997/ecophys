# Paper G candidate memo: separating RNA population shifts from probe-induced emissions

**Status: private development memo; no qualified Paper G machine card.**

## Question

In the 236-nt HIV-1 Rev response element (RRE), the number and weight of inferred structural clusters change between 2.5 and 5.0 mM NMIA. Does the probe concentration change the native conformer population, or does it change the modification process and therefore the mapping from conformers to observed reads?

Both outcomes matter. A population shift would identify a chemically induced structural intervention. An unchanged population with altered emissions would show that concentration-aware inference is required before interpreting cluster weights biologically. A null result would still be useful if it is obtained with an independent, same-construct measurement.

## What is already established

Arnold et al. (2025) report two DRACO-inferred clusters at the lower NMIA concentration and an additional 9% cluster at the higher concentration, with a separate RT-stop/Rsample analysis also changing with concentration. The selected NMR experiments concern smaller hairpins and imino-water exchange, so they do not provide an independent population measurement for this RRE.

DRACO already models correlated mutation information and has published simulations showing dependence on read length and coverage. Its reporting summary gives a 5,000× minimum coverage from simulations and ignores mutation frequencies below 0.005; those values are method-specific operating points, not evidence that the Arnold et al. cluster change is biological. DRACO also used COMRADES contacts as orthogonal support for an alternative SARS-CoV-2 3′-UTR conformation, but that is a different RNA and a different intervention.

Sherpa et al. (2015) physically separated alternative RRE conformers by native-gel migration before performing in-gel NMIA SHAPE. Their structural assay used a 232-nt RRE with a 3′ structure cassette. This establishes a useful independent separation method, but it does not yet match Arnold et al.'s 236-nt construct, preparation, or the paired 2.5/5.0 mM intervention.

## Why the obvious control is insufficient

Randomly deleting high-dose mutation indicators is not an exact low-dose experiment. For a fixed-conformer first-hit model with high-dose site probability (p_H), low-dose exposure ratio (alpha), the physical probability is

\[
p_L=1-(1-p_H)^\alpha.
\]

A fixed stochastic map from one observed high-dose bit to one low-dose bit has an affine mean (a+(b-a)p_H). It cannot reproduce this nonlinear relation for all (p_H). Simple thinning agrees only to first order:

\[
\alpha p_H=p_L-\frac{\alpha(1-\alpha)}{2}p_H^2+O(p_H^3).
\]

The control can therefore diagnose a first-order regime, but it cannot establish that a low-dose read set has the same likelihood as a physically low-dose experiment. Full event counts or a validated kinetic model could change this conclusion; a binary mutation record alone does not.

## A possible learning contribution

The most defensible ML formulation is a **joint latent-state and probe-kinetics model**. It would infer native conformer weights, site-specific emission parameters, and probe-induced coupling from paired dose/time data while predicting an independently measured observable. The model should be compared with:

1. independent mixture fitting at each dose;
2. a shared-population model with dose-specific emissions;
3. a physically constrained kinetic model without a learned residual;
4. a learned residual model under the same input and acquisition budget.

The decisive prediction is held-out structure or reaction kinetics for the same construct, not reconstruction of the same SHAPE-MaP reads. A useful positive result would be a dose-invariant population estimate that predicts the independent observable while the unconstrained mixture model fails. A useful null result would show that the two explanations remain observationally equivalent under the available intervention, closing the biological interpretation while retaining a measurement-method result.

## Required evidence before escalation

- Sequence alignment proving that the Sherpa construct and Arnold construct share the assayed RRE region and identifying the cassette difference.
- A same-construct independent observable, such as native-gel-separated populations or a validated kinetic readout, measured under the two NMIA conditions or under a dose-preserving intervention.
- A frozen dose, folding, and readout protocol with replicate-level data and an untouched confirmation partition.
- A prediction target that is unavailable to the cluster-fitting baseline.
- An outcome-blind cost comparison showing that any learned component adds information or reduces acquisition cost.

Without these items, “probe-aware deconvolution” remains a plausible method direction rather than an ICLR/ICML main contribution. The current recommendation is to keep the line as a bounded development lead and stop generic expansion of correlated-read clustering, contact inference, or post-hoc dose correction.

## Sources

- Arnold et al. (2025), *Investigating the interplay between RNA structural dynamics and RNA chemical probing experiments*, [Nucleic Acids Research](https://academic.oup.com/nar/article/53/7/gkaf290/8114316).
- Morandi et al. (2021), *Genome-scale deconvolution of RNA structure ensembles*, [Nature Methods](https://doi.org/10.1038/s41592-021-01075-w). The selected author manuscript reports the coverage and mutation-frequency operating points and the COMRADES validation: [PDF](https://pure.rug.nl/ws/portalfiles/portal/228551218/s41592_021_01075_w.pdf).
- Sherpa et al. (2015), *The HIV-1 Rev response element (RRE) adopts alternative conformations that promote different rates of virus replication*, [Nucleic Acids Research](https://pmc.ncbi.nlm.nih.gov/articles/PMC4482075/).

All claims in this memo are development evidence from published work. No raw sequencing, spectra, model weights, scientific implementation, simulation, or training was accessed or run.
