# PDEBench 1D Burgers coordinate-schema freeze

Frozen before download or inspection of file ID 281363.

The exact expected HDF5 schema is `tensor`, `x-coordinate`, and `t-coordinate`. The scalar tensor
must be float32 with shape `[10000,201,1024]`. The periodic spatial grid spans `[-1,1)` with 1024
cell centers: first coordinate `-0.9990234375`, uniform spacing `0.001953125`, and period 2. The
used time coordinate has 201 entries from 0 through 2 with spacing 0.01; the released raw vector
is expected to contain one unused trailing coordinate at 2.01, matching the established PDEBench
1D file convention.

Coordinate absolute tolerance is `1e-6`. Any shape, dtype, start, period, monotonicity, uniformity,
time length, or trailing-coordinate mismatch terminates this data-admission attempt. It cannot be
reinterpreted from model results or repaired by silently changing the coordinate contract.

