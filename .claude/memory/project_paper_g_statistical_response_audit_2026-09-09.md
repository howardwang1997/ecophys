# Paper G statistical fidelity and forced-response primary audit

PRIVATE / INTERNAL. Formal:
`papers/proposal/ecomd_paper_g_statistical_response_reentry_audit_2026-09-09.md`.
Contract:`research/paper_g/statistical_response_reentry_audit_20260909.yaml`.

Decision not_trigger; zero removed blockers or candidate harvest. Three targets
are distinct: finite paired-window moments, long-run physical measures, and
responses to specified impulses or held forcing. No matched primary disagreement.

Park et al.2411.06311v2 (NeurIPS2024 metadata separately confirmed) already study
statistical fidelity, Jacobian training and unrolling. Strong generated-orbit
C1 control and typical shadowing are additional conditions, not ordinary test
loss. Symbolic NODE2608.22112v1 AppendixC bounds paired-window statistics;
that does not contradict the physical-measure result. Falasca2506.22552v8 is a
direct parent for full/partial observation, stochastic closure and forced response.
Final conference text is not silently equated with a later arXiv version.

Retained elementary controls: mean and population-standard-deviation vector
errors are bounded by paired RMSE. Stable flows -epsilon*x and epsilon*(1-x)
have equal derivatives and small fixed-window differences but distinct physical
measures as their common relaxation rate vanishes. Adding y=1-x gives exact
conservation. This is nonuniformity in a family, not a fixed-gap theorem refutation.

Stable isotropic OU drifts -gamma*I+(2*pi*k/tau)*J have identical full sampled
path laws and sampled mean-map Jacobians. The same held force separates them;
grid-time instantaneous resets do not. This is classical system aliasing, not
a failure measured in the source triad or a new cycle29 impulse counterexample.

Future work needs a contribution beyond these parents and explicit relaxation,
sampling, generator and action assumptions. No new cycle, F3, forecast, card,
scientific implementation, outcome access or compute. Paper D evidence roles
and the broader Paper G objective remain unchanged.

Verified 2026-09-09T09:12:10Z: graph293 /edges274 /locators1261; evidence895;
re-entry111 /qualified0; cycles21 /raw133 /cards0 unchanged. Scoped canonical
validation, source/contract/trigger parity,18 existing tests and git diff --check
passed. Receipt:`logs/private/paper_g_statistical_response_20260909_verification.md`.
