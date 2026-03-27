# Author: Lenard Felix
 
from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from client.network.actions import request_leave_game, request_start_game
from client.ui.controls import Button
from client.ui.player_rows_view import draw_player_rows
from client.ui.theme import TEXT_MUTED
from client.screens.menu.menu_screen import MenuScreen
from shared.models import GamePhase

if TYPE_CHECKING:
    from client.screens.core.scene_manager import SceneManager


class PostGameScreen(MenuScreen):
    def __init__(self, surface: pg.Surface, scene_manager: SceneManager) -> None:
        super().__init__(surface, scene_manager, title="Post Game")
        self.menu_button = Button(pg.Rect(self.content_rect.x, self.content_rect.bottom - 54, 180, 44), "Main Menu", self._leave_post_game, variant="primary")
        self.play_again_button = Button(
            pg.Rect(self.content_rect.x + 202, self.content_rect.bottom - 54, 180, 44),
            "Play Again",
            self._play_again,
        )

    def _play_again(self) -> None:
        request_start_game(self.scene_manager.connection, self.scene_manager.runtime_state)

    def _leave_post_game(self) -> None:
        request_leave_game(self.scene_manager.connection, self.scene_manager.runtime_state, in_game=False)

    def handle_content_event(self, event: pg.event.Event) -> None:
        super().handle_content_event(event)
        self.menu_button.handle_event(event)
        self.play_again_button.handle_event(event)

    def draw_content(self, rect: pg.Rect) -> None:
        super().draw_content(rect)
        game_state = self.scene_manager.game_state
        if game_state is None or game_state.phase != GamePhase.POSTGAME:
            return
        subtitle = self.body_font.render("Placements", True, TEXT_MUTED)
        self.surface.blit(subtitle, (self.content_rect.x, self.content_rect.y + 54))
        draw_player_rows(self.surface, pg.Rect(self.content_rect.x, self.content_rect.y + 92, self.content_rect.width, 360), game_state.ordered_players, active_player_id=None, post_game=True)
        self.menu_button.draw(self.surface, self.button_font)
        self.play_again_button.draw(self.surface, self.button_font)
        if self.scene_manager.runtime_state.global_error_message:
            error = self.small_font.render(self.scene_manager.runtime_state.global_error_message, True, (150, 58, 48))
            self.surface.blit(error, (self.content_rect.x, self.content_rect.bottom - 88))
