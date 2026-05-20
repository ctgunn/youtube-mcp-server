"""Comments resource-family wrappers for Layer 1 YouTube integrations."""

from mcp_server.integrations.wrappers import (
    CommentsDeleteWrapper,
    CommentsInsertWrapper,
    CommentsListWrapper,
    CommentsSetModerationStatusWrapper,
    CommentsUpdateWrapper,
    build_comments_delete_wrapper,
    build_comments_insert_wrapper,
    build_comments_list_wrapper,
    build_comments_set_moderation_status_wrapper,
    build_comments_update_wrapper,
)

FAMILY_NAME = "comments"
RESOURCE_NAMES = ("comments",)
BUILDER_FUNCTIONS = {
    "comments.list": build_comments_list_wrapper,
    "comments.insert": build_comments_insert_wrapper,
    "comments.update": build_comments_update_wrapper,
    "comments.setModerationStatus": build_comments_set_moderation_status_wrapper,
    "comments.delete": build_comments_delete_wrapper,
}

__all__ = [
    "BUILDER_FUNCTIONS",
    "CommentsDeleteWrapper",
    "CommentsInsertWrapper",
    "CommentsListWrapper",
    "CommentsSetModerationStatusWrapper",
    "CommentsUpdateWrapper",
    "FAMILY_NAME",
    "RESOURCE_NAMES",
    "build_comments_delete_wrapper",
    "build_comments_insert_wrapper",
    "build_comments_list_wrapper",
    "build_comments_set_moderation_status_wrapper",
    "build_comments_update_wrapper",
]
