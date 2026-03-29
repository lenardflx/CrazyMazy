# Author: Lenard Felix
 
from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from client.screens.game.views.player_panel_view import PlayerPanelView
from shared.types.enums import GamePhase, NpcDifficulty
from client.ui.controls import Button
from client.ui.theme import TEXT_MUTED, TEXT_PRIMARY
from client.screens.menu.menu_screen import MenuScreen

if TYPE_CHECKING:
    from client.screens.core.scene_manager import SceneManager


class LobbyScreen(MenuScreen):
    def __init__(self, surface: pg.Surface, scene_manager: SceneManager) -> None:
        super().__init__(surface, scene_manager, title="Lobby")
        self.player_panel_view = PlayerPanelView()
        button_y = self.content_rect.bottom - 54
        self.start_button = Button(pg.Rect(self.content_rect.x, button_y, 160, 44), "Start Game", self._start_game, variant="primary")
        self.add_npc_button = Button(pg.Rect(self.content_rect.x + 180, button_y, 140, 44), "Add NPC", self._add_npc)
        self.leave_button = Button(pg.Rect(self.content_rect.x + 340, button_y, 160, 44), "Leave Lobby", self._confirm_leave)

    def _add_npc(self) -> None:
        self.show_choice(
            "Add NPC",
            "Choose the difficulty for the new NPC.",
            [
                ("Easy NPC", lambda: self.scene_manager.game_service.add_npc(NpcDifficulty.EASY), "secondary"),
                ("Normal NPC", lambda: self.scene_manager.game_service.add_npc(NpcDifficulty.NORMAL), "secondary"),
                ("Hard NPC", lambda: self.scene_manager.game_service.add_npc(NpcDifficulty.HARD), "secondary"),
            ],
        )

    def _start_game(self) -> None:
        self.scene_manager.game_service.start_game()

    def _confirm_leave(self) -> None:
        self.show_confirm("Leave Lobby?", "Return to the main menu?", self._leave_lobby, confirm_label="Leave")

    def _leave_lobby(self) -> None:
        self.scene_manager.game_service.leave_game(in_game=False)

    def handle_content_event(self, event: pg.event.Event) -> None:
        super().handle_content_event(event)
        game_state = self.scene_manager.game_state
        self.add_npc_button.enabled = game_state is not None and game_state.can_add_npc
        self.start_button.enabled = game_state is not None and game_state.can_start
        self.add_npc_button.handle_event(event)
        self.start_button.handle_event(event)
        self.leave_button.handle_event(event)

    def draw_content(self, rect: pg.Rect) -> None:
        super().draw_content(rect)
        game_state = self.scene_manager.game_state
        if game_state is None or game_state.phase != GamePhase.PREGAME:
            return
        code = self.section_font.render(f"Code: {game_state.code}", True, TEXT_PRIMARY)
        self.surface.blit(code, (self.content_rect.x, self.content_rect.y + 62))
        size = self.body_font.render(f"Board Size: {game_state.board_size}", True, TEXT_MUTED)
        self.surface.blit(size, (self.content_rect.x, self.content_rect.y + 98))
        self.player_panel_view.draw(
            self.surface,
            pg.Rect(self.content_rect.x, self.content_rect.y + 146, self.content_rect.width, 288),
            game_state,
        )

        self.add_npc_button.draw(self.surface, self.button_font)
        self.start_button.draw(self.surface, self.button_font)
        self.leave_button.draw(self.surface, self.button_font)
        if self.error_message:
            error = self.small_font.render(self.error_message, True, (150, 58, 48))
            self.surface.blit(error, (self.content_rect.x, self.content_rect.bottom - 88))
