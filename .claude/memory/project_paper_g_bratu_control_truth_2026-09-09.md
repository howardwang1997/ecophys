# Paper G Bratu and controlled-dynamics truth preflight

PRIVATE / INTERNAL. Formal:
`papers/proposal/ecomd_paper_g_bratu_control_truth_preflight_2026-09-09.md`.
Contract:`research/paper_g/bratu_control_truth_preflight_20260909.yaml`.

Partial capability; no removed blocker or re-entry. LEFNO v1.0 commit
80eb5a0d36b264a882be6ded172f016869eba478 and five source text hashes fixed.
Source bodies stay in a private temporary cache; only metadata in project.

Classical Bratu family gives explicit nonlinear stationary profiles,
lambda(theta)=8theta^2sech(theta)^2 and a unique fold theta*tanh(theta)=1.
Differentiating the stationary equation and pairing with the positive principal
eigenfunction proves sign(mu1)=-sign(lambda_prime). This supplies branch
stability and a positive null mode at the fold, not a new theorem or dynamic truth.

The local-NO NMI work already performs bifurcation/spectral analysis. Its control
follow-up2509.23975v1 explicitly uses approximate actuator self-tests and leaves
NO-controller deployment under original-plant mismatch open. Exact held-input
gain is integral exp(sA)B ds; an endpoint kick is a different action/approximation.
An elementary scalar stability reversal and small-a*tau null retained. No
instability of the paper's actual settings is inferred.

Source generator defines continuous ICs but exports transition arrays, uses
return-length acceptance and random transition-pair splits. Historical latent/RNG
replay, source-data lineage and project-compliant independent confirmation are
unqualified. FD and Chebfun are two constructions in one research lineage.
Tolerances are not certified dynamic error bounds. README declares CC BY-NC-SA4.0;
complete dependency/data rights and execution feasibility are not qualified.

No third neural-PDE measurement cycle, candidate, F3, forecast, machine card,
scientific implementation or outcome access. Next update needs a distinct
scientific contribution and complete same-target control/truth qualification.
Prior Paper D evidence roles and broader Paper G objective remain unchanged.

Verified 2026-09-09T08:56:26Z: graph293 /edges274 /locators1254; evidence890;
re-entry110 /qualified0; cycles21 /raw133 /cards0 unchanged. Scoped canonical
validation, source/contract parity, five source hashes,18 existing tests and
git diff --check passed. Receipt:`logs/private/paper_g_bratu_truth_20260909_verification.md`.
