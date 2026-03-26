from __future__ import annotations

from dataclasses import dataclass

import pygame as pg

from client.ui.game_board_view import BoardLayout, board_layout, spare_tile_panel_layout


@dataclass(slots=True, frozen=True)
class GameScreenLayout:
    board_panel: pg.Rect
    side_panel: pg.Rect
    spare_panel: pg.Rect
    players_panel: pg.Rect
    board: BoardLayout
    rotate_left_button: pg.Rect
    rotate_right_button: pg.Rect


def create_game_screen_layout(surface_rect: pg.Rect, board_size: int) -> GameScreenLayout:
    board_panel = pg.Rect(24, 96, 770, surface_rect.height - 120)
    side_panel = pg.Rect(820, 96, surface_rect.width - 844, surface_rect.height - 120)
    spare_panel = pg.Rect(side_panel.x, side_panel.y, side_panel.width, 236)
    players_panel = pg.Rect(side_panel.x, side_panel.y + 254, side_panel.width, side_panel.height - 254)

    board = board_layout(board_panel, board_size)
    spare_panel_buttons = spare_tile_panel_layout(spare_panel)

    return GameScreenLayout(
        board_panel=board_panel,
        side_panel=side_panel,
        spare_panel=spare_panel,
        players_panel=players_panel,
        board=board,
        rotate_left_button=spare_panel_buttons.left_button,
        rotate_right_button=spare_panel_buttons.right_button,
    )
