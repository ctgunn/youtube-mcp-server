# Research: YT-227 Layer 2 Tool `membershipsLevels_list`

## Decision: Expose one public Layer 2 tool named `membershipsLevels_list`

**Rationale**: The YT-227 seed explicitly requires Layer 2 to expose `membershipsLevels_list` as the low-level public tool for the upstream `membershipsLevels.list` endpoint. The PRD requires one endpoint-backed Layer 2 tool per supported YouTube Data API operation, and the existing shared contracts use endpoint-style public names. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/PRD.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/227-memberships-levels-list/spec.md`

**Alternatives considered**:

- Combine this with `members_list`. Rejected because YT-226 owns member listing and YT-227 owns membership-level listing.
- Rename to `membership_levels_list`. Rejected because the seed and PRD name the public Layer 2 tool `membershipsLevels_list`.
- Defer public exposure to a Layer 3 workflow. Rejected because YT-227 is specifically a Layer 2 endpoint-backed tool slice.

## Decision: Reuse the existing YT-127 Layer 1 `membershipsLevels.list` wrapper

**Rationale**: The Layer 1 wrapper already exists under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/memberships_levels.py`, exposes operation key `membershipsLevels.list`, requires OAuth access, requires `part`, records quota cost `1`, rejects undocumented modifiers, and preserves empty result sets as successful outcomes. Reusing it preserves the Layer 1/Layer 2 boundary and avoids redefining upstream request execution in the public tool. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/memberships_levels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/127-memberships-levels-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/127-memberships-levels-list/research.md`

**Alternatives considered**:

- Add a separate Layer 2 transport path. Rejected because tools should depend on integration interfaces and not duplicate request execution, auth, quota, or upstream error logic.
- Change the Layer 1 wrapper first. Rejected because current Layer 1 metadata already matches YT-227's quota, auth, and request-shape requirements.
- Mock membership-level results only in Layer 2. Rejected because the public tool must be endpoint-backed through the Layer 1 capability.

## Decision: Support only required `part=snippet` in the public input contract

**Rationale**: YT-127 models `membershipsLevels.list` as a deterministic required-`part` request and keeps optional filters, paging controls, and delegation inputs unsupported. Existing Layer 2 tools narrow their public input schema to supported repo-local endpoint behavior and reject additional properties. The smallest testable YT-227 schema is therefore one required string `part` with supported value `snippet` and `additionalProperties: false`. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/memberships_levels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/127-memberships-levels-list/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/members.py`

**Alternatives considered**:

- Accept arbitrary `part` values. Rejected because the feature spec requires supported part-selection validation and current implementation patterns use explicit supported values.
- Add `pageToken` and `maxResults`. Rejected because YT-127 identifies filters and paging inputs as unsupported for this endpoint slice.
- Pass through unknown fields for future compatibility. Rejected because deterministic public contracts and clear invalid-request feedback are required by YT-201/YT-202 conventions.

## Decision: Keep quota cost `1` visible in metadata, descriptions, usage notes, examples, and results

**Rationale**: The YT-227 seed, YT-127 wrapper, and YT-227 specification agree that `membershipsLevels.list` has official quota cost `1`. Existing Layer 2 tools make quota visible across discovery metadata, descriptions, examples, and near-raw results so client developers can understand cost before invocation and in returned context. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/memberships_levels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/members.py`

**Alternatives considered**:

- Put quota only in metadata. Rejected because the spec requires description and examples to visibly state quota cost.
- Recheck remote documentation during planning. Rejected because this workflow uses local feature requirements and no unresolved local discrepancy exists.
- Omit quota from successful results. Rejected because nearby Layer 2 endpoint-backed tools preserve quota context in their public result wrappers.

## Decision: Model access as OAuth-required, owner-scoped, and channel-membership constrained

**Rationale**: Both YT-127 and YT-227 require OAuth and owner/channel-membership access constraints to be visible. The public contract should reject missing OAuth locally as `authentication_failed` and map owner visibility or channel-membership eligibility failures to `authorization_failed` unless the normalized upstream category provides a more specific safe category. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/227-memberships-levels-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/memberships_levels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/members.py`

