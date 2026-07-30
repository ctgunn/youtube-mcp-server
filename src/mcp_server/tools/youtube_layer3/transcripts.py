"""Transcript-family scaffolding for Layer 3 public YouTube tools.

This module declares transcript-family placement metadata only. Concrete
transcript handlers such as ``transcripts_searchTranscript`` belong to later
YT-302+ slices.
"""

from mcp_server.tools.youtube_layer3.families import get_layer3_family

FAMILY_SCAFFOLDING = get_layer3_family("transcripts")
PLANNED_TOOLS = FAMILY_SCAFFOLDING.planned_tools
