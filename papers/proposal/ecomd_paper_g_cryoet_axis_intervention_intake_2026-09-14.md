# Paper G cryo-ET axis-intervention intake

PRIVATE / INTERNAL — 2026-09-14. Excluded from public evidence.

No distinctive new formulation survives this source intake. Generic missing-wedge completion, physical dual-axis comparison and downstream evaluation already have direct parents. This is a narrow allocation decision, not closure of cryo-ET research.

[IsoNet (2022)](https://www.nature.com/articles/s41467-022-33957-8) already learns completion from rotated, additionally masked subtomograms. [DeepDeWedge (2024)](https://www.nature.com/articles/s41467-024-51438-y) combines masked restoration with denoising. Its main theoretical statement assumes symmetric mask sampling and nonoverlapping missing wedges; the authors explicitly distinguish this idealization from practical training and discuss nearly invisible oriented objects. No unrestricted recovery guarantee is attributed to either method.

[Wachsmuth-Melm et al. (2026)](https://link.springer.com/article/10.1186/s44330-026-00056-9) directly compare dual-axis on-lamella data with IsoNet and DeepDeWedge. A is acquired before B. Figure 4 combines half the frames from each approximately 65-electron/angstrom-squared series. The paper reports incomplete learned restoration, discusses accumulated dose, and identifies EMPIAR-13168/EMD-56089. These published comparisons are development evidence; archives were not accessed.

[Jones, Deshmukh and Pande (2026)](https://doi.org/10.1107/S2059798326001166) already evaluate template matching, subtomogram averaging and segmentation, and propose an FSC-based loss. Their selected particle-detection comparisons use references curated from raw-data processing/averaging. They do not furnish independent truth for every rare membrane structure. A generic downstream benchmark or Fourier loss is therefore not a new contribution.

Two standard controls constrain any later formulation:

1. In a finite-grid Fourier-mask model, paired measurements M_A F x and M_B F x cannot distinguish x from x+h when F h lies in the common unobserved region. Small real perturbations can preserve positivity around a positive baseline. This does not construct a biologically valid membrane-topology twin or assert a universal continuum tomography impossibility. Physical axis rotation expands measured support; software rotation does not create an independent observation of the same specimen.
2. Let a frame acquired at cumulative delivered dose D_j measure P_j x(D_j). Discarding other recorded frames does not change D_j. For x(D)=x0 exp(-kD), thinning cannot substitute x(D_j/2) for x(D_j). This distinction vanishes for k=0. The control does not quantify damage in the cited study or invalidate its observed comparison. A true acquisition-budget claim needs delivered history as well as retained signal budget.

Thus neither a more isotropic image nor agreement with the combined reconstruction alone provides complete structural truth. No new empirical contrast beyond these parents was established, and no full final truth contract was imposed at intake. Stop the generic completion chain; retain the acquisition/support conditions for a later concrete question.

Four primaries at selected depth and two standard controls recorded; no new question/cycle/status/F2/F3/forecast/card/saturation. Paper G89/29/0; graph333/279/1986; evidence1299. No outcome payload, implementation, simulation, training, hardware, outreach or delegation. The ICLR/ICML objective remains incomplete.
