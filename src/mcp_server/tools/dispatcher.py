"""Tool registry and invocation dispatch."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

from mcp_server.tools.retrieval import FETCH_TOOL_SCHEMA, SEARCH_TOOL_SCHEMA, fetch_tool, search_tool

BASELINE_TOOL_SCHEMAS = {
    "server_ping": {
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
    "server_info": {
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
    "server_list_tools": {
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
}

BASELINE_TOOL_DESCRIPTIONS = {
    "server_ping": "Return service status and timestamp",
    "server_info": "Return server version, environment, and build metadata",
    "server_list_tools": "Return currently registered tool names and descriptions",
    "search": "Search the retrieval corpus for relevant documents.",
    "fetch": "Fetch the full contents of a previously identified document.",
}

DEFAULT_SERVER_METADATA = {
    "version": "0.1.0",
    "environment": "dev",
    "build": {
        "buildId": "local",
        "commit": "unknown",
        "buildTime": "unknown",
    },
}


class ToolRegistrationError(ValueError):
    """Raised when tool registration payload is invalid."""


class DuplicateToolError(ValueError):
    """Raised when a duplicate tool name is registered."""


def normalize_tool_name(name: str) -> str:
    if not isinstance(name, str) or not name.strip():
        raise ToolRegistrationError("tool name is required")
    return name.strip().lower()


class InMemoryToolDispatcher:
    def __init__(self, tools=None, server_metadata=None):
        self._tools: dict[str, dict[str, Any]] = {}
        self._server_metadata = self._normalize_server_metadata(server_metadata)

        initial_tools = tools if tools is not None else self._baseline_tool_definitions()

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
        if input_schema.get("type") != "object":
            raise ToolRegistrationError("inputSchema must define an object schema")
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

    def _tool_descriptor(self, entry: dict[str, Any]) -> dict[str, Any]:
        return {
            "name": entry["name"],
            "description": entry["description"],
            "inputSchema": entry["inputSchema"],
        }

    def list_tools(self):
        items = []
        for normalized in sorted(self._tools.keys()):
            entry = self._tools[normalized]
            items.append(self._tool_descriptor(entry))
        return items

    def _baseline_tool_definitions(self):
        return [
            {
                "name": "server_ping",
                "description": BASELINE_TOOL_DESCRIPTIONS["server_ping"],
                "inputSchema": BASELINE_TOOL_SCHEMAS["server_ping"],
                "handler": self._server_ping,
            },
            {
                "name": "server_info",
                "description": BASELINE_TOOL_DESCRIPTIONS["server_info"],
                "inputSchema": BASELINE_TOOL_SCHEMAS["server_info"],
                "handler": self._server_info,
            },
            {
                "name": "server_list_tools",
                "description": BASELINE_TOOL_DESCRIPTIONS["server_list_tools"],
                "inputSchema": BASELINE_TOOL_SCHEMAS["server_list_tools"],
                "handler": self._server_list_tools,
            },
            {
                "name": "search",
                "description": BASELINE_TOOL_DESCRIPTIONS["search"],
                "inputSchema": SEARCH_TOOL_SCHEMA,
                "handler": search_tool,
            },
            {
                "name": "fetch",
                "description": BASELINE_TOOL_DESCRIPTIONS["fetch"],
                "inputSchema": FETCH_TOOL_SCHEMA,
                "handler": fetch_tool,
            },
        ]

    def _normalize_server_metadata(self, server_metadata):
        metadata = server_metadata or {}
        build = metadata.get("build") if isinstance(metadata.get("build"), dict) else {}
        return {
            "version": metadata.get("version") or DEFAULT_SERVER_METADATA["version"],
            "environment": metadata.get("environment") or DEFAULT_SERVER_METADATA["environment"],
            "build": {
                "buildId": build.get("buildId") or DEFAULT_SERVER_METADATA["build"]["buildId"],
                "commit": build.get("commit") or DEFAULT_SERVER_METADATA["build"]["commit"],
                "buildTime": build.get("buildTime")
                or DEFAULT_SERVER_METADATA["build"]["buildTime"],
            },
        }

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

        if isinstance(properties, dict):
            for key, value in arguments.items():
                definition = properties.get(key, {})
                expected_type = definition.get("type")
                if expected_type == "string":
                    if not isinstance(value, str):
                        raise ValueError(f"{key} must be a string")
                    min_length = definition.get("minLength")
                    if isinstance(min_length, int) and len(value) < min_length:
                        raise ValueError(f"{key} must be at least {min_length} characters")
                elif expected_type == "integer":
                    if not isinstance(value, int):
                        raise ValueError(f"{key} must be an integer")
                    minimum = definition.get("minimum")
                    if isinstance(minimum, int) and value < minimum:
                        raise ValueError(f"{key} must be greater than or equal to {minimum}")

        self._validate_composed_schema(schema, arguments)

    def _validate_composed_schema(self, schema: dict, arguments: dict):
        self._validate_required_combinations("oneOf", schema, arguments)
        self._validate_required_combinations("anyOf", schema, arguments)

    def _validate_required_combinations(self, keyword: str, schema: dict, arguments: dict):
        options = schema.get(keyword)
        if not isinstance(options, list):
            return

        matched = False
        for option in options:
            if not isinstance(option, dict):
                continue
            required = option.get("required", [])
            if not isinstance(required, list):
                continue
            if all(field in arguments for field in required):
                matched = True
                break

        if not matched:
            required_sets = []
            for option in options:
                if isinstance(option, dict) and isinstance(option.get("required"), list) and option["required"]:
                    required_sets.append(" + ".join(option["required"]))
            if required_sets:
                raise ValueError(f"arguments must satisfy one of the required combinations: {', '.join(required_sets)}")

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

    def _server_ping_payload(self):
        return {
            "status": "ok",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _server_ping(self, _arguments):
        return self._server_ping_payload()

    def _server_info(self, _arguments):
        return {
            "version": self._server_metadata["version"],
            "environment": self._server_metadata["environment"],
            "build": self._server_metadata["build"].copy(),
        }

    def _server_list_tools(self, _arguments):
        return self.list_tools()
