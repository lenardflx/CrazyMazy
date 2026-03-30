# Author: Lenard Felix

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import pygame as pg

from shared.lib.lobby import VALID_BOARD_SIZES
from client.ui.controls import Button, TextInput
from client.ui.theme import TEXT_PRIMARY
from client.screens.menu.menu_screen import MenuScreen
if TYPE_CHECKING:
    from client.screens.core.scene_manager import SceneManager

PLACEHOLDER_NAME = "Enter your Name"


class CreateLobbyScreen(MenuScreen):
    """
    Screen for creating a new game lobby. Allows the player to enter their name and choose a board size.
    Submitting the form sends a create-lobby request to the server via LobbyService.
    """

    def __init__(self, surface: pg.Surface, scene_manager: SceneManager) -> None:
        super().__init__(surface, scene_manager, title="Create Lobby")
        form = self.scene_manager.runtime_state.create_lobby
        center_x = self.content_rect.centerx
        self.name_input = TextInput(pg.Rect(center_x - 180, self.content_rect.y + 96, 360, 46), form.player_name,
                                    placeholder=PLACEHOLDER_NAME if scene_manager.client_settings.get_name() == "" else scene_manager.client_settings.get_name())
        sizes = tuple(sorted(VALID_BOARD_SIZES))
        self.size_buttons = []
        for index, size in enumerate(sizes):
            button = Button(
                pg.Rect(center_x - ((len(sizes) * 86 + (len(sizes) - 1) * 8) // 2) + index * 94, self.content_rect.y + 192, 86, 42),
                str(size),
                self._set_board_size_action(size),
                variant="primary" if form.board_size == size else "secondary",
            )
            self.size_buttons.append(button)
        self.create_button = Button(
            pg.Rect(center_x - 100, self.content_rect.y + 282, 200, 48),
            "Create Lobby",
            self._create_lobby,
            variant="primary",
        )

    def _set_board_size(self, size: int) -> None:
        """Update the selected board size in the runtime state and highlight the corresponding button."""
        self.scene_manager.runtime_state.create_lobby.board_size = size
        for button in self.size_buttons:
            button.variant = "primary" if button.label == str(size) else "secondary"

    def _set_board_size_action(self, size: int) -> Callable[[], None]:
        """Return a closure that sets the board size to the given value when called.
        This is needed because Python closures capture by reference, so we need to bind the size value here.
        """
        def handle_click() -> None:
            self._set_board_size(size)

        return handle_click

    def _create_lobby(self) -> None:
        """Submit the form and request the server to create a new lobby with the entered name and selected board size."""
        self.scene_manager.lobby_service.create_lobby(
            self.name_input.text,
            self.scene_manager.runtime_state.create_lobby.board_size,
        )
        self.scene_manager.client_settings.set_name(self.name_input.text)
        self.scene_manager.client_settings.write_JSON()
        
    def handle_content_event(self, event: pg.event.Event) -> None:
        """Handle input events for the form controls."""
        super().handle_content_event(event)
        self.name_input.handle_event(event)
        for button in self.size_buttons:
            button.handle_event(event)
        self.create_button.handle_event(event)

    def draw_content(self, rect: pg.Rect) -> None:
        """Draw the form controls and any error messages."""
        super().draw_content(rect)
        caption = self.body_font.render("Board Size", True, TEXT_PRIMARY)
        self.surface.blit(caption, caption.get_rect(center=(self.content_rect.centerx, self.content_rect.y + 172)))
        self.name_input.draw(self.surface, self.small_font, self.body_font, "Player Name")
        for button in self.size_buttons:
            button.draw(self.surface, self.button_font)
        self.create_button.draw(self.surface, self.button_font)
        if self.error_message:
            error = self.small_font.render(self.error_message, True, (150, 58, 48))
            self.surface.blit(error, error.get_rect(center=(self.content_rect.centerx, self.content_rect.y + 346)))
