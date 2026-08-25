# Bourse disposable market-counterexample preflight

**Date:** 2026-08-25
**Decision:** PRE-AUTHORIZATION ONLY — DO NOT RUN
**Scientific status:** no topic card, no route-status effect, no evidence claim

## Purpose

This is a contract for a small question-generation instrument, not a proposed paper. The
instrument would use a pinned synthetic limit-order-book simulator to search for minimal
counterexamples to candidate market-physics statements. Its value is mainly negative: kill
an attractive but non-invariant story before EcoMD implementation, data purchase, or GPU
work. A positive sandbox pattern may only motivate a new D-3 child card and remains
permanently `sandbox_exploratory_tainted`.

The sandbox must not optimize stylized-fact fit, select a best seed, or relabel a known
failure family as a discovery. In particular, response differences caused by hidden-state
projection, event batching, tick coordinates, order identity, generic Markov-kernel
noncommutation, finite-size crossover, or hard price-time events are rejection reasons, not
candidate results.

## Candidate generator contract

- **Engine:** Bourse 0.4.0 at commit
  `17285fde5a5293b55fed9236c7f35a859160a5f5`, MIT.
- **Permitted role:** disposable CPU-only question generator and falsifier.
- **Native semantics used:** integer price lattice, price-time priority, order/trade
  histories, top-ten L2 observations, fixed-size simulation steps, and seeded randomized
  shuffling of end-of-step instructions.
- **Replay claim:** deterministic from-scratch runs under a frozen seed and complete input
  program only.
- **Explicit nonclaims:** Bourse is not a continuous-time exchange twin, a real-data bridge,
  an independent confirmation system, or a bit-complete mid-trajectory checkpoint. JSON
  book persistence does not capture the agent population, scheduler, and every RNG state.

Official source and behavior records are frozen as `bourse_simulator`, `bourse_de_docs`, and
`bourse_book_docs` in `research/discovery/evidence_registry.yaml`.

## Frozen question space

Each branch must begin with one market-native transformation and one directional falsifier.
The only initial transformation families are:

1. split or merge equal-price orders while preserving signed price-level volume;
2. compare native modify with cancel-and-replace under a matched displayed pre-state;
3. permute the same within-step instruction multiset while preserving all aggregate inputs;
4. refine the integer price/quantity units with the economic state rescaled exactly; and
5. clone or merge an agent policy while preserving aggregate capital, order flow, and the
   from-scratch seed namespace.

These families are deliberately hostile controls. Most are expected to reproduce an existing
route-graph failure. A branch survives only if it produces a minimal response distinction
that cannot be assigned to a registered failure family, remains invariant under unit and
identity refinements, and can be translated without changing the estimand to a second native
simulator. The sandbox itself cannot establish any of those final conditions.

The allowed screening observables are the joint finite-horizon path of spread, top-ten L2
depth, fills, cancellations, queue survival, transaction price, and exact cash/inventory
conservation residual. No scalar anomaly score or tail exponent may be promoted by itself.

## Prospective units and split

The prospective unit is `fixture_id × randomness_slot`, with eight frozen mechanism and
population fixtures. The authorization, if later approved, must materialize only the
following identifiers:

- exploration: the eight fixed public seed slots 0--7 within every fixture, 64 units;
- confirmation: eight future public-randomness beacon pulse identifiers within every fixture,
  64 units. Their seeds are defined prospectively by a domain-separated SHA-256 derivation
  from pulse values emitted only after sandbox closure and the D0 confirmation freeze.

The fixture definitions, unit files, code manifest, simulator source tree, dependency lock,
and OCI image must be hashed before authorization. A partition label without the actual
sorted unit files is invalid. Numeric confirmation seeds must not appear in the repository,
launcher, image, branch config, or user prompt during DX. Merely reserving known seeds 8--15
would not be a holdout because simulator code could generate those outcomes early.

## Resource and multiplicity limits

- 14,400 CPU-seconds;
- 1,000,000,000 stored bytes;
- zero GPU-seconds and zero monetary cost;
- at most eight hash-chained branches across the asset campaign; and
- seven calendar days from authorization to terminal taint disposition.

Every `branch_opened` record must precede its run and freeze the hypothesis, falsifier,
multiplicity family, tests, seeds, code digest, and config digest. Adaptive follow-ups count
as new branches; deleting or rewriting a failed branch is forbidden.

## Hard stop rules

Stop the campaign and create no child card if any of the following holds:

- seeded from-scratch replay is not exact under the frozen image;
- the effect disappears under the corresponding unit, identity, or aggregate-input control;
- the discrepancy is explained by an existing failure family or by Bourse's fixed-step
  shuffling semantics;
- the result is only a familiar stylized fact, parameter sensitivity, or best-seed effect;
- obtaining the effect requires editing Bourse's matching or scheduler core;
- no same-estimand translation to a genuinely independent engine can be stated before
  confirmation; or
- any confirmation unit, repository secret, network service, GPU, paid asset, or unmounted
  workspace path becomes accessible.

## Preconditions still missing

This preflight intentionally creates no sandbox manifest or partition artifact. Execution
remains forbidden until all of the following happen in order:

1. the `research-governance` pull-request check is merged, made required on the protected
   base branch, and force-push/deletion protections are enabled;
2. an OCI launcher is independently reviewed and pinned by SHA-256, with no network, a
   read-only root filesystem, no repository mount, no secrets, CPU-only device access, a
   read-only exploration mount, and an artifact-only output mount;
3. the Bourse source/dependency snapshot and image digest are frozen, and isolation is
   tested without generating market outcomes;
4. the confirmation beacon, pulse times, domain separator, seed-derivation function and
   outage fallback are frozen while all pulse values are still in the future;
5. a separate user-authorized change adds only the v2 manifest, decision, immutable inputs,
   and single `authorized` genesis event; and
6. that authorization-only change is merged before any branch can open.

The workflow file alone is not branch protection, and a self-reported runtime receipt is an
audit record rather than cryptographic proof of host isolation. Until the above controls are
deployed, the expected scientific value does not justify execution.

## Calibrated value

The estimated probability that this bounded probe motivates a genuinely new D-3 card is
5--10%; the probability that such a child ultimately supports an NCS/NMI-scale paper is much
lower. The main expected return is rapid, auditable rejection of non-invariant topics. This
is sufficient to retain the preflight, but not to authorize the sandbox automatically.
