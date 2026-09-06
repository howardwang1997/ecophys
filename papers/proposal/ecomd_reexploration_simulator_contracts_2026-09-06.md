---
note: >-
  D-1 component deliverable (gate checklist row 3 of
  ecomd_reexploration_experiment_plan_2026-09-06.md section 10; plan section 2
  "Lineages + gates"). Authored 2026-09-06 under PI decision
  pi_reexploration_d1_authorization_20260906 (theorem/literature/schema work only).
  Every code claim carries a file:line citation from THIS repository at git HEAD
  1f15516b8f044f426af3dacd006b3cd997d59ef2 (2026-09-06). Statements are labeled
  [EXISTS] (verified in code at HEAD) or [D0 BUILD] (does not exist; spec for the
  pre-freeze build list). Nothing here authorizes execution: GPU training,
  confirmatory measurement, market-data access and outcome inspection remain
  gated on D0 freeze plus their own [AUTH] steps.
---

# L1/L2 simulator contracts (D-1 gate checklist row 3)

Purpose: freeze, per lineage, the seven contract surfaces required by the experiment
plan section 2 — input grammar; ABS/INC semantics; through-M enforcement path +
estimator hook; RNG wiring; checkpoint contract; conformance binding; transfer-gate
scoping — plus the D0 hash inventory. This document is a D0 freeze artifact: a
reviewer must be able to check every [EXISTS] claim against the cited line and every
[D0 BUILD] item against the build register (section 4).

Companion authority chain (this doc is subordinate to all four):
- `ecomd_reexploration_experiment_plan_2026-09-06.md` (design; section 2 = these gates)
- `ecomd_reexploration_contract_v1_2026-09-06.md` (C1–C16, gates G1–G12; statistical authority)
- `ecomd_reexploration_theory_appendix_2026-09-06.md` (T1 P0–P9, T2/T3, S1a/S3; formalism)
- `ecomd_reexploration_d1_killer_tests_and_ops_2026-09-06.md` (KT-A4 estimator menu; ops)

---

## 0. Verification method used for this document

- All source files were read at git HEAD `1f15516b8f044f426af3dacd006b3cd997d59ef2`.
- The lab-asset conformance suite was executed CPU-only in conda env `ecophys`
  (`python -m pytest tests/test_lab_asset_conformance.py tests/test_lab_asset_adapter.py -q`):
  **32 passed** = the 27 conformance tests + 5 adapter tests. The count "27" refers to
  `tests/test_lab_asset_conformance.py` alone; note `scripts/lab_asset/run_conformance.py`
  runs BOTH files (`run_conformance.py:14-17`), so the CLI verdict covers 32 tests.
- The frozen bundle was read read-only; `schema_spec.json` sha256
  `c2341ce73f8c32d1b395fad81f0bd4c68a3ac0de0e235ea4d638acc48c24346a` matches
  `bundle_manifest.json` (no mutation; STOP-class rule of the PI decision respected).
- No GPU, no market data, no network fetch, no model training, no endpoint measurement.

---

## 1. Shared engine contract both lineages bind to (lab-asset-v3)

Both lineages consume the SAME truth engine and corpus machinery; lineage-specific
surfaces are sections 2–3. The engine contract is [EXISTS] and frozen.

**Request grammar (the only legal inputs to the truth engine).**
`scripts/lab_asset/schema.py` defines exactly four request types —
`OrderRequest` (schema.py:135-146), `CancelRequest` (schema.py:148-155),
`ReplaceRequest` (schema.py:157-169), `LatencyChoice` (schema.py:123-131) — each
carrying `ThreeClocks` (client/receipt/match ticks, schema.py:94-101) and `round_id`.
`scripts/lab_asset/adapter.py::to_request` (adapter.py:42-138) additionally defines the
arm-invariant client-message dict format (`new`/`cancel`/`replace`/`latency`) that maps
onto these typed requests; `client_view` (adapter.py:141-159) maps tape records back to
client-visible payloads. IMPORTANT SCOPING: `adapter.py` is a *platform-fork wire
adapter* (client messages ⇄ engine), NOT a lineage-training adapter (tape → model
tensors). The lineage corpus adapter does not exist and is a [D0 BUILD] item (§2.1/§3.1).

**Event grammar (engine output).** 14 event types (schema.py:77-91): `session_start`,
`latency_choice`, `latency_choice_rejected`, `order_request`, `order_accepted`,
`order_rejected`, `cancel_request`, `order_cancelled`, `cancel_rejected`,
`replace_request`, `order_replaced`, `replace_rejected`, `execution`, `session_end`.
Per-event payload field lists are frozen in
`experiments/lab_asset_a2/a2_exit_20260905/schema_spec.json` (`payload_fields` key).
Every record is sealed with four hashes — `pre/post_state_hash` (identity layer: full
book with FIFO order, cash, inventory, induced counters, order metadata/status/parent,
used client ids, latency choices, counters, last match tick and **engine RNG state**;
schema.py:239-296, rng_state at schema.py:259) and `pre/post_aggregate_state_hash`
(anonymous level quantities and totals only; schema.py:299-325). `TapeRecord` envelope
at schema.py:190-201.

