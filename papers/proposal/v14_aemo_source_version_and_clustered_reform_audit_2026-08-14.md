# AEMO source-version and clustered-reform audit

**Date:** 2026-08-14

**Decision:** `ASYNC_MECHANISM_OBSERVATION_TOPOLOGY_REQUIRED`

**Gate consequence:** preserve the bounded-prefix result as `FAIL_VERSION_CLOCK_CONTRACT`; do not reinterpret
the 7/10 gate as a pass, open a full archive, read a `D` row or start model training. The next contract must key
versions by delivery channel and must represent the 24 October 2021 WDR/data-model release separately from the
1 October 2021 Five-Minute Settlement rule.

## 1. Question

The frozen bounded-prefix audit expected three report versions that did not match the untouched 2020-09 and
2022-04 public archives:

| Object | Frozen expectation | Observed information header | Added observed field |
|---|---|---|---|
| legacy period offer | `OFFER,BIDPEROFFER,2` | `OFFER,BIDPEROFFER,1` | none relative to the frozen projection |
| dispatch load | `DISPATCH,UNIT_SOLUTION,2` | `DISPATCH,UNIT_SOLUTION,3` | `DISPATCHMODETIME` |
| unit identity | `PARTICIPANT_REGISTRATION,DUDETAILSUMMARY,4` | `PARTICIPANT_REGISTRATION,DUDETAILSUMMARY,5` | `DISPATCHSUBTYPE` |

All member, package, table and required-field checks passed. The remaining question was whether the mismatches
were harmless serialization revisions, changes in the observation process, or evidence of another economic
mechanism boundary.

## 2. Official evidence and classification

