# PDEBench Burgers data-admission runtime amendment

Recorded 2026-09-01 NZST after the first data-admission process exited and before any dataset byte
was downloaded or inspected.

The frozen data-admission command failed while importing the runner because the declared V100b
environment lacked `h5py`. The preserved log contains only
`ModuleNotFoundError: No module named 'h5py'`; no partial or complete dataset file was created and
no data or model outcome exists.

This is a runtime-only dependency amendment. The successful V100a PDEBench environment contains
Python 3.11.15, NumPy 2.4.6, PyTorch 2.3.1+cu121, OmegaConf 2.3.1, and h5py 3.16.0. The designated
V100b environment has the same first four versions and lacks only h5py. Install exactly
`h5py==3.16.0` into the designated Conda prefix, verify those five versions, and retry the exact
same frozen data-admission command once with a new log. Preserve the first failure log.

No dataset identity, viscosity, schema, split, invariant threshold, restriction method, model,
seed, analysis rule, or scientific interpretation may change under this amendment. A failure
after the dependency import succeeds is governed by the original terminal data-gate policy.
