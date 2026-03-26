# Author: Lenard Felix

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

import pygame as pg

from client.network.actions import request_give_up, request_leave_game, request_move_player, request_shift_tile
from client.screens.core.base_screen import BaseScreen
from client.screens.game.game_layout import GameScreenLayout, create_game_screen_layout
from client.ui.controls import Button
from client.ui.dialogs import ConfirmDialog
from client.ui.game_board_view import draw_board, draw_spare_tile_panel
from client.ui.player_rows_view import draw_player_rows
from client.ui.theme import BACKGROUND, TEXT_PRIMARY, font
from shared.models import TurnPhase

if TYPE_CHECKING:
    from client.state.display_state import ClientDisplayState, TileView
    from client.screens.core.scene_manager import SceneManager


class GameScreen(BaseScreen):
    def __init__(self, surface: pg.Surface, scene_manager: SceneManager) -> None:
        super().__init__(surface)
        self.scene_manager = scene_manager
        self.title_font = font(28, bold=True)
        self.small_font = font(15)
        self.button_font = font(18, bold=True)
        self.dialog: ConfirmDialog | None = None
        self.give_up_button = Button(pg.Rect(surface.get_width() - 280, 24, 120, 40), "Give Up", self._confirm_give_up)
        self.menu_button = Button(pg.Rect(surface.get_width() - 144, 24, 120, 40), "Menu", self._confirm_quit)

    def _confirm_quit(self) -> None:
        self.dialog = ConfirmDialog(self.surface.get_rect(), "Leave Match?", "Return to the main menu?", self._leave_to_menu, self._close_dialog, confirm_label="Leave")

    def _confirm_give_up(self) -> None:
        self.dialog = ConfirmDialog(self.surface.get_rect(), "Give Up?", "This ends your mocked run.", self._give_up, self._close_dialog, confirm_label="Give Up")

    def _close_dialog(self) -> None:
        self.dialog = None

    def _leave_to_menu(self) -> None:
        request_leave_game(self.scene_manager.connection, self.scene_manager.runtime_state, in_game=True)
        self.dialog = None

    def _give_up(self) -> None:
        request_give_up(self.scene_manager.connection, self.scene_manager.runtime_state)
        self.dialog = None

    def handle_event(self, event: pg.event.Event) -> None:
        if self.dialog is not None:
            self.dialog.handle_event(event)
            return

        self.give_up_button.handle_event(event)
        self.menu_button.handle_event(event)

        display = self.scene_manager.display_state
        layout = self._game_layout(display)
        if layout is None or event.type != pg.MOUSEBUTTONDOWN or event.button != 1:
            return

        if self._can_shift(display):
            if layout.rotate_left_button.collidepoint(event.pos):
                self._rotate_spare(-1)
                return
            if layout.rotate_right_button.collidepoint(event.pos):
                self._rotate_spare(1)
                return
            for arrow in layout.board.arrows:
                if not arrow.rect.collidepoint(event.pos):
                    continue
                if request_shift_tile(
                    self.scene_manager.connection,
                    self.scene_manager.runtime_state,
                    arrow.side,
                    arrow.index,
                    self.scene_manager.runtime_state.game.spare_rotation,
                ):
                    self.scene_manager.runtime_state.game.spare_rotation = 0
                return

        if self._can_move(display):
            for position, cell in layout.board.cells.items():
                if cell.collidepoint(event.pos):
                    request_move_player(self.scene_manager.connection, self.scene_manager.runtime_state, position[0], position[1])
                    return

    def update(self, dt: float) -> None:
        del dt

    def draw(self) -> None:
        self.surface.fill(BACKGROUND)
        display = self.scene_manager.display_state
        layout = self._game_layout(display)
        if layout is None:
            return

        viewer_turn = self._viewer_turn(display)
        shift_enabled = self._can_shift(display)
        draw_board(self.surface, layout.board, display.board, display.players, shift_enabled=shift_enabled)
        draw_spare_tile_panel(
            self.surface,
            layout.spare_panel,
            self._display_spare_tile(display),
            display.active_treasure_type,
            rotation_enabled=shift_enabled,
        )
        draw_player_rows(self.surface, layout.players_panel, display.players, active_player_id=display.current_player_id)

        status = self.title_font.render(self._turn_text(viewer_turn, display.turn_phase), True, TEXT_PRIMARY)
        self.surface.blit(status, (24, 28))
        self.give_up_button.draw(self.surface, self.button_font)
        self.menu_button.draw(self.surface, self.button_font)

        error_message = self.scene_manager.runtime_state.game.error_message
        if error_message:
            error = self.small_font.render(error_message, True, (150, 58, 48))
            self.surface.blit(error, (24, 60))
        if self.dialog is not None:
            self.dialog.draw(self.surface)

    def _game_layout(self, display: ClientDisplayState) -> GameScreenLayout | None:
        if not display.is_game or display.board is None or display.spare_tile is None:
            return None
        return create_game_screen_layout(self.surface.get_rect(), display.board_size)

    def _viewer_turn(self, display: ClientDisplayState) -> bool:
        return display.viewer_id == display.current_player_id

    def _can_shift(self, display: ClientDisplayState) -> bool:
        return self._viewer_turn(display) and display.turn_phase == TurnPhase.SHIFT

    def _can_move(self, display: ClientDisplayState) -> bool:
        return self._viewer_turn(display) and display.turn_phase == TurnPhase.MOVE

    def _rotate_spare(self, direction: int) -> None:
        game_state = self.scene_manager.runtime_state.game
        game_state.spare_rotation = (game_state.spare_rotation + direction) % 4

    def _display_spare_tile(self, display: ClientDisplayState) -> TileView:
        spare_rotation = self.scene_manager.runtime_state.game.spare_rotation
        return replace(display.spare_tile, rotation=(display.spare_tile.rotation + spare_rotation) % 4)

    # TODO: we probably also want to display a color or smth to make it easier to identify whose turn it is, or even a dialog/popup when the player's turn starts
    def _turn_text(self, viewer_turn: bool, turn_phase: TurnPhase) -> str:
        if viewer_turn and turn_phase == TurnPhase.SHIFT:
            return "Your turn: insert a tile"
        if viewer_turn and turn_phase == TurnPhase.MOVE:
            return "Your turn: move"
        return "Waiting for another player"
