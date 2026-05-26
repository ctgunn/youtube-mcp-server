# Contract: YT-202 Layer 2 Metadata, Naming, and Quota Standards

## Purpose

Define the public MCP-facing metadata standard for every Layer 2 endpoint-backed YouTube Data API tool. Later endpoint slices from YT-203 through YT-255 must use this contract to expose upstream identity, deterministic public names, official quota cost, auth mode, availability state, usage notes, and response-boundary expectations before invocation.

This contract extends the YT-201 shared Layer 2 public tool contract. It does not add concrete endpoint-backed tool behavior by itself.

## Contract Scope

- Required public metadata fields
- Public tool naming standard
- Quota visibility in metadata, descriptions, and usage notes
- Auth mode disclosure
- Availability and caveat disclosure
- Response-shaping boundary classification
- Representative metadata example coverage
- Validation and review expectations

This contract does not define Layer 3 composed tools, hosted transport behavior, persistence, external dependencies, or endpoint-specific upstream execution.

## Required Metadata Fields

Every Layer 2 endpoint-backed tool definition must expose:

- Public MCP tool name
- Mapped YouTube resource name
- Mapped YouTube method name
- Stable operation key used to reference Layer 1 behavior
- Official quota-unit cost
- Auth mode: `api_key`, `oauth_required`, or `mixed/conditional`
- Availability state
- Caller-facing description
- Caller-facing usage notes or example notes
- Caveats when applicable
- Response-boundary classification

These fields must be available to discovery, review, or representative contract surfaces before a caller invokes the tool.

## Public Tool Naming

Layer 2 public tool names must:

- Use `resource_method`
- Omit a redundant `youtube_` prefix
- Preserve meaningful upstream camelCase method suffixes
- Stay deterministic across documentation, examples, tests, and registration metadata

Required examples:

| Upstream Endpoint | Public Tool Name |
|-------------------|------------------|
| `videos.list` | `videos_list` |
| `playlists.insert` | `playlists_insert` |
| `comments.setModerationStatus` | `comments_setModerationStatus` |
| `videos.getRating` | `videos_getRating` |
| `videos.reportAbuse` | `videos_reportAbuse` |
| `playlistItems.list` | `playlistItems_list` |

## Quota Visibility

Every Layer 2 tool must expose official quota-unit cost in:

- Structured metadata
- Tool description text
- Usage notes or example notes

High-cost tools must include an explicit warning before invocation. High-cost examples include search, captions mutation/download, and video upload operations.

Quota values must be positive integers. If official documentation is inconsistent, the tool metadata or adjacent caveat note must record the inconsistency rather than silently choosing a value.

## Auth Mode Disclosure

Each Layer 2 tool must declare one auth mode:

- `api_key`: API-key access is sufficient for the documented operation mode
- `oauth_required`: OAuth credentials are required before invocation
- `mixed/conditional`: Credential requirements depend on selector, caller context, ownership, privacy, mutation mode, or another documented condition

Mixed or conditional auth must include a safe condition note. Auth disclosure must not include credentials, token values, secret names, or private configuration details.

## Availability and Caveat Disclosure

Each Layer 2 tool must declare an availability state. Supported states are:

- `active`
- `deprecated`
- `unavailable`
- `region_constrained`
- `owner_only`
- `media_constrained`
- `documentation_caveat`

Endpoint constraints must be visible in metadata, descriptions, or usage notes. Caveats include deprecation, upstream availability limits, owner-only access, region-specific behavior, media handling, high quota cost, and official-documentation inconsistencies.

## Response-Boundary Classification

Every representative Layer 2 tool contract must classify successful response behavior as:

- `near_raw`: preserves upstream endpoint shape with minimal framing
- `lightly_reshaped`: adds MCP clarity fields while staying traceable to one endpoint
- `out_of_scope`: uses composition, enrichment, ranking, heuristics, or cross-endpoint aggregation and therefore belongs outside Layer 2

Layer 2 responses may include light wrapper fields for:

- Upstream endpoint identity
- Safe metadata such as quota cost or requested parts
- Pagination clarity
- Mutation acknowledgment
- Upload result identity
- Safe content wrappers for downloads or media-related payloads

Layer 2 responses must preserve upstream-visible items, paging tokens, requested parts, resource fields, mutation acknowledgments, upload result identity, or downloaded content metadata when those concepts exist upstream.

Layer 2 responses must not present higher-level composition, ranking, enrichment, or heuristic interpretation as raw endpoint behavior.

## Representative Example Coverage

YT-202 validation must include at least 10 representative resource-method examples covering:

- Simple read
- Paginated read
- CamelCase method names
- OAuth-only operation
- Mixed-auth operation
- Mutation
- Media or upload operation
- High-quota operation
- Availability-constrained or deprecated endpoint
- Non-list response shape such as lookup, download, upload result, or mutation acknowledgment

Representative examples prove standards only. They must not imply endpoint execution exists before the matching YT-203 through YT-255 endpoint slice implements it.

## Validation Expectations

Reviewers must be able to verify that:

- Required metadata fields are present
- Public name matches the resource-method pair
- Quota cost appears in metadata, description, and usage notes
- High-cost endpoints warn before invocation
- Auth mode and availability state are explicit
- Caveats are visible and safe
- Response boundaries stay near-raw or lightly reshaped
- Out-of-scope Layer 3-style behavior is rejected
- New or changed Python functions include reStructuredText docstrings

Focused validation should include:

```bash
python3 -m pytest tests/unit/test_layer2_shared_scaffolding.py tests/contract/test_layer2_shared_contract.py tests/contract/test_layer2_tool_catalog_contract.py tests/integration/test_layer2_tool_registration.py
```

Final validation after implementation code changes must include:

```bash
python3 -m pytest
python3 -m ruff check .
```

## Security and Safety Rules

Public metadata, examples, descriptions, usage notes, errors, logs, and tests must not expose:

- API keys
- OAuth tokens
- Secret values
- Stack traces
- Signed URLs
- Unsafe raw media payloads
- Sensitive channel-owner or delegated-owner credential details

Safe public details may include public tool name, upstream resource and method, quota cost, auth mode, availability state, safe parameter names, caveat categories, and remediation hints.

## Implementation Alignment

The planned implementation should extend existing shared Layer 2 modules rather than introduce a new architecture:

- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py` for metadata records, auth declarations, availability declarations, and naming validation
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py` for response-boundary classification and safe convention metadata
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py` for representative non-executing metadata examples
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer2_tool_catalog_contract.py` and related Layer 2 tests for standards validation

Implemented alignment:

- Public metadata is returned through `Layer2ToolContract.to_tool_metadata()`.
- Unsafe public metadata keys are rejected before discovery-style exposure.
- Representative descriptors include metadata while preserving non-executing handler behavior.
- Naming validation rejects redundant provider prefixes and snake_case rewrites of official method names.
- Response-boundary metadata is serialized through shared `ResponseBoundary` helpers and included in representative contract metadata.
