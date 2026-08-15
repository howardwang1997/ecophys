# AEMO NEMDE two-interval XML conformance v1

**Frozen:** 2026-08-15 06:31:08 UTC

**Parent:** `a20d778626523eb6546fce9629680ab1fed7fc53`

**Manifest:** `data/manifests/aemo_nemde_xml_conformance_v1.yaml`

## Question

Do the exact interval-144 members identified by the passed tail inventory form valid production NEMDE XML cases
with the input, output and price-setting structure described by AEMO in both the pre- and post-5MS regimes?

This remains a development-only source/schema test. It does not run NEMDE, estimate replay error, infer strategic
intent or inspect a target event.

## Frozen byte selection

The prior committed inventory uniquely selected the two members before XML access:

| Date | Member | Local-header offset | Compressed bytes | CRC32 |
|---|---|---:|---:|---|
| 2021-01-01 | `NEMSPDOutputs_2021010114400.loaded` | 57,637,442 | 404,030 | `11f971a8` |
| 2021-12-01 | `NEMSPDOutputs_2021120114400.loaded` | 65,590,506 | 459,136 | `ebbea93d` |

Each source receives exactly one 1 MiB HTTP range beginning at the frozen local-header offset. The exact ranges are
`57637442-58686017` and `65590506-66639081`. Retry, extension, replacement and full download are prohibited. Both
opaque responses must be size/SHA-256 verified in R2 before the first local header or XML byte is parsed. Bytes
after the selected compressed member are ignored.

## Immutable gates

For each object, the local header must reproduce the frozen member name, flags, deflate method, CRC, compressed
size and uncompressed size. Raw-deflate decoding must reach EOF with no tail, match the exact uncompressed size and
CRC, contain no DTD/entity declaration and parse as XML.

The local-name inventory must contain exactly one each of `NemSpdInputs`, `NemSpdOutputs` and `SolutionAnalysis`.
The input section must contain AEMO's documented `Case`, region, trader, period, interconnector and generic-
constraint groups. The output must contain case, period, region, interconnector, trader and constraint solution
groups. `SolutionAnalysis` must be nonempty. Action-like attribute names are reported against a frozen vocabulary
but are not a gate because the official guide describes semantics more reliably than exact attribute spelling.

`PASS_NEMDE_XML_CONFORMANCE` unlocks only design of a one-day, 288-case alignment/replay audit. It does not make
the exact solver executable, establish raw participant submissions/rejections, or authorize causal/model claims.
Raw redistribution remains prohibited pending written AEMO clarification. Total source data are 2 MiB; all GPU,
remote-worker and paid-data requirements are zero.
