# Author: Lenard Felix, Raphael Eiden
 
from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from client.easter_egg import WaitingChessDialog
from client.screens.game.views.player_panel_view import PlayerPanelView
from shared.types.enums import GamePhase, NpcDifficulty
from client.ui.controls import Button
from client.ui.theme import TEXT_MUTED, TEXT_PRIMARY
from client.screens.menu.menu_screen import MenuScreen
from client.lang import DisplayMessage, language_service

if TYPE_CHECKING:
    from client.screens.core.scene_manager import SceneManager

EASTER_EGG_WAITING_DELAY = 20.0

class LobbyScreen(MenuScreen):
    """
    The lobby screen shown after joining or creating a game. Displays the join code, board size,
    and current player list. The lobby leader can start the game or add NPCs; all players can leave.
    """

    def __init__(self, surface: pg.Surface, scene_manager: SceneManager) -> None:
        super().__init__(surface, scene_manager, title=language_service.get_message(DisplayMessage.LOBBY_WORD))
        self.player_panel_view = PlayerPanelView(self.content_rect, scene_manager.lobby_service)
        self._waiting_elapsed = 0.0
        self._waiting_prompt_shown = False
        if self.back_button is not None:
            self.back_button.on_click = self._confirm_leave
        button_y = self.content_rect.bottom - 54
        self.start_button = Button(
            pg.Rect(self.content_rect.x, button_y, 160, 44),
            language_service.get_message(DisplayMessage.GAME_START),
            self._start_game,
            variant="primary",
            enabled=False,
        )
        self.add_npc_button = Button(
            pg.Rect(self.content_rect.x + 180, button_y, 140, 44),
            language_service.get_message(DisplayMessage.GAME_ADD_NPC),
            self._add_npc,
            enabled=False,
        )
        self.leave_button = Button(pg.Rect(self.content_rect.x + 340, button_y, 160, 44), language_service.get_message(DisplayMessage.GAME_LEAVE_LOBBY), self._confirm_leave)

    def _sync_action_buttons(self) -> None:
        game_state = self.scene_manager.game_state
        self.add_npc_button.enabled = game_state is not None and game_state.can_add_npc
        self.start_button.enabled = game_state is not None and game_state.can_start

    def _add_npc(self) -> None:
        """Open a choice dialog letting the leader pick an NPC difficulty to add to the lobby."""
        self.show_choice(
            language_service.get_message(DisplayMessage.GAME_ADD_NPC),
            language_service.get_message(DisplayMessage.GAME_DIFFICULTY_CHOOSE),
            [
                (language_service.get_message(DisplayMessage.GAME_NPC_EASY), lambda: self.scene_manager.game_service.add_npc(NpcDifficulty.EASY), "secondary"),
                (language_service.get_message(DisplayMessage.GAME_NPC_MED), lambda: self.scene_manager.game_service.add_npc(NpcDifficulty.NORMAL), "secondary"),
                (language_service.get_message(DisplayMessage.GAME_NPC_HARD), lambda: self.scene_manager.game_service.add_npc(NpcDifficulty.HARD), "secondary"),
            ],
        )

    def _start_game(self) -> None:
        """Request the server to start the game. Only the lobby leader can do this."""
        self.scene_manager.game_service.start_game()

    def _confirm_leave(self) -> None:
        """Open a confirmation dialog before leaving the lobby."""
        self.show_confirm(language_service.get_message(DisplayMessage.GAME_LEAVE_LOBBY), language_service.get_message(DisplayMessage.TUTORIAL_TO_MENU), self._leave_lobby, confirm_label=language_service.get_message(DisplayMessage.GAME_LEAVE))

    def _open_waiting_game(self) -> None:
        self.dialog = WaitingChessDialog(self.surface.get_rect(), self._close_waiting_game)

    def _close_waiting_game(self) -> None:
        self.dialog = None

    def _leave_lobby(self) -> None:
        """Confirm action to leave the lobby and return to the main menu."""
        self.scene_manager.game_service.leave_game(in_game=False)

    def update_content(self, dt: float) -> None:
        self._sync_action_buttons()
        game_state = self.scene_manager.game_state
        if game_state is None or game_state.phase != GamePhase.PREGAME:
            self._waiting_elapsed = 0.0
            self._waiting_prompt_shown = False
            if isinstance(self.dialog, WaitingChessDialog):
                self.dialog = None
            return

        self._waiting_elapsed += dt
        if (
            self._waiting_elapsed >= EASTER_EGG_WAITING_DELAY
            and not self._waiting_prompt_shown
            and self.dialog is None
        ):
            self._waiting_prompt_shown = True
            self.show_confirm(
                language_service.get_message(DisplayMessage.EASTER_EGG_WAITING_TITLE),
                language_service.get_message(DisplayMessage.EASTER_EGG_WAITING_BODY),
                self._open_waiting_game,
                confirm_label=language_service.get_message(DisplayMessage.EASTER_EGG_WAITING_CONFIRM),
            )

        if isinstance(self.dialog, WaitingChessDialog):
            self.dialog.update(dt)

    def handle_content_event(self, event: pg.event.Event) -> None:
        """Handle events and update button enabled-state based on the current game state."""
        super().handle_content_event(event)
        self._sync_action_buttons()
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
        code = self.section_font.render(
            f"{language_service.get_message(DisplayMessage.GAME_CODE)}: {game_state.code}",
            True,
            TEXT_PRIMARY,
        )
        self.surface.blit(code, (self.content_rect.x, self.content_rect.y + 62))
        size = self.body_font.render(
            language_service.get_message(DisplayMessage.GAME_BOARD_SIZE) + str(game_state.board_size),
            True,
            TEXT_MUTED,
        )
        self.surface.blit(size, (self.content_rect.x, self.content_rect.y + 98))
        visibility = self.body_font.render(
            f"{language_service.get_message(DisplayMessage.LOBBY_PUBLIC) if game_state.is_public else language_service.get_message(DisplayMessage.LOBBY_PRIVATE)} {language_service.get_message(DisplayMessage.LOBBY_WORD)}, {game_state.active_player_count}/{game_state.player_limit} {language_service.get_message(DisplayMessage.GAME_PLAYERS)}",
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
