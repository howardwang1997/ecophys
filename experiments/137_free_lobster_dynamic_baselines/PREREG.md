# Experiment 137 — free LOBSTER dynamic queue and observation-only baselines

**Frozen:** 2026-08-19, before model fitting  
**Status:** zero-cost real-data feasibility; not an EcoMD-vs-market result  
**Resources:** five already-present LOBSTER sample archives; 2 × V100 and 1 × RTX 2060; no H20/purchase

## Question

Can the observation bridge represent real dynamic price levels and queues without lookahead, and are simple
observation-only baselines strong enough that a later EcoMD claim must beat them? This closes part of the gap
left by exp136's fixed-grid, self-generated messages. It does not fit EcoMD and therefore cannot establish that
EcoMD explains real order flow.

The official Tardis first-of-month Binance sample remains the intended crypto schema check, but its documented
download URL returned Cloudflare HTTP 403 from two independent egresses on 2026-08-19. That access failure is
kept separate from this experiment and is not silently replaced by a claim that LOBSTER represents crypto.

## Frozen independent paths and split

Use exactly one archive for each of AAPL, AMZN, GOOG, MSFT and SPY. Duplicate depth variants of AAPL/MSFT are
excluded to avoid pseudo-replication. Retain the first 200,000 rows and top 10 levels; SPY L50 is explicitly
censored to L10. For every symbol use the first 60% of eligible event transitions for training, the next 20%
for diagnostics only, and the final 20% for the reported test score. No random row split is allowed.

At event `t`, features use the post-event displayed book and messages observed no later than `t`; the target is
the type/side class of event `t+1`. Types 1--5 crossed with bid/ask direction give ten classes. Rows with any
other type/direction are excluded before the chronological split.

## Frozen observation-only baselines

- **unconditional:** train-split class frequencies with Laplace smoothing;
- **Markov:** previous-event-to-next-event transition table with Laplace smoothing;
- **Hawkes-style history:** multinomial linear model on exponentially decayed class counts with fixed 0.1,
  1 and 10 second time scales (a history baseline, not a fitted continuous-time Hawkes likelihood);
- **queue-reactive L1/L5/L10:** multinomial linear models using spread, displayed depth/imbalance, top queues,
  last mid-price change and observed event rate at the declared depth;
- **combined:** previous-class one-hot, history and L10 queue features;
- **latency stress:** refit the combined model with all features stale by 5 and 20 events.

Continuous features are standardized with train-split moments only. Linear models use zero initialization,
400 fixed AdamW steps, batch size 8,192, learning rate 0.03 and weight decay `1e-4`. Validation does not select
steps or hyperparameters. Report test cross-entropy, accuracy and gain over the matching unconditional model.

## Frozen gates

1. timestamps never decrease; books never cross/lock; sizes are nonnegative and levels are ordered;
2. visible type 1--4 messages reconstruct their exact dynamic price-level queue change at rate at least 0.999;
3. every declared model/stress score and fitted parameter is finite on all five paths;
4. all five symbol paths and every declared depth/latency variant complete;
5. on at least four of five symbols, the best non-unconditional observation-only model improves test
   cross-entropy by at least 0.01 nats/event.

Gate 5 is a baseline-relevance gate, not evidence for EcoMD. Failure means the chosen next-event mark task or
features are not a credible control and must be redesigned before G3. Thresholds cannot change in this version.

## Interpretation boundary

A pass establishes a leakage-free dynamic-book evaluator and nontrivial controls on one free market day. It
does not establish temporal generalization, crypto/equity universality, a full Hawkes point-process likelihood,
an EcoMD advantage or G3/G4. Multi-day crypto and US-equity L2 remain required after the upstream method gate.