**Alternatives considered**:

- Allow API-key-only access. Rejected because repo-local contracts mark this endpoint OAuth-required.
- Hide owner constraints in implementation only. Rejected because callers must understand access limits before invoking the tool.
- Add delegated owner context in this slice. Rejected because delegation inputs are outside the current Layer 1 wrapper boundary and YT-227 scope.

## Decision: Preserve near-raw list results with selected part context and empty-success semantics

**Rationale**: The feature spec requires a near-raw endpoint-backed shape that preserves returned membership-level resources, selected part context, relevant owner-access context, and upstream fields. YT-127 also treats empty membership-level collections as valid success when request shape and access are valid. The result mapper should preserve returned `items`, `kind`, `etag`, and other upstream fields when present, without fabricating optional fields or adding enrichment. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/227-memberships-levels-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/127-memberships-levels-list/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/members.py`

**Alternatives considered**:

- Convert membership levels into summaries. Rejected because Layer 2 should stay close to the upstream endpoint.
- Treat empty `items` as an error. Rejected because a valid channel may have no returned membership-level records.
- Add member or subscriber enrichment. Rejected because this slice is not a cross-endpoint or Layer 3 workflow.

## Decision: Use shared Layer 2 safe error categories and sanitize diagnostics

**Rationale**: Existing Layer 2 tools map local validation and normalized upstream failures into shared safe categories such as `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `endpoint_unavailable`, and `upstream_failure`. YT-227 should reuse that shape and sanitize diagnostics so OAuth tokens, raw upstream bodies, stack traces, and unsafe request context are not exposed. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/members.py`

**Alternatives considered**:

- Raise raw upstream errors directly. Rejected because public MCP tools must provide safe, deterministic error messages.
- Introduce membership-level-specific error categories. Rejected because shared categories are sufficient and simpler for clients.
- Include raw request context in details. Rejected because the constitution requires avoiding secret and unsafe diagnostic exposure.

## Decision: Add a new `memberships_levels` Layer 2 module and register it in default discovery

**Rationale**: The shared family list already includes `memberships_levels`, Layer 1 resource modules use that family name, and the existing `members_list` pattern places endpoint-backed public behavior in one concrete resource-family module. Adding `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/memberships_levels.py`, exporting it from `youtube_common/__init__.py`, and registering its descriptor in `dispatcher.py` is the smallest consistent public-tool path. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/members.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`

**Alternatives considered**:

- Put the tool in `members.py`. Rejected because membership levels and channel members are separate resource families and endpoints.
- Put the tool only in dispatcher. Rejected because public contracts, validation, result mapping, and tests belong in a cohesive resource-family module.
- Create a broader memberships package. Rejected because one endpoint-backed tool does not justify a larger architecture.

## Decision: Validate with contract, unit, integration, registry, and full-suite checks

**Rationale**: The constitution requires Red-Green-Refactor, contract-first design, integration coverage, and a full repository test-suite run. YT-227 will add contract tests for metadata/examples, unit tests for validation/result/error mapping, integration tests for registry discovery and dispatcher execution, and final `pytest` plus `ruff check .`. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/.specify/memory/constitution.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/227-memberships-levels-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/226-members-list/plan.md`

**Alternatives considered**:

- Only add unit tests. Rejected because MCP-facing discovery and registry behavior require contract and integration coverage.
- Skip full-suite verification. Rejected by the constitution.
- Defer docstring checks to review. Rejected because new and changed Python functions must include reStructuredText docstrings as part of implementation.

## Clarification Closure

All planning-time clarifications for YT-227 are resolved in this research artifact. No unresolved clarification markers remain.
