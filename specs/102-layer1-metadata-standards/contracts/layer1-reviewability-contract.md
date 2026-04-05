# Contract: YT-102 Layer 1 Reviewability Contract

## Purpose

Define the internal review contract that future Layer 2 and Layer 3 authors depend on when choosing representative Layer 1 wrappers for composition.

## Consumer Expectations

Higher-layer planning and review consumers may rely on:

- stable wrapper identity using resource and operation naming
- maintainer-visible HTTP method and path shape
- visible quota cost for each representative wrapper
- explicit auth expectations, including mixed or conditional explanations
- explicit lifecycle or documentation caveats where relevant
- review surfaces that keep `operationKey`, `authMode`, `quotaCost`, `authConditionNote`, and `caveatNote` visible together

Higher-layer planning and review consumers must not need to rely on:

- raw upstream documentation as the only source of quota or auth expectations
- runtime credential payloads to understand wrapper auth behavior
- hidden caveats stored only in implementation history or reviewer memory

## Comparison Rules

Representative wrapper artifacts must support comparison across wrappers for:

- endpoint identity
- quota cost
- auth expectations
- caveat severity and implications

If two wrappers differ materially on quota or auth behavior, the contract artifacts must make that difference visible enough for a maintainer to choose between them quickly.

## Caveat Consumption Rules

When a wrapper carries a lifecycle or documentation caveat, the consumer must be able to understand:

- what type of caveat applies
- why it matters for reuse
- whether it changes auth, availability, or planning assumptions

Free-form notes that omit these implications do not satisfy the reviewability contract.

## Validation Expectations

Representative proof for YT-102 must show:

- one or more wrappers can be reviewed for identity, quota, and auth expectations without external research
- at least one mixed or caveated scenario is documented clearly enough for a maintainer to interpret
- artifact-based tests protect against regressions that make quota, auth, or caveat information harder to find

Required coverage:

- contract checks for metadata-standard artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/102-layer1-metadata-standards/contracts/`
- unit coverage for metadata completeness rules
- integration or contract checks showing future higher-layer planning can still compare representative wrappers through the existing Layer 1 foundation

## Non-Goals

- This contract does not require new public MCP tool metadata.
- This contract does not require end-to-end hosted transport changes.
- This contract does not require expansion to the full endpoint inventory in YT-102.
