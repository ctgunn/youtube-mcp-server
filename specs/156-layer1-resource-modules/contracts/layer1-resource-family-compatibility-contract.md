# Contract: YT-156 Layer 1 Resource-Family Compatibility

## Purpose

Define the internal Layer 1 compatibility contract for reorganizing completed YouTube Data API integration capabilities into resource-family modules while preserving established import paths and endpoint behavior.

This contract is internal to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`. It does not introduce a public MCP tool, hosted route, or new YouTube endpoint capability.

## Contract Scope

- Resource-family organization for completed Layer 1 endpoint capabilities from YT-103 through YT-155
- Compatibility imports for existing downstream code and tests
- Maintainer-visible wrapper metadata, request-shape validators, and builder access
- Behavior preservation for endpoint contracts already covered by Layer 1 tests

This contract does not define new public MCP schemas, new hosted transport behavior, new endpoint semantics, or downstream migration away from existing imports.

## Required Resource Families

The refactor must provide resource-family organization for:

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

Each family must expose the endpoint capabilities that belong to it without changing the capability contract.

## Compatibility Import Expectations

The following import paths must remain compatible:

- `mcp_server.integrations`
- `mcp_server.integrations.wrappers`
- `mcp_server.integrations.youtube`

Compatibility means:

- Existing builder function names continue to resolve
- Existing wrapper classes used by tests or downstream code continue to resolve
- Existing package-level exports continue to resolve
- Existing YouTube transport and request-building helpers continue to resolve
- Imported capabilities expose the same metadata, validation behavior, execution behavior, response shape, and normalized failure behavior as before the refactor

Resource-family modules may own the implementation, but compatibility facades must preserve existing access.
In this implementation slice, compatibility facades remain intentionally available while resource-family modules provide the family-oriented access surface used by future Layer 2 and Layer 3 work.

## Endpoint Behavior Invariants

For every completed Layer 1 endpoint capability from YT-103 through YT-155, the refactor must preserve:

- `resource_name`
- `operation_name`
- `operation_key`
- `http_method`
- `path_shape`
- `quota_cost`
- `auth_mode`
- required fields
- optional fields
- exclusive selector behavior
- request validation rules
- credential attachment behavior
- upstream request construction behavior
- successful response payload shape
- normalized upstream failure categories and messages
- maintainer-facing caveat and lifecycle notes

No endpoint may gain or lose promised request modes as part of this feature.

## Shared Foundation Invariants

Resource-family modules must use existing shared foundations for:

- auth context and credential handling
- request execution
- retry policy
- observability hooks
- endpoint contracts
- normalized upstream errors
- generic YouTube request construction

Shared foundations must not be copied into each family or forked into family-specific variants unless a later feature deliberately changes the contract.

## Review Validation Expectations

Validation must prove that maintainers can:

- find a representative family without broad-file traversal
- import representative capabilities through both old and new access paths
- verify identical review surfaces for old and new builder access
- run existing resource-family contract tests successfully
- run compatibility checks for package-level and `wrappers.py` imports
- confirm no public MCP behavior was introduced or changed
- confirm new or changed Python functions include reStructuredText docstrings

## Invariants

- YT-156 is a behavior-preserving refactor
- Compatibility shims may remain intentionally
- Resource-family organization must not create circular imports through `mcp_server.integrations.__init__`
- Secrets, OAuth tokens, API keys, channel-owner identity, delegated-owner credentials, and raw media payloads must never appear in docs, logs, normalized results, or tests
