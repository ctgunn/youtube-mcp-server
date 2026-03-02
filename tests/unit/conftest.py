import os
import sys

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
