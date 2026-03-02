"""Tool registry and invocation dispatch."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable


class ToolRegistrationError(ValueError):
    """Raised when tool registration payload is invalid."""


class DuplicateToolError(ValueError):
    """Raised when a duplicate tool name is registered."""


def normalize_tool_name(name: str) -> str:
    if not isinstance(name, str) or not name.strip():
        raise ToolRegistrationError("tool name is required")
    return name.strip().lower()


class InMemoryToolDispatcher:
    def __init__(self, tools=None):
        self._tools: dict[str, dict[str, Any]] = {}

        default_tools = [
            {
                "name": "server_ping",
                "description": "Return service status and timestamp",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                },
                "handler": self._server_ping,
            }
        ]

        initial_tools = tools if tools is not None else default_tools

        if isinstance(initial_tools, dict):
            # Backward-compatible bootstrap for {name: {description, handler}}.
            for name, entry in initial_tools.items():
                self.register_tool(
                    name=name,
                    description=entry.get("description", ""),
                    input_schema=entry.get("inputSchema")
                    or entry.get("input_schema")
                    or {"type": "object", "properties": {}, "additionalProperties": True},
                    handler=entry.get("handler"),
                )
        else:
            for tool in initial_tools:
                self.register_tool(
                    name=tool.get("name"),
                    description=tool.get("description"),
                    input_schema=tool.get("inputSchema") or tool.get("input_schema"),
                    handler=tool.get("handler"),
                )

    def register_tool(self, name: str, description: str, input_schema: dict, handler: Callable):
        if not isinstance(description, str) or not description.strip():
            raise ToolRegistrationError("tool description is required")
        if not isinstance(input_schema, dict):
            raise ToolRegistrationError("inputSchema must be an object")
        if not callable(handler):
            raise ToolRegistrationError("tool handler must be callable")

        normalized = normalize_tool_name(name)
        if normalized in self._tools:
            raise DuplicateToolError("tool already registered")

        self._tools[normalized] = {
            "name": name.strip(),
            "normalizedName": normalized,
            "description": description.strip(),
            "inputSchema": input_schema,
            "handler": handler,
        }

    def list_tools(self):
        items = []
        for normalized in sorted(self._tools.keys()):
            entry = self._tools[normalized]
            items.append(
                {
                    "name": entry["name"],
                    "description": entry["description"],
                }
            )
        return items

    def _validate_arguments(self, schema: dict, arguments: dict):
        schema_type = schema.get("type")
        if schema_type == "object" and not isinstance(arguments, dict):
            raise ValueError("arguments must be an object")

        if not isinstance(arguments, dict):
            raise ValueError("arguments must be an object")

        required = schema.get("required", [])
        if isinstance(required, list):
            for field in required:
                if field not in arguments:
                    raise ValueError(f"arguments missing required field: {field}")

        additional = schema.get("additionalProperties", True)
        properties = schema.get("properties", {})
        if additional is False and isinstance(properties, dict):
            allowed = set(properties.keys())
            unexpected = [key for key in arguments.keys() if key not in allowed]
            if unexpected:
                raise ValueError(f"arguments contain unsupported field: {unexpected[0]}")

    def call_tool(self, tool_name: str, arguments=None):
        arguments = arguments or {}
        if not isinstance(arguments, dict):
            raise ValueError("arguments must be an object")

        normalized = normalize_tool_name(tool_name)
        entry = self._tools.get(normalized)
        if entry is None:
            raise KeyError(tool_name)

        handler = entry.get("handler")
        if handler is None:
            raise RuntimeError("Tool handler missing")

        self._validate_arguments(entry.get("inputSchema", {}), arguments)
        return handler(arguments)

    def _server_ping(self, _arguments):
        return {
            "status": "ok",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
