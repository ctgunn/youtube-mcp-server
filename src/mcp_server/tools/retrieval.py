"""Foundational deep-research retrieval tools."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


SEARCH_TOOL_SCHEMA = {
    "type": "object",
    "required": ["query"],
    "properties": {
        "query": {"type": "string", "minLength": 1},
        "pageSize": {"type": "integer", "minimum": 1},
        "cursor": {"type": "string"},
    },
    "additionalProperties": False,
}

FETCH_TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "resourceId": {"type": "string"},
        "uri": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}


@dataclass(frozen=True)
class RetrievalSource:
    resource_id: str
    uri: str
    title: str
    snippet: str
    source_name: str
    content: str
    excerpt: str
    content_type: str = "text/html"


class RetrievalError(Exception):
    """Structured retrieval error for MCP-safe mapping."""

    def __init__(self, mcp_code: str, message: str, *, category: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.mcp_code = mcp_code
        self.category = category
        self.details = {"category": category, **(details or {})}


SAMPLE_SOURCES: tuple[RetrievalSource, ...] = (
    RetrievalSource(
        resource_id="res_remote_mcp_001",
        uri="https://example.com/remote-mcp-research",
        title="Remote MCP Research Workflows",
        snippet="Guidance for hosted MCP consumers evaluating remote research tools.",
        source_name="Example Research",
        content=(
            "Remote MCP research workflows depend on discoverable tools, stable result identifiers, "
            "and structured content retrieval for downstream reasoning."
        ),
        excerpt="Remote MCP research workflows depend on discoverable tools.",
    ),
    RetrievalSource(
        resource_id="res_agent_builder_002",
        uri="https://example.com/openai-agent-builder-mcp",
        title="OpenAI Agent Builder MCP Integration",
        snippet="Practical notes for connecting protected MCP services to hosted agent workflows.",
        source_name="Example Research",
        content=(
            "OpenAI Agent Builder integrations need predictable tool discovery, protected hosted access, "
            "and fetchable source content that agents can consume directly."
        ),
        excerpt="OpenAI Agent Builder integrations need predictable tool discovery.",
    ),
    RetrievalSource(
        resource_id="res_streamable_http_003",
        uri="https://example.com/streamable-http-mcp",
        title="Streamable HTTP MCP Contracts",
        snippet="Why transport alignment matters for hosted tool invocation and verification.",
        source_name="Example Research",
        content=(
            "Streamable HTTP MCP contracts ensure hosted verification, session reuse, and tool calls behave "
            "consistently across local and remote environments."
        ),
        excerpt="Streamable HTTP MCP contracts ensure hosted verification.",
    ),
)


def _normalize_query(arguments: dict[str, Any]) -> tuple[str, int, int]:
    query = str(arguments.get("query", "")).strip()
    if not query:
        raise ValueError("query must be a non-empty string")

    page_size = arguments.get("pageSize", 10)
    if not isinstance(page_size, int):
        raise ValueError("pageSize must be an integer")
    if page_size <= 0:
        raise ValueError("pageSize must be greater than 0")

    cursor = arguments.get("cursor")
    if cursor is None or cursor == "":
        offset = 0
    else:
        try:
            offset = int(str(cursor))
        except ValueError as exc:
            raise ValueError("cursor must be a numeric offset token") from exc
        if offset < 0:
            raise ValueError("cursor must be greater than or equal to 0")

    return query.lower(), page_size, offset


def _search_results(query: str) -> list[RetrievalSource]:
    if query == "no-match-sentinel":
        return []
    terms = [term for term in query.split() if term]
    ranked: list[tuple[int, RetrievalSource]] = []
    for source in SAMPLE_SOURCES:
        haystack = " ".join((source.title, source.snippet, source.content, source.source_name)).lower()
        score = sum(1 for term in terms if term in haystack)
        if score:
            ranked.append((score, source))
    ranked.sort(key=lambda item: (-item[0], item[1].resource_id))
    return [source for _, source in ranked]


def search_tool(arguments: dict[str, Any]) -> dict[str, Any]:
    query, page_size, offset = _normalize_query(arguments)
    results = _search_results(query)
    page = results[offset : offset + page_size]
    payload = []
    for index, source in enumerate(page, start=offset + 1):
        payload.append(
            {
                "resourceId": source.resource_id,
                "uri": source.uri,
                "title": source.title,
                "snippet": source.snippet,
                "sourceName": source.source_name,
                "position": index,
            }
        )
    response = {
        "results": payload,
        "totalReturned": len(payload),
    }
    next_offset = offset + len(page)
    if next_offset < len(results):
        response["nextCursor"] = str(next_offset)
    return response


def _find_by_resource_id(resource_id: str) -> RetrievalSource | None:
    for source in SAMPLE_SOURCES:
        if source.resource_id == resource_id:
            return source
    return None


def _find_by_uri(uri: str) -> RetrievalSource | None:
    for source in SAMPLE_SOURCES:
        if source.uri == uri:
            return source
    return None


def fetch_tool(arguments: dict[str, Any]) -> dict[str, Any]:
    resource_id = arguments.get("resourceId")
    uri = arguments.get("uri")
    if resource_id is not None and not isinstance(resource_id, str):
        raise ValueError("resourceId must be a string")
    if uri is not None and not isinstance(uri, str):
        raise ValueError("uri must be a string")

    resource_id = str(resource_id or "").strip() or None
    uri = str(uri or "").strip() or None
    if not resource_id and not uri:
        raise ValueError("resourceId or uri is required")

    source_from_id = _find_by_resource_id(resource_id) if resource_id else None
    source_from_uri = _find_by_uri(uri) if uri else None
    if resource_id and uri:
        if source_from_id is None or source_from_uri is None or source_from_id.resource_id != source_from_uri.resource_id:
            raise ValueError("resourceId and uri must identify the same source")

    source = source_from_id or source_from_uri
    if source is None:
        raise RetrievalError(
            "RESOURCE_NOT_FOUND",
            "Requested source is not available.",
            category="unavailable_source",
            details={"resourceId": resource_id, "uri": uri},
        )

    return {
        "resourceId": source.resource_id,
        "uri": source.uri,
        "title": source.title,
        "content": source.content,
        "excerpt": source.excerpt,
        "contentType": source.content_type,
        "retrievalStatus": "complete",
    }
