# Experiment 142 — results

**Decision:** **PASS**
**Implementation:** `44daf531db4d72dbbee6776f929cd21df7882135`
**Protocol SHA-256:** `b8a77fad4bce7032eec5c5030fa71007b18375d3014464ae4a3ecc01eda6e270`

## Gate outcomes

- G1: PASS
- G2: PASS
- G3: PASS
- G4: PASS
- G5: PASS
- G6: PASS
- G7: PASS
- G8: PASS
- G9: PASS

All three frozen positive declarations were evaluated, as were all twelve single-defect mutations. The current
adapter was accepted only as `synthetic_fixture`, with its frozen event-counter warning. The aggregate-bin P3
and structurally admissible aggregate-event P2 declarations were accepted at their declared levels.

Every invalid declaration was rejected before its callback ran. Callback counts were zero for all twelve
mutations and exactly one for each valid declaration.

## Current-adapter probe

- Rows / latent steps: 256 / 256
- Fixed timestamp formula exact: True
- Unique consecutive IDs: 256 / True
- Removal/execution rows: 132
- Those rows referencing a prior ID: 0
- Declared price process: emitted_book
- Declared size unit: model_coordinate

## Interpretation

This result verifies a code-enforced vocabulary and pre-fit firewall only. It does not validate real-data fit,
causal latent inference, order-level mechanics, identifiability, audit-method novelty or market physics. A
separate preregistration is required for aggregate-bin reconstruction and any later external-data experiment.
