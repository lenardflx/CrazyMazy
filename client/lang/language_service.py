from enum import StrEnum
from typing import Dict

from shared.protocol import ErrorCode


class DisplayMessage(StrEnum):
    SERVER_NOT_REACHABLE = "common.server_not_reachable"


class LanguageService:
    # TODO: depends on client settings and message repo
    def __init__(self) -> None:
        self.error_messages: Dict[ErrorCode, str] = {
            ErrorCode.GAME_NOT_FOUND: "This game does not exist",
            ErrorCode.NO_PUBLIC_LOBBY: "No public lobby available right now",
        }

        self.general_messages: Dict[DisplayMessage, str] = {
            DisplayMessage.SERVER_NOT_REACHABLE: "Server not reachable",
        }

    def get_message(self, message: DisplayMessage | ErrorCode) -> str:
        if isinstance(message, DisplayMessage):
            return self.general_messages.get(message, f"msg::{str(message)}")
        elif isinstance(message, ErrorCode):
            return self.error_messages.get(message, f"err::{str(message)}")
        else:
            return "Error loading message, unknown message type."