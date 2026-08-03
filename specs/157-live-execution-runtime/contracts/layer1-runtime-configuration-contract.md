# Layer 1 Runtime Configuration Contract

## Purpose

Define how application runtime configuration supplies credentials and execution settings to the shared Layer 1 live runtime without exposing secret values or changing public MCP tool schemas.

## Configuration Inputs

| Setting | Required when | Meaning | Safe diagnostics |
| --- | --- | --- | --- |
| `YOUTUBE_API_KEY` | An API-key operation is invoked; existing hosted profile validation may also require it. | Opaque credential for public API-key access. | Only the setting name and absence/invalidity may be reported. |
| `YOUTUBE_OAUTH_TOKEN` | An OAuth-required operation is invoked. | Opaque upstream OAuth access token. Token acquisition and refresh are outside this feature. | Only the setting name and absence/invalidity may be reported. |
| Live timeout/retry settings | Runtime construction. | Existing shared live-executor controls. | Values may be reported when non-secret. |

The runtime configuration is read at application composition time and injected into the dispatcher/descriptors. Individual tools and wrappers do not read environment variables directly.

## Credential Selection

| Existing operation requirement | Required runtime input | Result when unavailable |
| --- | --- | --- |
| API key | Nonblank `YOUTUBE_API_KEY` | Safe normalized configuration/authentication failure; no execution and no representative result. |
| OAuth required | Nonblank `YOUTUBE_OAUTH_TOKEN` | Safe normalized configuration/authorization failure; no execution and no representative result. |
| Mixed/conditional | The credential selected by existing selector and wrapper rules. | Do not silently choose another mode; return the safe failure for the selected mode. |

Credential values are available only to the in-process request constructor. They must not be placed in descriptor metadata, handler defaults, MCP responses, normalized errors, logs, test names, fixtures, or documentation examples.

## Live-Default and Injection Rules

1. Normal configured application, HTTP transport, and dispatcher construction selects the shared live executor.
2. A live executor uses existing endpoint metadata, wrapper validation, request shaping, retry policy, observability hooks, error normalization, and response normalizers.
3. Explicitly supplied executor, opener, credential, or representative transport dependencies remain allowed for isolated tests and deliberate local-development use.
4. The absence of an explicitly supplied test/local dependency never authorizes an implicit representative default in configured runtime construction.
5. A configuration, credential, or upstream failure returns a safe normalized failure; it never returns a static or sample successful payload.

## Compatibility and Rollback

- Existing public tool names, input schemas, metadata, result shapes, and safe error categories remain unchanged.
- Existing wrapper contracts and resource-specific validation remain unchanged.
- The addition is backward-compatible for callers that explicitly inject an executor or credential in tests.
- If live runtime configuration is rolled back or unavailable, the safe behavior is a clear normalized failure, not a return to implicit representative production results.
