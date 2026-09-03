# PDEBench Burgers verified-mirror transport amendment

Frozen 2026-09-01 NZST while the DaRUS Wget fallback remained active, before any complete
Burgers file or data-admission outcome existed and before any Burgers model run.

The official `pdebench/Burgers` Hugging Face dataset provides
`1D_Burgers_Sols_Nu0.01.hdf5` at verified repository commit `f4d2fc1`. Its file page reports
8.23 GB and SHA-256
`646f59072348fff722ffe65b47eda755fe1fe106f1dd4a76887cdb89b885ce7b`.
This is maintained under the PDEBench organization and carries the same CC BY 4.0 license.

The mirror is authorized only as a candidate byte transport. It may replace the slow DaRUS
partial transfer if and only if the locally reconstructed file simultaneously has:

- exact frozen size 8,232,968,312 bytes;
- exact DaRUS v8 MD5 `e6d9a4f62baf9a29121a816b919e2770`; and
- exact Hugging Face file SHA-256
  `646f59072348fff722ffe65b47eda755fe1fe106f1dd4a76887cdb89b885ce7b`.

Passing all three proves that the candidate is the same frozen byte sequence, not an alternate
scientific dataset. The candidate may be downloaded locally with the already installed
`huggingface_hub`/`hf_xet` client, with the Xet chunk cache disabled to avoid a second 8 GB local
copy. The active Wget remains an untouched fallback during candidate acquisition.

After a local triple-hash pass, terminate only the exact Wget PID, preserve its partial bytes under
the deployment's `excluded/transport_partial/` directory, SCP the verified candidate to a distinct
temporary remote filename, and repeat the same size, MD5, and SHA-256 checks remotely before an
atomic rename to the frozen final filename. The unchanged preparation script then performs the
full schema, finiteness, mass-drift, and conservative-restriction admission scan.

Any mismatch is terminal for the candidate and leaves Wget as the fallback. No model, threshold,
split, viscosity, schema, scientific endpoint, or analysis rule changes under this amendment.

