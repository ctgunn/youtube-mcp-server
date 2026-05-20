"""Comment thread resource-family wrappers for Layer 1 YouTube integrations."""

from mcp_server.integrations.wrappers import (
    CommentThreadsInsertWrapper,
    CommentThreadsListWrapper,
    build_comment_threads_insert_wrapper,
    build_comment_threads_list_wrapper,
)

FAMILY_NAME = "comment_threads"
RESOURCE_NAMES = ("commentThreads",)
BUILDER_FUNCTIONS = {
    "commentThreads.list": build_comment_threads_list_wrapper,
    "commentThreads.insert": build_comment_threads_insert_wrapper,
}

__all__ = [
    "BUILDER_FUNCTIONS",
    "CommentThreadsInsertWrapper",
    "CommentThreadsListWrapper",
    "FAMILY_NAME",
    "RESOURCE_NAMES",
    "build_comment_threads_insert_wrapper",
    "build_comment_threads_list_wrapper",
]
