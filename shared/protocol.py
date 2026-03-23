# Author: Lenard Felix

from __future__ import annotations

import json
import socket
from dataclasses import dataclass, field


class EventType:
    """
      client_<module>_<action> for client-to-server messages
      server_<module>_<action> for server-to-client messages
    """

    # Health
    CLIENT_HEALTH_PING = "client_health_ping"
    SERVER_HEALTH_PONG = "server_health_pong"  # TODO: replace with models since this is not a real event type

    # Lobby
    CLIENT_CREATE_LOBBY  = "client_create_lobby"
    CLIENT_JOIN_LOBBY    = "client_join_lobby"
    CLIENT_LEAVE_LOBBY   = "client_leave_lobby"
    SERVER_LOBBY_CREATED = "server_lobby_created"
    SERVER_LOBBY_JOINED  = "server_lobby_joined"


@dataclass
class Message:
    type: str
    payload: dict = field(default_factory=dict)

    @staticmethod
    def from_dict(data: dict) -> Message:
        return Message(type=data["type"], payload=data.get("payload", {}))

    def to_dict(self) -> dict:
        return {"type": self.type, "payload": self.payload}