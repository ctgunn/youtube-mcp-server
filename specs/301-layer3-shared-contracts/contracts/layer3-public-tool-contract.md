# Contract: YT-301 Layer 3 Public Tool Contract

## Purpose

Define the shared MCP-facing contract for higher-level YouTube public tools. Later Layer 3 slices from YT-302 onward must use this contract rather than redefining grouped naming, repeated parameters, response provenance, heuristic disclosures, ranking/filtering semantics, composition boundaries, auth/quota caveats, partial-result behavior, or safe errors.

This contract defines shared behavior only. It does not add a concrete Layer 3 public tool by itself.

## Contract Scope

- Grouped Layer 3 public tool naming
- Shared user-facing parameter conventions
- Response field provenance categories
- Heuristic and inferred-field disclosure rules
- Reusable ranking and filtering semantics
- Composition and fan-out disclosure rules
- Auth, quota, partial-result, and unavailable-data caveats
- Safe caller-facing error categories
- Representative examples used to validate shared rules

This contract does not define near-raw Layer 2 endpoint tools, hosted transport changes, persistence, OAuth flows, transcript provider fallback policy, or individual Layer 3 tool execution behavior.

## Public Tool Naming

Layer 3 public tool names must:

- Use one of the grouped public prefixes: `videos_*`, `channels_*`, `playlists_*`, or `transcripts_*`
- Omit a redundant `youtube_` provider prefix
- Use the initial Layer 3 catalog names from the PRD unless a later slice explicitly amends the public catalog
- Stay deterministic across discovery metadata, examples, tests, and documentation

Initial catalog names that YT-301 shared rules must validate:

| Family | Public Tool Names |
|--------|-------------------|
| `videos` | `videos_getVideo`, `videos_searchVideos`, `videos_getStatistics` |
| `transcripts` | `transcripts_getTranscript`, `transcripts_listLanguages`, `transcripts_getTimestampedCaptions`, `transcripts_searchTranscript` |
| `channels` | `channels_getChannel`, `channels_getChannels`, `channels_searchChannels`, `channels_findCreators`, `channels_listVideos`, `channels_listPlaylists`, `channels_getStatistics`, `channels_searchContent` |
| `playlists` | `playlists_getPlaylist`, `playlists_getPlaylistItems`, `playlists_searchItems`, `playlists_getVideoTranscripts` |

## Shared Parameter Rules

Layer 3 tools must use stable MCP-facing parameter names. Shared conventions must define requiredness, defaults, bounds, invalid-value behavior, and applicable families before a later tool slice accepts a repeated parameter.

Required shared parameter convention coverage:

| Parameter | Shared Meaning |
|-----------|----------------|
| `videoId` | One YouTube video identifier |
| `channelId` | One YouTube channel identifier |
| `channelIds` | Bounded list of YouTube channel identifiers |
| `playlistId` | One YouTube playlist identifier |
| `query` | Caller-facing search or match text |
| `language` | Transcript or caption language selection |
| `maxResults` | Bounded result count requested by the caller |
| `order` | Upstream or catalog-supported ordering request |
| `parts` | Optional result part selection when a tool supports it |
| ISO 8601 date filters | Inclusive or exclusive date-window filters as defined per convention |
| pagination or continuation fields | Caller-visible continuation behavior where a tool supports it |

Bounded fan-out parameters such as transcript match limits, sample-video limits, playlist item limits, and one-result-per-channel behavior must also be documented through shared conventions before use.

## Response Provenance Rules

Every Layer 3 result contract must distinguish:

- `raw_upstream`: values copied from lower-layer or upstream YouTube data without semantic reinterpretation
- `normalized`: fields reshaped, renamed, grouped, or defaulted for stable MCP consumption
- `heuristic_inferred`: fields inferred from available data, ranking rules, filters, text extraction, contact parsing, creator classification, recency signals, or other approximate methods

Response field provenance must be visible in contract examples and review evidence. A field may not silently move from heuristic to normalized or raw without a documented contract update.

## Heuristic Disclosure Rules

Every heuristic or inferred field must disclose:

- Field or signal name
- Basis used to infer the value
- Known limitations or uncertainty
- Applicable tools or families
- Safe caller guidance

Required shared heuristic coverage includes creator classification, contact extraction, latest-upload signals, subscriber-band fit, ranking scores, transcript match snippets, and playlist fan-out summary signals wherever later tools expose them.

Heuristics must not expose credentials, private owner context, raw email harvesting internals beyond safe public result fields, stack traces, signed URLs, or raw media payloads.

## Ranking and Filtering Rules

Reusable ranking and filtering rules must define semantics once and list the families or workflow shapes where they apply.

Required shared rule coverage includes:

- `creatorOnly`
- subscriber minimum and maximum filters
- latest-upload date filters
- `uniqueChannels`
- sample-video limits
- transcript match limits
- `sortBy`
- playlist item and transcript fan-out bounds

Unsupported ranking or filtering combinations must produce deterministic safe validation errors. Later tool contracts must not imply that a shared rule applies globally when it is family-specific.

## Composition Boundary Rules

Every Layer 3 contract must disclose whether the tool performs:

- direct retrieval
- normalized single-resource shaping
- multi-resource composition
- enrichment
- server-side filtering
- ranking
- fan-out

Composite, enriched, ranked, filtered, or fan-out tools must document auth sensitivity, quota impact, boundedness, partial-result behavior, and unavailable-data handling before implementation.

Layer 3 contracts may reference Layer 2 and Layer 1 metadata for lower-layer identity, quota, auth, availability, and response-boundary facts, but they must not copy near-raw Layer 2 behavior as if it were the Layer 3 public contract.

## Error and Partial Result Rules

Layer 3 tools must use safe caller-facing error categories compatible with MCP expectations and existing YouTube contracts.

Shared error and result-status categories must cover:

- invalid parameters
- unavailable or hidden resource data
- authorization-sensitive data
- quota exhaustion
- upstream failure
- partial enrichment failure
- transcript unavailable
- fan-out limit reached
- unsupported filter or sort
- no matching results

Safe error details may include public tool name, family, safe parameter names, dependency category, retry hints, partial-result status, and user-remediation hints.

Safe error details must not include API keys, OAuth tokens, secret values, stack traces, raw signed URLs, raw media payloads, or sensitive channel-owner/delegation details.

## Representative Shape Coverage

YT-301 must validate this contract against representative examples for:

- simple video retrieval
- video or channel search
- ranked or filterable creator discovery
- transcript retrieval
- transcript text search
- channel batch lookup
- playlist item listing
- playlist item search
- playlist transcript fan-out

Representative examples prove shared coverage only; they do not constitute public Layer 3 tool implementation.

## Review Validation Expectations

Reviewers must be able to verify that:

- All 19 initial public names are valid grouped Layer 3 names
- Repeated parameters have shared conventions before use
- Representative response fields are categorized as raw, normalized, or heuristic/inferred
- Heuristic fields include basis and limitation notes
- Ranking and filtering rules define semantics and applicability
- Composition boundaries disclose auth, quota, boundedness, and partial-result behavior
- Safe error categories exclude secrets and stack traces
- The slice does not introduce concrete public Layer 3 tool behavior beyond representative examples
- Any new or changed Python functions include reStructuredText docstrings

## Implementation Alignment

The planned shared implementation uses `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/contracts.py` for public contract records and naming, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/conventions.py` for parameter, response provenance, heuristic, ranking, filtering, and composition conventions, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/examples.py` for representative non-executing examples, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/families.py` for family scaffolding metadata.
