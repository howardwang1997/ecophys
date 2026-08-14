# AEMO two-clock bounded ZIP-prefix header validation

**Frozen:** 2026-08-14T10:35:26Z

**Parent commit:** `2f650ab0753ce4a6f7bd0611dd9c42327f6e0137`

**Scientific role:** development-only observation-contract validation. It cannot establish row quality, behavior or
a market effect.

## Question

Do the untouched archive objects in the loader-validated 2020-09 and 2022-04 months expose the exact
package/table/version and field identities predicted by the two-clock contract?

The loader gate passed before this protocol was written. ZIP and CSV content from these months had not been
requested. A parser preflight used only the already consumed 2021-03 discovery daily-offer object; it confirmed
that AEMO supports bounded byte ranges and that the first MMSDM `I` row can be recovered from a ZIP prefix.

## Frozen objects and expectations

The exact ten URL set contains, in fixed order, `BIDDAYOFFER`, `BIDPEROFFER`, `DISPATCHOFFERTRK`, `DISPATCHLOAD`
and `DUDETAILSUMMARY` for 2020-09 and 2022-04. Expected member names, package/table/version triples and required
fields are frozen in `data/manifests/aemo_prefix_header_audit_v4.yaml`.

The 2020-09 period contract is legacy `OFFER,BIDPEROFFER,2`; the 2022-04 period contract is
`BIDS,BIDOFFERPERIOD,1`. Dispatch applied-offer and unit-solution identities and effective-dated unit identity must
also remain available on both sides.

## Bounded acquisition and gates

Each exact URL receives one `Range: bytes=0-262143` request. The collector reads a body only after HTTP 206 and
never falls back to HTTP 200 or a full download. It parses the first ZIP local-file header, decompresses no more
than 65,536 prefix bytes, and accepts only an MMSDM `I` row before any `D` row.

The experiment passes only if all ten objects:

- return HTTP 206 with a valid zero-based `Content-Range`;
- remain within the 262,144-byte response cap;
- expose the exact frozen first CSV member;
- expose the exact package/table/version triple; and
- contain every frozen required field.

No missing or mismatched object may be replaced. Raw prefix bytes are not committed; URL, response headers, byte
count, prefix SHA-256 and parsed `I` metadata are retained.

## Lock

No `D` row, row count, full archive, CRC scan, row filter, join, target outcome, paid data, remote worker or GPU is
authorized. A pass confirms only header-level feasibility and still does not unlock row access or full download.
