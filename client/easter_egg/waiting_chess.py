from __future__ import annotations

from pathlib import Path

import pygame as pg

from .waiting_chess_game import WaitingChessGame
from client.lang import DisplayMessage, language_service
from client.ui.controls import Button
from client.ui.dialogs import BaseDialog
from client.ui.theme import TEXT_MUTED, blend_color, draw_pixel_rect, font, render_text

_BOARD_LIGHT = (222, 213, 198)
_BOARD_DARK = (147, 121, 94)
_BOARD_SELECTED = (208, 182, 88)
_BOARD_MOVE_HINT = (108, 156, 115)
_CHESS_ASSET_DIR = Path(__file__).resolve().parents[2] / "assets" / "chess"
_PIECE_CACHE: dict[tuple[str, int], pg.Surface] = {}

_PIECE_FILES = {
    "P": "Pawn",
    "N": "Knight",
    "B": "Bishop",
    "R": "Castle",
    "Q": "Queen",
    "K": "King",
}


def _piece_surface(piece: str, size: int) -> pg.Surface:
    """Return a cached, scaled surface for the given piece character and tile size. Uppercase = white, lowercase = black."""
    key = (piece, size)
    cached = _PIECE_CACHE.get(key)
    if cached is not None:
        return cached
    name = _PIECE_FILES[piece.upper()]
    variant = "1" if piece.isupper() else "2"
    path = _CHESS_ASSET_DIR / f"{name} ({variant}).png"
    surface = pg.transform.scale(pg.image.load(path.as_posix()).convert_alpha(), (size, size))
    _PIECE_CACHE[key] = surface
    return surface


class WaitingChessDialog(BaseDialog):
    """Modal chess dialog shown as an easter egg while the player waits in the lobby pregame phase."""

    WIDTH = 420

    def __init__(self, surface_rect: pg.Rect, on_close) -> None:
        rect = pg.Rect(surface_rect.centerx - self.WIDTH // 2, surface_rect.centery - 260, self.WIDTH, 520)
        super().__init__(
            surface_rect,
            language_service.get_message(DisplayMessage.EASTER_EGG_CHESS_TITLE),
            language_service.get_message(DisplayMessage.EASTER_EGG_CHESS_YOUR_MOVE),
            rect,
        )
        self.game = WaitingChessGame()
        self._board_rect = pg.Rect(self.rect.x + 50, self.rect.y + 120, 320, 320)

        footer_y = self.rect.bottom - 58
        self.reset_button = Button(
            pg.Rect(self.rect.x + 26, footer_y, 132, 40),
            language_service.get_message(DisplayMessage.EASTER_EGG_CHESS_RESET),
            self.game.reset,
        )
        self.close_button = Button(
            pg.Rect(self.rect.right - 158, footer_y, 132, 40),
            language_service.get_message(DisplayMessage.SETTINGS_CLOSE),
            on_close,
            variant="primary",
        )

    def update(self, dt: float) -> None:
        self.game.update(dt)
        self.message = self._status_text()

    def handle_event(self, event: pg.event.Event) -> bool:
        if self.handle_buttons(event, [self.reset_button, self.close_button]):
            return True
        if event.type != pg.MOUSEBUTTONUP or event.button != 1:
            return False
        square = self._square_at(event.pos)
        if square is None:
            return False
        self.game.click_square(square)
        return True

    def draw(self, surface: pg.Surface) -> None:
        self.draw_frame(surface)
        self.draw_text(surface, body_y=66)
        self._draw_board(surface)
        self.draw_buttons(surface, [self.reset_button, self.close_button])

    def _draw_board(self, surface: pg.Surface) -> None:
        """Render the 8x8 board with piece sprites, selection highlight, move hints, and axis labels."""
        tile_size = self._board_rect.width // 8
        legal_destinations = self.game.legal_destinations()

        for rank in range(8):
            for file in range(8):
                square = f"{chr(ord('a') + file)}{8 - rank}"
                tile = pg.Rect(
                    self._board_rect.x + file * tile_size,
                    self._board_rect.y + rank * tile_size,
                    tile_size,
                    tile_size,
                )
                color = _BOARD_LIGHT if (file + rank) % 2 == 0 else _BOARD_DARK
                if square == self.game.selected_square:
                    color = _BOARD_SELECTED
                elif square in legal_destinations:
                    color = _BOARD_MOVE_HINT
                draw_pixel_rect(surface, tile, color, border=blend_color(color, (0, 0, 0), 0.25))

                piece = self.game.piece_at(square)
                if piece != ".":
                    piece_surface = _piece_surface(piece, tile_size - 12)
                    surface.blit(piece_surface, piece_surface.get_rect(center=tile.center))

        axis_font = font(14)
        for file in range(8):
            label = render_text(axis_font, chr(ord("a") + file), TEXT_MUTED)
            surface.blit(label, label.get_rect(center=(self._board_rect.x + file * tile_size + tile_size // 2, self._board_rect.bottom + 12)))
        for rank in range(8):
            label = render_text(axis_font, str(8 - rank), TEXT_MUTED)
            surface.blit(label, label.get_rect(center=(self._board_rect.x - 12, self._board_rect.y + rank * tile_size + tile_size // 2)))

    def _status_text(self) -> str:
        """Return the localized status line shown below the dialog title."""
        if self.game.game_over:
            return language_service.get_message(DisplayMessage.EASTER_EGG_CHESS_GAME_OVER)
        if self.game.white_to_move:
            return language_service.get_message(DisplayMessage.EASTER_EGG_CHESS_YOUR_MOVE)
        return language_service.get_message(DisplayMessage.EASTER_EGG_CHESS_THINKING)

    def _square_at(self, pos: tuple[float, float]) -> str | None:
        """Convert a pixel position to an algebraic square name (e.g. 'e4'), or None if outside the board."""
        if not self._board_rect.collidepoint(pos):
            return None
        tile_size = self._board_rect.width // 8
        file = int((pos[0] - self._board_rect.x) // tile_size)
        rank = int((pos[1] - self._board_rect.y) // tile_size)
        if not (0 <= file < 8 and 0 <= rank < 8):
            return None
        return f"{chr(ord('a') + file)}{8 - rank}"
