# EcoMD prediction-market truth-asset trigger audit — lasting decisions

- Formal result:
  `papers/proposal/ecomd_prediction_market_truth_asset_trigger_audit_2026-09-05.md`.
- Two new public assets are real `partial_capability` advances but remove zero recorded blocker and
  authorize no candidate harvest, raw outcome access, implementation, simulator run, SSH or GPU.
- Polymarket-v1 supplies a CC-BY-4.0 first-generation settlement archive with ground-truth
  aggressor side, per-fill fees, maker/taker wallets and CTF preparation/split/merge/resolution/
  redemption events. It is useful trade-level truth, not complete intervention truth.
- Its data card explicitly omits order-book snapshots, quote updates, cancellations and off-chain
  resting depth. Two latent books can therefore produce the same settlement tape but arbitrarily
  different responses to an added order, priority rule, latency or fee action.
- The 2026 Polymarket fee rollout is platform-selected and bundles taker fees with maker rebates.
  Realized fees are measurable, but assignment, interference and complete pre-state are not solved;
  the source paper already analyzes the outcomes and reports pre-trend, migration, heterogeneous-
  effect and clustered-inference limitations. Moving Hugging Face `main` also mixes later CTF
  additions, so any future use must pin and declare a paper-bound file manifest.
- OpenMarket is frozen at source tag `v0.5.2`, commit
  `6e6cc240f32ab9fd2f8fa602bd0aba823b24bfee`; its `v0.4.3-unified` split has
  727,098,247 deduplicated rows, 202 snapshots and 2,936,031 paired events. It exports source and
  collector timestamps plus Polymarket mid/best bid/best ask/top size.
- OpenMarket has one collector, an unresolved roughly plus-or-minus-99-ms constant source-clock
  offset, an unrecoverable April-to-May gap, and top-of-book rather than L3 lifecycle. Large Binance
  moves are observational, not assigned actions. Hawkes learning under unknown synchronization
  shifts is already a direct method parent.
- Combining settlement fills with top-of-book ticks still omits cancelled/unfilled orders,
  queue-ahead and ownership, full depth, private routing, inventory and adaptive policy state. The
  two assets observe the same platform and are not independent same-estimand truth systems.
- The fixed-noise-tape idea is closed without a new route node. EcoMD's generator advances across
  training iterations; BPTT checkpoint handling only prevents recomputation from rewinding it. A
  hypothetical fixed tape bank is ordinary sample-average approximation, held-out-tape testing is
  environment generalization, and matched tapes are common random numbers. The event-gradient
  variant duplicates three existing closed stochastic-semantic routes.
- Re-entry requires a frozen full L3/order-lifecycle asset, versioned assignment and interference,
  an untouched rule family, deterministic common-action adapters, and independent confirmation;
  OpenMarket additionally needs a second clock lineage or a nonvacuous offset-invariant estimand and
  a defensibly exogenous driver.
- Post-validation registry state: 424 evidence records, 48 trigger audits with zero qualified;
  route graph unchanged at 248 nodes, 265 edges and 935 locators.
