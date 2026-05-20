"""Captions resource-family wrappers for Layer 1 YouTube integrations."""

from mcp_server.integrations.wrappers import (
    CaptionsDeleteWrapper,
    CaptionsDownloadWrapper,
    CaptionsInsertWrapper,
    CaptionsListWrapper,
    CaptionsUpdateWrapper,
    build_captions_delete_wrapper,
    build_captions_download_wrapper,
    build_captions_insert_wrapper,
    build_captions_list_wrapper,
    build_captions_update_wrapper,
)

FAMILY_NAME = "captions"
RESOURCE_NAMES = ("captions",)
BUILDER_FUNCTIONS = {
    "captions.list": build_captions_list_wrapper,
    "captions.insert": build_captions_insert_wrapper,
    "captions.update": build_captions_update_wrapper,
    "captions.download": build_captions_download_wrapper,
    "captions.delete": build_captions_delete_wrapper,
}
RESPONSE_NORMALIZER_KEYS = ("captions.download", "captions.delete")

__all__ = [
    "BUILDER_FUNCTIONS",
    "CaptionsDeleteWrapper",
    "CaptionsDownloadWrapper",
    "CaptionsInsertWrapper",
    "CaptionsListWrapper",
    "CaptionsUpdateWrapper",
    "FAMILY_NAME",
    "RESOURCE_NAMES",
    "RESPONSE_NORMALIZER_KEYS",
    "build_captions_delete_wrapper",
    "build_captions_download_wrapper",
    "build_captions_insert_wrapper",
    "build_captions_list_wrapper",
    "build_captions_update_wrapper",
]
