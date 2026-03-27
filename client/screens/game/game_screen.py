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


class GameScreen(BaseScreen):
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
        self.dialog = ConfirmDialog(
            self.surface.get_rect(),
            "Leave Match?",
            "Return to the main menu?",
            self._leave_to_menu,
            self._close_dialog,
            confirm_label="Leave",
        )

    def _confirm_give_up(self) -> None:
        self.dialog = ConfirmDialog(
            self.surface.get_rect(),
            "Give Up?",
            "Give up and spectate the rest of the match?",
            self._give_up,
            self._close_dialog,
            confirm_label="Give Up",
        )

    def _close_dialog(self) -> None:
        self.dialog = None

    def _leave_to_menu(self) -> None:
        self.scene_manager.game_service.leave_game(in_game=True)
        self.dialog = None

    def _give_up(self) -> None:
        self.scene_manager.game_service.give_up()
        self.dialog = None

    def handle_event(self, event: pg.event.Event) -> None:
        if self.dialog is not None:
            self.dialog.handle_event(event)
            return

        self.give_up_button.handle_event(event)
        self.menu_button.handle_event(event)

        runtime_game = self.scene_manager.runtime_state.game
        if runtime_game.shift_animation is not None or runtime_game.move_animation is not None:
            return

        game_state = self.scene_manager.game_state
        layout = self._game_layout(game_state)
        if game_state is None or layout is None or event.type != pg.MOUSEBUTTONDOWN or event.button != 1:
            return

        click = self.board_view.resolve_click(
            event.pos,
            layout,
            game_state,
        )
        self._handle_board_click(click)

    def update(self, dt: float) -> None:
        runtime_game = self.scene_manager.runtime_state.game
        shift_animation = runtime_game.shift_animation
        if shift_animation is not None:
            shift_animation.advance(dt)
            if shift_animation.is_finished:
                runtime_game.shift_animation = None

        move_animation = runtime_game.move_animation
        if move_animation is not None:
            move_animation.advance(dt)
            if move_animation.is_finished:
                runtime_game.move_animation = None

    def draw(self) -> None:
        self.surface.fill(BACKGROUND)
        game_state = self.scene_manager.game_state
        layout = self._game_layout(game_state)
        if game_state is None or layout is None:
            return

        spare_tile = game_state.rotated_spare_tile(self.scene_manager.runtime_state.game.spare_rotation)
        if spare_tile is None:
            return
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

        status = self.title_font.render(game_state.turn_prompt, True, TEXT_PRIMARY)
        self.surface.blit(status, (24, 28))
        self.give_up_button.draw(self.surface, self.button_font)
        self.menu_button.draw(self.surface, self.button_font)

        error_message = self.scene_manager.runtime_state.game.error_message
        if error_message:
            error = self.small_font.render(error_message, True, (150, 58, 48))
            self.surface.blit(error, (24, 60))
        if self.dialog is not None:
            self.dialog.draw(self.surface)

    def _game_layout(self, game_state: SnapshotGameState | None) -> GameBoardLayout | None:
        if game_state is None or game_state.phase != GamePhase.GAME or game_state.spare_tile is None:
            return None
        return self.board_view.layout(self.surface.get_rect(), game_state.board_size)

    def _rotate_spare(self, direction: int) -> None:
        game_state = self.scene_manager.runtime_state.game
        game_state.spare_rotation = (game_state.spare_rotation + direction) % 4

    def _handle_board_click(self, click: BoardClick | None) -> None:
        if click is None:
            return
        match click:
            case ("rotate", direction):
                self._rotate_spare(direction)
            case ("shift", side, index):
                if self.scene_manager.game_service.shift_tile(
                    side,
                    index,
                    self.scene_manager.runtime_state.game.spare_rotation,
                ):
                    self.scene_manager.runtime_state.game.spare_rotation = 0
            case ("move", x, y):
                self.scene_manager.game_service.move_player(x, y)