**Allocation kernels.** The engine implements exactly two arms:
`AllocationRule.FIFO` and `AllocationRule.RANDOM_UNIT_WITHIN_PRICE` (schema.py:22-24).
FIFO fills `min(remaining, maker_qty)` per maker record (matching.py:292-296, 589-590);
random-unit draws one unit per execution record via
`self.rng.randrange(eligible_units)` over remaining resting units at the execution
price and records `allocation_draw = {price, eligible_units, selected_unit,
maker_order_id}` (matching.py:592-604; payload attach at matching.py:344-345).
Contract C3 lists the priority kernel set as {fifo, pro_rata, random_unit}: **pro_rata
is NOT an engine kernel** — it exists only as exact-law arithmetic in S3/EP3 (theory
appendix Part I §0 and §5). All engine-executed cube cells therefore deploy
{fifo, random_unit} only. Flag for the prereg panel: C3's kernel sentence should say
"engine kernels {fifo, random_unit}; pro_rata exact-arithmetic only" to keep contract
text and engine truth aligned.

**Conservation and settlement.** Cash and inventory are settled integer-exactly per
fill (`_settle`, matching.py:627-655: `cash[buyer] -= price*qty`, `cash[seller] += …`,
inventory mirrored, per-unit induced-surplus accounting). NOTE for corpus design:
cash/inventory are engine STATE, not tape payload fields — they enter tapes only
through the state hashes. Conserving-channel truth series (volume units, cash ticks)
for endpoint Y must therefore be extracted by regenerating the tape and reading engine
state (`lab_asset.replay.regenerate`, replay.py:64-131, returns the re-executed
engine's tape; the live engine object exposes `.cash`/`.inventory`). [D0 BUILD] item
E-4: corpus emitter that derives conserving-channel series from `regenerate()`.

**Determinism / replay.** The engine is deterministic given (prestate, request
stream): single `random.Random(prestate.seed)` (matching.py:44) with its state bound
into `state_hash`. `lab_asset.replay.replay` re-executes the request stream and
compares record-by-record — sequence, event type, all four hashes, and byte-level
`record_to_json` equality (replay.py:134-170; comparison at 157-169).
`lab_asset.verify_fixtures.verify_bundle` re-validates manifest hashes AND byte-exact
tape regeneration from disk (verify_fixtures.py:42-70). These are the instruments
behind analyzer gates G6 (horizon-one clearing identity), G9 (determinism replay) and
G3 (schema/manifest binding).

**F_exec corpus projection is schema-native.** Under frozen decision D1_01 the
through-M training corpus is F_exec = execution payloads + `allocation_draw` +
pre/post BBO prices. The frozen `schema_spec.json` payload field list for
`execution` is exactly `[execution, aggressor_role, maker_role, allocation_draw?,
pre_best_bid, pre_best_ask, post_best_bid, post_best_ask]` — the F_exec projection is
a pure selection among recorded payload fields (no new recording, no engine change).
The projection step itself (tape → per-event tensors) is [D0 BUILD] (item E-1).

---

## 2. Lineage L1 = EcoMD v2 transformer/potential

Identity: `ecomd/models/ecomd_v2.py::EcoMDv2Potential` (ecomd_v2.py:330-372) —
persistent typed agents (TypeEmbedding, ecomd_v2.py:86-130), Kyle global potential
`V_kyle = λ·||(1/N)Σ_i π_θ(s_i, τ_i)||²` (ecomd_v2.py:159-214), typed relational pair
kernel with learnable K×K coupling T and SPS random-edge subsampling
(TypedRelationalPotential, ecomd_v2.py:222-322; edge sampler `_sample_edges`
ecomd_v2.py:138-151). It composes into the full simulator as the pairwise term of
`EcoMDSimulator` under `pairwise_kind == "ecomd_v2"` (ecomd/models/ecomd.py:681-704).

### 2.1 Input grammar

[EXISTS] The model consumes **agent-state tensors + market-context tensors**, not
market events: `EcoMDv2Potential.forward(s, context=None)` takes `s ∈ R^{N×d_state}`
and ignores context (ecomd_v2.py:365-372); inside `EcoMDSimulator.step`, the context
vector `[log_price, volatility, last_log_return]` (+ optional memory/global readouts)
is built at ecomd.py:1110-1116 and feeds the external potential and integrator; the
pair kernel sees only `s` (v2) plus type embeddings. Input channels into a rollout:
initial state `sim.init_state(generator=…)` (ecomd.py:931), price state
`sim.init_price()` (ecomd.py:940), or a state-complete `SimulatorState`
(ecomd.py:142-162). There is **no code path today that ingests lab-asset-v3 events**:
no import of `lab_asset` anywhere in `ecomd/`, no event-to-tensor encoder.

[D0 BUILD] L1 corpus adapter (item L1-1): a projector mapping the F_exec projection of
a lab-asset-v3 tape to L1's input surface. Spec: per clearing round t, inputs =
anonymous book-state summary + conserving channels from `regenerate()` (E-4), flow
tensor z_t (predicted by L1's new head, L1-2) and the F_exec event records of round t
as supervision/target context. The adapter must be a pure function of (prestate, tape,
seed) with its own hash; schema events map 1:1 via `schema_spec.json` payload fields;
`order_accepted.resting_quantity` and all request-side events are EXCLUDED under F_exec
(D1_01: under F_exec+orders the fibers collapse toward points and T1–T3 lose their
engine-grounded form). Rejected/accepted/cancelled/replace request streams feed the
DGP request generator (E-2), not the lineage input, except as tape-derived features
that exist in F_exec (they do not — requests are not in F_exec).

### 2.2 ABS/INC semantics

[EXISTS] The simulator is **absolute-state, incremental-update**: `s` is an absolute
agent-state tensor; each `step` computes forces and integrates
`s_next = s + drift + stoch_displacement (+ jumps)` (ecomd/physics/integrator.py:445,
jump add at 447; drift = (f_cons + f_diss)/γ·dt computed in `step`,
integrator.py:397-422; noise `eps` sampled with the rollout generator at
integrator.py:383). The increment and its velocity form are already materialized:
`velocity = (s_next − s)/dt` (integrator.py:470), and `IntegratorStep.s_next`/
displacement are returned per step (integrator.py:41-48). The rollout maintains an
absolute clock with a consistency check (`SimulatorState.step_idx` vs
`price_state.step`, ecomd.py:1456-1460).

[EXISTS-but-different-object] The cube's coordinate axis c ∈ {absolute next state,
increment} (contract C3) is a property of the **trained prediction head's target**, and
no supervised next-state/increment head exists: L1's only training objective today is
stylized-fact moment matching on self-rollouts (`moment_matching_loss`,
ecomd/training/losses.py:270-350; consumed by `compute_loss`, losses.py:790+), with
targets built from a return series (losses.py:358-373). [D0 BUILD] L1-2: the two
coordinate heads (predict `x_{t+1}` vs predict `x_{t+1} − x_t` on conserving-channel /
book-state targets), trained by supervised rollout error against DGP truth per
contract C5. Both are mechanically supported by the existing integrator outputs
(absolute `s_next` and its increment are both already computed, integrator.py:445-470).

### 2.3 Through-M enforcement path + estimator hook

[EXISTS] Nothing. The engine (`scripts/lab_asset/matching.py`) is pure Python with
integer state — its Jacobian is zero a.e. as a function of real-valued flow
parameters; no torch binding, no differentiable wrapper, no estimator code exists in
`ecomd/` or `scripts/lab_asset/`. The plan's through-M arms are [AUTH]-gated and the
machinery is [D0 BUILD]. Spec of the build (items L1-3a/b), consistent with synthesis
ruling 6 and KT-A4:

- **Composition point**: between L1's per-step flow output z_t and the next-round
  conserving-channel state. Concretely: `EcoMDSimulator.rollout_state`
  (ecomd.py:1436-1446) iterates `step()`; the through-M wrapper intercepts the
  predicted round-t flow, executes it through the exact engine M (kernel per cell
  spec: fifo or random_unit), and feeds the engine's post-round anonymous state +
  conserving channels forward as the next input. The wrapper is external to
  `ecomd_v2.py` (no change to the potential), implemented as a composition layer plus
  a Python↔torch bridge onto `ReferenceEngine.submit` (matching.py:248).
- **Estimator 1 (primary): straight-through, pinned scale.** Forward: exact integer M
  output. Backward: identity gradient on cleared units, zero on uncleared units — the
  Paper D rank-one gauge generalized, literally T2's minimal special case (plan ruling
  6). Pinned scale = the backward pass-through coefficient is a frozen constant, not
  learned. Registered as a torch autograd function whose backward is the masked
  identity; config (scale value, mask rule) hashed at D0.
