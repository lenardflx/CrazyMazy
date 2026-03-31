# Author: Lenard Felix

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import pygame as pg

from client.screens.core.base_screen import BaseScreen
from client.screens.game.views.board_view import BoardClick, BoardView, GameBoardLayout
from client.screens.game.views.player_panel_view import PlayerPanelView
from client.state.runtime_state import GameRuntimeState, TreasureCollectAnimation
from client.textures import UI_IMAGES
from client.ui.controls import Button
from client.ui.dialogs import ConfirmDialog
from client.ui.helper import format_ms_to_clock
from client.ui.theme import BACKGROUND, TEXT_PRIMARY, font, draw_pixel_rect, PANEL, ACCENT_DARK, PANEL_SHADOW, PANEL_ALT
from shared.types.enums import GamePhase, TurnPhase
from shared.game.snapshot import SnapshotGameState

if TYPE_CHECKING:
    from client.screens.core.scene_manager import SceneManager


class GameScreen(BaseScreen):
    """
    The GameScreen is responsible for displaying the game board and player panels, and handling user interactions during the game.
    It also manages the give up and quit buttons, which allow the player to leave the game or give up and spectate the rest of the match.
    """

    def __init__(self, surface: pg.Surface, scene_manager: SceneManager) -> None:
        super().__init__(surface)
        self.scene_manager = scene_manager
        self.board_view = BoardView()
        self.player_panel_view = PlayerPanelView(None, scene_manager.lobby_service)
        self.title_font = font(28)
        self.small_font = font(15)
        self.button_font = font(18)
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

    @property
    def _game_runtime(self) -> GameRuntimeState:
        return self.scene_manager.runtime_state.game

    @property
    def _game_snapshot(self) -> SnapshotGameState | None:
        return self.scene_manager.game_state

    def handle_event(self, event: pg.event.Event) -> None:
        """Handle a Pygame event. This covers all actions on the screen. It passes the events to the different UI elements."""

        # If a dialog is open, pass the event to the dialog and return early to prevent interactions with the game screen behind the dialog.
        if self.dialog is not None:
            self.dialog.handle_event(event)
            return

        # Top right buttons for giving up and quitting the match
        if self.give_up_button is not None:
            self.give_up_button.handle_event(event)
        self.menu_button.handle_event(event)

        # If there is an ongoing animation, ignore board clicks to prevent interactions during the animation.
        runtime_game = self._game_runtime
        if runtime_game.shift_animation is not None or runtime_game.move_animation is not None:
            return

        # Resolve the game layout based on the current game state. If we cant resolve a layout, we cant resolve board clicks, so return early.
        game_state = self._game_snapshot
        layout = self._game_layout()
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
        runtime_game = self._game_runtime
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
                if move_animation.collected_treasure_type is not None:
                    # TODO: play treasure collect SFX when the card flip animation starts.
                    runtime_game.treasure_collect_animation = TreasureCollectAnimation(
                        player_id=move_animation.player_id,
                        treasure_type=move_animation.collected_treasure_type,
                    )
                runtime_game.move_animation = None

        # Treasure collect animation
        treasure_animation = runtime_game.treasure_collect_animation
        if treasure_animation is not None:
            treasure_animation.advance(dt)
            if treasure_animation.is_finished:
                runtime_game.treasure_collect_animation = None

    def draw(self) -> None:
        """Draw the game screen."""

        # Fill the background
        #self.surface.fill(BACKGROUND)
        scaled = pg.transform.scale(UI_IMAGES["SPACE_BACKGROUND"], self.surface.get_size())
        self.surface.blit(scaled, (0, 0))

        # Resolve the game layout based on the current game state
        game_state = self._game_snapshot
        layout = self._game_layout()
        if game_state is None or layout is None:
            return

        # Resolve the spare tile
        runtime = self._game_runtime
        spare_tile = game_state.rotated_spare_tile(runtime.spare_rotation)
        if spare_tile is None:
            return

        # Draw the Board and the Panel
        self.board_view.draw(
            self.surface,
            layout,
            game_state,
            spare_tile,
            runtime.shift_animation,
            runtime.move_animation,
        )
        self.player_panel_view.draw(
            self.surface,
            layout.players_panel,
            game_state,
            treasure_animation=runtime.treasure_collect_animation,
            pending_collect=(
                None
                if runtime.move_animation is None or runtime.move_animation.collected_treasure_type is None
                else (runtime.move_animation.player_id, runtime.move_animation.collected_treasure_type)
            ),
        )

        # Render a status text about the current turn.
        self._draw_turn_indicator()

        if self.give_up_button is not None:
            self.give_up_button.draw(self.surface, self.button_font)
        self.menu_button.draw(self.surface, self.button_font)

        self._draw_overlay(layout)

        # Render the dialog on top, if one is active
        if self.dialog is not None:
            self.dialog.draw(self.surface)

    def _draw_turn_indicator(self):
        rect = pg.Rect(21.0, 19.0, 600, 65)
        draw_pixel_rect(surface=self.surface, rect=rect, fill=PANEL, shadow=PANEL_SHADOW, border=ACCENT_DARK)

        # make sure we don't exceed the maximum length reserved for the
        # turn status text. This does not happen normally, but we cannot
        # be sure due to variable language.
        turn_text = self._game_snapshot.turn_prompt[:30]
        if len(self._game_snapshot.turn_prompt) >= 30:
            turn_text += "..."

        status = self.title_font.render(turn_text, True, TEXT_PRIMARY)
        self.surface.blit(status, (rect.left + 10, rect.top + 8))

        turn_end = self._game_snapshot.turn.turn_end_timestamp
        if turn_end is None:
            return

        timer_rect = pg.Rect(rect.right - 145, rect.top + 8, 130, 50)
        draw_pixel_rect(surface=self.surface, rect=timer_rect, fill=PANEL_ALT, border=PANEL_SHADOW)

        now = time.time_ns() // 1_000_000

        if now > turn_end:
            timer_content = "00:00"
        else:
            timer_content = format_ms_to_clock(turn_end - now)

        timer_text = self.title_font.render(timer_content, True, TEXT_PRIMARY)
        self.surface.blit(timer_text, (timer_rect.left + 25, timer_rect.top + 7))


    def _draw_overlay(self, layout: GameBoardLayout) -> None:
        """Hook for subclasses to draw additional overlays on top of the board."""
        pass

    def _game_layout(self) -> GameBoardLayout | None:
        """
        Resolve the game board layout based on the current game state.
        If the game state is not in the correct phase or the spare tile is not available, return None to indicate that we cant resolve a layout.
        """
        game_state = self._game_snapshot
        if game_state is None or game_state.phase != GamePhase.GAME or game_state.spare_tile is None:
            return None
        return self.board_view.layout(self.surface.get_rect(), game_state.board_size)

    def _rotate_spare(self, direction: int) -> None:
        """
        Rotate the spare tile in the given direction. The direction is an integer where 1 represents a clockwise rotation and -1 represents a counterclockwise rotation.
        The rotation is applied to the spare tile in the game state, and the new rotation is stored in the runtime state to be applied when the player performs a shift action.
        We do not send this to the server since it only cares about the final rotation when the player performs a shift action, and this allows the player to preview the rotation before applying it.
        """

        self._game_runtime.spare_rotation = (self._game_runtime.spare_rotation + direction) % 4

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
                    self._game_runtime.spare_rotation,
                ):
                    # If shift action was successful, reset the spare tile rotation in the runtime state to 0
                    self._game_runtime.spare_rotation = 0
            # If the click is a move click, perform a move action to the given x and y coordinates.
            case ("move", x, y):
                self.scene_manager.game_service.move_player(x, y)
