# Layer 1 Channel and Community Live-Call Contract

## Purpose

Define the configured default execution contract for the existing channel and community resource families. This contract retrofits their public descriptors to the YT-157 shared live runtime without changing the exposed MCP tool contracts or the underlying Layer 1 wrapper contracts.

## In-Scope Operations

| Resource family | Operations |
| --- | --- |
| Activities | `activities.list` |
| Captions | `captions.list`, `captions.insert`, `captions.update`, `captions.download`, `captions.delete` |
| Channel banners | `channelBanners.insert` |
| Channels | `channels.list`, `channels.update` |
| Channel sections | `channelSections.list`, `channelSections.insert`, `channelSections.update`, `channelSections.delete` |
| Comments | `comments.list`, `comments.insert`, `comments.update`, `comments.setModerationStatus`, `comments.delete` |
| Comment threads | `commentThreads.list`, `commentThreads.insert` |

## Configured Default Behavior

1. Normal application composition loads existing YT-157 live settings, constructs one configured runtime, and passes it through the HTTP transport to the dispatcher.
2. The dispatcher must pass the configured runtime executor and credential availability to the descriptors for every operation in scope.
3. A descriptor validates public arguments, selects authorization by its existing selector/write rules, and calls its existing Layer 1 wrapper with the shared executor.
4. The wrapper validates its existing request shape and delegates a `RequestExecution` to the existing concrete transport.
5. The concrete transport preserves the metadata-defined target, method, parameters, body, and upload form, attaches the selected credential, and returns the existing normalized success or normalized failure.
6. A configured default invocation must never create or select a family-local representative executor, placeholder credential, static result, or separate direct upstream path.

## Authorization and Request Rules

| Rule | Required behavior |
| --- | --- |
| API-key operation | Use a nonblank configured API key only where existing metadata/selector rules permit it. |
| OAuth-required operation | Use a nonblank configured OAuth credential; do not fall back to an API key. |
| Conditional operation | Use the credential mode selected by existing wrapper/handler rules; do not infer another mode from credential availability. |
| Query-only operation | Preserve the metadata-defined query target and parameters. |
| JSON-body operation | Preserve existing body validation and submit the validated body through the shared transport. |
| Raw-media or multipart operation | Preserve existing media validation and submit the declared form through the shared transport. |

## Compatibility Guarantees

The following remain unchanged for all in-scope operations:

- Public MCP tool name, description, input schema, metadata, quota and authorization disclosure, availability information, and caller examples.
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

- Parameterized request-level tests cover all 20 operations: path, method, parameters, selected credential mode/location, body or upload form where applicable, normalized success, and normalized upstream failure.
- Seven configured public-tool flow tests prove one flow per resource family reaches the shared live request path through transport and dispatcher composition.
- Existing unit and contract tests prove unchanged wrapper validation, descriptor schema/metadata, result shape, and safe error behavior.
- Final validation runs `python3 -m pytest` followed by `python3 -m ruff check .`.
