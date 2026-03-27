from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, cast

import pygame as pg

from client.textures import TILE_IMAGES, TREASURE_IMAGES
from client.ui.theme import DISABLED, MOVE_HIGHLIGHT, PANEL, PANEL_ALT, TEXT_PRIMARY, blend_color, font
from shared.models import InsertionSide, PlayerColor, TreasureType
from shared.state.game_state import SnapshotGameState, SnapshotPlayerState, Tile


PLAYER_COLOR_VALUES = {
    PlayerColor.RED: (210, 74, 74),
    PlayerColor.BLUE: (63, 109, 215),
    PlayerColor.GREEN: (80, 156, 93),
    PlayerColor.YELLOW: (209, 173, 59),
}

BoardClick = (
    tuple[Literal["rotate"], int]
    | tuple[Literal["shift"], InsertionSide, int]
    | tuple[Literal["move"], int, int]
    | None
)


@dataclass(slots=True, frozen=True)
class ArrowTarget:
    rect: pg.Rect
    side: InsertionSide
    index: int


@dataclass(slots=True, frozen=True)
class GameBoardLayout:
    board_rect: pg.Rect
    cell_size: int
    cells: dict[tuple[int, int], pg.Rect]
    arrows: list[ArrowTarget]
    spare_panel: pg.Rect
    spare_tile_rect: pg.Rect
    rotate_left_button: pg.Rect
    rotate_right_button: pg.Rect
    treasure_stack_rect: pg.Rect
    players_panel: pg.Rect


