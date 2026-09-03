# Gradient-coupling factorial-join integrity runtime amendment

Registered 2026-09-01T09:57:11Z while the Advection factorial was incomplete and outcome-blind,
before any formal gradient diagnostic record existed and before the version-2 mechanism snapshot
was deployed.

## Integrity gap and correction

The scientific protocol requires each diagnostic to reconstruct the exact factorial seed's
training subset and initial tensor and to bind one executable source snapshot. The version-2
analyzer verified absolute/residual pairing within diagnostic records but did not independently
cross-check those two hashes against the completed factorial records at join time. It also checked
required source-manifest entries record by record without requiring one identical manifest across
all 60 records.

The corrected analyzer now fails closed unless, for every seed and both coordinates:

1. the diagnostic initialization SHA-256 equals the paired factorial initialization SHA-256;
2. the diagnostic full training-index SHA-256 equals the paired factorial training-index SHA-256;
3. all diagnostic records share one byte-equivalent canonical source SHA-256 manifest.

These checks do not change a statistic, record, seed, model, bootstrap draw, threshold, or
interpretation. They only make the frozen provenance and pairing requirements executable at the
final join. Regression tests independently alter both coordinate records for one seed's training
index, alter both initialization hashes, and split one source manifest; every mutation is rejected.

## Versioned lineage

- parent bootstrap runtime decision SHA-256:
  `92b859499fa7cc8ffc2d3541032437f16809d9f71d9af2c1092e4c339f8a5ab0`;
- superseded version-2 analyzer SHA-256:
  `3ce291bd38eaf51266b68ed5419b1fb453dc0ae36261e43e5526b9863f696d28`;
- corrected analyzer SHA-256:
  `549c0382b4466e7eea8447ccc401625696b7216f02990233100d2d76b8cefbd2`;
- corrected regression-test SHA-256:
  `6d7e2ccc73659ddd6f6f495c5b1ba29359a51b8300ab245e1078df8b47ccd337`.

The complete focused constraint/PDEBench suite passes 64/64 and Ruff passes. A new version-3
snapshot and machine decision are mandatory; versions 1 and 2 remain preserved and must not be
deployed. The original activation condition and scientific interpretation remain unchanged.
