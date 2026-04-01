"""Language message keys used by the client UI."""

from enum import StrEnum
from typing import TypeAlias

from shared.protocol import ErrorCode


class DisplayMessage(StrEnum):
    """Stable keys for UI text that is not provided by the server."""

    SERVER_NOT_REACHABLE = "common.server_not_reachable"
    MAIN_MENU_CREATE = "main_menu.create"
    MAIN_MENU_JOIN = "main_menu.join"
    MAIN_MENU_TUTORIAL = "main_menu.tutorial"
    MAIN_MENU_OPTIONS = "main_menu.options"
    MAIN_MENU_QUIT = "main_menu.quit"
    MAIN_MENU_WELCOME = "main_menu.welcome"
    MAIN_MENU_START_WITH_TUTORIAL = "main_menu.start_with_tutorial"
    MAIN_MENU_START = "main_menu.start"
    MAIN_MENU_SKIP = "main_menu.skip"
    MAIN_MENU_QUIT_TITLE = "main_menu.quit_title"
    MAIN_MENU_QUIT_MESSAGE = "main_menu.quit_message"
    MAIN_MENU_CONNECTED_TO = "main_menu.connected_to"


MessageKey: TypeAlias = DisplayMessage | ErrorCode
