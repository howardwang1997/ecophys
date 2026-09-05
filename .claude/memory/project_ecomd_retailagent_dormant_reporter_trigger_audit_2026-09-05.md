# EcoMD RetailAgent and dormant-reporter trigger audit (2026-09-05)

## Durable decision

Two fresh sources were screened and both are `not_trigger`. No candidate harvesting, outcome
access, implementation, simulation, EcoMD run, SSH, or GPU work is authorized. No route node was
created.

## RetailAgent reusable results

RetailAgent evaluates binary long/flat actions on fixed historical price paths using

`A=sum_t (p_t-pbar) r_t`.

The complement `q=1-p` satisfies `A(q,r)=-A(p,r)` identically; this is a sign diagnostic, not an
executable best response. For any nonconstant fixed action trace and passive returns `r0`, response
maps `r_plus=r0+lambda(p-pbar)` and `r_minus=r0-lambda(p-pbar)` agree on the absent-policy path but
give `A_plus/minus=A0 plus/minus lambda sum(p-pbar)^2`. Fixed-path timing therefore has no sign or
magnitude bound for interactive deployment without restrictions on orders, impact, information,
latency, inventory, and strategic response.

The memory contrast is conditioned on a treatment-dependent switcher set. The paper reports
`w=0`: 1194/1500 both-action paths and `-62.8` bp; `w=1`: 1054/1500 and `-74.1` bp. Because constant
paths have `A=0`, the exact zero-extended means are `-49.9888` and `-52.0676` bp, a `-2.0788` bp
contrast rather than the conditional `-11.3` bp. This does not refute the explicitly descriptive
conditional claim, but it is not a population causal effect. An always-switcher effect is a
standard principal-stratification problem.

Interactive LLM asset markets are already implemented by Lopez-Lira, Henning et al., and StockSim;
performative prediction owns the generic deployment-feedback framing. EcoMD-only exploitability is
value in a chosen game, not field truth. Re-enter only for a frozen self-financing order grammar, a
new finite-sample deployment certificate, common complete semantics across two independent engines,
external response truth, and selection-aware all-attempt evaluation.

## Dormant-reporter reusable results

Brewster--Cluzel define a node's dormant/promiscuous class from its labelled deviations under all
ten fixed shocks relative to control, a pooled response threshold, noise level, and inference
objective. Panels are selected separately per network and fixed shock set. Their
held-out-initial-condition check largely preserves the internal result, so snapshot leakage is not
the transfer kill. The stronger blockers are that class status is learned after labelled pilot
responses, the spring rule consumes per-condition pilot means/spreads for every candidate, and no
panel is shown to transfer to unseen networks or shock families.

LOB levels are not stable costly sensors under recentering/refinement; EcoMD agents are latent and
split-dependent; engineered features reduce to feature selection; venue feeds would require real
cost/rights and synchronized labelled interventions. Scheduled announcement type is already known
and its dose/content varies; unscheduled failures lack repeated assigned support; EcoMD shocks give
only source-simulator labels.

SSPOC directly owns sparse sensor placement for classification. Robust Submodular Observation
Selection owns max-min observation design, non-unit costs, event detection, and approximation
guarantees. Under diagonal shared covariance, every pairwise squared Mahalanobis separation is
modular in the selected reporters, so worst-pair selection is a robust submodular instance. A
correlated-covariance lower-quantile approximation or finite-sample separation theorem could be
re-audited only if it is genuinely beyond those parents and is paired with native market reporters
and external shock truth.

Formal result:
`papers/proposal/ecomd_retailagent_dormant_reporter_trigger_audit_2026-09-05.md`.

