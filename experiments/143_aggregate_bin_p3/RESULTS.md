# Experiment 143 — results

**Decision:** **PASS**
**Implementation:** `2b54170e17d4b6fb549c94cf8bb65370555e9994`
**Protocol SHA-256:** `2fca1cf1ae8b36db7e882d826b0c96bc76c942f07ef8e6c2216f25ad4d9832c7`

## Gate outcomes

- G1: PASS — chronology_provenance
- G2: PASS — schema_units_clock
- G3: PASS — hand_fixture
- G4: PASS — generated_reconstruction
- G5: PASS — state_completeness
- G6: PASS — train_only_firewall
- G7: PASS — parameter_recovery
- G8: PASS — negative_controls
- G9: PASS — identifiability
- G10: PASS — code_quality_complete_reporting

## Reconstruction

- Generated bins / raw rows: 4096 / 104160
- Mark counts exact: True
- Executed share volume exact: True
- Maximum return error: 1.700e-16
- Chunk/checkpoint return bit-exact: True

## Train-only P3 controls

- Return latent/observation-only RMSE ratio: 0.313397
- Log-volume latent/observation-only RMSE ratio: 0.437417
- Direction latent minus observation-only: 0.100119 nats/event
- Anchored minus sign-flipped direction: 0.457133 nats/event
- Held-out corruption left fit exact: True
- Training corruption changed fit hash: True
- Identifiability warning: `COEFFICIENTS_CONDITIONAL_ON_FROZEN_LATENT_SCALE`

## Interpretation

This result validates generated aggregate-bin reconstruction and a train-only P3 measurement implementation.
It does not validate EcoMD on market data, event/order mechanics, latent-agent recovery, audit novelty or market
physics. Event/order support remains FAIL; external evidence remains F4.
