# CoW competition HEAD enumeration results

**Executed:** 2026-08-15 08:43--08:50 UTC

**Protocol commit:** `c2bea87c23d4415071077d3b7784cb059e24474f`

**Decision:** `FAIL_MINIMUM_ELIGIBLE_COUNT_NO_GET`

## Result

All access-integrity gates passed, but the preregistered minimum sample size did not. Exactly 384 frozen IDs were
requested once with HEAD in the declared order. All 384 returned a terminal permitted status: 93 HTTP 200 and 291
HTTP 404. The required eligible count was at least 100.

No resolved manifest was generated. No competition response body may be opened, no seven-row top-up may be run,
and neither the threshold nor the candidate frame may be changed for this experiment.

| Gate | Observed | Required | Result |
|---|---:|---:|---|
| candidate requests | 384 | 384 | pass |
| exact candidate order and indexes | 384/384 | 100% | pass |
| request method | HEAD only | HEAD only | pass |
| terminal statuses | 384/384 in `{200,404}` | 100% | pass |
| transport-error rows | 0 | 0 | pass |
| attempts per ID | 1 | retained; bounded | pass |
| response-body bytes read | 0 | 0 | pass |
| forbidden body/header fields retained | 0 | 0 | pass |
| eligible IDs | 93 | at least 100 | **fail** |

The local eligible fraction is 93/384 = 24.21875%. It is not a population prevalence or historical-retention
estimate. It differs from the prior consumed sparse frame's 33/100 rate, which is consistent with time-varying use
of the shared sequence by fast-path quotes and empty auctions. No causal explanation is identified from status
codes alone.

## Artifacts

- status-only request ledger:
  `artifacts/head_request_ledger.jsonl`, SHA-256
  `2f9ae3e94aae1cb02e23d2e85eba44914b45f450e6414475ecc8b3137749dcd9`;
- compact summary:
  `artifacts/head_enumeration_summary.json`, SHA-256
  `4c52b570dcef855e686eb39997f30fcc7703c58b60598da3328c48133579176b`;
- candidate-list SHA-256:
  `ea4ad29d44185999c18d89338147a9394324d664c7c3280637266798787bbf35`;
- status-200 ID-list SHA-256:
  `21eb3b0a4168c402bb933f13f9733a05a9e99ae4598c00f84c13baf5b1e8a2a4`.

## Scientific disposition

HEAD is a technically clean existence enumerator, and the run confirms that the prior 404s need not indicate
transport failure. It does not, however, pass the sealed sample-size gate. The 93 IDs remain transparency metadata,
not an authorized GET set.

CoW payload work can reopen only through a prospectively frozen route that is not a post-hoc top-up—for example,
an official historical-list endpoint, an official database snapshot or a separately justified collaboration.
Until then, V14's free exact-mechanism development should move to a system whose full event index and executable
state transition are public on-chain. All GPU/model work remains locked.

## Resources

Wall time was about 6.5 minutes at one request per second. Paid data, competition-body bytes, GPU-hours and remote
worker use were all zero.
