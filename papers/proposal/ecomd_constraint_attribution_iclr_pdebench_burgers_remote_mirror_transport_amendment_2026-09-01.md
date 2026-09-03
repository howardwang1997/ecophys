# Burgers verified-mirror remote transport amendment

Registered 2026-09-01T09:48:25Z after the official Hugging Face mirror passed the frozen local
content-identity gate, before the HDF5 admission scan, before any Burgers model run, and without
accessing a partial Advection metric.

## Fixed content identity

The candidate remains exactly `pdebench/Burgers`, file
`1D_Burgers_Sols_Nu0.01.hdf5`, commit
`f4d2fc1541c43bd8c1cc8d4639760f59efa6439b`. Its completed local bytes passed all three frozen
identities:

- size `8232968312`;
- DaRUS MD5 `e6d9a4f62baf9a29121a816b919e2770`;
- SHA-256 `646f59072348fff722ffe65b47eda755fe1fe106f1dd4a76887cdb89b885ce7b`.

The previously authorized SCP copy remains an independent fallback. Its throughput sample was
approximately 0.4--1.2 MB/s. A 16,777,216-byte discarded range request from V100b to the exact
commit returned HTTP 206 at 1,307,533 bytes/s. This amendment permits that same host to download
the same fixed object to a second temporary filename. It changes transport only, not content.

## Authorized race and adoption gate

On V100b, `curl` may download with redirects, retries, and automatic continuation to
`/data/ecophys_pdebench_burgers_nu0p01/1D_Burgers_Sols_Nu0.01.hdf5.hf_direct_candidate`.
The active SCP temporary file remains untouched and keeps running as fallback. No HDF5 library or
value-level command may open either candidate during the race.

Whichever candidate first reaches the expected byte count must then pass the same remote size,
MD5, and SHA-256 gate. Only after all three match may the losing transfer be terminated, its
partial output moved intact to the deployment root's `excluded/transport_partial/`, and the
verified winner atomically renamed to the frozen final dataset path. A mismatch or oversized file
is excluded and never adopted; the other route continues. The unchanged full HDF5 admission script
is still mandatory after adoption and remains terminal on schema, finiteness, coordinate,
restriction-identity, or invariant-drift failure.

This amendment does not authorize a viscosity, threshold, seed, model, grid, optimizer, analysis,
or interpretation change. It cannot reveal any model metric or convert a failed data gate into a
scientific result.
