# Layer 1 Catalog, Membership, and Playlist Live-Call Contract

## Purpose

Define configured default execution for the existing catalog, membership, and playlist resource families. This contract retrofits their public descriptors to the YT-157 shared live runtime without changing exposed MCP tool contracts or underlying Layer 1 wrapper contracts.

## In-Scope Operations

| Resource family | Operations | Access | Request form |
| --- | --- | --- | --- |
| Guide categories | `guideCategories.list` | API key | GET query |
| Localization | `i18nLanguages.list`, `i18nRegions.list` | API key | GET query |
| Members | `members.list` | OAuth | GET query |
| Membership levels | `membershipsLevels.list` | OAuth | GET query |
| Playlist images | `playlistImages.list`, `playlistImages.insert`, `playlistImages.update`, `playlistImages.delete` | OAuth | GET/DELETE query; insert/update multipart metadata and media |
| Playlist items | `playlistItems.list`, `playlistItems.insert`, `playlistItems.update`, `playlistItems.delete` | API key list; OAuth mutations | GET/DELETE query; insert/update JSON |
| Playlists | `playlists.list`, `playlists.insert`, `playlists.update`, `playlists.delete` | Selector-driven list; OAuth mutations | GET/DELETE query; insert/update JSON |

## Configured Default Behavior

1. Normal application composition loads existing YT-157 live settings, constructs one configured runtime, and passes it through the HTTP transport to the dispatcher.
2. The dispatcher passes the configured runtime executor and applicable credential availability to descriptors for every operation in scope.
3. A descriptor validates public arguments, selects authorization by its existing selector or write rules, and calls its existing Layer 1 wrapper with the shared executor.
4. The wrapper validates its existing request shape and delegates a `RequestExecution` to the existing concrete transport.
5. The concrete transport preserves metadata-defined target, method, parameters, body, and upload form; attaches the selected credential; and returns the existing normalized success or normalized failure.
6. A configured default invocation must never create or select a family-local representative executor, placeholder credential, static result, or separate direct upstream path.

## Authorization and Request Rules

| Rule | Required behavior |
| --- | --- |
| API-key operation | Use a nonblank configured API key only where existing metadata and selector rules permit it. A missing key must produce the established safe caller-facing failure at invocation time. |
| OAuth-required operation | Use a nonblank configured OAuth credential; do not fall back to an API key. |
| Conditional playlist list | Use an API key for `channelId` or `id`; use OAuth for `mine`; do not infer another mode from credential availability. |
| Query-only operation | Preserve the metadata-defined query target and parameters. |
| JSON-body operation | Preserve existing body validation and submit the validated body through the shared transport. |
| Playlist-image media operation | Preserve existing metadata and media validation and submit the declared multipart form through the shared transport. |

## Compatibility Guarantees

The following remain unchanged for all in-scope operations:

- Public MCP tool name, description, input schema, metadata, quota and authorization disclosure, lifecycle information, and caller examples.
- Layer 1 endpoint metadata, method/path declaration, selector and body validation, quota documentation, and authorization rule.
- Family-specific result mapping, response-normalizer selection, safe public error category/message, and no-match behavior.
- Shared retry selection and safe integration observability behavior.
- Explicit wrapper, executor, opener, and credential injection for isolated tests or deliberate local development.

## Failure and Security Rules

| Condition | Required outcome |
| --- | --- |
| Missing or blank selected credential | Existing safe normalized configuration/authentication/authorization failure; no request and no representative success. |
| Invalid input or incompatible selector | Existing validation failure before live execution. |
| Upstream authorization rejection, malformed response, timeout, quota, or service failure | Existing normalized family-specific public failure after shared retry selection where applicable. |
| Explicit test/local executor or opener | Allowed only when supplied deliberately; it must not be selected by configured default composition. |
| Diagnostic, log, result, or test evidence | Must omit API keys, OAuth tokens, bearer headers, credential-bearing URLs, raw body/media, stack traces, and unfiltered upstream failures. |

## Verification Obligations

- Parameterized request-level tests cover all 17 operations: path, method, parameters, selected credential mode/location, body or upload form where applicable, normalized success, and normalized upstream failure.
- Seven configured public-tool flow tests prove one flow per resource family reaches the shared live request path through transport and dispatcher composition.
- Existing unit and contract tests prove unchanged wrapper validation, descriptor schema/metadata, result shape, and safe error behavior.
- Final validation runs `python3 -m pytest` followed by `python3 -m ruff check .`.
