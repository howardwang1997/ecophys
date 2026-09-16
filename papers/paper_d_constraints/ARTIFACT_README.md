# Paper D reproducibility material

The 2026-09-09 manuscript separates the original Advection FNO, U-Net and shallow-water
intervention cubes from post-hoc seed-distribution, forecast-skill and physical-history
analyses. The current PDF is `main.pdf`; selected scientific data views and generated tables
are in `revision/`. Every new analysis retains its evidence role and interval definition.

The current five-paper scientific review packet is maintained in the companion cognition
workspace under `output/five-paper-revision-20260909.zip`. Its scope is revised PDFs and
selected data views, not a full inference/training reproduction archive.

The existing `artifact_manifest.json` and dated full archives refer to their original versions.
The full experiment archive is retained for internal provenance and requires a current
publication whitelist before use as an anonymous submission artifact. The public builder
rejects internal deployment and incident records.

Compile this manuscript with `tectonic main.tex`. The original immutable checkpoint locks
bind 360 trained weights; the weights and source trajectories are stored separately from
the scientific PDF/data views. The manuscript specifies the theoretical assumptions,
original confirmation protocols, post-hoc estimands and uncertainty scopes.
