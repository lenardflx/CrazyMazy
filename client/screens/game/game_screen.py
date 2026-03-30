# Author: Lenard Felix

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from client.screens.core.base_screen import BaseScreen
from client.screens.game.views.board_view import BoardClick, BoardView, GameBoardLayout
from client.screens.game.views.player_panel_view import PlayerPanelView
from client.ui.controls import Button
from client.ui.dialogs import ConfirmDialog
from client.ui.theme import BACKGROUND, TEXT_PRIMARY, font
from shared.types.enums import GamePhase
from shared.game.snapshot import SnapshotGameState

if TYPE_CHECKING:
    from client.screens.core.scene_manager import SceneManager

#Die eigentliche Spielansicht
class GameScreen(BaseScreen):
    """
    The GameScreen is responsible for displaying the game board and player panels, and handling user interactions during the game.
    It also manages the give up and quit buttons, which allow the player to leave the game or give up and spectate the rest of the match.
    """

    def __init__(self, surface: pg.Surface, scene_manager: SceneManager) -> None:
        super().__init__(surface)
        self.scene_manager = scene_manager
        self.board_view = BoardView()
        self.player_panel_view = PlayerPanelView()
        self.title_font = font(28, bold=True)
        self.small_font = font(15)
        self.button_font = font(18, bold=True)
        self.dialog: ConfirmDialog | None = None
        self.give_up_button = Button(pg.Rect(surface.get_width() - 280, 24, 120, 40), "Give Up", self._confirm_give_up)
        self.menu_button = Button(pg.Rect(surface.get_width() - 144, 24, 120, 40), "Menu", self._confirm_quit)

    def _confirm_quit(self) -> None:
        """Open a confirmation dialog to confirm if the player really wants to leave the match and return to the main menu."""
        self.dialog = ConfirmDialog(
            self.surface.get_rect(),
            "Leave Match?",
            "Return to the main menu?",
            self._leave_to_menu,
            self._close_dialog,
            confirm_label="Leave",
        )

    def _confirm_give_up(self) -> None:
        """Open a confirmation dialog to confirm if the player really wants to give up and spectate the rest of the match."""
        self.dialog = ConfirmDialog(
            self.surface.get_rect(),
            "Give Up?",
            "Give up and spectate the rest of the match?",
            self._give_up,
            self._close_dialog,
            confirm_label="Give Up",
        )

    def _close_dialog(self) -> None:
        """Close the currently open dialog. This applies to both the give up and quit confirmation dialogs."""
        self.dialog = None

    def _leave_to_menu(self) -> None:
        """Confirm action to leave the match and return to the main menu. This is triggered by the quit confirmation dialog."""
        self.scene_manager.game_service.leave_game(in_game=True)
        self.dialog = None

    def _give_up(self) -> None:
        """Confirm action to give up and spectate the rest of the match. This is triggered by the give up confirmation dialog."""
        self.scene_manager.game_service.give_up()
        self.dialog = None

    def handle_event(self, event: pg.event.Event) -> None:
        """Handle a Pygame event. This covers all actions on the screen. It passes the events to the different UI elements."""

        # If a dialog is open, pass the event to the dialog and return early to prevent interactions with the game screen behind the dialog.
        if self.dialog is not None:
            self.dialog.handle_event(event)
            return

        # Top right buttons for giving up and quitting the match
        self.give_up_button.handle_event(event)
        self.menu_button.handle_event(event)

        # If there is an ongoing animation, ignore board clicks to prevent interactions during the animation.
        runtime_game = self.scene_manager.runtime_state.game
        if runtime_game.shift_animation is not None or runtime_game.move_animation is not None:
            return

        # Resolve the game layout based on the current game state. If we cant resolve a layout, we cant resolve board clicks, so return early.
        game_state = self.scene_manager.game_state
        layout = self._game_layout(game_state)
        if game_state is None or layout is None or event.type != pg.MOUSEBUTTONDOWN or event.button != 1:
            return

        # Resolve the board click based on the mouse position and the current game state, and handle the click accordingly
        click = self.board_view.resolve_click(
            event.pos,
            layout,
            game_state,
        )
        self._handle_board_click(click)

    def update(self, dt: float) -> None:
        """
        Update the game screen animations.
        This is responsible for advancing the shift and move animations,
        and clearing them when they are finished.
        """

        # Shift animation
        runtime_game = self.scene_manager.runtime_state.game
        shift_animation = runtime_game.shift_animation
        if shift_animation is not None:
            shift_animation.advance(dt)
            if shift_animation.is_finished:
                runtime_game.shift_animation = None

        # Move animation
        move_animation = runtime_game.move_animation
        if move_animation is not None:
            move_animation.advance(dt)
            if move_animation.is_finished:
                runtime_game.move_animation = None

    def draw(self) -> None:
        """Draw the game screen."""

        # Fill the background
        self.surface.fill(BACKGROUND)

        # Resolve the game layout based on the current game state
        game_state = self.scene_manager.game_state
        layout = self._game_layout(game_state)
        if game_state is None or layout is None:
            return

        # Resolve the spare tile
        spare_tile = game_state.rotated_spare_tile(self.scene_manager.runtime_state.game.spare_rotation)
        if spare_tile is None:
            return
        
        # Draw the Board and the Panel
        self.board_view.draw(
            self.surface,
            layout,
            game_state,
            spare_tile,
            self.scene_manager.runtime_state.game.shift_animation,
            self.scene_manager.runtime_state.game.move_animation,
        )
        self.player_panel_view.draw(
            self.surface,
            layout.players_panel,
            game_state,
        )

        # Render a status text about the current turn.
        status = self.title_font.render(game_state.turn_prompt, True, TEXT_PRIMARY)
        self.surface.blit(status, (24, 28))
        self.give_up_button.draw(self.surface, self.button_font)
        self.menu_button.draw(self.surface, self.button_font)

        # Render a error message if any
        error_message = self.scene_manager.runtime_state.game.error_message
        if error_message:
            error = self.small_font.render(error_message, True, (150, 58, 48))
            self.surface.blit(error, (24, 60))

        # Render the dialog on top, if one is active
        if self.dialog is not None:
            self.dialog.draw(self.surface)

    def _game_layout(self, game_state: SnapshotGameState | None) -> GameBoardLayout | None:
        """
        Resolve the game board layout based on the current game state.
        If the game state is not in the correct phase or the spare tile is not available, return None to indicate that we cant resolve a layout.
        """
        if game_state is None or game_state.phase != GamePhase.GAME or game_state.spare_tile is None:
            return None
        return self.board_view.layout(self.surface.get_rect(), game_state.board_size)

    def _rotate_spare(self, direction: int) -> None:
        """
        Rotate the spare tile in the given direction. The direction is an integer where 1 represents a clockwise rotation and -1 represents a counterclockwise rotation.
        The rotation is applied to the spare tile in the game state, and the new rotation is stored in the runtime state to be applied when the player performs a shift action.
        We do not send this to the server since it only cares about the final rotation when the player performs a shift action, and this allows the player to preview the rotation before applying it.
        """

        game_state = self.scene_manager.runtime_state.game
        game_state.spare_rotation = (game_state.spare_rotation + direction) % 4

    def _handle_board_click(self, click: BoardClick | None) -> None:
        """Handle a click on the game board."""

        # If the click is None, it means that the click was not on a valid board element, so we can ignore it and return early.
        if click is None:
            return
        
        # Handle the click based on its type.
        match click:
            # If the click is a rotate click, rotate the spare tile in the given direction.
            case ("rotate", direction):
                self._rotate_spare(direction)
            # If the click is a shift click, perform a shift action on the game board with the given side and index.
            case ("shift", side, index):
                if self.scene_manager.game_service.shift_tile(
                    side,
                    index,
                    self.scene_manager.runtime_state.game.spare_rotation,
                ):
                    # If shift action was successful, reset the spare tile rotation in the runtime state to 0
                    self.scene_manager.runtime_state.game.spare_rotation = 0
            # If the click is a move click, perform a move action to the given x and y coordinates.
            case ("move", x, y):
                self.scene_manager.game_service.move_player(x, y)
