# Research: YT-302 Video Details

## Decision: Extend the Existing Composed Videos Family

Implement the concrete public tool in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`, using the existing public name `videos_getVideo` and video-family conventions.

**Rationale**: YT-301 assigns this exact tool name to the `videos` family. The existing module is intentionally the family placement seam for this work, so using it retains catalog validation and keeps related public tools cohesive.

**Alternatives considered**:

- Extend `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`: rejected because it contains endpoint-near-raw tools rather than normalized public workflows.
- Create a new family or parallel module: rejected because the existing composed videos family is the correct placement and retains the established naming convention.

## Decision: Use `videos.list` as the Sole Lookup Dependency

Adapt the existing `videos_list` capability and its `videos.list` integration wrapper for one identifier, then map its first returned item into the public normalized result. Do not expose the lower-level collection envelope.

**Rationale**: The PRD and shared contract identify `videos.list` as the video-detail dependency. It already performs direct lookup with public-compatible access, one-unit quota behavior, request execution, and sanitized upstream error handling.

**Alternatives considered**:

- Expose `videos_list` directly: rejected because it requires callers to provide source parts, permits multi-ID retrieval, returns a collection envelope, and treats an empty list as a valid endpoint result.
- Add a new integration or use multiple source resources: rejected because no additional source is required for a single normalized detail result.

## Decision: Always Retrieve Core Parts and Union Requested Parts

Require one nonblank `videoId`. Accept optional `parts` only as a unique array drawn from `snippet`, `contentDetails`, `statistics`, `status`, and `topicDetails`. Always include `snippet` and `contentDetails` in the lower-level request because the default response spans both; union valid requested values without duplicates. Treat `parts: []` the same as omitting `parts`.

**Rationale**: Default fields such as title and duration originate from different source groups. This preserves a complete, stable core response while allowing additive detail groups.

**Alternatives considered**:

- Require callers to choose core groups: rejected because the feature promises a default normalized result.
- Silently ignore unknown or duplicate values: rejected because deterministic validation is required.

## Decision: Normalize One Item and Preserve Missingness

Map the returned item into core `videoId`, `title`, `description`, `publishedAt`, `channelId`, `channelTitle`, `duration`, `categoryId`, `tags`, and `thumbnails`. Add optional groups only when requested. Preserve available source values; omit or explicitly identify unavailable fields rather than deriving substitutes. Classify fields as raw-source or normalized; this tool exposes no heuristic fields.

**Rationale**: Callers need a stable result without losing the distinction between reshaped source values and absent data. The shared public-tool contract requires visible provenance and prohibits silent inference.

**Alternatives considered**:

- Return the source item unchanged: rejected because it defeats the normalized contract.
- Fill missing details with guesses or defaults: rejected because it would misrepresent unavailable data.

## Decision: Translate Empty Lookup to a Safe Unavailable Outcome

Convert an empty lower-level item list and source not-found or removed outcomes to `unavailable_resource`. Do not reveal whether the video is private, deleted, restricted, or nonexistent. Map invalid input to `invalid_parameters`, access failures to `authorization_sensitive_data`, quota failures to `quota_exhaustion`, and other source failures to `upstream_failure`.

**Rationale**: A collection lookup can legitimately return no items, but this tool promises either one video or a safe unavailable outcome. Shared error categories let callers respond consistently without sensitive details.

**Alternatives considered**:

- Return an empty collection: rejected because callers asked for one video.
- Reveal the precise availability reason: rejected because it can disclose non-public information.

## Decision: Use the Existing Descriptor and Dispatcher Pattern

Create a concrete descriptor with public name, input schema, handler, and safe discovery metadata; export it through the composed package and register it in the default dispatcher. Do not use the existing representative descriptor because it intentionally has an inert handler.

**Rationale**: The dispatcher is the existing production discovery and invocation seam. This approach satisfies the contract-first requirement and avoids transport or registry redesign.

**Alternatives considered**:

- Keep the tool as a representative contract only: rejected because YT-302 requires executable behavior.
- Add a separate registry or transport route: rejected because the existing dispatcher already provides the required public interface.

## Decision: Use Test-First, Multi-Level Verification

Begin with failing unit tests for validation, lower-request construction, normalization, sparse fields, and errors; contract tests for discovery metadata and mappings; and integration tests for default registration and invocation. End with `python3 -m pytest` and `python3 -m ruff check .`. Add reStructuredText docstrings to every changed Python function.

**Rationale**: This follows the constitution's mandatory Red-Green-Refactor, integration coverage, full-suite, and documentation requirements.

**Alternatives considered**:

- Documentation-only or targeted-only checks: rejected because they do not prove executable public behavior or meet the full-suite requirement.
- Relax docstrings for small helpers or test doubles: rejected by the constitution.