- **Estimator 2 (audit, KT-A4): perturb-and-MAP, pinned noise.** Forward: z_t + ε_t
  with ε drawn from a dedicated frozen RNG substream (`spawn(seed,"train_kernel",…)`,
  see §2.4), discrete allocation by MAP (argmax over the perturbed within-pool
  weights, matching the engine's within-price pool structure), gradient via the pinned
  noise (reparam-style). Two-estimator retrain of the audit cell is [AUTH] per D1_07;
  frozen downgrade = estimator-conditional reporting with both shown (contract C16
  amendment ledger).
- **Fixture competence gate** [D0 BUILD, CPU-legal]: read-only fixture unit test of
  both estimators on the frozen bundle fixtures (both arms): straight-through forward
  must reproduce the recorded tape via `replay` byte-exactly (G6 semantics at horizon
  one); PAM with noise=0 must reduce to the exact kernel. Runs pre-D0 on CPU only.

### 2.4 RNG wiring

Contract C1 defines the RNG tree: one seed root spawning named substreams
`data` (prestate + request stream), `init`, `minibatch`, `train_kernel`,
`kernel:1..K` (K=8 default, movable within {4,8,16} by the DGP-only preflight D1_06;
derivation frozen by library+version pin — ops plan §3 item 3 fixes
`numpy SeedSequence.spawn`). Mapping onto L1's actual seeding surface:

- **data** — [EXISTS at engine level] `prestate.seed` seeds the engine's only RNG
  (`random.Random(prestate.seed)`, matching.py:44) and is pinned by the prestate hash.
  The request stream comes from the DGP request generator: [D0 BUILD] (E-2, M0/M1-lumpable
  policy class per C2(a); master seeds hashed at D0).
- **init** — [EXISTS, two surfaces] (i) persistent type labels:
  `torch.Generator().manual_seed(cfg.v2_type_seed)` (ecomd.py:699; default
  `v2_type_seed=42`, ecomd.py:442; consumed by TypeEmbedding, ecomd_v2.py:108-112);
  (ii) initial agent state: `init_state(generator=gen)` with the rollout generator
  (ecomd.py:931, 1417); parameter init is PyTorch default RNG, seeded globally in the
  trainer (below). [D0 BUILD] bind the init substream name to `spawn(seed,"init")`
  explicitly.
- **minibatch** — [GAP] `train_distributed.py` has no data-loader minibatch ordering
  today (training rolls out from simulator state; train_distributed.py:783-829); the
  shared minibatch-order stream required by C1/G2 exists only as ops spec.
  [D0 BUILD] as part of the supervised training loop (L1-2).
- **train_kernel** — [D0 BUILD] with the estimator menu (§2.3); one seed-spawned
  stream replayed across all through-M arms within a seed (C2 note 3).
- **kernel:1..8** — [D0 BUILD] inference-kernel streams, replayed identically across
  cells within a seed; deterministic-kernel cells execute 8 identical evaluations
  (gate G8 byte-identity). No inference-stream machinery exists in `ecomd/eval/` today
  for engine kernels.
- **Trainer rank seeding** [EXISTS]: `rank_seed = seed + rank*10000`;
  `gen.manual_seed(rank_seed [+ start_iter if not state_complete])`;
  `auxiliary_gen.manual_seed(rank_seed + 5_000_000)`; and when resuming without a
  saved runtime, `torch.manual_seed / torch.cuda.manual_seed / np.random.seed /
  random.seed` are all set to `rank_seed` (train_distributed.py:722-733).
- **HONEST GAP (load-bearing for G8/G9):** L1's SPS edge sampling inside the v2 pair
  kernel is **not generator-threaded**: `_sample_edges` calls global
  `torch.rand(n, n, device=device)` (ecomd_v2.py:145), and the step-generator binding
  in `EcoMDSimulator.step` is applied ONLY to `StochasticPairwisePotential`
  (ecomd.py:1245-1247; comment there documents the 2026-05-22 fix for the *other*
  class). Consequences: (a) within-run reproducibility of v2 edge draws relies on the
  global seeding at train_distributed.py:729; (b) byte-identical cross-node replay of
  a v2 rollout (G6/G9 semantics) additionally requires identical global-RNG
  consumption order — an assumption, not a contract. [D0 BUILD] item L1-4: thread the
  rollout `generator` into `TypedRelationalPotential._sample_edges` (mirror the
  `_step_generator` pattern already present for `StochasticPairwisePotential`), so the
  named-substream contract covers every stochastic consumer in L1. This is a code
  change to a frozen-lineage file and must land BEFORE D0 freeze with its own test.

### 2.5 Checkpoint contract

[EXISTS] Two composable formats, both `torch.load(..., map_location="cpu")`-loadable:

1. **Trainer checkpoint** `save_checkpoint` (train_distributed.py:417-465): atomic
   write (`_atomic_torch_save`, 410-414), payload = `format_version` (=2, line 308),
   `iter_idx`, `world_size`, `state_complete`, `sim_state_dict`, `optim_state_dict`,
   `rank_runtimes` (per-rank `SimulatorState.to_checkpoint()` including rollout RNG
   state, ecomd.py:234-261; state-complete checkpoints REQUIRE SimulatorState.rng_state,
   train_distributed.py:332-340), `targets`, `sim_config`, `train_config`, optional
   `execution_metadata`. Loader `try_load_checkpoint` uses
   `torch.load(path, map_location="cpu", weights_only=False)` (train_distributed.py:481)
   with world_size / state_complete / rank-runtime validation (482-520). Post-training,
   `training_log.json` records `checkpoint_sha256` (train_distributed.py:1252-1279) —
   the hook the analyzer's G4 checkpoint-lock manifest builds on.
2. **Simulator dynamic state** `SimulatorState.to_checkpoint/from_checkpoint`
   (ecomd.py:234-317, format_version 1): s, s_prev, price_state, recurrent latents
   (h_regime/h_agent/h_global), step_idx, fundamental, shock state, integrator and
   pairwise caches, `rng_state`.

[D0 BUILD] L1-5: cube-specific additions — (i) optimizer-stripped, CPU-offloaded final
"lock" checkpoint variant (surgery cells read parameters only; ops §3 item 4) emitted
alongside the state-complete format; (ii) `n_draws`, `allocation_rule`, seed and
corpus-manifest binding inside the checkpoint payload or sidecar so G4/G10 checks are
self-contained. Nothing here changes the existing loader contract.

### 2.6 Conformance binding

The 27 tests of `tests/test_lab_asset_conformance.py` bind the ENGINE; a lineage
"passes" them operationally by consuming only corpora that the engine+validator
certify. Exact pre-training checklist per L1 corpus tape (all [EXISTS] instruments):

1. `lab_asset.replay.replay(prestate, tape).ok == True` — record-by-record equality
   including all four hashes (replay.py:134-170).
2. `lab_asset.verify_fixtures.verify_bundle`-style byte-exact regeneration from disk
   (verify_fixtures.py:42-70) on both nodes (G6/G9, ops §3 item 2).
3. Dual-arm CRN premise: identical `aggregate_state_hash` sequence at completed
   request boundaries across fifo/random_unit arms on the same request stream — the
   property pinned by `test_aggregate_state_matches_across_arms_at_request_boundaries`
   (test file line 272) and `test_identity_hash_preserves_fifo_order_while_aggregate_hash_does_not`
   (line 261).
4. `schema_version == "lab-asset-v3"` and manifest hash match against
   `bundle_manifest.json` (anchor `fea8b136…9581c`; G3).

The 27 tests, grouped by what they certify for the lineage contract (names verbatim;
line numbers from `tests/test_lab_asset_conformance.py`):

- Determinism/replay (directly gate G6/G8/G9): `test_bit_level_determinism_and_hash_chain`
  (360), `test_deterministic_replay_reproduces_recorded_tape` (384),
  `test_replay_detects_tampered_tape` (399),
  `test_replay_reproduces_and_detects_tampering_on_replace_tape` (565),
  `test_a2_exit_bundle_round_trip_and_tamper_detection` (597).
- Kernel law + CRN (gate the engine-law-mismatch STOP risk and C2(a)):
  `test_random_unit_draws_are_quantity_weighted_and_recorded` (221),
  `test_random_unit_allocation_is_invariant_to_contiguous_child_splitting` (241),
  `test_fifo_is_arrival_ordered_and_partial_maker_keeps_priority` (208),
  `test_identity_hash_preserves_fifo_order_while_aggregate_hash_does_not` (261),
  `test_aggregate_state_matches_across_arms_at_request_boundaries` (272).
- Request grammar the corpus adapter must respect (rejection semantics the request
  generator must never trip unintentionally): `test_partial_fill_chain_and_basic_rejections`
  (110), `test_cash_inventory_actor_and_clock_constraints` (131),
  `test_induced_value_unit_capacities_are_enforced` (165),
  `test_self_trade_prevention_covers_every_crossed_level` (186),
  `test_rejection_ids_are_sequential_across_families` (512),
  `test_cancel_lifecycle_and_ownership` (196),
  `test_replace_resting_to_resting_records_lineage_and_quotes` (434),
  `test_replace_that_crosses_executes_against_opposite_book` (457),
  `test_replace_rejections_are_reason_coded_and_resource_freeing` (471),
  `test_replace_frees_reserved_resources_for_larger_quantity` (493),
  `test_latency_choice_is_recorded_rejected_and_replayable` (298),
  `test_initial_book_is_loaded_and_resource_checked` (343),
  `test_roles_recorded_and_prestate_validated` (543),
  `test_pre_post_quotes_on_accepted_actions` (530),
  `test_golden_marketable_cross_settles_holdings` (93),
  `test_session_start_commits_complete_prestate` (85),
  `test_isolated_race_removes_the_marginal_return_to_speed` (311).

Day-5 trainability quality gate (plan section 2; [AUTH] at run time, thresholds frozen
now): NaN ≤ 5% at long rollout; R00 validation ≤ 3× L1 seed-median; ≥ 28/30 seeds
complete. Early-warning only; the convergence-failure halt rule (>15% nonfinite on any
mandatory cell, or >3/30 seeds lost → STOP + PI) is unchanged.

### 2.7 Transfer-gate C9 restated for L1

L1 is the PRIMARY lineage (block B1 = L1 × lab-asset-v3; contract C9's primary cell is
B1 × kernel-swap × horizon 16). Restated: the B1 ordered classification at the primary
cell is single-prespecified, not Holm-adjusted, not overridable by secondaries; Holm
family = sign-flip tests on the 16 mandatory interaction cells (4 axes × 4 horizons)
within B1; axis-contrast secondaries = three (J_axis − J_ID) at h=16, Holm within the
triple. L1 carries the paper's confirmatory weight: B1 failure modes (reference
degeneracy in all four strata, KT-A1 kill pattern) are STOP-class at paper level, not
boundary reports. "Claims scoped L1" (§3.7) is the CONSEQUENCE of an L2 gate failure
and does not weaken any L1 statement.

