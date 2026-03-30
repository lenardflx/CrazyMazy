# Author: Lenard Felix
 
from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from client.screens.game.views.player_panel_view import PlayerPanelView
from client.ui.controls import Button
from client.ui.theme import TEXT_MUTED
from client.screens.menu.menu_screen import MenuScreen
from shared.types.enums import GamePhase, PlayerResult

if TYPE_CHECKING:
    from client.screens.core.scene_manager import SceneManager


class PostGameScreen(MenuScreen):
    """
    The screen shown after a game has ended, showing the results and allowing the player to return to the main menu or start a new game.
    """

    def __init__(self, surface: pg.Surface, scene_manager: SceneManager) -> None:
        super().__init__(surface, scene_manager, title="Game Over")
        self.player_panel_view = PlayerPanelView()
        self.menu_button = Button(pg.Rect(self.content_rect.x, self.content_rect.bottom - 54, 180, 44), "Main Menu", self._leave_post_game, variant="primary")
        self.play_again_button = Button(
            pg.Rect(self.content_rect.x + 202, self.content_rect.bottom - 54, 180, 44),
            "Play Again",
            self._play_again,
        )

    def _play_again(self) -> None:
        """Start a new game with the same settings as the previous game."""
        # TODO: check how the service handles this. I think the ideal approach for future would be to return to a new lobby and insert all players into the new lobby. 
        # Also if the leader gives up, he cannot start a new game rn. Should he stay leader until leaving the lobby?
        self.scene_manager.game_service.start_game()

    def _leave_post_game(self) -> None:
        """Leave the post game screen and return to the main menu."""
        self.scene_manager.game_service.leave_game(in_game=False)

    def handle_content_event(self, event: pg.event.Event) -> None:
        """Handle events for the post game screen."""
        super().handle_content_event(event)
        self.menu_button.handle_event(event)
        self.play_again_button.handle_event(event)

    def draw_content(self, rect: pg.Rect) -> None:
        """Draw the post game screen content, including the results and buttons."""

        # If the game state is not in the post game phase, just draw the default.
        game_state = self.scene_manager.game_state
        if game_state is None or game_state.phase != GamePhase.POSTGAME:
            super().draw_content(rect)
            return
        
        # If the player has won or is placed, show that in the title. Otherwise just show "Game Over".
        self.title = self._result_title()
        super().draw_content(rect)

        # Draw the player panels for all players, showing their results and stats.
        self.player_panel_view.draw(
            self.surface,
            pg.Rect(self.content_rect.x, self.content_rect.y + 72, self.content_rect.width, 380),
            game_state,
            post_game=True,
        )

        # Draw the buttons to return to the main menu or start a new game.
        self.menu_button.draw(self.surface, self.button_font)
        self.play_again_button.draw(self.surface, self.button_font)
        if self.scene_manager.runtime_state.global_error_message:
            error = self.small_font.render(self.scene_manager.runtime_state.global_error_message, True, (150, 58, 48))
            self.surface.blit(error, (self.content_rect.x, self.content_rect.bottom - 88))

    def _result_title(self) -> str:
        """Determine the title to display based on the player's result in the game."""
        game_state = self.scene_manager.game_state
        if game_state is None:
            return "Game Over"
        viewer = game_state.viewer_player
        if viewer is None:
            return "Game Over"
        if viewer.result == PlayerResult.WON:
            return "You Win"
        if viewer.placement is not None:
            return f"You Placed {viewer.placement}"
        return "Game Over"