| Finding | Official evidence | Classification and consequence |
|---|---|---|
| The `BIDPEROFFER` version-2 expectation came from the wrong delivery contract. | AEMO's [Data Model v5.00 specification](https://aemo.com.au/-/media/files/electricity/nem/5ms/systems-workstream/2021/emms-technical-specification-5ms-data-model-v500-marked-up.pdf) identifies discontinued records by `File ID`, delivered filename and CSV report type. Its `OFFER,BIDPEROFFER,2` mapping is specifically for `NEXT_DAY_OFFER_ENERGY` and `NEXT_DAY_OFFER_FCAS`. It separately labels monthly-DVD changes as non-Data-Model file changes. The untouched object is a `PUBLIC_DVD_BIDPEROFFER` monthly archive whose own information header is version 1. | `DELIVERY_CHANNEL_SCOPED`. The original v2 gate correctly fails, but v2 was an unsupported transfer from a participant next-day report to a public monthly archive. Report version is not a global property of a database table. This conclusion is an inference from AEMO's explicit file-ID scoping plus the observed header; AEMO does not document the 2020 public-DVD v1 object in the cited v5.00 mapping. |
| Data Model v5.1 entered production on 24 October 2021. | AEMO's [October 2021 EMMS release specification](https://www.aemo.com.au/-/media/files/market-it-systems/der-guides/emms/2021/emms-release-schedule-and-technical-specification-oct-21.pdf) gives production implementation on 18--24 October and production go-live on 24 October. | `OBSERVATION_RELEASE_CLOCK`. A post-5MS month cannot be versioned only by the 1 October 5MS rule date. |
| `DISPATCH,UNIT_SOLUTION,3` adds `DISPATCHMODETIME` without changing the declared primary key. | The same v5.1 specification lists report type `DISPATCH,UNIT_SOLUTION,3`, retains the `DUID, INTERVENTION, RUNNO, SETTLEMENTDATE` key and defines `DISPATCHMODETIME` as minutes in the current fast-start dispatch mode, sourced from NEMDE's `FSTARGETMODETIME`. Its change summary labels the addition as an FSIP change. | `DYNAMIC_STATE_OBSERVATION_EXTENSION`. Stable columns can be projected for row identity, but the field is scientifically meaningful state. A cross-version model must mark it unavailable before v3 and either model the latent fast-start state, stratify/exclude affected units, or show invariance to its omission. |
| `DUDETAILSUMMARY` v5 adds the identity needed to distinguish WDR loads. | The v5.1 specification lists `PARTICIPANT_REGISTRATION,DUDETAILSUMMARY,5`, retains the `DUID, START_DATE` key and defines `DISPATCHSUBTYPE=WDR` for wholesale-demand-response loads. AEMO explicitly warns that `DISPATCHTYPE` alone can produce incorrect analysis. | `MECHANISM_IDENTITY_EXTENSION`. Dropping this field is invalid for loads. Generator-only projections retain row identity but do not remove market-wide WDR spillovers. |
| WDR began on the same day as the v5.1 release, 23 days after 5MS. | AEMO states that the [Wholesale Demand Response mechanism](https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/market-operations/wdrm) commenced on 24 October 2021; AEMO records 5MS commencement on [1 October 2021](https://www.aemo.com.au/initiatives/major-programs/past-major-programs/five-minute-settlement). | `CLUSTERED_REAL_MECHANISM`. October is not one post-5MS regime: 1--23 October has 5MS without live WDR, whereas 24 October onward has 5MS, WDR and v5.1 observation changes. |
| The new submission-method field did not make transition provenance observable. | The v5.1 specification adds private `BIDOFFERFILETRK.SUBMISSION_METHOD` with values such as FTP/API/WEB, but explicitly says it would not be populated within the WDR project timeline. | `DECLARED_BUT_UNOBSERVED`. It is a transport field, not proof of legacy versus 5-minute bid semantics, and it cannot recover historical submission mode during this release. Public report shape must not be treated as participant interface choice because AEMO also generated compatibility reports. |

The official PDF was checked through both its extracted text and rendered pages for the production schedule,
`SUBMISSION_METHOD` warning, `DISPATCHMODETIME` definition, `DUDETAILSUMMARY` primary key and
`DISPATCHSUBTYPE` definition. The page rendering agreed with the text layer. The rendered archival copy came from
AEMO's [NEMWeb historical documentation archive](https://nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/2022/MMSDM_2022_11/MMSDM_Historical_Data_SQLLoader/DOCUMENTATION/MMS%20Data%20Model/v5.1/EMMS%20Release%20Schedule%20and%20Technical%20Specification%20-%20October%202021.pdf),
was 1,323,904 bytes and had SHA-256
`e105809a162cdc3df798bf404ecd9c8ab6d32b98bffd48fd1bf94f60c00cbd5c`. Its relevant content was independently
matched against AEMO's current direct v5.1 document linked above.

## 3. Revised event topology

The correct observation object is not a single schema clock. It is an asynchronous graph of rule, reporting,
delivery-channel and table-specific changes:

```text
2021-03-08  O_bid: emulated five-minute reporting enters production
      |
2021-04-01  M_bid: dual legacy/new bidding interfaces begin
      |             underlying interface choice remains partly unobserved
2021-10-01  M_5MS: native five-minute settlement rule commences
      |
2021-10-24  M_WDR: wholesale demand response commences
              + O_v5.1: Data Model v5.1 goes live
                  |-- S_dispatch v3: observes DISPATCHMODETIME
                  |-- S_identity v5: observes DISPATCHSUBTYPE/WDR
                  `-- S_submit: SUBMISSION_METHOD declared but not populated
```

For an object `x`, the minimum version identity is therefore

\[
V(x)=\bigl(\text{delivery channel},\ \text{file ID/archive family},\ \text{member},\
\text{package},\ \text{table/report},\ \text{report version},\ \text{effective interval}\bigr).
\]

The action/rule state must be stored separately from `V(x)`. Equality of projected numerical fields does not
establish equality of action semantics, and a new observation field does not by itself establish a new market
mechanism.

## 4. Consequences for the historical development experiment

### 4.1 Temporal regimes

At minimum, the AEMO development design needs these intervals:

| Interval | Mechanisms | Observation qualification |
|---|---|---|
| before 2021-03-08 | legacy settlement and bidding | legacy bid reports |
| 2021-03-08 through 2021-03-31 | legacy actions | reporting bridge; direct measurement-shock negative control |
| 2021-04-01 through 2021-09-30 | pre-commencement settlement; dual bidding interfaces under equality constraints | compatibility/current reports coexist; underlying submission route is partly identified |
| 2021-10-01 through 2021-10-23 | 5MS live; WDR not live | short diagnostic isolation window under pre-v5.1 observation |
| from 2021-10-24 | 5MS plus WDR | v5.1 identity/state observation; source-specific report versions |

The 23-day isolation interval is useful for diagnostics, not a clean stand-alone causal estimate: anticipation,
adaptation, seasonality and other contemporaneous shocks remain possible. Month-level October treatment coding is
prohibited.

### 4.2 Projection rules

- `PUBLIC_DVD_BIDPEROFFER` may be projected only under an archive-family-specific frozen contract. The observed
  2020-09 version-1 object remains discovery evidence and cannot validate its own repaired expectation.
- `UNIT_SOLUTION` v2/v3 may share stable row keys and declared core fields, but every analysis must expose the
  `DISPATCHMODETIME` availability boundary and a fast-start sensitivity analysis.
- `DUDETAILSUMMARY` v4/v5 must not be collapsed for loads. WDR identity is required from 24 October; excluding WDR
  rows does not eliminate equilibrium spillovers from the mechanism.
- A report-generation label is not an observed participant submission choice during emulation. Unknown interface
  provenance must remain unknown or enter partial-identification bounds.

### 4.3 Model-to-observation bridge

The simulator should emit latent economic state and actions before any source adapter is applied. A versioned
observation operator then maps them to the fields actually visible under each source contract, including missing
state, compatibility replication, coarsening and unpopulated provenance. This is a general method requirement for
V14 rather than an AEMO parser exception.

A development model fails the bridge test if it:

1. infers adaptation at the 8 March reporting-only boundary;
2. attributes the 24 October joint WDR/v5.1 boundary solely to 5MS;
3. uses `DISPATCHTYPE` alone to classify post-release loads;
4. assumes `DISPATCHMODETIME` existed before its report version; or
5. recovers a latent submission route from report shape without an identified measurement model.

## 5. NCS/NMI implication

For an NCS route, this supports a substantive computational-method problem: intervention prediction under
asynchronous mechanism and observation changes, tested on a real staged reform. The method must outperform
single-clock and schema-normalization baselines beyond AEMO; a detailed data-cleaning postmortem alone is not an
NCS contribution.

For an NMI route, the burden is higher. The observation operator or learning objective must be genuinely new and
transfer across independently governed systems. Encoding known release dates in a graph is infrastructure, not
methodological novelty.

## 6. Executed gate and next admissible gate

The source-contract matrix was frozen at commit `39c45dddf736e418a3e112a5a4689a782e918466`. Its selection rule chose
2021-02 as the nearest complete month before the reporting bridge and 2021-11 as the nearest complete month after
the WDR/v5.1 boundary, without checking availability. All ten fresh objects passed HTTP, parsing, exact
channel/package/table/version and required/forbidden-field projections. This independently confirms the scientific
header matrix, including `PUBLIC_DVD` bid-period version 1 and the v5.1 state/identity additions.

The overall protocol nevertheless failed `FAIL_FULL_ARCHIVE_TRANSFER_GUARD`. Each fixed request allowed 256 KiB,
but the two `DUDETAILSUMMARY` objects were only 150,150 and 162,163 compressed bytes. Their `Content-Range` values
show that every compressed byte was returned. The parser inflated only its bounded prefix and opened no `D` row,
but the raw summary's hard-coded `full_archive_downloaded=false` is incorrect. The immutable raw summary and
separate adjudication are preserved in `experiments/v14_aemo_source_contract_audit/`.

The next protocol must:

1. detect a complete-object response from `Content-Range` and fail it automatically;
2. use a smaller fixed byte range that cannot consume the known small identity objects;
3. prove header parse sufficiency on synthetic or already consumed material;
4. select new untouched months mechanically and prohibit rerunning or replacing 2021-02/2021-11; and
5. retain all mechanism, channel, fast-start, WDR and partial-provenance constraints.

No row-level E1 sample, bulk synchronization, causal claim, paid data, prospective outcome or GPU training is
authorized.

The network-unexecuted repair is now specified at
`experiments/v14_aemo_source_contract_repair/PREREGISTRATION.md`. Its offline proof supports an exact 64 KiB cap,
and its exclusion rule selects 2021-01/2021-12. These are development confirmation months, not new held-out causal
events. The protocol must be committed and pushed before one no-replacement execution.