### 2.8 L1 contribution to the D0 hash inventory

See section 5, items A–C.

---

## 3. Lineage L2 = recurrent fact-surrogate

Identity per plan section 2 / ops §0: L2 = recurrent fact-surrogate,
`ecomd/training/fact_surrogates.py`. HONEST BASELINE, stated once and load-bearing for
everything below: **`fact_surrogates.py` (183 lines) is a library of four
differentiable surrogate FUNCTIONS, not a model** — `gain_loss_skew` (lines 55-64),
`agg_gaussianity` (72-84), `soft_fano` (92-118), `dfa_hurst_surrogate` (126-183) —
mirroring the numpy estimators of `ecomd/eval/stylized_facts.py` (its own docstring,
lines 1-18; surrogate-kill tests in `tests/test_fact_surrogates.py`). It has no
recurrent cell, no parameters, no training loop, no checkpoint, no seeding surface, no
event ingestion. The "recurrent fact-surrogate LINEAGE" is therefore substantially a
[D0 BUILD]; what exists and is reusable is enumerated below. This is consistent with
plan section 10 ("Provided (design) … Remains: write both contracts") — the D-1 gate
claimed design, not code, and this document says exactly which is which.

### 3.1 Input grammar

[EXISTS, reusable components] (i) The four surrogate functions consume 1-D return
tensors (fact_surrogates.py:55-183); (ii) `ecomd/eval/stylized_facts.py::compute_all`
runs all 11 Cont-2001 metrics on numpy log returns + optional volume
(stylized_facts.py:698-744) — the ops plan's stylized-fact vector on ID + kswap tapes;
(iii) recurrent machinery exists INSIDE the L1 simulator as optional tiers but is not
an independent model: per-agent `AgentMemoryGRU` (nn.GRUCell,
ecomd/models/agent_memory.py:43-104), `RegimeGRU` (regime_latent.py), global state
(global_state.py) — these are composition points to copy, not the lineage itself.
[D0 BUILD] L2-1: the recurrent fact-surrogate model — a recurrent next-state/increment
predictor over lab-asset-v3 F_exec streams (input grammar identical to L1's adapter
output, E-1/L1-1, so the corpus contract is lineage-invariant), with per-step hidden
state over clearing rounds, trained with a fact-surrogate-augmented loss (the existing
four surrogates + moment terms enter losses.py's `multi_fact_terms` path today,
losses.py:341-347 and 458-500 — the composition pattern to reuse) plus the supervised
rollout error per C5. Architecture, hidden size, and context window frozen at D0.

