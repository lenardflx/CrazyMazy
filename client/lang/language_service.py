from enum import StrEnum
from typing import Dict

from shared.protocol import ErrorCode, DisplayMessage
from client.state.app_data import ClientData
from client.lang.messages import messages


class LanguageService:
    def __init__(self) -> None:
        client_data = ClientData()
        self.language = client_data.get_language()
        self.error_messages: Dict[ErrorCode, str] = {
            ErrorCode.GAME_NOT_FOUND: messages[ErrorCode.GAME_NOT_FOUND][self.language],
            ErrorCode.NO_PUBLIC_LOBBY: messages[ErrorCode.NO_PUBLIC_LOBBY][self.language],
        }
        self.general_messages: Dict[DisplayMessage, str] = {
            DisplayMessage.SERVER_NOT_REACHABLE: messages[DisplayMessage.SERVER_NOT_REACHABLE][self.language],
        }

    def get_message(self, message: DisplayMessage | ErrorCode) -> str:
        if isinstance(message, DisplayMessage):
            return self.general_messages.get(message, f"msg::{str(message)}")
        elif isinstance(message, ErrorCode):
            return self.error_messages.get(message, f"err::{str(message)}")
        else:
            return messages[DisplayMessage.UNKNOWN_MESSAGE_TYPE][self.language]
