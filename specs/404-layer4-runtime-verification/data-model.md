# Data Model: Layer 4 Configured-Runtime Capability and Live Verification

## Capability Matrix Case

Represents one reviewed deterministic MCP invocation for a configured YouTube family and one expected capability boundary.

| Field | Description | Validation |
| --- | --- | --- |
| `family` | Discovery-derived YouTube resource or composed family. | Non-empty; must match a discovered YouTube family exactly. |
| `toolName` | Public MCP tool selected for the family. | Must be returned by `tools/list` and belong to `family`. |
| `arguments` | Reviewed safe object arguments. | Object; selects the intended public or owner-sensitive conditional path; contains no real secret or media. |
| `configuredCapability` | Available configuration used for the case. | API-key-only, OAuth-capable, or absent required capability. |
| `expectedOutcome` | Required capability result. | Exactly API-key executable, OAuth-required, or unavailable. |
| `expectedErrorCategory` | Safe error category for unavailable cases. | Required only when success is not expected. |
| `expectedRequest` | Expected safe request facts for executable cases. | Required only for executable cases; specifies path shape, method, credential mode, and maximum count. |
| `purpose` | Reviewer explanation of case safety and coverage. | Non-empty text. |

**Relationship**: Every discovered YouTube family has one or more Capability Matrix Cases. Each case produces exactly one Verification Result. Generic baseline/retrieval tools are reported as excluded from this matrix.

## Controlled Request Record

Represents non-secret evidence that a configured MCP invocation reached the live runtime boundary without network I/O.

| Field | Description | Validation |
| --- | --- | --- |
| `toolName` | Tool associated with the captured request. | References the executing matrix case. |
| `family` | Family associated with the request. | Matches the matrix case family. |
| `pathShape` | Upstream route path without query parameters. | Matches the case's expected path shape. |
| `method` | Intended request method. | Matches the case's expected method. |
| `credentialMode` | Selected capability form. | API key or OAuth; never includes a credential value. |
| `requestCount` | Count of controlled opener calls for the case. | At least one only for executable cases; never exceeds its documented bound. |

The record must not contain a full URL, query string, headers, request body, response body, token, key, signed URL, or raw media.

## Capability Coverage Report

Represents aggregate deterministic coverage for a run.

| Field | Description | Validation |
| --- | --- | --- |
| `discoveredYouTubeFamilies` | Families obtained from public discovery metadata. | Non-empty unique set. |
| `excludedNonYouTubeTools` | Generic descriptors intentionally outside the matrix. | Explicitly recorded; not classified as unavailable YouTube capability. |
| `matrixFamilies` | Families represented by active matrix records. | Must exactly equal `discoveredYouTubeFamilies`. |
| `missingFamilies` | Discovered families without a case. | Must be empty. |
| `staleFamilies` | Matrix families not discovered. | Must be empty. |
| `results` | One Verification Result per executed case. | Each references a valid matrix case and satisfies its expected outcome. |

## Verification Result

Represents the credential-safe public-route outcome for one matrix or live-smoke case.

| Field | Description | Validation |
| --- | --- | --- |
| `subject` | Tool or family under verification. | Non-empty known identity. |
| `kind` | Matrix or live-smoke result type. | One of the documented verification types. |
| `outcome` | Success, safe availability error, excluded, or actionable failure. | Must match the selection and expected classification. |
| `safeCategory` | Error/availability category where applicable. | Credential-safe; required for failed/unavailable outcome. |
| `summary` | Minimal operator-facing evidence. | Must be actionable and must not contain unsafe fields. |

## Live Smoke Allowlist Entry

Represents one explicitly approved live operation for manual verification.

| Field | Description | Validation |
| --- | --- | --- |
| `toolName` | Public read-only MCP tool approved for live execution. | Must be explicitly maintained, currently discovered, and not in an excluded operation class. |
| `arguments` | Reviewed public reference input. | Object; no private IDs, secrets, or sensitive content. |
| `requiredCapability` | Credential requirement. | API-key public-read only for OPS-404. |
| `requestBound` | Maximum allowed upstream calls. | Positive finite count. |
| `timeoutBound` | Maximum time permitted for a call. | Positive finite duration consistent with configured runtime policy. |
| `purpose` | Why this operation is safe and valuable as smoke evidence. | Non-empty text. |

**State transitions**: `draft` → `reviewed` → `active`; an active entry becomes `stale` when discovery removes the tool and is rejected before live invocation. Any entry not explicitly active is `excluded` and must not be invoked.
