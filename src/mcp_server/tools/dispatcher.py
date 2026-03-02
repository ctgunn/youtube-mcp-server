"""Tool registry and invocation dispatch."""

from __future__ import annotations

from datetime import datetime, timezone


class InMemoryToolDispatcher:
    def __init__(self, tools=None):
        default_tools = {
            "server_ping": {
                "description": "Return service status and timestamp",
                "handler": self._server_ping,
            }
        }
        self._tools = tools if tools is not None else default_tools

    def list_tools(self):
        items = []
        for name in sorted(self._tools.keys()):
            entry = self._tools[name]
            items.append(
                {
                    "name": name,
                    "description": entry.get("description", ""),
                }
            )
        return items

    def call_tool(self, tool_name: str, arguments=None):
        arguments = arguments or {}
        if not isinstance(arguments, dict):
            raise ValueError("arguments must be an object")

        entry = self._tools.get(tool_name)
        if entry is None:
            raise KeyError(tool_name)

        handler = entry.get("handler")
        if handler is None:
            raise RuntimeError("Tool handler missing")

        return handler(arguments)

    def _server_ping(self, _arguments):
        return {
            "status": "ok",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
