# Contract: YT-301 Layer 3 Scaffolding Contract

## Purpose

Define the maintainer-facing organization rules for Layer 3 higher-level YouTube tools. Later YT-302+ slices must use this scaffolding to place public contract definitions, shared conventions, family-specific helpers, representative examples, tests, and caveat notes consistently.

This contract defines layout and dependency boundaries only. It does not add concrete public Layer 3 tool behavior by itself.

## Package Boundary

Layer 3 shared scaffolding belongs under:

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/
```

The package may depend on existing lower-layer contracts for metadata and dependency facts:

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/
```

Layer 3 scaffolding must not move or duplicate Layer 1 execution logic, Layer 2 near-raw endpoint behavior, hosted transport behavior, or persistence concerns.

## Shared Module Responsibilities

Planned shared modules:

| Module | Responsibility |
|--------|----------------|
| `contracts.py` | Layer 3 public contract records, grouped naming validation, safe public metadata validation |
| `conventions.py` | Shared parameter conventions, response provenance categories, heuristic disclosures, ranking/filtering rules, composition boundaries |
| `examples.py` | Representative non-executing Layer 3 examples proving shared coverage across families and workflow shapes |
| `families.py` | Family registry for videos, channels, playlists, transcripts, planned tool names, and placement metadata |
| `videos.py` | Video-family scaffolding and later video-family tool definitions/helpers |
| `channels.py` | Channel-family scaffolding and later channel-family tool definitions/helpers |
| `playlists.py` | Playlist-family scaffolding and later playlist-family tool definitions/helpers |
| `transcripts.py` | Transcript-family scaffolding and later transcript-family tool definitions/helpers |

Shared cross-cutting rules belong in `contracts.py`, `conventions.py`, `examples.py`, and `families.py`. Family modules own only family-specific declarations and reusable helpers.

## Family Placement Rules

Every Layer 3 family must define:

- Family name
- Public prefix
- Planned public tool names
- Contract definition area
- Input schema area
- Composed handler area for later concrete tool slices
- Reusable family helper area
- Representative example area
- Unit, contract, and integration-style test locations
- Caveat and exception note location

Later tool slices must add concrete behavior within the owning family area rather than a single monolithic shared module.

## Planned Tool Ownership

| Family | Public Prefix | Planned Tools |
|--------|---------------|---------------|
| videos | `videos_*` | `videos_getVideo`, `videos_searchVideos`, `videos_getStatistics` |
| channels | `channels_*` | `channels_getChannel`, `channels_getChannels`, `channels_searchChannels`, `channels_findCreators`, `channels_listVideos`, `channels_listPlaylists`, `channels_getStatistics`, `channels_searchContent` |
| playlists | `playlists_*` | `playlists_getPlaylist`, `playlists_getPlaylistItems`, `playlists_searchItems`, `playlists_getVideoTranscripts` |
| transcripts | `transcripts_*` | `transcripts_getTranscript`, `transcripts_listLanguages`, `transcripts_getTimestampedCaptions`, `transcripts_searchTranscript` |

## Test Placement Rules

Layer 3 shared tests should use the existing repository test tiers:

```text
/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer3_shared_scaffolding.py
/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer3_shared_contract.py
/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer3_tool_catalog_contract.py
/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer3_tool_registration.py
```

Required test responsibilities:

- Unit tests validate naming helpers, parameter conventions, response provenance, heuristic disclosures, ranking/filtering rules, composition boundaries, safe metadata, and family maps.
- Contract tests validate public Layer 3 contract completeness and all 19 planned catalog names.
- Integration-style tests validate that shared metadata can flow toward MCP discovery and registration expectations when later concrete tools are added.
- Final validation after implementation must include `python3 -m pytest` and `python3 -m ruff check .`.

## Red-Green-Refactor Expectations

Implementation tasks generated from this plan must start with failing tests.

Red examples:

- Missing grouped family prefix is rejected.
- Repeated parameter has no default, bound, or invalid-value behavior.
- Response field lacks raw, normalized, or heuristic category.
- Heuristic field lacks basis or limitation notes.
- Composite tool lacks auth, quota, boundedness, or partial-result caveats.
- Planned tool cannot be mapped to a family module.

Green examples:

- Add the smallest shared contract or convention record needed for the failing check to pass.
- Add representative examples only, not concrete public tool execution.
- Reuse Layer 2 metadata for upstream dependency facts instead of duplicating endpoint rules.

Refactor examples:

- Consolidate duplicated convention wording.
- Keep family-specific helpers out of cross-family shared modules.
- Preserve or add reStructuredText docstrings for every new or changed Python function.
- Run targeted tests, then full `python3 -m pytest` and `python3 -m ruff check .`.

## Dependency Rules

Allowed dependencies:

- Layer 2 YouTube shared contracts for upstream identity, auth, quota, availability, and response-boundary facts
- Layer 1 resource metadata for official operation inventory and lower-layer dependency references
- Existing MCP registry and dispatcher contracts for discovery and invocation compatibility
- Python standard library dataclasses, enums, and JSON-compatible dictionaries

Disallowed dependencies for this slice:

- New external packages
- New persistence or cache layer
- Hosted transport changes
- Concrete Layer 3 upstream execution
- New authentication flow behavior
- Tool-specific behavior for YT-302+ slices

## Caveat and Exception Recording

Family-specific caveats discovered later must be recorded in the owning family module and public tool contract. Shared caveats that affect multiple families must be promoted to `conventions.py` and reflected in this feature's shared contract artifacts when relevant.

Examples of caveats that must be visible to callers:

- Hidden or unavailable counts
- Authorization-sensitive caption access
- Region-limited or deleted resources
- Partial enrichment failures
- High-quota fan-out
- Heuristic uncertainty
- Unsupported sort or filter combinations

## Security and Observability Boundaries

Layer 3 public metadata, examples, errors, logs, and review evidence must not expose:

- API keys
- OAuth tokens
- Secret values
- Stack traces
- Signed URLs
- Raw media payloads
- Sensitive owner or delegation context
- Misleading heuristic certainty

Layer 3 tooling must preserve existing request context and logging expectations when later concrete handlers are implemented, including tool name, request identifiers, status, latency, and safe error category.

## Review Validation Expectations

Reviewers must be able to verify that:

- Every planned Layer 3 tool maps to one family and one grouped name.
- Shared conventions are centralized before family modules use them.
- Family modules remain cohesive and do not accumulate unrelated tool behavior.
- Representative examples cover all four families and the major workflow shapes.
- Later slices can reference YT-301 without redefining cross-cutting Layer 3 rules.
- Any new or changed Python functions include reStructuredText docstrings.
<!-- Filename normalized to avoid implementation-layer numbering. -->
