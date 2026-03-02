import os
import sys

sys.path.insert(0, os.path.abspath("src"))

from mcp_server.app import create_app
from mcp_server.transport.http import MCPHTTPTransport


def make_app_with_dispatcher(dispatcher=None):
    if dispatcher is None:
        return create_app()
    return MCPHTTPTransport(dispatcher=dispatcher)
