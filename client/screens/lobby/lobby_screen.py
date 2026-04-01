# Author: Lenard Felix, Raphael Eiden
 
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
    """
    The lobby screen shown after joining or creating a game. Displays the join code, board size,
    and current player list. The lobby leader can start the game or add NPCs; all players can leave.
    """

    def __init__(self, surface: pg.Surface, scene_manager: SceneManager) -> None:
        super().__init__(surface, scene_manager, title="Lobby")
        self.player_panel_view = PlayerPanelView(self.content_rect, scene_manager.lobby_service)
        button_y = self.content_rect.bottom - 54
        self.start_button = Button(
            pg.Rect(self.content_rect.x, button_y, 160, 44),
            "Start Game",
            self._start_game,
            variant="primary",
            enabled=False,
        )
        self.add_npc_button = Button(
            pg.Rect(self.content_rect.x + 180, button_y, 140, 44),
            "Add NPC",
            self._add_npc,
            enabled=False,
        )
        self.leave_button = Button(pg.Rect(self.content_rect.x + 340, button_y, 160, 44), "Leave Lobby", self._confirm_leave)

    def _add_npc(self) -> None:
        """Open a choice dialog letting the leader pick an NPC difficulty to add to the lobby."""
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
        """Request the server to start the game. Only the lobby leader can do this."""
        self.scene_manager.game_service.start_game()

    def _confirm_leave(self) -> None:
        """Open a confirmation dialog before leaving the lobby."""
        self.show_confirm("Leave Lobby?", "Return to the main menu?", self._leave_lobby, confirm_label="Leave")

    def _leave_lobby(self) -> None:
        """Confirm action to leave the lobby and return to the main menu."""
        self.scene_manager.game_service.leave_game(in_game=False)

    def handle_content_event(self, event: pg.event.Event) -> None:
        """Handle events and update button enabled-state based on the current game state."""
        super().handle_content_event(event)
        game_state = self.scene_manager.game_state
        # The start and add-NPC buttons are only enabled when the server says we can take those actions.
        self.add_npc_button.enabled = game_state is not None and game_state.can_add_npc
        self.start_button.enabled = game_state is not None and game_state.can_start
        self.add_npc_button.handle_event(event)
        self.start_button.handle_event(event)
        self.leave_button.handle_event(event)

        # Trigger events for player-specific buttons such as KICK
        # self.player_panel_view.handle_button_click(event)
        self.player_panel_view.handle_player_panel_event(event)

    def draw_content(self, rect: pg.Rect) -> None:
        """Draw the lobby information, player list, and action buttons.
        The lobby information and player list are only shown if we have a valid game state from the server."""
        super().draw_content(rect)
        game_state = self.scene_manager.game_state
        if game_state is None or game_state.phase != GamePhase.PREGAME:
            return
        code = self.section_font.render(f"Code: {game_state.code}", True, TEXT_PRIMARY)
        self.surface.blit(code, (self.content_rect.x, self.content_rect.y + 62))
        size = self.body_font.render(f"Board Size: {game_state.board_size}", True, TEXT_MUTED)
        self.surface.blit(size, (self.content_rect.x, self.content_rect.y + 98))
        visibility = self.body_font.render(
            f"{'Public' if game_state.is_public else 'Private'} Lobby, {game_state.active_player_count}/{game_state.player_limit} Players",
            True,
            TEXT_MUTED,
        )
        self.surface.blit(visibility, (self.content_rect.x, self.content_rect.y + 122))
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
