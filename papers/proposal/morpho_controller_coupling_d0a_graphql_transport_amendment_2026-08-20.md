# Morpho D0A v2 — GraphQL transport amendment

## Trigger

The first clean v1 invocation from pushed commit `e49a331b631677413e2e034f17de977a69021ab9` received no
allocator-role payload. The Morpho API returned HTTP 404 with `Cannot GET` for the exact documented V1 REST
allocator path. The runner exhausted its three identical retries and stopped without creating a result artifact.
A separate diagnostic GET reproduced the same 404 and 131-byte error body.

No vault role, allocator address, transaction history, amount, rate, utilization or outcome was returned. This is
a transport-contract failure, not a scientific D0A pass or fail.

## Single amendment

V2 replaces the unavailable REST GET with the official documentation's GraphQL exact-vault role query at
`https://api.morpho.org/graphql`. Each of the same three candidates is queried separately. The query requests only
vault address, current name and allocator addresses. V1/V2 response shapes are parsed separately and the returned
vault address must equal the frozen input.

The REST documentation advertised role-grant transaction hashes, while the documented GraphQL selection exposes
only current addresses. V2 therefore removes grant hashes from retained D0A fields and defers exact grant-event
provenance to D0B. Grant hashes were never used by a D0A hard gate.

## What does not change

- the three operators, anchor vaults, addresses, chains and vault versions;
- all documentary sources and policy-family labels;
- the official Public Allocator exclusion;
- exactly one non-public allocator per anchor;
- three pairwise-distinct non-public allocator addresses;
- three independent operator labels and at least two policy descriptions;
- all forbidden data, stop rules and zero-GPU rule.

The v1 config remains committed with SHA-256
`49ab2ae1aa9571ccdfcd7f4a1eb469ebcc26063b69b5202d29eb168a89bc04c3`. V2 cannot add candidates, inspect
histories or relax a scientific threshold. It receives one formal run only after its code/config are clean,
committed and pushed.
