# Author: Lenard Felix
 
from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from client.lang import language_service
from shared.lib.names import generate_display_name
from client.ui.theme import TEXT_MUTED, render_text
from client.ui.controls import Button, TextInput
from client.screens.menu.menu_screen import MenuScreen

if TYPE_CHECKING:
    from client.screens.core.scene_manager import SceneManager

PLACEHOLDER_NAME = "Enter your Name"

class JoinLobbyScreen(MenuScreen):
    """
    Screen for joining an existing lobby. Allows the player to enter their name and a lobby join code.
    Submitting the form sends a join-lobby request to the server via LobbyService.
    """

    def __init__(self, surface: pg.Surface, scene_manager: SceneManager) -> None:
        super().__init__(surface, scene_manager, title="Join Lobby")
        form = self.scene_manager.runtime_state.join_lobby
        center_x = self.content_rect.centerx
        stored_name = scene_manager.client_settings.get_name()
        self.name_input = TextInput(
            pg.Rect(center_x - 186, self.content_rect.y + 96, 300, 46),
            form.player_name if stored_name == "" else stored_name,
            placeholder=PLACEHOLDER_NAME if stored_name == "" else stored_name,
        )
        self.random_name_button = Button(
            pg.Rect(self.name_input.rect.right + 12, self.name_input.rect.y, 60, 46),
            "",
            self._roll_name,
            icon="dice",
        )
        self.code_input = TextInput(pg.Rect(center_x - 110, self.content_rect.y + 216, 220, 46), form.join_code, placeholder="AB12", max_length=8)
        self.join_button = Button(
            pg.Rect(center_x - 90, self.content_rect.y + 274, 180, 48),
            "Join With Code",
            self._join_lobby,
            variant="primary",
        )
        self.join_public_button = Button(
            pg.Rect(center_x - 90, self.content_rect.y + 356, 180, 48),
            "Join Public",
            self._join_public_lobby,
        )

    def _join_lobby(self) -> None:
        """Submit the form and request the server to join the lobby matching the entered join code."""
        error = self.scene_manager.lobby_service.join_lobby(
            self.name_input.text,
            self.code_input.text,
        )
        if error:
            self.set_error_message(language_service.get_message(error))

    def _join_public_lobby(self) -> None:
        error = self.scene_manager.lobby_service.join_lobby(
            self.name_input.text,
            self.code_input.text,
            join_public=True,
        )
        if error:
            self.set_error_message(language_service.get_message(error))

    def _roll_name(self) -> None:
        self.name_input.text = generate_display_name()
        self.name_input.active = False

    def handle_content_event(self, event: pg.event.Event) -> None:
        """Handle input events for the form controls."""
        super().handle_content_event(event)
        self.name_input.handle_event(event)
        self.random_name_button.handle_event(event)
        self.code_input.handle_event(event)
        self.join_button.handle_event(event)
        self.join_public_button.handle_event(event)

    def update_content(self, dt: float) -> None:
        self.name_input.update(dt)
        self.code_input.update(dt)

    def draw_content(self, rect: pg.Rect) -> None:
        """Draw the form controls and any error messages."""
        super().draw_content(rect)
        self.name_input.draw(self.surface, self.small_font, self.body_font, "Player Name")
        self.random_name_button.draw(self.surface, self.button_font)
        self.code_input.draw(self.surface, self.small_font, self.body_font, "Join Code")
        self.join_button.draw(self.surface, self.button_font)
        or_label = render_text(self.small_font, "or", TEXT_MUTED)
        self.surface.blit(or_label, or_label.get_rect(center=(self.content_rect.centerx, self.content_rect.y + 338)))
        self.join_public_button.draw(self.surface, self.button_font)