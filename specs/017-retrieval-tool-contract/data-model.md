# Data Model: FND-017 Retrieval Tool Contract Completeness

## Entity: ToolDiscoveryContract
Description: The MCP-visible descriptor for one retrieval tool as returned by `tools/list`.

Fields:
- `name` (string, required): Stable tool name exposed to MCP clients.
- `description` (string, required): Consumer-facing description of the tool purpose.
- `inputSchema` (object, required): Machine-readable definition of accepted request fields, required fields, allowed combinations, and unsupported shapes.

Validation rules:
- `inputSchema` MUST be sufficient for a client to construct a valid request without relying on separate undocumented rules.
- `inputSchema` MUST reject unsupported extra fields when the tool contract is defined as closed.
- Discovery metadata MUST remain aligned with the actual runtime acceptance and rejection behavior for the same tool.

## Entity: SearchRequestShape
Description: A valid or invalid request pattern a client may submit to the `search` tool.

Fields:
- `query` (string, required): Non-empty discovery query.
- `pageSize` (integer, optional): Positive result-page size.
- `cursor` (string, optional): Continuation token for a later page.

Validation rules:
- `query` MUST be present and non-empty for every valid request.
- `pageSize`, when present, MUST be a positive integer.
- `cursor`, when present, MUST use the retrieval contract’s accepted continuation-token format.
- Any unsupported field or malformed field value MUST be rejected consistently with the published contract.

## Entity: FetchIdentifierPattern
Description: One supported or unsupported identifier combination for targeting a source with `fetch`.

Fields:
- `resourceIdPresent` (boolean, required): Whether the request includes a search-derived resource identifier.
- `uriPresent` (boolean, required): Whether the request includes a canonical source URI.
- `relationship` (string, required): Whether the supplied identifiers are absent, single-source, matching, or conflicting.
- `valid` (boolean, required): Whether the pattern is accepted by the published contract.

Validation rules:
- A pattern with neither identifier present MUST be invalid.
- A pattern with only `resourceId` present MUST be valid when the identifier is otherwise well-formed.
- A pattern with only `uri` present MUST be valid when the identifier is otherwise well-formed.
- A pattern with both identifiers present MUST be valid only when they identify the same source.
- A pattern with conflicting identifiers MUST be invalid.

## Entity: FetchRequestShape
Description: A concrete `fetch` request built from one of the supported identifier patterns.

Fields:
- `resourceId` (string, optional): Search-derived retrieval identifier.
- `uri` (string, optional): Canonical source identifier.

Validation rules:
- The request MUST satisfy one of the supported `FetchIdentifierPattern` values published in discovery metadata.
- Unsupported extra fields MUST be rejected.
- Runtime validation MUST return a stable structured error when the request does not match a valid pattern.

## Entity: ValidationOutcome
Description: The observable result of applying the retrieval contract to a request shape.

Fields:
- `accepted` (boolean, required): Whether the request is allowed to execute.
- `failureCategory` (string, optional): Stable category for a rejected or unavailable request.
- `failureCode` (string, optional): Stable MCP-safe error-code family for a rejected request.

Validation rules:
- Every request shape marked valid by discovery metadata MUST produce `accepted = true` when the identifiers refer to a real supported source.
- Every request shape marked invalid by discovery metadata MUST produce `accepted = false` with a stable structured failure.
- Empty `search` results MUST remain a successful outcome and MUST NOT be represented as invalid input.

## Entity: VerificationExample
Description: A documented local or hosted example proving that a retrieval request can be constructed from discovery output alone.

Fields:
- `discoveryEvidence` (object, required): The tool descriptor or equivalent evidence used to build the call.
- `requestShape` (object, required): The concrete `search` or `fetch` request derived from discovery.
- `expectedOutcome` (string, required): Success, empty-result, or structured failure expectation.
- `verificationLevel` (string, required): Local, contract, integration, or hosted.

Validation rules:
- Verification examples MUST cover at least one valid `search` request.
- Verification examples MUST cover every supported valid `fetch` identifier pattern.
- Verification examples MUST cover the primary invalid retrieval shapes called out by the published contract.

## Relationships

- `ToolDiscoveryContract` defines one or more valid `SearchRequestShape` or `FetchRequestShape` values.
- `FetchIdentifierPattern` constrains which `FetchRequestShape` values are valid.
- `ValidationOutcome` records whether a `SearchRequestShape` or `FetchRequestShape` matches the `ToolDiscoveryContract`.
- `VerificationExample` proves that a request shape derived from `ToolDiscoveryContract` yields the documented `ValidationOutcome`.

## State Transitions

1. Client reads `ToolDiscoveryContract` from `tools/list`.
2. Client constructs a `SearchRequestShape` or `FetchRequestShape` based on the published schema.
3. Service applies structural and runtime validation to the request shape.
4. Valid request shapes proceed to execution and return success or an explicit non-error empty result.
5. Invalid request shapes return a stable `ValidationOutcome` with structured failure details.
6. `VerificationExample` records that the discovered contract and the live validation behavior matched for the tested scenario.
