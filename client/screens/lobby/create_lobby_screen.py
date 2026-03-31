# Author: Lenard Felix

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import pygame as pg

from client.lang import language_service
from shared.lib.lobby import VALID_BOARD_SIZES, VALID_INSERT_TIMEOUTS, VALID_MOVE_TIMEOUTS
from client.ui.controls import Button, TextInput
from client.ui.theme import TEXT_PRIMARY
from client.screens.menu.menu_screen import MenuScreen

if TYPE_CHECKING:
    from client.screens.core.scene_manager import SceneManager


class CreateLobbyScreen(MenuScreen):
    """
    Screen for creating a new game lobby. Allows the player to enter their name and choose a board size.
    Submitting the form sends a create-lobby request to the server via LobbyService.
    """

    def __init__(self, surface: pg.Surface, scene_manager: SceneManager) -> None:
        super().__init__(surface, scene_manager, title="Create Lobby")
        form = self.scene_manager.runtime_state.create_lobby
        center_x = self.content_rect.centerx
        self.name_input = TextInput(pg.Rect(center_x - 180, self.content_rect.y + 96, 360, 46), form.player_name, placeholder="Your name")
        sizes = tuple(sorted(VALID_BOARD_SIZES))
        insert_timeouts = tuple(sorted(VALID_INSERT_TIMEOUTS))
        move_timeouts = tuple(sorted(VALID_MOVE_TIMEOUTS))

        self.board_size_y = self.content_rect.y + 192

        self.size_buttons = []
        for index, size in enumerate(sizes):
            button = Button(
                pg.Rect(center_x - ((len(sizes) * 86 + (len(sizes) - 1) * 8) // 2) + index * 94, self.content_rect.y + 198, 86, 42),
                str(size),
                self._set_board_size_action(size),
                variant="primary" if form.board_size == size else "secondary",
            )
            self.size_buttons.append(button)
        self.private_button = Button(
            pg.Rect(center_x - 137, self.content_rect.y + 286, 128, 42),
            "Private",
            self._set_public_action(False),
            variant="primary" if not form.is_public else "secondary",
        )
        self.public_button = Button(
            pg.Rect(center_x + 9, self.content_rect.y + 286, 128, 42),
            "Public",
            self._set_public_action(True),
            variant="primary" if form.is_public else "secondary",
        )
        self.player_limit_buttons: list[Button] = []
        for index, limit in enumerate((2, 3, 4)):
            button = Button(
                pg.Rect(center_x - 137 + index * 94, self.content_rect.y + 372, 86, 42),
                str(limit),
                self._set_player_limit_action(limit),
                variant="primary" if form.player_limit == limit else "secondary",
            )
            self.player_limit_buttons.append(button)

        self.insert_timeout_buttons = []
        self.insert_timeout_y = self.size_buttons[-1].rect.bottom + 20
        for index, timeout in enumerate(insert_timeouts):
            button = Button(
                pg.Rect(center_x - (((len(insert_timeouts) + 1) * 86 + (len(insert_timeouts)) * 8) // 2) + index * 94, self.insert_timeout_y, 86, 42),
                str(timeout),
                self._set_board_size_action(timeout),
                variant="primary" if form.insert_timeout == timeout else "secondary",
            )
            self.insert_timeout_buttons.append(button)
        self.insert_timeout_buttons.append(Button(
            pg.Rect(center_x - (((len(insert_timeouts) + 1) * 86 + (len(insert_timeouts)) * 8) // 2) + len(insert_timeouts) * 94, self.insert_timeout_y, 86, 42),
            str("∞"),
            self._set_board_size_action(-1),
            variant="primary" if form.insert_timeout == -1 else "secondary",
        ))

        self.move_timeout_buttons = []
        # self.move_timeout_y = self.insert_timeout_buttons[-1] + 20
        for index, timeout in enumerate(move_timeouts):
            button = Button(
                pg.Rect(center_x - ((len(move_timeouts) * 86 + (len(move_timeouts) - 1) * 8) // 2) + index * 94,
                        self.insert_timeout_y, 86, 42),
                str(timeout),
                self._set_board_size_action(timeout),
                variant="primary" if form.insert_timeout == timeout else "secondary",
            )
            self.move_timeout_buttons.append(button)


        self.create_button = Button(
            pg.Rect(center_x - 100, self.content_rect.y + 430, 200, 48),
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

    def _set_public(self, is_public: bool) -> None:
        self.scene_manager.runtime_state.create_lobby.is_public = is_public
        self.private_button.variant = "secondary" if is_public else "primary"
        self.public_button.variant = "primary" if is_public else "secondary"

    def _set_public_action(self, is_public: bool) -> Callable[[], None]:
        def handle_click() -> None:
            self._set_public(is_public)

        return handle_click

    def _set_player_limit(self, player_limit: int) -> None:
        self.scene_manager.runtime_state.create_lobby.player_limit = player_limit
        for button in self.player_limit_buttons:
            button.variant = "primary" if button.label == str(player_limit) else "secondary"

    def _set_player_limit_action(self, player_limit: int) -> Callable[[], None]:
        def handle_click() -> None:
            self._set_player_limit(player_limit)

        return handle_click

    def _create_lobby(self) -> None:
        """Submit the form and request the server to create a new lobby with the entered name and selected board size."""
        error = self.scene_manager.lobby_service.create_lobby(
            self.name_input.text,
            self.scene_manager.runtime_state.create_lobby.board_size,
            is_public=self.scene_manager.runtime_state.create_lobby.is_public,
            player_limit=self.scene_manager.runtime_state.create_lobby.player_limit,
        )
        if error:
            self.error_message = language_service.get_message(error)

    def handle_content_event(self, event: pg.event.Event) -> None:
        """Handle input events for the form controls."""
        super().handle_content_event(event)
        self.name_input.handle_event(event)
        for button in self.size_buttons:
            button.handle_event(event)
        self.private_button.handle_event(event)
        self.public_button.handle_event(event)
        for button in self.player_limit_buttons:
            button.handle_event(event)
        self.create_button.handle_event(event)

    def draw_content(self, rect: pg.Rect) -> None:
        """Draw the form controls and any error messages."""
        super().draw_content(rect)
        self.name_input.draw(self.surface, self.small_font, self.body_font, "Player Name")
        board_label = self.body_font.render("Board Size", True, TEXT_PRIMARY)
        self.surface.blit(board_label, board_label.get_rect(center=(self.content_rect.centerx, self.content_rect.y + 174)))
        for button in self.size_buttons:
            button.draw(self.surface, self.button_font)
        type_label = self.body_font.render("Lobby Type", True, TEXT_PRIMARY)
        self.surface.blit(type_label, type_label.get_rect(center=(self.content_rect.centerx, self.content_rect.y + 262)))
        self.private_button.draw(self.surface, self.button_font)
        self.public_button.draw(self.surface, self.button_font)
        limit_label = self.body_font.render("Player Limit", True, TEXT_PRIMARY)
        self.surface.blit(limit_label, limit_label.get_rect(center=(self.content_rect.centerx, self.content_rect.y + 348)))
        for button in self.player_limit_buttons:
            button.draw(self.surface, self.button_font)
        self.create_button.draw(self.surface, self.button_font)
        if self.error_message:
            error = self.small_font.render(self.error_message, True, (150, 58, 48))
            self.surface.blit(error, error.get_rect(center=(self.content_rect.centerx, self.content_rect.y + 492)))
