# Research: YT-226 Layer 2 Tool `members_list`

## Decision: Use current official quota cost `2` for the public Layer 2 contract

**Rationale**: The YT-226 seed and existing YT-126 local metadata describe quota cost `1`, but the current Google `members.list` reference, last updated 2026-06-01 UTC, lists quota cost `2` per call. Because the public Layer 2 tool must document the official quota cost before invocation, YT-226 should align metadata, descriptions, examples, tests, and any touched Layer 1 review surface to `2`.

**Alternatives considered**:
- Keep the seed/local value `1`. Rejected because it would expose stale quota information in a public MCP contract.
- Mark the quota as unknown. Rejected because the official reference resolves the value.
- Hide quota from examples. Rejected because YT-201/YT-202 and the feature spec require visible quota disclosure.

## Decision: Support the repo-local request boundary with required `part`, required `mode`, optional `pageToken`, and optional `maxResults`

**Rationale**: The existing YT-126 Layer 1 wrapper exposes `part` plus `mode` as required fields and `pageToken` plus `maxResults` as optional paging fields. The official endpoint also includes `hasAccessToLevel` and `filterByMemberChannelId`, but those are not available in the local Layer 1 contract. The smallest safe Layer 2 scope is therefore to expose the fields supported by YT-126 and reject unsupported filters clearly.

**Alternatives considered**:
- Add `hasAccessToLevel` and `filterByMemberChannelId` in this slice. Rejected because it would broaden YT-226 beyond the current Layer 1 dependency and require a separate YT-126 contract revision.
- Treat `mode` as optional because the official endpoint has a default. Rejected because YT-126 requires mode and YT-226 needs deterministic membership-view context in results.
- Exclude paging fields. Rejected because both local inventory and Layer 1 metadata identify `pageToken` and `maxResults` as supported list-style inputs.

## Decision: Validate mode values as `all_current` and `updates`

**Rationale**: Current official documentation identifies `all_current` and `updates` as supported membership retrieval modes. Local tests already use `updates`, and using the explicit official set lets the Layer 2 handler reject unsupported mode values before they become ambiguous upstream failures.

**Alternatives considered**:
- Allow any non-empty mode string. Rejected because invalid modes would bypass the caller-facing validation boundary.
- Support only `updates`, matching current local examples. Rejected because official docs define `all_current` and `updates`, and `all_current` is the current listing mode callers naturally expect.

## Decision: Enforce Layer 2 validation in the handler, not only in discovery schema

**Rationale**: Existing dispatcher behavior does not make JSON schema the only enforcement boundary. The `members_list` handler must explicitly validate part values, mode values, paging bounds, unsupported fields, OAuth-required access mode, and out-of-scope filters/actions so callers receive deterministic safe failures.

**Alternatives considered**:
- Rely on schema metadata alone. Rejected because local patterns validate in handlers and because schema discovery does not guarantee runtime enforcement.
- Let the Layer 1 wrapper reject all invalid input. Rejected because Layer 2 owns caller-facing MCP error categories, examples, and safe diagnostics.

## Decision: Model `members_list` as OAuth-required, owner-only, channel-membership constrained, and active

**Rationale**: The current official docs and YT-126 local contract agree that `members.list` requires OAuth-backed channel-owner authorization and can only be used for eligible channel-memberships-enabled creator channels. The endpoint is present in current docs, so the public availability state can remain active while caveats explain owner-only and channel-membership constraints.

**Alternatives considered**:
- Use API-key or mixed auth. Rejected because no local or official source describes a public API-key path for member listing.
- Mark the endpoint unavailable. Rejected because the official docs describe an active endpoint with specific eligibility constraints.
- Hide owner-only details from metadata. Rejected because callers need to understand eligibility before spending quota.

## Decision: Preserve near-raw list results with membership-mode, pagination, and access context

**Rationale**: Layer 2 tools should stay close to upstream behavior while adding MCP clarity. A successful `members_list` result should preserve returned `items`, `kind`, `etag`, `nextPageToken`, and `pageInfo` when present, plus wrapper fields such as endpoint, quota cost, requested parts, selected mode, auth mode, and access caveats. Empty `items` remains a successful result.

**Alternatives considered**:
- Return only a summarized member count. Rejected because that would turn the tool into higher-level analytics rather than low-level endpoint access.
- Treat empty member lists as errors. Rejected because an eligible request may validly return no member records.
- Add membership-level enrichment. Rejected because `membershipsLevels_list` and higher-level tools own that behavior.

## Decision: Add a dedicated Layer 2 members module and standard contract/test artifacts

**Rationale**: The `members` resource family already exists in shared scaffolding, but no Layer 2 module is present. Adding `/src/mcp_server/tools/youtube_common/members.py` mirrors existing resource-family modules, keeps owner-scoped member listing separate from membership-level lookup, and fits the registration/export/test conventions used by `comments_list`, `i18nRegions_list`, and `guideCategories_list`.

**Alternatives considered**:
- Place `members_list` in `comments.py` or `channels.py`. Rejected because member listing is a separate YouTube resource family.
- Combine members and memberships levels in one module now. Rejected because YT-226 is scoped to one public tool and YT-227 owns membership-level listing.
- Implement only docs with no dispatcher registration. Rejected because Layer 2 public tools must be discoverable and callable through the MCP registry.
