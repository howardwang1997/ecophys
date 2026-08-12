# Experiment 144 result — negative controls confirmed

**Formal decision:** `NEGATIVE_CONTROLS_CONFIRMED`  
**Candidate admission:** false  
**Novelty pass:** false  
**Raw SHA-256:** `92351520b073d6674c0629380020599273c2beada29faf06437546a421eddcf8`

## Chronology

- Preregistration commit: `3964b45c9dc1b98c706612ab773ffd4ce417127d`.
- Implementation commit: `24e7097107f8197508508c154a752ca9184b379f`.
- Formal freeze/run commit: `0a07c0228440dc896867fe7f69a6fb2181ff29c2`.
- The formal runner executed once from a clean checkout and created the raw artifact without overwrite.

## W1 — stacked observability

| Quantity | Result | Frozen expectation |
|---|---:|---:|
| rank of `C1^T C1` | 1 | 1 |
| rank of `C2^T C2` | 1 | 1 |
| rank of summed Gramian | 2 | 2 |
| summed eigenvalues | `[1.0, 1.0]` | `[1.0, 1.0]` |
| max difference from vertically stacked Gramian | `0.0` | `<=1e-12` |

Decision: `CONFIRMED_GENERIC_REDUCTION`.

The fixture demonstrates that complementary mechanisms can repair rank deficiency, but the calculation is exactly
ordinary stacked observability. It is a useful necessary sanity check and zero evidence that the proposed NMI
mechanism-excitation margin is new.

## W2 — order effect without adaptation

Both fixed matrices were valid row-stochastic operators. With no adaptive state or learned transition:

- `p0 P_A P_B y = 0.45500000000000007`;
- `p0 P_B P_A y = 0.38000000000000006`;
- swapped-order difference = `0.07500000000000001`;
- direct commutator response = `0.07499999999999996`.

Decision: `CONFIRMED_ORDER_EFFECT_WITHOUT_ADAPTATION`.

The tiny floating discrepancy between the last two values is below the frozen `1e-12` tolerance. A raw order
effect, response commutator or loop area therefore cannot identify behavioral adaptation. NCS-M1 can remain open
only in its stricter excess-over-frozen form with relaxation and confounding controls.

## Candidate consequences

- **NMI-T1 received no support:** its easiest witness is explicitly generic. A subsequent same-session audit of
  switching-system identification, active intervention design and the event-layer information identity retired it
  as `RETIRED_PRIOR_ART`; that retirement is not an exp144 gate output.
- **NCS-M1 remains `ATTACKING`:** the naive certificate is falsified. The next allowed work is to identify whether
  `R_obs-R_frozen` is causally identified and stable across adequate frozen baselines; no real data is opened yet.
- No candidate advances to `CONJECTURE` or `READY_FOR_HUMAN_AUDIT`.

## Resource audit

- Inputs: committed constants only.
- Market data files read: 0.
- Sealed periods opened: 0.
- Network access during formal run: false.
- Device: Mac CPU; wall time `0.02685` s inside the runner.
- GPU use: 0.0 hours. Neither V100 nor the RTX2060 was contacted.

No data purchase, compute expansion or worker queue is authorized by this result.
