# ICLR final pilot cell lock

Date: 2026-08-31, after clean provenance replacements completed and before any pilot OOD metric or
confirmation outcome was accessed.

## Immutable inputs

- Selector input manifest:
  `experiments/constraint_attribution_iclr/pilot/final_selector_input_20260831.json`
- Input-manifest SHA-256:
  `d6e8fd774cfa37f5b24478dbcc583ced30af37938a916414b261d7e5be5b94b4`
- Ten included files, 4,980 unique raw records, 4,800 eligible records, and zero provenance
  failures. B/C selection admits only learning rates `{0.0003,0.001}`; 180 B `lr=0.003` records
  remain immutable but excluded.
- Full clean H-near replacement SHA-256:
  `934a74662a480a8197775b2399e89f9a0dce7d9531c06ba6d6b8c51b8974215d`
- Corrected clean C-ad2d replacement SHA-256:
  `d0bf4646a85e5c41cda8b170df5f21481b82e5705ecb88abc34b1e7ea6db0f11`

The old H-near and C files and provisional lock are excluded exactly as recorded in the input
manifest. Raw files were never rewritten.

## Final ID-only lock

- Lock: `experiments/constraint_attribution_iclr/pilot/pilot_lock_final_idonly_20260831.json`
- Lock SHA-256:
  `5100ae5ca6f757a5166fba3692fd912e19e7a0c7a4da65980488e92a402c604e`
- Selection accessed pilot ID RMSE and compute proxy only.
- Confirmation partition remains the untouched paired seeds 1000--1029.
- The lock contains 58 unique mechanism/cell confirmation jobs across ten systems.

Primary branch status:

| system | free--free-res | free-res--hard |
|---|---|---|
| A-advection | fixed-compute non-overlap | matched ID+compute |
| A-Burgers | matched ID+compute | matched ID+compute |
| A-diffusion | fixed-compute non-overlap | matched ID+compute |
| B-advection | matched ID+compute | matched ID+compute |
| B-Burgers | matched ID+compute | matched ID+compute |
| B-diffusion | fixed-compute non-overlap | fixed-compute non-overlap |
| C-ad2d | matched ID+compute | matched ID+compute |
| H-near | fixed-compute non-overlap | matched ID+compute |
| H-strong | matched ID+compute | matched ID+compute |
| M2-FIFO | matched ID+compute | matched ID+compute |

The corrected C grid therefore does not trigger its omitted-cell expansion. All already expanded
systems have exhausted their single predeclared search; remaining non-overlap uses the frozen
fixed-compute wording and cannot justify another grid or wider tolerance.

## Next gate

Package the lock, confirmation manifest/configs, runners, analyzer, fail-fast provenance utility,
protocol amendments, and tests into a new hash-verified confirmation snapshot. Set
`ECOPHYS_GIT_HEAD=86dd76ee0127c5eb7945a5806bdad74548c62459` and `ECOPHYS_DIRTY=1` on every remote command.
Before the production jobs, run a one-record provenance preflight on each server. Do not inspect
pilot OOD while preparing or launching confirmation.
