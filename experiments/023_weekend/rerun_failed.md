# Weekend batch — failed configs rerun plan

12 configs from the weekend batch failed:

## Group A: F4-F8 — "parameter incompatibility" (5 configs)

These changed `simulator.hidden`, `simulator.d_state`, or `simulator.sps_k_random`.
Mac smoke confirmed they DO run when no checkpoint exists.

**Most likely cause**: stale `checkpoint.pt` from a prior run with different
shape, OR config-side validation issue specific to H20 device. Without logs
we can't pin it. Two diagnostics:

1. **Try with explicit fresh start** (delete any stale ckpt before each):
   ```bash
   for L in f4_hidden64 f5_hidden96 f6_dstate64 f7_sps100 f8_sps200; do
       rm -f experiments/023_weekend/results_$L/checkpoint.pt
   done
   bash scripts/h20_weekend.sh F            # SKIP_DONE=1 still skips done; remove dir to force
   ```

2. **Try Mac --smoke first** to see if the config validates:
   ```bash
   conda run -n ecophys python -m ecomd.training.train_distributed \
       --config experiments/023_weekend/config_f4_hidden64.yaml --smoke
   ```

## Group B: F11, F14, H series — OOM (7 configs)

Hardware-bound. Below are smaller-chunk replacements. Append to weekend
batch as `*_safe.yaml` versions.

| Original | Fix |
|---|---|
| F11 chunk_steps=32 | drop to 20 |
| F14 F3-loss + hidden=64 + 3-asset | drop chunk_steps to 16 |
| H0 N=20K chunk=20 | drop to 16 |
| H1 N=50K chunk=14 | drop to 8 |
| H2 N=20K + F3 loss chunk=20 | drop to 16 |
| H3 N=50K + F3 loss chunk=14 | drop to 8 |
| H4 N=100K chunk=8 | drop to 4, OR skip (yolo) |

(See `rerun_failed_oom.sh` for ready-to-run shrunk variants.)