### 3.2 ABS/INC semantics

[EXISTS] Nothing at lineage level (no model). The engine-side semantics of §1 apply:
absolute state, increments derivable from consecutive regenerated states; contract
amendment (3) pins the R00 reference coordinate to INCREMENT, so L2's increment head is
the reference cell's native coordinate. [D0 BUILD] L2-1 must implement BOTH coordinate
heads (the cube needs all 4 trained arms: {ABS, INC} × {raw, through-M} per lineage,
contract C3/C14: 240 trainings = 4 arms × 30 seeds × 2 lineages).

### 3.3 Through-M enforcement path + estimator hook

[EXISTS] Nothing beyond §1's engine. [D0 BUILD] L2-2: same composition layer as L1-3
(item E-3, shared, lineage-agnostic — this is a deliberate single-build-two-users
decision; the wrapper's inputs/outputs are the adapter tensors of E-1, not L1-specific
state), same two estimators (straight-through pinned scale primary; perturb-and-MAP
pinned noise audit), attached at the recurrent head's per-step flow output. Estimator
configs hashed once at D0 and shared across lineages (KT-A4 menu).

### 3.4 RNG wiring

[EXISTS] Nothing at lineage level. [D0 BUILD] L2-3: named-substream seeding identical
to L1's map (§2.4): `spawn(seed,"data"/"init"/"minibatch"/"train_kernel"/"kernel:1..K")`
via `numpy SeedSequence.spawn` (ops §3 item 3), seeds 12000–12029 (B3/B4 namespace,
D1_10; supersedes the ops draft's "1000-1029/2000-2014 continuing repo convention" —
flagged in §6). Init substream covers recurrent hidden-state initialization; parameter
init; no global-RNG consumers permitted (the L1 lesson of §2.4 becomes an L2
requirement from day one: every stochastic consumer must draw from a named substream
or be deterministic).