class BoardView:
    def __init__(self) -> None:
        self.title_font = font(18, bold=True)

    def layout(self, surface_rect: pg.Rect, board_size: int) -> GameBoardLayout:
        board_panel = pg.Rect(24, 96, 770, surface_rect.height - 120)
        side_panel = pg.Rect(820, 96, surface_rect.width - 844, surface_rect.height - 120)
        spare_panel = pg.Rect(side_panel.x, side_panel.y, side_panel.width, 236)
        players_panel = pg.Rect(side_panel.x, side_panel.y + 254, side_panel.width, side_panel.height - 254)

        cell_size = min((board_panel.width - 64) // board_size, (board_panel.height - 64) // board_size)
        board_rect = pg.Rect(board_panel.x + 32, board_panel.y + 32, cell_size * board_size, cell_size * board_size)
        spare_tile_rect = pg.Rect(spare_panel.x + 18, spare_panel.y + 52, 112, 112)

        cells = {
            (col, row): pg.Rect(
                board_rect.x + col * cell_size,
                board_rect.y + row * cell_size,
                cell_size - 4,
                cell_size - 4,
            )
            for row in range(board_size)
            for col in range(board_size)
        }
        arrows = self._build_arrows(board_rect, cell_size, board_size)

        return GameBoardLayout(
            board_rect=board_rect,
            cell_size=cell_size,
            cells=cells,
            arrows=arrows,
            spare_panel=spare_panel,
            spare_tile_rect=spare_tile_rect,
            rotate_left_button=pg.Rect(spare_tile_rect.x, spare_tile_rect.bottom + 16, 52, 40),
            rotate_right_button=pg.Rect(spare_tile_rect.right - 52, spare_tile_rect.bottom + 16, 52, 40),
            treasure_stack_rect=pg.Rect(spare_panel.right - 136, spare_panel.y + 52, 100, 140),
            players_panel=players_panel,
        )

    def draw(self, surface: pg.Surface, layout: GameBoardLayout, game_state: SnapshotGameState, spare_tile: Tile) -> None:
        self._draw_board(surface, layout, game_state)
        self._draw_spare_panel(surface, layout, spare_tile, game_state)

    def resolve_click(self, pos: tuple[int, int], layout: GameBoardLayout, game_state: SnapshotGameState) -> BoardClick:
        if game_state.can_shift:
            if layout.rotate_left_button.collidepoint(pos):
                return "rotate", -1
            if layout.rotate_right_button.collidepoint(pos):
                return "rotate", 1
            for arrow in layout.arrows:
                if arrow.rect.collidepoint(pos):
                    return "shift", arrow.side, arrow.index

        if game_state.can_move:
            for (x, y), cell in layout.cells.items():
                if cell.collidepoint(pos) and game_state.is_position_reachable((x, y)):
                    return "move", x, y
        return None

    def _build_arrows(self, board_rect: pg.Rect, cell_size: int, board_size: int) -> list[ArrowTarget]:
        arrows: list[ArrowTarget] = []
        for index in range(1, board_size, 2):
            center_x = board_rect.x + index * cell_size + cell_size // 2 - 16
            center_y = board_rect.y + index * cell_size + cell_size // 2 - 16
            arrows.extend(
                (
                    ArrowTarget(pg.Rect(center_x, board_rect.y - 38, 32, 32), InsertionSide.TOP, index),
                    ArrowTarget(pg.Rect(center_x, board_rect.bottom + 6, 32, 32), InsertionSide.BOTTOM, index),
                    ArrowTarget(pg.Rect(board_rect.x - 38, center_y, 32, 32), InsertionSide.LEFT, index),
                    ArrowTarget(pg.Rect(board_rect.right + 6, center_y, 32, 32), InsertionSide.RIGHT, index),
                )
            )
        return arrows

    def _draw_board(self, surface: pg.Surface, layout: GameBoardLayout, game_state: SnapshotGameState) -> None:
        pg.draw.rect(surface, PANEL_ALT, layout.board_rect.inflate(20, 20), border_radius=20)
        pg.draw.rect(surface, PANEL, layout.board_rect, border_radius=16)

        for position, rect in layout.cells.items():
            tile = game_state.tile_at(position)
            if tile is None:
                continue
            self._draw_tile(
                surface,
                rect,
                tile,
                home_color=game_state.home_color_at(position),
                highlight=game_state.is_position_reachable(position),
            )

        for player in game_state.ordered_players:
            if player.position is None:
                continue
            pg.draw.circle(surface, player_color(player), layout.cells[player.position].center, max(8, layout.cell_size // 7))

        for arrow in layout.arrows:
            self._draw_arrow(surface, arrow, enabled=game_state.can_shift)

    def _draw_spare_panel(
        self,
        surface: pg.Surface,
        layout: GameBoardLayout,
        tile: Tile,
        game_state: SnapshotGameState,
    ) -> None:
        pg.draw.rect(surface, PANEL, layout.spare_panel, border_radius=20)
        surface.blit(self.title_font.render("Current Tile", True, TEXT_PRIMARY), (layout.spare_panel.x + 18, layout.spare_panel.y + 16))

        self._draw_tile(surface, layout.spare_tile_rect, tile)

        button_fill = PANEL_ALT if game_state.can_shift else blend_color(PANEL_ALT, DISABLED, 0.7)
        button_text = TEXT_PRIMARY if game_state.can_shift else DISABLED
        for rect, label in ((layout.rotate_left_button, "<"), (layout.rotate_right_button, ">")):
            pg.draw.rect(surface, button_fill, rect, border_radius=12)
            surface.blit(self.title_font.render(label, True, button_text), self.title_font.render(label, True, button_text).get_rect(center=rect.center))

        for offset in range(3):
            pg.draw.rect(surface, (224, 218, 210), layout.treasure_stack_rect.move(offset * 6, -offset * 6), border_radius=8)
        treasure_surface = _treasure_surface(game_state.active_treasure_type, (76, 76))
        if treasure_surface is not None:
            surface.blit(treasure_surface, treasure_surface.get_rect(center=layout.treasure_stack_rect.center))

    def _draw_tile(
        self,
        surface: pg.Surface,
        rect: pg.Rect,
        tile: Tile,
        *,
        home_color: PlayerColor | None = None,
        highlight: bool = False,
    ) -> None:
        radius = max(6, min(14, min(rect.size) // 7))
        pg.draw.rect(surface, (77, 62, 48, 40), rect.move(0, 2), border_radius=radius)

        tile_image = pg.transform.scale(_tile_surface(tile), rect.size)
        clipped = pg.Surface(rect.size, pg.SRCALPHA)
        clipped.blit(tile_image, (0, 0))
        if highlight:
            highlight_surface = pg.Surface(rect.size, pg.SRCALPHA)
            highlight_surface.fill((*MOVE_HIGHLIGHT, 70))
            clipped.blit(highlight_surface, (0, 0))

        mask = pg.Surface(rect.size, pg.SRCALPHA)
        pg.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius)
        clipped.blit(mask, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
        surface.blit(clipped, rect)

        if home_color is not None:
            badge = pg.Rect(rect.x + 8, rect.bottom - 20, 12, 12)
            pg.draw.circle(surface, PLAYER_COLOR_VALUES[home_color], badge.center, 6)
            pg.draw.circle(surface, (247, 239, 224), badge.center, 6, 2)

        treasure_surface = _treasure_surface(tile.treasure, (22, 22))
        if treasure_surface is not None:
            surface.blit(treasure_surface, treasure_surface.get_rect(topright=(rect.right - 6, rect.y + 6)))

    def _draw_arrow(self, surface: pg.Surface, arrow: ArrowTarget, *, enabled: bool) -> None:
        fill = (214, 186, 144) if enabled else blend_color(PANEL_ALT, DISABLED, 0.7)
        pg.draw.rect(surface, blend_color(fill, (88, 72, 58), 0.35), arrow.rect.move(0, 2), border_radius=12)
        pg.draw.rect(surface, fill, arrow.rect, border_radius=12)

        cx, cy = arrow.rect.center
        color = (52, 41, 33) if enabled else (118, 112, 106)
        points = {
            InsertionSide.TOP: [(cx - 7, cy - 2), (cx + 7, cy - 2), (cx, cy + 7)],
            InsertionSide.BOTTOM: [(cx - 7, cy + 2), (cx + 7, cy + 2), (cx, cy - 7)],
            InsertionSide.LEFT: [(cx + 7, cy), (cx - 2, cy - 7), (cx - 2, cy + 7)],
            InsertionSide.RIGHT: [(cx - 7, cy), (cx + 2, cy - 7), (cx + 2, cy + 7)],
        }
        pg.draw.polygon(surface, color, points[arrow.side])


def player_color(player: SnapshotPlayerState) -> tuple[int, int, int]:
    return PLAYER_COLOR_VALUES[cast(PlayerColor, player.piece_color)]


def _tile_surface(tile: Tile) -> pg.Surface:
    return pg.transform.rotate(TILE_IMAGES[tile.type.value], (-90 * tile.orientation.value) % 360)


def _treasure_surface(treasure_type: str | TreasureType | None, size: tuple[int, int]) -> pg.Surface | None:
    if treasure_type is None:
        return None
    key = treasure_type.value if isinstance(treasure_type, TreasureType) else treasure_type
    return pg.transform.scale(TREASURE_IMAGES[key], size)
