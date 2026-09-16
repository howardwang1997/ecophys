> PRIVATE / INTERNAL status update, September12: the PI approved the scoped exception below; independent review and the separate local freeze passed. The resulting sandbox `g_response_dx_20260912` is now terminal/quarantined with no usable scientific report. The proposal text below is retained as the original reviewed decision record. See `logs/private/paper_g_response_dx_terminal_audit_20260912.json`; it cannot authorize a retry.

# Paper G response DX: prepared implementation and remaining execution decision

PRIVATE / INTERNAL. Not scientific evidence, a topic card or a completed sandbox authorization.

## Approved work and completed preparation

The PI approved the September 11 response preflight with “授权”, followed by
“继续”. The approval is recorded in
`research/discovery/decisions/pi_paper_g_response_dx_preparation_20260911.yaml`.
Do not ask the PI to approve that same experiment or preparation again.

The private implementation is in `research/paper_g/response_dx/`. It contains
the stipulated Fourier–Galerkin Burgers RHS, DOP853 reference, RK4 check,
orthonormal cosine/sine observation coordinates, current-time resets, complete
five-step pulse histories, the four predictor arms, matched widths, a NumPy
tanh network with analytic backpropagation and Adam, and the frozen mean-response
screen. No campaign initial state, trajectory, model fit or response outcome
has been generated. Unit checks use analytic arrays or fully mocked data.

Prepared inputs enumerate 128 training, 32 diagnostic and 32 response units,
plus 64 future confirmation identifiers whose data remain unmaterialized.
The 16 branch configs reserve 10,800 CPU-seconds in total; other previously
approved limits remain unchanged. The optimizer implementation fixes Xavier
normal weights, zero biases, Adam betas (0.9,0.999), epsilon 1e-8, and a common
batch permutation seed 402. These outcome-free implementation choices were
not selected using performance. Initialization seeds remain 201 and 202.

The three Linux/arm64 wheels were downloaded from official PyPI and individually
matched to its SHA-256 metadata. NumPy 2.4.4, SciPy 1.17.1 and PyYAML 6.0.3 are
pinned in `requirements.lock`; wheel metadata and bundled licence texts are
retained in the private preparation directory. All are existing project
dependencies. No new production dependency or model was introduced.

The offline image is
`sha256:afd631b67aba328e4145c0654542e80f51aeb4ef08f5d85f17bd57319bb0193f`.
Its source-bound conformance report records 14 successful isolation checks,
normal completion, and successful rejection of output overflow, invalid tar
and timeout. The image has no host repository-tree or confirmation-data mount,
no network or GPU, a read-only root/config, one CPU quota, and bounded output.
Nine preparation tests, lint, and strict typing of five source files passed.
These are implementation/runtime checks, not physical results or independent
scientific replication. The conformance report explicitly does not certify an
independent runtime review.

Confirmation uses a fixed future NIST Beacon v2 pulse selected strictly after
both DX termination and D0 freeze, with a ten-minute margin. Only the derivation
rule is recorded now; no pulse or confirmation seed was retrieved. The official
[NIST service description](https://csrc.nist.gov/Projects/interoperable-randomness-beacons/beacon-20)
documents signed, timestamped pulses and the next-pulse endpoint. The frozen
rule requires future certificate/signature verification and forbids replacing
the selected pulse after inspection. This is an infrastructure contract, not
a Paper G source contribution.

## Unresolved execution gates

1. Independent runtime review remains outstanding. Self-checks do not satisfy it.
2. The previously documented research baseline currently reports
   `protected: false`. GitHub's classic protection and ruleset endpoints return
   HTTP403 with the message “Upgrade to GitHub Pro or make this repository public
   to enable this feature.” The exact read-only observations are in
   `preparation/governance_access.json`. No remote settings were changed.
3. Therefore the existing mandatory protected-base authorization merge cannot
   currently be completed. No schema-v2 sandbox manifest, authorization genesis
   or scientific branch has been created. A validated final unit/asset manifest
   and execution freeze also remain to be sealed after review.

The relevant inherited requirement is in `docs/research_discovery_loop.md`,
“Optional DX”: “This enforces a separate authorization merge before execution.”
It additionally requires independent runtime review. Approval of the experiment
did not claim that either requirement had passed.

## Concrete proposed exception — not adopted or authorized

To retain a private repository and zero monetary cost, request one narrowly
scoped PI decision for this campaign only:

- Permit one independent review sub-agent to read the code, frozen configs,
  isolation receipts, partition rules and runtime launcher. It must not run the
  scientific campaign, alter science files, contact others or access confirmation
  data. Its report is private and must name unresolved findings; a finding is
  not cleared merely by rerunning a test. Any material correction needs review
  of the corrected hash before the campaign can start.
- Replace only the GitHub-enforced protected-branch merge requirement for this
  campaign with a separate local authorization commit and a hashed review bundle
  anchored in the conversation before execution. Build the authorization in an
  isolated checkout from an explicit base; include every required dependency
  and verify the resulting checkout. Do not include or commit unrelated worktree
  changes. Freeze the resulting commit ID, input/config/code/image digests,
  independent review report and an authorization-only genesis before any branch.
- Retain the existing validator's `--base-ref` checks against the exact frozen
  commit ID, including byte-identical inputs/manifests and append-only events.
  Run the relevant governance checks locally on the sealed checkout; a mutable
  branch name is not an acceptable base. If a complete validated checkout cannot
  be produced, stop rather than relax another gate.
- Preserve the OCI boundary, confirmation isolation, immutable branch requests,
  all budgets, no-retry quarantine rule, exploratory taint, and bans on paper
  claims, route promotion, outreach, payment and public release. Keep the global
  protocol unchanged; record the PI-approved exception separately with its exact
  manifest scope. It expires with this one campaign.

This substitute has weaker repository-access enforcement: a local owner can
delete or rewrite refs, while the anchored digests make changes detectable.
It is not equivalent to a server-enforced protected branch and therefore is
presented for an explicit decision, not silently installed. Nothing in this
document authorizes the exception or delegation. Existing experiment approval
remains valid regardless of the answer.

## Scientific status

The history-response route remains `failed_closed` and Paper G still has no
qualified topic card. A future empirical residual would only motivate a new
contribution audit; it cannot itself establish novelty or authorize harvesting.
The intended ICML/NMI/NCS research objective remains unachieved.