### 3.5 Checkpoint contract

[EXISTS] Nothing at lineage level. [D0 BUILD] L2-4: adopt the trainer checkpoint
format of §2.5 verbatim (`format_version` 2 payload keys; `torch.load(…,
map_location="cpu", weights_only=False)`; state-complete with per-rank RNG runtime)
so analyzer G4/G5 and surgery-cell locking treat both lineages uniformly. The L2
checkpoint must additionally carry the recurrent hidden state at the save boundary
(the `SimulatorState.h_agent` slot pattern, ecomd.py:250-252, is the precedent shape).

### 3.6 Conformance binding

Identical to §2.6 (the same 27 tests + replay/verify instruments certify the SAME
corpora; the L2 corpus adapter consumes the same certified tensors): replay OK per
tape; byte-exact regeneration on both nodes; dual-arm aggregate-hash CRN equality;
schema_version + manifest binding. Additionally L2-specific pre-training checks
[D0 BUILD]: (i) deterministic decode at eval (C2(d): no sampling heads) verified by
double-execution byte-identity on a fixed 5% sample; (ii) trainability smoke (finite
loss on D1 corpus, N ≤ 500 on Mac per workflow rules) as the ops Stage-1 mechanical
trigger input ("L2 trainability/transfer gate passed" trigger, ops §2).

