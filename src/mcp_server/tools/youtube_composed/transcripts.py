"""Transcript-family scaffolding for higher-level public YouTube tools.

This module declares transcript-family placement metadata only. Concrete
transcript handlers such as ``transcripts_searchTranscript`` belong to later
YT-302+ slices.
"""

from mcp_server.tools.youtube_composed.families import get_family

FAMILY_SCAFFOLDING = get_family("transcripts")
PLANNED_TOOLS = FAMILY_SCAFFOLDING.planned_tools
