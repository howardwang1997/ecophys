# Reproducibility artifact

This directory accompanies the anonymous ICLR 2027 manuscript *When Are Exact Conservation Layers
Plug-and-Play? Identifying Training--Inference Path Dependence in Neural PDE Surrogates*.

## What is included

The release bundle contains the manuscript source, frozen experiment protocols and machine
decisions, Hydra configurations, validation and analysis code, complete JSONL records, analysis
JSON, checkpoint-lock manifests, and the generated figure/table inputs. It covers:

- 30-seed PDEBench Advection FNO: 150 core records, 120 checkpoint locks, and 90 zero-training
  intervention-cube records;
- 30-seed PDEBench Advection U-Net: 150 core records, 120 checkpoint locks, and 90 zero-training
  intervention-cube records;
- 30-seed PDEBench 2D shallow water: 150 core records, 120 checkpoint locks, and 90 zero-training
  intervention-cube records;
- 60 Advection local-gradient records and 60 direct input-gauge records; and
- 1,830 valid records from the separate synthetic stress test, together with the two preserved
  zero-record numerical incidents.

The public PDEBench HDF5 files and trained checkpoint bytes are not redistributed. Data locks give
their exact identifiers, byte counts, licenses, and hashes; checkpoint locks bind each reported
record to its final weight file by run ID, path, payload schema, byte count, and SHA-256.
Because formal blocks were frozen at different times, a source path can legitimately have several
historical hashes. The bundle retains the immutable deployment snapshots, and the verifier checks
every record's `(path, SHA-256)` pair against either the current file or an archived snapshot; it
does not overwrite this history with the latest file at that path.

For double-blind review, the packager deterministically redacts personal home-directory, email,
copyright-holder, package-author, named private-SSH-login, and private-network-address strings from
otherwise byte-preserved text files, including text members of nested deployment snapshots, and
normalizes nested archive ownership metadata. The artifact
manifest records each affected path, its internal source hash, released hash, and transformation
category. The verifier accepts an original provenance hash only when the corresponding released
bytes match that mapping. The packager fails rather than alter a frozen numerical JSONL, canonical
analysis JSON, or current scientific configuration; no manuscript result is changed by this
identity-only step.
Legacy deployment `.sha256` and `.sha256s` files attest the pre-redaction source bytes and are
retained as historical records; `ARTIFACT_MANIFEST.json` is authoritative for released payload
bytes and records both sides of every permitted transformation.

Two separately registered public-data protocols stopped before model execution. The Burgers file
failed its frozen spatial-coordinate-start check, and the compressible Navier--Stokes file failed
its frozen time-coordinate shape check. Both terminal decisions and the available admission log are
included; each block has zero model records and contributes no estimate to the manuscript. These
data-contract failures are distinct from the two numerical incidents in the synthetic stress test.

## Environment

Create a dedicated Python 3.11 Conda environment and install the exact analysis stack used for the
byte-identical rebuild:

```bash
conda create -n ecophys-paper-d -c conda-forge \
  python=3.11 pip tectonic=0.17.0 poppler=26.02.0
conda run -n ecophys-paper-d pip install -r \
  papers/paper_d_constraints/requirements-analysis.txt
```

The recorded GPU runs used PyTorch/CUDA on two independent V100 32 GB workers. Rebuilding tables,
figures, analyses from released records, and the paper does not require a GPU.
The pinned file above reproduces the released-record analysis environment; it is not a claim that
stochastic CUDA training is bitwise portable. Every formal record separately captures its Python,
NumPy, PyTorch, CUDA, cuDNN, GPU, Git, and source-file provenance.

## Verification and rebuild

From the repository root, verify the release manifest and regenerate all result-derived TeX before
building the paper:

```bash
conda run -n ecophys-paper-d python scripts/build_paper_d_supplement.py --verify
conda run -n ecophys-paper-d python scripts/build_paper_d_supplement.py --regenerate
conda run -n ecophys-paper-d pytest -q \
  tests/test_constraint_iclr*.py tests/test_paper_d*.py tests/test_build_paper_d_supplement.py
cd papers/paper_d_constraints
env SOURCE_DATE_EPOCH=0 conda run -n ecophys-paper-d tectonic main.tex
```

The verifier fails closed on a missing file, a SHA-256 mismatch, an incomplete registered record
block, a failed integrity gate, or a result-derived table/macro that differs from regeneration.
The full raw-data-to-model rerun commands are retained in the frozen configs and launch scripts;
they require locally staged HDF5 data matching the published locks.

Maintainers can create the deterministic release archive after placing the verified PDF at the
registered output path:

```bash
conda run -n ecophys-paper-d python scripts/build_paper_d_supplement.py \
  --package output/paper_d_constraints_artifact.tar.gz
```

## Outcome-access chronology

The FNO cube, shallow-water replication, gauge intervention, and U-Net architecture-transfer test
each have a prospectively frozen protocol and machine decision. Runtime amendments may change only
transport or integrity mechanics. In particular, U-Net metrics remained sealed until both fixed
15-seed worker shards exited, exact 75+75 coverage was established, all 120 checkpoints were
validated, and the one-shot core and cube analyzers completed.
