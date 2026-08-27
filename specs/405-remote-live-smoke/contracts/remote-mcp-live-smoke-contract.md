# Remote MCP Live-Smoke Contract

## Purpose and scope

This contract defines an internal, operator-triggered verification workflow for a running remote MCP server. It validates existing public MCP transport behavior and configured live YouTube execution. It does not add public tools, change client tool schemas or result envelopes, alter server authentication behavior, or make remote smoke part of ordinary automation.

## Authorization and command contract

| Requirement | Contract |
| --- | --- |
| Opt-in | The command requires `RUN_REMOTE_MCP_LIVE_SMOKE=1` and a non-empty `REMOTE_MCP_URL` before constructing a request. |
| Endpoint authentication | Set `REMOTE_MCP_AUTH_REQUIRED=1` when the selected endpoint requires bearer authentication and provide `MCP_AUTH_TOKEN`; the client sends it as bearer authorization on initialization and all continuation requests. A missing declared credential fails closed before remote activity. |
| Safe preflight failure | Missing, malformed, or rejected prerequisites yield a fixed credential-safe message/category and no raw input, token, header, session, URL query, or exception text. |
| Execution boundary | The command is manual and must remain excluded from `make test`, `make quality`, CI, and automated deployment gates. |

## Remote MCP transport contract

The client sends JSON-RPC requests to the remote MCP URL with JSON and event-stream acceptability.

| Step | Request requirement | Required response handling |
| --- | --- | --- |
| Initialize | Send `initialize` with safe client information and endpoint-required authentication. | Require a successful JSON-RPC initialization response, retain negotiated protocol version and returned session continuation value, and stop safely if initialization fails. |
| Discovery | Send `tools/list` with retained session/protocol/authentication information. | Require a valid catalog of uniquely named tools and capture only tool name plus optional `metadata.upstream.operationKey`. |
| Invocation | Send `tools/call` with retained session/protocol/authentication information, the discovered public name, and reviewed object arguments. | Accept a direct JSON-RPC envelope or the JSON-RPC event in a streamed call response. Normalize only the needed envelope; do not retain or output raw response data. |

No in-process application, dispatcher, fixture response, or local transport can satisfy this contract.

## Selection and fixture contract

| Requirement | Contract |
| --- | --- |
| Authority | The target's `tools/list` result determines whether an explicitly approved entry is currently available. It does not authorize a newly discovered tool. |
| Allowlist | Select only active entries from the reviewed 12-entry API-key public-read allowlist. Each entry has a bounded public object input, purpose, expected endpoint identity, and finite request bound. |
| Derived fixture | The approved `comments_list` input may derive exactly one public parent identifier in memory from the selected `commentThreads_list` response; it is never persisted or reported. |
| Exclusions | Create, update, delete, upload, download, rating, abuse-report, moderation, subscription, OAuth-required, owner-only, credential-sensitive, retrieval, baseline-server, and every non-allowlisted discovered tool are reported as excluded and never invoked. Eligibility cannot be inferred from a name, suffix, or generic read metadata. |
| Bounds | A run performs no more than 12 selected calls, plus one initialization and one discovery request. Each remote request has a finite 30-second timeout. Remaining selected work is reported as `bound_reached`, never retried indefinitely. |

The `test-remote-layer2-live-smoke` command retains the original 12-call Layer
2 suite. The separate `test-remote-layer3-live-smoke` command performs no more than 10
reviewed API-key-compatible Layer 3 calls, plus one initialization and one
discovery request. It validates each composed result against reviewed normalized
result fields, rather than the Layer 2 endpoint identity envelope. It excludes
caption/transcript OAuth workflows and higher-cost search/enrichment fan-out.

The aggregate `test-remote-live-smoke` command executes the Layer 2 and Layer
3 suites in separate sessions. It therefore preserves both suites' individual
limits and reports their results and combined bounded counts without combining
their allowlists or authorization contexts.

## Result, identity, and redaction contract

| Result condition | Required safe outcome |
| --- | --- |
| Structured successful result | Report `success`, tool identity, verified endpoint identity, and optional top-level item count only. Where the result contains `endpoint`, it must match the allowlist expectation and discovered `upstream.operationKey` when published. A mismatch is `actionable_failure`. |
| Documented public-data availability response | Report `safe_availability_error` with the documented stable category only. |
| Transport, session, timeout, malformed protocol, or unexpected result | Report `actionable_failure` with a fixed safe category, then continue only when the run/session bounds permit. |
| Unapproved discovered tool | Report `excluded` and make no call. |
| Limit prevents a selected call | Report `bound_reached` for that selected tool and make no call. |

The operator report presents one compact line per selected tool and aggregate passed, excluded, and request-bound counts. The in-memory report and any persisted evidence may contain only tool identity, selected/excluded state, terminal outcome, stable safe category, verified endpoint identity, item count, and bounded counts/timings. They must not contain credentials, authorization values, request headers, session IDs, complete endpoint URLs/query strings, request arguments, derived identifiers, raw upstream bodies, raw JSON-RPC error messages, or exception text.

## Compatibility and validation contract

- Existing tool names, discovery descriptors, input schemas, server results, server authentication, and session semantics remain unchanged; this is a verification consumer of those contracts, so no migration or versioning plan is required.
- A controlled loopback HTTP responder verifies the exact public request order, authentication forwarding without report leakage, session/version continuity, direct JSON and streamed response normalization, safe selection, bounds, identity comparison, and redaction without an external request.
- `make test-tools` and `make test-runtime` remain deterministic regression evidence. `make test` remains required specification evidence; `make quality` remains the full constitutional completion gate. The authorized remote command is separate evidence only.
