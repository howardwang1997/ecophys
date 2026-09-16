# Paper G dynamic-PDE truth-source preflight

PRIVATE / INTERNAL. Formal:
`papers/proposal/ecomd_paper_g_dynamic_truth_source_preflight_2026-09-09.md`.
Contract:`research/paper_g/dynamic_truth_preflight_20260909.yaml`.
Manifest:`research/paper_g/dynamic_truth_source_manifest_20260909.json`.

Partial capability, no removed contribution blocker or re-entry. Source commit
4ff3e3a4aa1561721b5571fa3a048a0a463e0568 and six code/config/license text hashes
are fixed. No source executed or data/weights/notebook outcomes opened.

The multisample advection source uses a conservative scheme with optional
second-order reconstruction and an initial mixture that includes absolute-value
and window operations. The exact script covers a single sine. A fixed seed and
parameter/file-name match are not proof of the same continuous initial function
or historical released-data lineage. Freeze the physical initial recipe before
changing solver grids. Do not infer an implementation defect or dataset bias.

Repository block averaging operates on stored grid values, not automatically
continuum cell integrals. Finite point samples or cell averages do not determine
arbitrary shifted initial fields; explicit sampling twins and aligned-shift/
band-limited nulls retained. Actual-generator membership is not established.

Dynamic identity: for e=u-v and adjoint z(t,x)=g(x+c*(T-t)),
<e(T),g>=<e(0),z(0)>-integral<r,z>-sum<j,z>. This standard transport identity
preserves a declared goal when initial error, residuals, jumps and integration
are controlled. Exact initial function gives direct characteristic truth.

The selected Giesselmann-Sikstel v1 theorem is one-dimensional and its remark3.5
leaves stability constants infeasible to compute. L1 itself is not fatal:
|D(v)-D(u)|<=2||m1-m2||infinity||v-u||1. Two-dimensional depth-only SWE still
lacks the requisite full-state/stability/observation certificate here.

Root license is MIT except stated; both advection files retain NEC noncommercial
internal-research and derivative/publication conditions. Do not call the whole
source permissively licensed. Only provenance metadata retained in project;
external source bodies are in a private temporary cache. No reuse/release grant.

No new cycle/question/F3/forecast/card. Preserve cycle30 closure, two-cycle
stopping rule and existing Paper D evidence roles. Next update needs a qualified
same-observable source capability or primary disagreement that changes a decision.

Verified2026-09-09T08:16:34Z: graph293 /edges274 /locators1236; evidence877;
triggers108 /qualified0; cycles21 /raw133 /cards0 unchanged. Scoped canonical
validation, six source hashes,18 existing tests and diff whitespace checks passed.
Receipt:`logs/private/paper_g_dynamic_truth_20260909_verification.md`.
