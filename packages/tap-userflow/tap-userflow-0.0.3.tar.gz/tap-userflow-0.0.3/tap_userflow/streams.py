"""Stream type classes for tap-userflow."""

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_userflow.client import UserFlowStream

# TODO: Delete this is if not using json files for schema definition
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")
# TODO: - Override `UsersStream` and `GroupsStream` with your own stream definition.
#       - Copy-paste as many times as needed to create multiple stream types.


class ContentStream(UserFlowStream):
    """Define custom stream."""
    name = "content"
    path = "/content"
    primary_keys = ["id"]
    replication_key = "id"
    order_by_key = "created_at"
    schema_filepath = SCHEMAS_DIR / "content.json"
    is_timestamp_replication_key = False
    replication_method = "INCREMENTAL"
    is_sorted = True
    check_sorted = False

class ContentSessionStream(UserFlowStream):
    name = "content_session"
    path = "/content_sessions"
    primary_keys = ["id"]
    replication_key = "id"
    order_by_key = "last_activity_at"
    schema_filepath = SCHEMAS_DIR /"content-session.json"
    is_timestamp_replication_key = False
    replication_method = "INCREMENTAL"
    is_sorted = True
    check_sorted = False