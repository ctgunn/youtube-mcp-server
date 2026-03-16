import os
import sys
from typing import Any

sys.path.insert(0, os.path.abspath("src"))


def sample_tool_definition(name="sample_tool"):
    return {
        "name": name,
        "description": "Sample test tool",
        "inputSchema": {
            "type": "object",
            "properties": {
                "value": {"type": "string"},
            },
            "required": [],
            "additionalProperties": False,
        },
        "handler": lambda arguments: {"echo": arguments.get("value", "")},
    }


def baseline_call_params(tool_name, arguments=None):
    return {
        "toolName": tool_name,
        "arguments": arguments or {},
    }


def sample_server_metadata(**overrides):
    metadata = {
        "version": "0.1.0",
        "environment": "dev",
        "build": {
            "buildId": "local",
            "commit": "unknown",
            "buildTime": "unknown",
        },
    }
    build_overrides = overrides.pop("build", None)
    metadata.update(overrides)
    if build_overrides:
        metadata["build"].update(build_overrides)
    return metadata


def parse_sse_payload(body: bytes | str) -> list[dict[str, Any]]:
    text = body.decode("utf-8") if isinstance(body, bytes) else body
    events: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    for line in text.splitlines():
        if not line.strip():
            if current:
                events.append(current)
                current = {}
            continue
        key, _, value = line.partition(":")
        current.setdefault(key, "")
        current[key] = value.lstrip()
    if current:
        events.append(current)
    return events
