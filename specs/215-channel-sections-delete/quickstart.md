# Quickstart: `channelSections_delete`

## Goal

Verify the YT-215 plan and future implementation for the public Layer 2 `channelSections_delete` MCP tool.

## Expected Tool Contract

- Tool name: `channelSections_delete`
- Endpoint: `channelSections.delete`
- Quota cost: `50`
- Auth: eligible OAuth required
- Required input: `id`
- Optional input: partner-only `onBehalfOfContentOwner`
- Request body: unsupported
- Result: deletion acknowledgment with safe operation context and no fabricated deleted resource fields

## Example Calls

Authorized delete:

```json
{
  "id": "section-123"
}
```

Partner-context delete:

```json
{
  "id": "section-123",
  "onBehalfOfContentOwner": "content-owner-id"
}
```

Unsupported body:

```json
{
  "id": "section-123",
  "body": {
    "snippet": {
      "title": "Do not send bodies to delete"
    }
  }
}
```

Expected unsupported-body category: `invalid_request`.

## Red Checks To Add First

```bash
pytest tests/contract/test_youtube_channel_sections_contract.py -k delete
pytest tests/unit/test_youtube_channel_sections.py -k delete
pytest tests/integration/test_youtube_channel_sections_registration.py -k delete
```

These checks should fail before implementation because `channelSections_delete` symbols, contract metadata, handler behavior, and registry integration are not yet present.

## Green Implementation Targets

1. Add `CHANNEL_SECTIONS_DELETE_*` constants, schema, description, usage notes, caveats, examples, and error type in `src/mcp_server/tools/youtube_common/channel_sections.py`.
2. Add contract, result mapper, validator, auth helper, upstream-error mapper, handler builder, descriptor builder, and default no-body delete transport.
3. Export symbols from `src/mcp_server/tools/youtube_common/__init__.py`.
4. Add representative contract entry in `src/mcp_server/tools/youtube_common/examples.py` if required by existing representative coverage.
5. Register the descriptor in the default dispatcher.

## Final Verification

Run focused checks:

```bash
pytest tests/contract/test_youtube_channel_sections_contract.py tests/unit/test_youtube_channel_sections.py tests/integration/test_youtube_channel_sections_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py
```

Run required full checks:

```bash
pytest
ruff check .
```

Review evidence should include passing focused output, full-suite output, lint output, and confirmation that all new or changed Python functions have reStructuredText docstrings.
