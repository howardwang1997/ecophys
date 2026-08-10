# LOBSTER academic sample provenance

## Source and custody

- Source family: LOBSTER academic sample files, `https://data.lobsterdata.com/sample/`.
- Vendor sample date: 2012-06-21 NASDAQ order flow.
- The exact download timestamp was not preserved by the original ingestion. The files first appear in repository
  commit `d586e521c6b4bdce32ae2e8a129a20d678d1e579` dated 2026-04-24. This first-seen date must not be presented
  as a known download time.
- All eight archives contain the same `LOBSTER_SampleFiles_ReadMe.txt`; its SHA-256 is
  `fd97b5f49391e11ef52c023ef8f3ca156baac7441b4d52240339f60844244d5b`.
- The embedded ReadMe identifies the material as LOBSTER academic data and documents the schema, but it does not
  contain an explicit redistribution license grant. Do not package or redistribute these ZIPs outside the
  existing research repository without a separate license review.

## Raw archive manifest

| Archive | SHA-256 |
|---|---|
| `LOBSTER_SampleFile_AAPL_2012-06-21_10.zip` | `326839316d67d7819ca0541ffdf73cdb044d6ae4105cce0ef9c615e8848e9d43` |
| `LOBSTER_SampleFile_AAPL_2012-06-21_50.zip` | `dac5ef12f918f34ba3ac64e013ccd1c64009dc7b17d3f247a3c81c71534ab0e5` |
| `LOBSTER_SampleFile_AMZN_2012-06-21_10.zip` | `5cff62a609b27aef82285382ad646c4c2facc0a692a60bedda633de64c4aa54f` |
| `LOBSTER_SampleFile_GOOG_2012-06-21_10.zip` | `2fa66b61c7c4d4cd3f19180aaa7f5937a26355f81b2ac8e4a84e36550e8dde4a` |
| `LOBSTER_SampleFile_MSFT_2012-06-21_1.zip` | `613f9638c95b4b04894d046f784ac7bb7cbc0744f5bd873ee2d67d2cb7570928` |
| `LOBSTER_SampleFile_MSFT_2012-06-21_10.zip` | `0825e00ec83cb8ac8b53fd1efb7f2138b7848659e625c49621ebd9b55757be4c` |
| `LOBSTER_SampleFile_MSFT_2012-06-21_50.zip` | `5994afa0ff5edf4a7213f36bade73d2a5f3c2060d60c25260807c3245b307a17` |
| `LOBSTER_SampleFile_SPY_2012-06-21_50.zip` | `2d562be866e6285aa6ca1e37a9a2ec4a6503b156a230948879beaf2431c7b991` |

These are raw vendor archives; there is no preprocessing hash distinct from the archive SHA-256. Every derived
artifact must record the exact archive hash, implementation git SHA, frozen protocol hash and any deterministic
timestamp transformation. Exp130 is the first schema/reconstruction audit; exp138 is the first preregistered
continuous-time baseline audit.
