# Reproducibility artifact

This directory accompanies the anonymous ICLR 2027 manuscript *When Conservation Layers Are Not
Plug-and-Play: Identifying Training--Inference Path Dependence in Neural PDE Surrogates*.

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

## Environment

Use Python 3.11 in the project Conda environment:

```bash
conda run -n ecophys pip install -e '.[dev]'
```

The recorded GPU runs used PyTorch/CUDA on two independent V100 32 GB workers. Rebuilding tables,
figures, analyses from released records, and the paper does not require a GPU.

## Verification and rebuild

From the repository root, verify the release manifest and regenerate all result-derived TeX before
building the paper:

```bash
conda run -n ecophys python scripts/build_paper_d_supplement.py --regenerate
conda run -n ecophys python scripts/build_paper_d_supplement.py --verify
cd papers/paper_d_constraints
conda run -n ecophys tectonic main.tex
```

The verifier fails closed on a missing file, a SHA-256 mismatch, an incomplete registered record
block, a failed integrity gate, or a result-derived table/macro that differs from regeneration.
The full raw-data-to-model rerun commands are retained in the frozen configs and launch scripts;
they require locally staged HDF5 data matching the published locks.

Maintainers can create the deterministic release archive after placing the verified PDF at the
registered output path:

```bash
conda run -n ecophys python scripts/build_paper_d_supplement.py \
  --package output/paper_d_constraints_artifact.tar.gz
```

## Outcome-access chronology

The FNO cube, shallow-water replication, gauge intervention, and U-Net architecture-transfer test
each have a prospectively frozen protocol and machine decision. Runtime amendments may change only
transport or integrity mechanics. In particular, U-Net metrics remained sealed until both fixed
15-seed worker shards exited, exact 75+75 coverage was established, all 120 checkpoints were
validated, and the one-shot core and cube analyzers completed.