Day-5 gate for L2 (plan section 2): same thresholds (NaN ≤5% long rollout; R00 val
≤3× L1 seed-median; ≥28/30 seeds complete) — note R00 for L2 is referenced to the
**L1** seed-median, i.e., the gate is cross-lineage by construction.

### 3.7 Transfer gate C9 restated for L2 + "claims scoped L1", operationally

C9 verbatim: "Architecture-transfer gate: B3 passes iff primary J material AND
≥ 8/16 mandatory cells material; failure reported as boundary." Restated per lineage:
B3 = L2 × lab-asset-v3 with its own 16-cell mandatory family and its own
kernel-swap/horizon-16 primary-analogue cell. The gate reads B3's own cells: B3's
kernel-swap h16 J must classify MATERIAL non-additivity AND at least 8 of B3's 16
mandatory cells must be material (Paper D U-Net fraction 6/12 preserved; C16
amendment (9)). Wording flag for the prereg panel: contract v1 says "primary J",
defined as the B1 cell; the intended transfer reading (from Part 2c: "block B3 passes
transfer iff primary J material AND ≥8/16") is the B3-analogue cell — pin this
sentence explicitly at D0 to remove the ambiguity. This document adopts the
B3-analogue reading.

Operational meaning of a FAILED gate ("claims scoped L1"), frozen now so it cannot be
negotiated post-hoc:

1. All confirmatory ordered classifications, Holm families, axis contrasts and SESOI
   statements are reported from B1 (L1) only; B3 results are REPORTED (reporting-all
   rule C10 — every cell, axis, horizon, flip and null appears in generated tables)
   but carry no confirmatory status and cannot corroborate any T2/T3 empirical
   ordering (O-A…O-E).
2. No pooled or cross-lineage estimate is computed or shown (no meta-analytic
   combination, no "replicated in 2/2 lineages" sentence anywhere, including the
   abstract).
3. The paper's architecture claim is scoped: "path-dependence attribution confirmed on
   the transformer/potential lineage; the recurrent fact-surrogate lineage shows an
   architecture boundary" — the U-Net-lesson phrasing; the boundary is a finding, not
   a failure to hide (KT-A5 honest-report rule).
4. The two-lineage D-1 GATE requirement ("simulator contracts ≥ 2 independent
   lineages", plan section 10) remains satisfied at CONTRACT level (this document +
   frozen configs); the empirical support level is single-lineage and the paper must
   say so.
5. Downstream claims that REQUIRE two lineages by their own wording (e.g., any
   "lineage-invariant" phrasing in T2/T3 instantiation text) must be struck or
   re-scoped to L1 before freeze — checked at the adversarial 3-reviewer pass (D1_08).

### 3.8 L2 contribution to the D0 hash inventory

See section 5, items D–E.

---

## 4. Consolidated D0 build register (everything labeled [D0 BUILD] above)

Shared engine/corpus items (single build, both lineages consume):

- **E-1** F_exec corpus projector: tape → per-round tensors (execution payloads,
  allocation_draw, pre/post BBO only; D1_01). Pure function of (prestate, tape, seed).
- **E-2** M0/M1-lumpable DGP request generator (episodes, actor mix, rates, bands,
  master seeds; C2(a) exact request-level CRN). Seed-tree `data` substream.
- **E-3** Through-M wrapper + Python↔torch bridge onto `ReferenceEngine` with the two
  frozen estimators (straight-through pinned scale; perturb-and-MAP pinned noise) +
  read-only fixture competence test on the frozen bundle (CPU-legal pre-D0).
- **E-4** Conserving-channel emitter: volume/cash series extracted from
  `regenerate()` engine state (cash/inventory are not tape payload fields; §1).
- **E-5** Frozen per-(lineage, DGP, arm, condition) Hydra configs + seed/stream
  manifest (11000–11029 / 12000–12029 + derivation salts; D1_10).

L1 items: **L1-1** corpus adapter; **L1-2** ABS/INC supervised heads (C5 endpoint);
**L1-4** generator-threading of v2 `_sample_edges` (fixes the global-RNG gap of §2.4;
must land pre-freeze with a test); **L1-5** lock-checkpoint variant + binding sidecar.

L2 items: **L2-1** the recurrent fact-surrogate model (both coordinate heads);
**L2-2** through-M attachment (via E-3); **L2-3** named-substream seeding (no
global-RNG consumers); **L2-4** checkpoint format adoption (§3.5) + deterministic-decode
check.

Estimator-menu configs (both estimators, hashed; KT-A4): included in E-3.

---

## 5. D0 freeze hash inventory (task item 8)

Everything below is hashed at D0 and bound into the prereg archive (plan section 9).
Git HEAD at authoring: `1f15516b8f044f426af3dacd006b3cd997d59ef2` (the freeze commit
will differ; hash AT freeze).

A. This document: `papers/proposal/ecomd_reexploration_simulator_contracts_2026-09-06.md`.

B. Frozen anchor bundle (read-only, NEVER mutated; PI decision D1_03):
`experiments/lab_asset_a2/a2_exit_20260905/bundle_manifest.json` + the 7 hashed files
(per-file sha256 in the manifest; `schema_spec.json` =
`c2341ce73f8c32d1b395fad81f0bd4c68a3ac0de0e235ea4d638acc48c24346a`; lineage
`fea8b136…9581c`). Enriched fixtures (D1_03) live in a NEW directory with its own
manifest referencing this bundle as parent — that new manifest is also hashed here.

C. L1 code surfaces (hash of the files at the freeze commit):
`ecomd/models/ecomd_v2.py`, `ecomd/models/ecomd.py`, `ecomd/physics/integrator.py`,
`ecomd/training/train_distributed.py`, `ecomd/training/losses.py`,
`ecomd/training/m0_contract.py`.

D. L2 code surfaces: `ecomd/training/fact_surrogates.py`,
`ecomd/eval/stylized_facts.py`, plus the L2-1 model file(s) once built.

E. Shared engine/instrument code: `scripts/lab_asset/{matching,schema,replay,adapter,
run_conformance,verify_fixtures,export_schema}.py`; `tests/test_lab_asset_conformance.py`
(27 tests) and `tests/test_lab_asset_adapter.py` (5 tests); conformance PASS receipt
from the freeze commit (both nodes re-run per ops §3 item 2).

F. Build-register outputs (hashed as they land, all pre-D0): E-1…E-5 artifacts
(corpus projector, request generator, through-M wrapper + estimator configs +
fixture-competence test evidence, conserving-channel emitter, Hydra configs + seed
manifest), L1-1/2/4/5, L2-1/2/3/4, and the fiber-resampler + enriched-fixture
conformance tests (D1_02/D1_03, owned by sibling components; listed here because
KT-A3/KT-M1 and the merged hostile-T0 floor depend on them).

---

## 6. Flags for the preregistration panel (inconsistencies found and resolutions adopted)

1. **C3 kernel set vs engine**: contract text lists pro_rata among M's kernels; the
   engine implements {fifo, random_unit} only (schema.py:22-24). Resolution adopted:
   pro_rata is exact-arithmetic-only (S3/EP3); C3 wording to be tightened at freeze.
2. **Seed namespaces**: ops §3 item 3 draft says 1000-1029/2000-2014; PI decision
   D1_10 and contract C1 adopt 11000–11029 / 12000–12029. D1_10 governs.
3. **"27 conformance tests"**: precise meaning = `tests/test_lab_asset_conformance.py`;
   the CLI runner `run_conformance.py` additionally runs the 5 adapter tests (32
   total). Freeze wording should say "27 + 5 adapter".
4. **C9 transfer-gate ambiguity** ("primary J" = B1 cell or B3-analogue): B3-analogue
   adopted (§3.7); panel to pin the sentence.
5. **Rank-seed collision surface**: existing `rank_seed = seed + rank*10000` +
   `auxiliary +5_000_000` (train_distributed.py:722-727) must not collide with the new
   substream names; the seed manifest (E-5) records the full derivation and the panel
   should require a collision check as part of G2.
6. **L2 existence gap**: plan/ops cost tables treat L2 as an existing 0.7/1.1 V100-h
   arm; in reality the model is a D0 build (§3). Compute anchors are therefore
   planning estimates, not measured baselines — the panel should note this in the
   risk register (throughput ladder already covers it via the contingent calendar).

---

*Provenance: D-1 execution wave component (simulator contracts), session 2026-09-06.
Grounding reads listed in section 0; companion docs per header. No GPU, no market
data, no execution.*
