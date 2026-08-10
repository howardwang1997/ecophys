# `data/sample/` — research-internal cache

Files historically tracked in this directory are **not part of the EcoMD public release
artifact**. The repository's MIT license covers code, not third-party datasets. Do not copy,
package, mirror, or redistribute these files merely because they are present in git.

## Redistribution status

| Source | Historical local material | Public-release decision |
|---|---|---|
| Yahoo Finance | SPY and index daily parquet shards | Exclude. Yahoo's help page restricts redistribution of Yahoo Finance information. |
| LOBSTER | 2012-06-21 academic sample ZIPs | Exclude unless LOBSTER gives written permission. The embedded sample readme contains no explicit redistribution grant. |
| Binance Data Vision | BTCUSDT and ETHUSDT minute parquet shards | Exclude until an explicit applicable redistribution license is recorded. |

Relevant source pages:

- Yahoo Finance exchanges and data providers: <https://help.yahoo.com/kb/account/exchanges-data-providers-yahoo-finance-sln2310.html>
- LOBSTER data samples: <https://data.lobsterdata.com/info/DataSamples.php>
- LOBSTER legal notice and terms: <https://data.lobsterdata.com/imprint.php>
- Binance Data Vision: <https://data.binance.vision/>

This is a conservative release decision, not legal advice. Internal research use must also
follow the terms under which each researcher obtained the data.

## Required replacement for a public artifact

The source preview uses deterministic synthetic trajectories for installation, schema,
rollout, and scoring smoke tests. For empirical reproduction, publish:

1. acquisition instructions pointing to the original provider;
2. expected raw-file hashes where the provider permits this;
3. deterministic preprocessing code and its git SHA;
4. temporal split manifests and derived-artifact hashes;
5. no raw vendor bytes unless redistribution permission is documented.

LOBSTER archive provenance and hashes are recorded in
[`LOBSTER/PROVENANCE.md`](LOBSTER/PROVENANCE.md). That provenance record explicitly does
not grant redistribution rights.
