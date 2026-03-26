# Author: Lenard Felix
 
from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from client.network.actions import request_leave_game, request_start_game
from client.ui.controls import Button
from client.ui.theme import PANEL, TEXT_MUTED, TEXT_PRIMARY
from client.screens.menu.menu_screen import MenuScreen

if TYPE_CHECKING:
    from client.screens.core.scene_manager import SceneManager


class LobbyScreen(MenuScreen):
    def __init__(self, surface: pg.Surface, scene_manager: SceneManager) -> None:
        super().__init__(surface, scene_manager, title="Lobby")
        self.start_button = Button(pg.Rect(self.content_rect.x, self.content_rect.bottom - 54, 160, 44), "Start Game", self._start_game, variant="primary")
        self.leave_button = Button(pg.Rect(self.content_rect.x + 182, self.content_rect.bottom - 54, 160, 44), "Leave Lobby", self._confirm_leave)

    def _start_game(self) -> None:
        request_start_game(self.scene_manager.connection, self.scene_manager.runtime_state)

    def _confirm_leave(self) -> None:
        self.show_confirm("Leave Lobby?", "Return to the main menu?", self._leave_lobby, confirm_label="Leave")

    def _leave_lobby(self) -> None:
        request_leave_game(self.scene_manager.connection, self.scene_manager.runtime_state, in_game=False)

    def handle_content_event(self, event: pg.event.Event) -> None:
        super().handle_content_event(event)
        self.start_button.enabled = self.scene_manager.display_state.can_viewer_start_lobby()
        self.start_button.handle_event(event)
        self.leave_button.handle_event(event)

    def draw_content(self, rect: pg.Rect) -> None:
        super().draw_content(rect)
        display = self.scene_manager.display_state
        if not display.is_lobby:
            return
        can_start = display.can_viewer_start_lobby()
        self.start_button.enabled = can_start
        code = self.section_font.render(f"Code: {display.code}", True, TEXT_PRIMARY)
        self.surface.blit(code, (self.content_rect.x, self.content_rect.y + 62))
        size = self.body_font.render(f"Board Size: {display.board_size}", True, TEXT_MUTED)
        self.surface.blit(size, (self.content_rect.x, self.content_rect.y + 98))

        for index, player in enumerate(display.players):
            row = pg.Rect(self.content_rect.x, self.content_rect.y + 146 + index * 58, self.content_rect.width, 46)
            fill = PANEL
            pg.draw.rect(self.surface, fill, row, border_radius=12)
            tags: list[str] = []
            if player["id"] == display.viewer_id:
                tags.append("You")
            if player["id"] == display.leader_id:
                tags.append("Leader")
            marker = " • ".join(tags)
            label = self.body_font.render(player["display_name"], True, TEXT_PRIMARY)
            status = self.small_font.render(marker, True, TEXT_MUTED) if marker else None
            self.surface.blit(label, (row.x + 16, row.y + 12))
            if status is not None:
                self.surface.blit(status, status.get_rect(midright=(row.right - 16, row.y + 23)))

        self.start_button.draw(self.surface, self.button_font)
        self.leave_button.draw(self.surface, self.button_font)
        if self.scene_manager.runtime_state.global_error_message:
            error = self.small_font.render(self.scene_manager.runtime_state.global_error_message, True, (150, 58, 48))
            self.surface.blit(error, (self.content_rect.x, self.content_rect.bottom - 88))
