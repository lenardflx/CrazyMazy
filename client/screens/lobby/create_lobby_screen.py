# Author: Lenard Felix, Raphael Eiden

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import pygame as pg

from client.lang import language_service
from client.state.runtime_state import ErrorPopupAnimation
from shared.lib.names import generate_display_name
from shared.lib.lobby import VALID_BOARD_SIZES, VALID_INSERT_TIMEOUTS, VALID_MOVE_TIMEOUTS
from client.ui.controls import Button, Slider, TextInput
from client.ui.theme import TEXT_PRIMARY, render_text
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
        stored_name = scene_manager.client_settings.get_name()
        option_width = 64
        option_height = 40
        option_gap = 8
        label_offset = 18
        name_y = self.content_rect.y + 84
        board_size_row_y = self.content_rect.y + 180
        settings_row_y = board_size_row_y + 78
        insert_timeout_row_y = settings_row_y + 88
        move_timeout_row_y = insert_timeout_row_y + 64
        type_group_center_x = center_x - 120
        limit_group_center_x = center_x + 120

        self.name_input = TextInput(
            pg.Rect(center_x - 170, name_y, 280, 46),
            form.player_name if stored_name == "" else stored_name,
            placeholder=PLACEHOLDER_NAME if stored_name == "" else stored_name,
        )
        self.random_name_button = Button(
            pg.Rect(self.name_input.rect.right + 10, self.name_input.rect.y, 54, 46),
            "",
            self._roll_name,
            icon="dice",
        )
        sizes = tuple(sorted(VALID_BOARD_SIZES))
        insert_timeouts = tuple(sorted(VALID_INSERT_TIMEOUTS))
        move_timeouts = tuple(sorted(VALID_MOVE_TIMEOUTS))
        self._insert_timeout_values = insert_timeouts + (None,)
        self._move_timeout_values = move_timeouts + (None,)
        self.size_buttons = self._build_option_buttons(
            center_x,
            board_size_row_y,
            [str(size) for size in sizes],
            option_width,
            option_height,
            option_gap,
            self._set_board_size_action,
            form.board_size,
        )
        self.private_button = Button(
            pg.Rect(type_group_center_x - 100, settings_row_y, 96, option_height),
            "Private",
            self._set_public_action(False),
            variant="primary" if not form.is_public else "secondary",
        )
        self.public_button = Button(
            pg.Rect(type_group_center_x + 4, settings_row_y, 96, option_height),
            "Public",
            self._set_public_action(True),
            variant="primary" if form.is_public else "secondary",
        )
        self.player_limit_buttons = self._build_option_buttons(
            limit_group_center_x,
            settings_row_y,
            ["2", "3", "4"],
            56,
            option_height,
            option_gap,
            self._set_player_limit_action,
            form.player_limit,
        )
        slider_width = 340
        self.insert_timeout_slider = Slider(
            pg.Rect(center_x - slider_width // 2, insert_timeout_row_y, slider_width, 14),
            "Insert Timeout",
            self._insert_timeout_index(form.insert_timeout),
            minimum=0,
            maximum=len(self._insert_timeout_values) - 1,
            value_formatter=lambda index: self._format_timeout(self._insert_timeout_values[index]),
            show_steps=True,
        )
        self.move_timeout_slider = Slider(
            pg.Rect(center_x - slider_width // 2, move_timeout_row_y, slider_width, 14),
            "Move Timeout",
            self._move_timeout_index(form.move_timeout),
            minimum=0,
            maximum=len(self._move_timeout_values) - 1,
            value_formatter=lambda index: self._format_timeout(self._move_timeout_values[index]),
            show_steps=True,
        )

        self._row_labels = [
            ("Board Size", center_x, board_size_row_y - label_offset),
            ("Lobby Type", type_group_center_x, settings_row_y - label_offset),
            ("Player Limit", limit_group_center_x, settings_row_y - label_offset),
        ]

        self.create_button = Button(
            pg.Rect(center_x - 92, move_timeout_row_y + 50, 184, 46),
            "Create Lobby",
            self._create_lobby,
            variant="primary",
        )

    def _build_option_buttons(
        self,
        center_x: int,
        y: int,
        labels: list[str],
        width: int,
        height: int,
        gap: int,
        action_factory: Callable[[int | str], Callable[[], None]],
        selected: int,
    ) -> list[Button]:
        buttons: list[Button] = []
        total_width = len(labels) * width + (len(labels) - 1) * gap
        start_x = center_x - total_width // 2
        for index, label in enumerate(labels):
            value = label if label == "∞" else int(label)
            buttons.append(
                Button(
                    pg.Rect(start_x + index * (width + gap), y, width, height),
                    label,
                    action_factory(value),
                    variant="primary" if selected == (-1 if label == "∞" else int(label)) else "secondary",
                )
            )
        return buttons

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

    def _insert_timeout_index(self, timeout: int) -> int:
        return self._insert_timeout_values.index(timeout)

    def _move_timeout_index(self, timeout: int) -> int:
        return self._move_timeout_values.index(timeout)

    def _format_timeout(self, timeout: int) -> str:
        return "Off" if timeout is None else f"{timeout} Sec"

    def _create_lobby(self) -> None:
        """Submit the form and request the server to create a new lobby with the entered name and selected board size."""
        form = self.scene_manager.runtime_state.create_lobby
        print(f"creating lobby with {form.insert_timeout}, {form.move_timeout}")
        error = self.scene_manager.lobby_service.create_lobby(
            self.name_input.text,
            form.board_size,
            is_public=form.is_public,
            player_limit=form.player_limit,
            insert_timeout=form.insert_timeout,
            move_timeout=form.move_timeout,
        )
        self.scene_manager.client_settings.set_name(self.name_input.text)
        self.scene_manager.client_settings.write_JSON()
        
        if error:
            self.set_error_message(error)

    def _roll_name(self) -> None:
        self.name_input.text = generate_display_name()
        self.name_input.active = False

    def handle_content_event(self, event: pg.event.Event) -> None:
        """Handle input events for the form controls."""
        super().handle_content_event(event)
        self.name_input.handle_event(event)
        self.random_name_button.handle_event(event)
        for button in self.size_buttons:
            button.handle_event(event)
        self.private_button.handle_event(event)
        self.public_button.handle_event(event)
        for button in self.player_limit_buttons:
            button.handle_event(event)
        if self.insert_timeout_slider.handle_event(event):
            self.scene_manager.runtime_state.create_lobby.insert_timeout = self._insert_timeout_values[self.insert_timeout_slider.value]
        if self.move_timeout_slider.handle_event(event):
            self.scene_manager.runtime_state.create_lobby.move_timeout = self._move_timeout_values[self.move_timeout_slider.value]
        self.create_button.handle_event(event)

    def update_content(self, dt: float) -> None:
        super().update_content(dt)
        self.name_input.update(dt)

    def draw_content(self, rect: pg.Rect) -> None:
        """Draw the form controls and any error messages."""
        super().draw_content(rect)
        self.name_input.draw(self.surface, self.small_font, self.body_font, "Player Name")
        self.random_name_button.draw(self.surface, self.button_font)
        for label, x, y in self._row_labels:
            rendered = render_text(self.body_font, label, TEXT_PRIMARY)
            self.surface.blit(rendered, rendered.get_rect(center=(x, y)))
        for button in self.size_buttons:
            button.draw(self.surface, self.button_font)
        self.private_button.draw(self.surface, self.button_font)
        self.public_button.draw(self.surface, self.button_font)
        for button in self.player_limit_buttons:
            button.draw(self.surface, self.button_font)
        self.insert_timeout_slider.draw(self.surface, self.small_font, self.small_font)
        self.move_timeout_slider.draw(self.surface, self.small_font, self.small_font)
        self.create_button.draw(self.surface, self.button_font)
