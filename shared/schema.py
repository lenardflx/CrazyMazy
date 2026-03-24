from __future__ import annotations

from typing import TypedDict


class ErrorPayload(TypedDict):
    code: str
    message: str


class SnapshotMember(TypedDict):
    member_id: str
    name: str
    is_host: bool


class SnapshotRoom(TypedDict):
    room_id: str
    member_count: int
    members: list[SnapshotMember]
    started: bool
    match_id: str | None


class SnapshotSelf(TypedDict):
    member_id: str | None


class SnapshotPayload(TypedDict):
    room: SnapshotRoom
    self: SnapshotSelf
