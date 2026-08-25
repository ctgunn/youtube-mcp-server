# Data Model: Layer 4 Default MCP Tool-Catalog Verification

## Discovered Tool

Represents one default public tool returned by the public discovery route during the current verification run.

| Field | Description | Validation |
| --- | --- | --- |
| `name` | Public tool name and fixture key. | Non-empty string; unique within the discovered catalog. |
| `description` | Public summary supplied by discovery. | String. |
| `inputSchema` | Public invocation shape. | Object. |
| `metadata.upstream.operationKey` | Optional upstream operation identity. | Used only when present with a returned endpoint value. |

**Relationship**: Every Discovered Tool must have exactly one Catalog Invocation Fixture and exactly one Route Invocation Result.

## Catalog Invocation Fixture

Represents the reviewed deterministic input and expected outcome for one public tool.

| Field | Description | Validation |
| --- | --- | --- |
| `toolName` | Public tool name covered by the fixture. | Must equal one discovered name; exactly one fixture per discovered name. |
| `arguments` | Safe deterministic invocation arguments. | JSON object; no credentials, raw media, or real external identifiers. |
| `expectedOutcome` | Expected route result kind. | Exactly `success` or `error`. |
| `expectedErrorCategory` | Safe MCP error category for no-data/error fixtures. | Required only for `error`; must be a documented category. |
| `purpose` | Brief reason the input is safe and representative. | Non-empty human-readable text. |

**State transitions**: `draft` → `reviewed` → `active`; an active fixture becomes `stale` when discovery no longer contains `toolName`, and it becomes `missing` when a discovered name has no active fixture. Both stale and missing states fail verification.

## Route Invocation Result

Represents one public-route response for one discovered tool and fixture pair.

| Field | Description | Validation |
| --- | --- | --- |
| `toolName` | Tool invoked. | Must reference one Discovered Tool and one fixture. |
| `requestId` | Unique verification request identifier. | Non-empty and traceable to the individual test case. |
| `response` | Returned MCP JSON-RPC envelope. | Must be an envelope; no uncaught process exception is acceptable. |
| `outcome` | Observed `success` or `error`. | Must match the fixture expectation. |
| `structuredContent` | Structured successful content. | Required and nonempty for success. |
| `observedErrorCategory` | Error category observed through the route. | Required for expected errors; must equal the fixture's category. |
| `observedEndpoint` | Endpoint value returned by structured content, if any. | If present together with an upstream operation key, values must match. |

## Catalog Coverage Report

Represents the aggregate test result for one catalog-discovery run.

| Field | Description | Validation |
| --- | --- | --- |
| `discoveredNames` | Names returned by public discovery. | Non-empty unique set. |
| `fixtureNames` | Names in the fixture registry. | Must exactly equal `discoveredNames`. |
| `missingNames` | Discovered names without fixtures. | Must be empty. |
| `staleNames` | Fixture names not discovered. | Must be empty. |
| `results` | One Route Invocation Result per discovered name. | Same cardinality and name set as `discoveredNames`. |

The report is valid only when both name differences are empty and every result passes its fixture contract.
