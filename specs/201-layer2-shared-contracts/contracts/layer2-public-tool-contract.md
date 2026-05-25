# Contract: YT-201 Layer 2 Public MCP Tool Contract

## Purpose

Define the shared public MCP-facing contract for Layer 2 YouTube Data API endpoint tools. Later endpoint slices from YT-203 through YT-255 must use this contract rather than redefining naming, metadata, input, response, auth, quota, caveat, or error conventions.

This contract defines shared behavior only. It does not add a concrete endpoint-backed tool by itself.

## Contract Scope

- Public Layer 2 MCP tool naming
- Required endpoint identity metadata
- Auth mode and quota visibility
- MCP-facing input contract conventions
- Near-raw response conventions
- Safe caller-facing error categories
- Caveat and deprecation visibility
- Representative examples used to validate shared rules

This contract does not define Layer 3 composed tools, heuristic workflows, hosted transport changes, new persistence, or individual endpoint implementation details.

## Public Tool Naming

Layer 2 public tool names must:

- Use `resource_method`
- Omit a redundant `youtube_` prefix
- Preserve meaningful upstream camelCase method suffixes
- Stay deterministic across documentation, registration, tests, and examples

Required examples:

| Upstream Endpoint | Public Tool Name |
|-------------------|------------------|
| `activities.list` | `activities_list` |
| `captions.insert` | `captions_insert` |
| `comments.setModerationStatus` | `comments_setModerationStatus` |
| `videos.getRating` | `videos_getRating` |
| `watermarks.unset` | `watermarks_unset` |

## Required Tool Metadata

Every Layer 2 tool contract must expose:

- Public MCP tool name
- Mapped YouTube resource and method
- Stable internal operation identity used to reach Layer 1 behavior
- Official quota-unit cost
- Auth mode: API-key, OAuth-required, or mixed/conditional
- Deprecation, availability, high-cost, media-handling, or documentation caveats when applicable
- Near-raw response convention
- Safe error categories

Descriptions must be understandable from MCP tool discovery without requiring the caller to read endpoint-specific implementation files.

## Input Contract Rules

Layer 2 inputs must stay close to upstream YouTube Data API request concepts.

Input contracts must document:

- Required fields
- Optional fields
- Mutually exclusive selectors
- Conditional selectors
- `part` selection when supported upstream
- Pagination fields when supported upstream
- Request body fields for create, update, moderation, abuse-report, or mutation operations
- Media or upload-related fields when supported upstream
- Delegation or content-owner fields when supported upstream

Validation failures must be deterministic and safe for MCP clients. Validation messages must not expose credentials, tokens, stack traces, or raw upstream internals.

## Response Contract Rules

Layer 2 responses must stay near-raw to upstream resource shape while remaining MCP-safe.

Responses must preserve upstream-visible concepts when present:

- Returned resource items
- Requested resource parts
- Paging tokens
- Mutation acknowledgments
- Upload or media operation result identity
- Downloaded content metadata or safe transport wrapper

Light wrapper fields are allowed only for:

- MCP clarity
- Upstream endpoint identity
- Safe metadata such as quota cost or requested parts
- Safe content delivery for payloads that cannot be returned as plain JSON fields

Layer 2 responses must not present higher-level composition, ranking, enrichment, or heuristic interpretation as if it were raw endpoint behavior.

## Auth and Quota Rules

Each Layer 2 tool must declare one of:

- `api_key`
- `oauth_required`
- `mixed/conditional`

Mixed or conditional auth must describe the selector, caller context, or request mode that changes the credential requirement.

Each Layer 2 tool must expose the official quota-unit cost. High-cost tools must call out the cost clearly in discovery metadata or review-facing contract evidence.

## Error Contract Rules

Layer 2 tools must map failures to stable MCP-safe categories:

- `authentication_failed`
- `authorization_failed`
- `quota_exhausted`
- `resource_not_found`
- `invalid_request`
- `deprecated_endpoint`
- `endpoint_unavailable`
- `upstream_failure`

Safe error details may include:

- Public tool name
- Upstream resource and method
- Safe parameter names
- Safe validation category
- Retry or remediation hint when available

Safe error details must not include:

- API keys
- OAuth tokens
- Secret values
- Stack traces
- Raw signed URLs
- Raw media payloads
- Sensitive channel-owner or delegated-owner credential details

## Representative Shape Coverage

YT-201 must validate this contract against representative examples for:

- Simple read endpoint
- Paginated list endpoint
- CamelCase method endpoint
- OAuth-only endpoint
- Mutation endpoint
- Upload or media-related endpoint
- High-quota endpoint
- Deprecated or availability-constrained endpoint

Representative examples prove shared coverage only; they do not constitute endpoint implementation.

## Review Validation Expectations

Reviewers must be able to verify that:

- A public name can be derived from a resource-method pair
- Required metadata is present for each representative example
- Auth and quota are visible before invocation
- Input rules explain upstream parameter mapping
- Response rules preserve near-raw semantics
- Safe error categories exclude secrets and stack traces
- The slice does not introduce actual endpoint-backed tool behavior beyond representative examples
- Any new or changed Python functions include reStructuredText docstrings

## Implementation Alignment

The shared implementation uses `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py` for public contract metadata and naming, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py` for input, response, and safe-error conventions, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py` for representative non-executing examples.
