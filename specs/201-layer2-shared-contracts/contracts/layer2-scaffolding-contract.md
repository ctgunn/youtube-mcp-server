# Contract: YT-201 Layer 2 Scaffolding and Resource-Family Layout

## Purpose

Define the internal scaffolding contract for adding Layer 2 endpoint-backed public MCP tools by YouTube resource family. Later endpoint slices must use this contract to place tool definitions, input contracts, handlers, response expectations, tests, examples, and caveat notes consistently.

This contract is internal to `/Users/ctgunn/Projects/youtube-mcp-server`. It supports public MCP tool consistency but does not itself add a concrete public endpoint tool.

## Contract Scope

- Shared Layer 2 helper boundary
- Resource-family ownership rules
- Expected locations for endpoint-specific public tool artifacts
- Test placement and Red-Green-Refactor evidence expectations
- Documentation and caveat placement
- Layer 1 dependency boundary
- Docstring and full-suite verification expectations

This contract does not define a new transport, a new persistence layer, or a new YouTube endpoint wrapper.

## Shared Layer 2 Boundary

Shared Layer 2 scaffolding may own:

- Public tool naming helpers
- Metadata records or validation helpers
- Auth mode and quota declaration helpers
- Common input mapping conventions
- Common response convention helpers
- Safe error category helpers
- Representative examples and fixtures
- Registration or discovery helpers that apply equally across endpoint families

Shared scaffolding must not own:

- Endpoint-specific request behavior
- Endpoint-specific upstream execution
- Endpoint-specific media handling
- Layer 3 composition, enrichment, ranking, or heuristics
- Duplicated Layer 1 request execution, auth, retry, observability, or error-normalization logic

## Resource-Family Ownership

Endpoint-specific Layer 2 tools must be organized by YouTube resource family. Family examples include:

- `activities`
- `captions`
- `channel_banners`
- `channels`
- `channel_sections`
- `comments`
- `comment_threads`
- `guide_categories`
- `localization`
- `members`
- `memberships_levels`
- `playlist_images`
- `playlist_items`
- `playlists`
- `search`
- `subscriptions`
- `thumbnails`
- `video_abuse_report_reasons`
- `video_categories`
- `videos`
- `watermarks`

Each family may own endpoint-specific definitions, schemas, handlers, examples, and tests for its public Layer 2 tools. Shared rules must remain centralized.

## Placement Expectations

Future endpoint slices must identify placements for:

- Tool definitions
- Input contract or schema builders
- Handler responsibilities
- Response expectation fixtures
- Auth, quota, caveat, and deprecation notes
- Unit tests
- Contract tests
- Integration or registry/discovery tests
- Quickstart or example updates when needed

The planned test locations for YT-201 shared scaffolding are:

- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer2_shared_scaffolding.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer2_shared_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer2_tool_catalog_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer2_tool_registration.py`

Later endpoint slices may add family-specific files while preserving these shared tests.

## Layer 1 Dependency Boundary

Layer 2 tools must depend on existing Layer 1 integration capabilities for request shaping, credential attachment, upstream execution, response normalization, and upstream error normalization.

Layer 2 shared scaffolding must not duplicate Layer 1:

- Auth context handling
- Request execution
- Retry policy
- Observability hooks
- Upstream request construction
- Upstream response parsing
- Upstream error normalization

Layer 2 may add public MCP-facing descriptions, schemas, result wrappers, and safe error categorization at the tool boundary.

## Documentation and Caveat Rules

Endpoint-specific caveats must be recorded where future authors and reviewers can find them without reading unrelated resource families.

Caveats include:

- Deprecated endpoints
- Availability-constrained endpoints
- Mixed or conditional auth
- High quota cost
- Media or upload-specific behavior
- Official documentation inconsistencies
- Delegated content-owner behavior

Shared caveat categories belong in Layer 2 shared scaffolding; endpoint-specific facts belong with the resource family.

## Test and Verification Contract

Implementation planning and later tasking must follow Red-Green-Refactor:

- **Red**: Add failing or characterization tests before implementation helpers or endpoint tools are added.
- **Green**: Add only the minimum shared code or endpoint-specific code required to satisfy the failing tests.
- **Refactor**: Remove duplication, keep shared behavior centralized, preserve reStructuredText docstrings, and rerun focused tests before full-suite validation.

Final validation for any implementation that changes code must include:

```bash
python3 -m pytest
python3 -m ruff check .
```

Focused YT-201 validation should include:

```bash
python3 -m pytest tests/unit/test_layer2_shared_scaffolding.py tests/contract/test_layer2_shared_contract.py tests/integration/test_layer2_tool_registration.py
```

## Docstring Contract

Every new or changed Python function must include a reStructuredText docstring that covers:

- Purpose
- Inputs
- Outputs
- Raised errors when relevant
- Side effects when relevant

This applies to naming helpers, metadata validators, schema builders, registration helpers, error mapping helpers, response wrapper helpers, and endpoint-family exports.

## Invariants

- YT-201 must remain shared scaffolding only
- Later endpoint slices must not redefine shared naming, auth, quota, response, or error rules
- Resource-family organization must prevent a monolithic Layer 2 endpoint-tool file
- Shared scaffolding must stay reusable across all YT-203 through YT-255 endpoint slices
- Secrets and stack traces must never appear in public tool errors, examples, logs, or tests

## Implementation Alignment

The resource-family scaffold lives in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py`. It records the required Layer 2 family names, family-specific placement metadata, shared/helper boundary rules, and a representative descriptor factory used by registration tests without adding endpoint execution.
