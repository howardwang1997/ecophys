#!/bin/zsh
# Auto-pull + adjudicate family C when the server JSONs land.
repo=/Users/howardwang/Desktop/playground/ecophys
outdir=$repo/experiments/constraint_attribution_audit/familyC
mkdir -p $outdir
echo "watcher started $(date)" >> $outdir/watcher.log
while true; do
  n=$(ssh -o BatchMode=yes -o ConnectTimeout=15 root@100.123.220.57 'ls /root/audit_out/C_*.json 2>/dev/null | wc -l' 2>/dev/null)
  echo "$(date) poll: $n/2 jsons" >> $outdir/watcher.log
  if [ "${n:-0}" -ge 2 ]; then
    scp -o BatchMode=yes "root@100.123.220.57:/root/audit_out/C_*.json" $outdir/ >> $outdir/watcher.log 2>&1
    /Users/howardwang/miniconda3/bin/conda run -n ecophys python $repo/scripts/analyze_constraint_audit.py \
      --records-dir $outdir --case ood_flat --out $outdir/verdicts.json \
      >> $outdir/watcher.log 2>&1
    echo "DONE $(date)" >> $outdir/watcher.log
    date > $outdir/PULLED.marker
    exit 0
  fi
  sleep 900
done
