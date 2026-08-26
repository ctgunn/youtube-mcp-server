# MCP Configured-Runtime Verification Contract

## Purpose and scope

This contract defines the internal Layer 4 verification boundary for configured YouTube runtime behavior and its related operator-triggered local live smoke workflow. It validates existing public MCP behavior. It does not add public tools, change public tool schemas, make a remote MCP client, or alter normal CI/deployment behavior.

## Discovery and coverage contract

The deterministic matrix obtains the active inventory using a JSON-RPC `tools/list` request through the public `/mcp` route.

| Requirement | Contract |
| --- | --- |
| YouTube family identification | An endpoint descriptor uses `metadata.resourceFamily`; a composed descriptor uses `metadata.family`. |
| Coverage authority | The discovered YouTube-family set is the sole authority for matrix-family coverage. |
| Matrix completeness | Every discovered YouTube family has at least one active reviewed case; missing and stale families fail with stable names. |
| Generic tools | `server_ping`, `server_info`, `server_list_tools`, `search`, and `fetch` are explicitly recorded as outside configured-YouTube capability coverage. |
| Conditional tools | A case declares reviewed arguments that resolve its desired public or OAuth-required path. Names and read-like metadata alone cannot select a capability. |

## Configured invocation contract

Each matrix case sends a JSON-RPC `tools/call` request through `/mcp` using its discovered `toolName` and object `arguments`.

| Expected case | Required MCP and request-boundary result |
| --- | --- |
| API-key executable | The response is a non-error MCP result with structured content; the controlled opener records the expected non-secret path shape, HTTP method, API-key mode, and bounded request count. |
| OAuth-required without OAuth authority | The response is a safe MCP error envelope with the documented authorization category; the opener records zero external request attempts. |
| API-key-required without API key | The response is a safe MCP error envelope with the documented authentication category; the opener records zero external request attempts. |
| Other unavailable configured capability | The response is the reviewed safe MCP error category; it must not present representative local content as a configured success. |

The deterministic matrix installs networking guards. Any socket or URL-opening action outside the controlled opener fails the test. A captured request record contains only safe facts; it contains no query string, URL credential, header, body, raw response, token, key, signed URL, or media.

## Error, compatibility, and redaction contract

- The matrix validates existing JSON-RPC/MCP success and error envelopes without changing their schemas.
- Safe availability errors use the existing protocol mapping and expose only a stable category, credential type/name where appropriate, and other sanitized details.
- Sentinel credential values used in tests must not occur in results, errors, record fields, log capture, exception messages, documentation examples, or persisted evidence.
- Client-facing tool names, discovery descriptors, input schemas, and successful result shapes remain unchanged.

## Opt-in live smoke contract

| Requirement | Contract |
| --- | --- |
| Authorization | The workflow requires `RUN_YOUTUBE_LIVE_SMOKE=1` and the credential required by every selected entry before app construction or live request. Missing prerequisites fail closed with a fixed credential-safe message. |
| Selection | Only explicit active allowlist entries are selected. Entries must be public, read-only, API-key capable, discovered, and use reviewed public reference inputs. |
| Exclusions | Mutations, uploads, downloads, deletes, ratings, reports, moderation, subscriptions, OAuth-required, owner-only, and all non-allowlisted tools are excluded and not invoked. |
| Invocation | Selected entries use the public MCP route and have finite request-count and timeout bounds. |
| Reporting | Emit one credential-safe result for every selected or excluded tool: structured success summary, documented safe availability error, exclusion, or actionable safe failure. No raw exception text, headers, inputs, request bodies, or upstream bodies may be emitted. |
| Execution boundary | The workflow is manual and opt-in. It is excluded from `make test`, `make quality`, CI, and automated deployment gates. OPS-405 owns remote running-server verification. |

## Contract validation

`make test-runtime` validates deterministic discovery-derived coverage, public-route invocation, capability classification, safe error mapping, live-runtime request construction, bounded records, and redaction without a network request. `make test-live-smoke` is a manually authorized command, not ordinary completion evidence. `make quality` remains the required full repository validation command.
