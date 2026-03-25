from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from client.network.actions import request_give_up, request_leave_game, request_move_player, request_shift_tile
from client.ui.controls import Button
from client.ui.dialogs import ConfirmDialog
from client.ui.game_views import board_layout, draw_board, draw_player_rows, draw_spare_tile_panel
from client.ui.theme import BACKGROUND, PANEL, TEXT_MUTED, TEXT_PRIMARY, font
from shared.models import TurnPhase
from client.screens.core.base_screen import BaseScreen
from client.screens.core.scene_types import SceneTypes

if TYPE_CHECKING:
    from client.screens.core.scene_manager import SceneManager


class GameScreen(BaseScreen):
    def __init__(self, surface: pg.Surface, scene_manager: SceneManager) -> None:
        super().__init__(surface)
        self.scene_manager = scene_manager
        self.title_font = font(28, bold=True)
        self.body_font = font(17)
        self.small_font = font(15)
        self.button_font = font(18, bold=True)
        self.dialog: ConfirmDialog | None = None
        self.requested_scene: SceneTypes | None = None
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

    def handle_event(self, event: pg.event.Event) -> BaseScreen | None:
        if self.dialog is not None:
            self.dialog.handle_event(event)
            if self.requested_scene is not None:
                next_screen = self.scene_manager.switch_scene(self.requested_scene, self.surface)
                self.requested_scene = None
                return next_screen
            if self.scene_manager.display_state.is_post_game:
                return self.scene_manager.switch_scene(SceneTypes.POST_GAME, self.surface)
            return None

        self.give_up_button.handle_event(event)
        self.menu_button.handle_event(event)
        display = self.scene_manager.display_state
        if not display.is_game or display.board is None or display.spare_tile is None:
            return self.scene_manager.switch_scene(SceneTypes.MAIN_MENU, self.surface)

        left_rect, right_rect = self._layout_sections()
        cells, arrows = board_layout(left_rect, display.board_size)[2:]
        viewer_turn = display.viewer_id == display.current_player_id
        shift_enabled = viewer_turn and display.turn_phase == TurnPhase.SHIFT
        move_enabled = viewer_turn and display.turn_phase == TurnPhase.MOVE

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            rotate_left, rotate_right = self._rotation_buttons(right_rect)
            if shift_enabled and rotate_left.collidepoint(event.pos):
                self.scene_manager.runtime_state.game.spare_rotation = (self.scene_manager.runtime_state.game.spare_rotation - 1) % 4
            if shift_enabled and rotate_right.collidepoint(event.pos):
                self.scene_manager.runtime_state.game.spare_rotation = (self.scene_manager.runtime_state.game.spare_rotation + 1) % 4
            for arrow in arrows:
                if shift_enabled and arrow.rect.collidepoint(event.pos):
                    if request_shift_tile(
                        self.scene_manager.connection,
                        self.scene_manager.runtime_state,
                        arrow.side,
                        arrow.index,
                        self.scene_manager.runtime_state.game.spare_rotation,
                    ):
                        self.scene_manager.runtime_state.game.spare_rotation = 0
            for position, cell in cells.items():
                if move_enabled and cell.collidepoint(event.pos):
                    request_move_player(self.scene_manager.connection, self.scene_manager.runtime_state, position[0], position[1])
        return None

    def update(self, dt: float) -> None:
        del dt

    def draw(self) -> None:
        self.surface.fill(BACKGROUND)
        display = self.scene_manager.display_state
        if not display.is_game or display.board is None or display.spare_tile is None:
            return
        spare_rotation = self.scene_manager.runtime_state.game.spare_rotation
        if spare_rotation:
            display.spare_tile.rotation = (display.spare_tile.rotation + spare_rotation) % 4
        left_rect, right_rect = self._layout_sections()
        viewer_turn = display.viewer_id == display.current_player_id
        shift_enabled = viewer_turn and display.turn_phase == TurnPhase.SHIFT
        draw_board(self.surface, left_rect, display, shift_enabled=shift_enabled)
        rotate_left, rotate_right = draw_spare_tile_panel(self.surface, pg.Rect(right_rect.x, right_rect.y, right_rect.width, 236), display)
        draw_player_rows(self.surface, pg.Rect(right_rect.x, right_rect.y + 254, right_rect.width, right_rect.height - 254), display.players, active_player_id=display.current_player_id)

        turn_text = self._turn_text(viewer_turn, display.turn_phase)
        status = self.title_font.render(turn_text, True, TEXT_PRIMARY)
        self.surface.blit(status, (24, 28))

        rotate_fill = PANEL if shift_enabled else (209, 201, 191)
        pg.draw.rect(self.surface, rotate_fill, rotate_left, border_radius=12)
        pg.draw.rect(self.surface, rotate_fill, rotate_right, border_radius=12)
        left_label = self.body_font.render("<", True, TEXT_PRIMARY if shift_enabled else TEXT_MUTED)
        right_label = self.body_font.render(">", True, TEXT_PRIMARY if shift_enabled else TEXT_MUTED)
        self.surface.blit(left_label, left_label.get_rect(center=rotate_left.center))
        self.surface.blit(right_label, right_label.get_rect(center=rotate_right.center))
        self.give_up_button.draw(self.surface, self.button_font)
        self.menu_button.draw(self.surface, self.button_font)
        if self.scene_manager.runtime_state.game.error_message:
            error = self.small_font.render(self.scene_manager.runtime_state.game.error_message, True, (150, 58, 48))
            self.surface.blit(error, (24, 60))
        if self.dialog is not None:
            self.dialog.draw(self.surface)
        if spare_rotation:
            display.spare_tile.rotation = (display.spare_tile.rotation - spare_rotation) % 4

    def _layout_sections(self) -> tuple[pg.Rect, pg.Rect]:
        left = pg.Rect(24, 96, 770, self.surface.get_height() - 120)
        right = pg.Rect(820, 96, self.surface.get_width() - 844, self.surface.get_height() - 120)
        return left, right

    def _rotation_buttons(self, right_rect: pg.Rect) -> tuple[pg.Rect, pg.Rect]:
        tile_rect = pg.Rect(right_rect.x + 18, right_rect.y + 52, 112, 112)
        return (
            pg.Rect(tile_rect.x, tile_rect.bottom + 16, 52, 40),
            pg.Rect(tile_rect.right - 52, tile_rect.bottom + 16, 52, 40),
        )

    # TODO: we probably also want to display a color or smth to make it easier to identify whose turn it is, or even a dialog/popup when the player's turn starts
    def _turn_text(self, viewer_turn: bool, turn_phase: TurnPhase) -> str:
        if viewer_turn and turn_phase == TurnPhase.SHIFT:
            return "Your turn: insert a tile"
        if viewer_turn and turn_phase == TurnPhase.MOVE:
            return "Your turn: move"
        return "Waiting for another player"
