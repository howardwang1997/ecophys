# Intervention registry v2 — human-readable decision

The canonical registry is `intervention_registry_v2.yaml`; its validator is
`ecomd.research.intervention_registry`. It contains rule, timing, design, schema/access and licence metadata only,
not market records or treatment statistics.

## Routing summary

| Role | Count | Cases |
|---|---:|---|
| `development_only` | 2 | US Tick Size Pilot; NYSE American speed bump |
| `sealed_candidate` | 0 | none |
| `reject` | 8 | Regulation SHO pilot; US, UK, Australian and EU short-sale restrictions; unimplemented US and Canadian fee pilots; NYSE floor closure |

`ready_for_data_contract: false`. A C1 contract requires at least one development case and one untouched independent
replication; the second condition is absent.

## Decisive screening logic

- Tick Size Pilot has unusually strong official controls but both forward and reverse periods are already studied.
- NYSE American supplies a documented launch/removal, but the removal is bundled with order-type and later DMM
  changes, multivenue routing spills over, and the launch is already studied.
- Emergency short-sale bans coincide with systemic crises and simultaneous policies; nominal untreated groups do
  not isolate a slow adaptive response.
- The US Transaction Fee Pilot and conditional Canadian rebate pilot never generated treatment.
- The NYSE floor closure is inseparable from COVID-19, extraordinary volatility, emergency rules and phased
  reopening.

## Governance note

No raw records were opened. Public pages and search summaries nevertheless exposed already-published numerical
summaries for the two development cases during screening. The machine registry records this as a protocol
deviation and its validator forbids either case from being relabelled `sealed_candidate`.

Validate with:

```bash
conda run -n ecophys python -m ecomd.research.intervention_registry \
  research/theory_exploration/intervention_registry_v2.yaml
```
