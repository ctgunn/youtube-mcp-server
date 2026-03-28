"""Foundational deep-research retrieval tools.

FND-023 aligns the external `search` and `fetch` contract to the OpenAI
retrieval compatibility shape while keeping the internal retrieval corpus simple.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


SEARCH_TOOL_SCHEMA = {
    "type": "object",
    "required": ["query"],
    "properties": {
        "query": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}

FETCH_TOOL_SCHEMA = {
    "type": "object",
    "required": ["id"],
    "properties": {
        "id": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}


@dataclass(frozen=True)
class RetrievalSource:
    document_id: str
    uri: str
    title: str
    snippet: str
    source_name: str
    content: str
    metadata: dict[str, Any]


class RetrievalError(Exception):
    """Structured retrieval error for MCP-safe mapping."""

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.category = category
        self.details = details or {}


SAMPLE_SOURCES: tuple[RetrievalSource, ...] = (
    RetrievalSource(
        document_id="doc-remote-mcp-001",
        uri="https://example.com/remote-mcp-research",
        title="Remote MCP Research Workflows",
        snippet="Guidance for hosted MCP consumers evaluating remote research tools.",
        source_name="Example Research",
        content=(
            "Remote MCP research workflows depend on discoverable tools, stable result identifiers, "
            "and structured content retrieval for downstream reasoning."
        ),
        metadata={"sourceName": "Example Research"},
    ),
    RetrievalSource(
        document_id="doc-agent-builder-002",
        uri="https://example.com/openai-agent-builder-mcp",
        title="OpenAI Agent Builder MCP Integration",
        snippet="Practical notes for connecting protected MCP services to hosted agent workflows.",
        source_name="Example Research",
        content=(
            "OpenAI Agent Builder integrations need predictable tool discovery, protected hosted access, "
            "and fetchable source content that agents can consume directly."
        ),
        metadata={"sourceName": "Example Research"},
    ),
    RetrievalSource(
        document_id="doc-streamable-http-003",
        uri="https://example.com/streamable-http-mcp",
        title="Streamable HTTP MCP Contracts",
        snippet="Why transport alignment matters for hosted tool invocation and verification.",
        source_name="Example Research",
        content=(
            "Streamable HTTP MCP contracts ensure hosted verification, session reuse, and tool calls behave "
            "consistently across local and remote environments."
        ),
        metadata={"sourceName": "Example Research"},
    ),
)


def _normalize_query(arguments: dict[str, Any]) -> str:
    query = str(arguments.get("query", "")).strip()
    if not query:
        raise ValueError("query must be a non-empty string")
    return query.lower()


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
    ranked.sort(key=lambda item: (-item[0], item[1].document_id))
    return [source for _, source in ranked]


def search_tool(arguments: dict[str, Any]) -> dict[str, Any]:
    query = _normalize_query(arguments)
    results = _search_results(query)
    return {
        "results": [
            {
                "id": source.document_id,
                "title": source.title,
                "url": source.uri,
            }
            for source in results
        ]
    }


def _find_by_document_id(document_id: str) -> RetrievalSource | None:
    for source in SAMPLE_SOURCES:
        if source.document_id == document_id:
            return source
    return None


def fetch_tool(arguments: dict[str, Any]) -> dict[str, Any]:
    document_id = arguments.get("id")
    if document_id is not None and not isinstance(document_id, str):
        raise ValueError("id must be a string")

    document_id = str(document_id or "").strip() or None
    if not document_id:
        raise ValueError("id is required")

    source = _find_by_document_id(document_id)
    if source is None:
        raise RetrievalError(
            "Requested source is not available.",
            category="unavailable_source",
            details={"id": document_id},
        )

    return {
        "id": source.document_id,
        "title": source.title,
        "text": source.content,
        "url": source.uri,
        "metadata": source.metadata,
    }
