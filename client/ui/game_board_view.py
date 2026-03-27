from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import cast

import pygame as pg

from client.textures import TILE_IMAGES, TREASURE_IMAGES
from client.state.display_state import PLAYER_COLOR_VALUES, TileView
from client.ui.theme import DISABLED, PANEL, PANEL_ALT, TEXT_PRIMARY, blend_color, font
from shared.models import InsertionSide, PlayerColor, TileType, TreasureType
from shared.schema import PositionPayload, PublicPlayerPayload

MOVE_HIGHLIGHT = (240, 207, 112)


@dataclass(slots=True, frozen=True)
class ArrowSpec:
    rect: pg.Rect
    side: InsertionSide
    index: int


@dataclass(slots=True, frozen=True)
class BoardLayout:
    board_rect: pg.Rect
    cell_size: int
    cells: dict[tuple[int, int], pg.Rect]
    arrows: list[ArrowSpec]


@dataclass(slots=True, frozen=True)
class SpareTilePanelLayout:
    tile_rect: pg.Rect
    left_button: pg.Rect
    right_button: pg.Rect
    stack_rect: pg.Rect


def board_layout(rect: pg.Rect, board_size: int) -> BoardLayout:
    cell_size = min((rect.width - 64) // board_size, (rect.height - 64) // board_size)
    board_rect = pg.Rect(rect.x + 32, rect.y + 32, cell_size * board_size, cell_size * board_size)

    cells: dict[tuple[int, int], pg.Rect] = {}
    for row in range(board_size):
        for col in range(board_size):
            cells[(col, row)] = pg.Rect(board_rect.x + col * cell_size, board_rect.y + row * cell_size, cell_size - 4, cell_size - 4)

    arrows: list[ArrowSpec] = []
    for index in range(1, board_size, 2):
        top_x = board_rect.x + index * cell_size + cell_size // 2 - 16
        left_y = board_rect.y + index * cell_size + cell_size // 2 - 16
        arrows.append(ArrowSpec(pg.Rect(top_x, board_rect.y - 38, 32, 32), InsertionSide.TOP, index))
        arrows.append(ArrowSpec(pg.Rect(top_x, board_rect.bottom + 6, 32, 32), InsertionSide.BOTTOM, index))
        arrows.append(ArrowSpec(pg.Rect(board_rect.x - 38, left_y, 32, 32), InsertionSide.LEFT, index))
        arrows.append(ArrowSpec(pg.Rect(board_rect.right + 6, left_y, 32, 32), InsertionSide.RIGHT, index))

    return BoardLayout(board_rect, cell_size, cells, arrows)


def spare_tile_panel_layout(rect: pg.Rect) -> SpareTilePanelLayout:
    tile_rect = pg.Rect(rect.x + 18, rect.y + 52, 112, 112)
    return SpareTilePanelLayout(
        tile_rect=tile_rect,
        left_button=pg.Rect(tile_rect.x, tile_rect.bottom + 16, 52, 40),
        right_button=pg.Rect(tile_rect.right - 52, tile_rect.bottom + 16, 52, 40),
        stack_rect=pg.Rect(rect.right - 136, rect.y + 52, 100, 140),
    )


def draw_board(
    surface: pg.Surface,
    layout: BoardLayout,
    board: Sequence[Sequence[TileView]],
    players: Sequence[PublicPlayerPayload],
    *,
    shift_enabled: bool,
) -> None:
    pg.draw.rect(surface, PANEL_ALT, layout.board_rect.inflate(20, 20), border_radius=20)
    pg.draw.rect(surface, PANEL, layout.board_rect, border_radius=16)

    for position, tile_rect in layout.cells.items():
        tile = board[position[1]][position[0]]
        draw_tile(surface, tile_rect, tile, highlight=False)

    for player in players:
        player_position: PositionPayload | None = player["position"]
        if player_position is None:
            continue
        player_rect = layout.cells[(player_position["x"], player_position["y"])]
        pg.draw.circle(surface, player_color(player), player_rect.center, max(8, layout.cell_size // 7))

    for arrow in layout.arrows:
        _draw_arrow(surface, arrow, enabled=shift_enabled)


def draw_spare_tile_panel(
    surface: pg.Surface,
    rect: pg.Rect,
    spare_tile: TileView,
    active_treasure_type: TreasureType | None,
    *,
    rotation_enabled: bool,
) -> None:
    pg.draw.rect(surface, PANEL, rect, border_radius=20)
    title_font = font(18, bold=True)
    surface.blit(title_font.render("Current Tile", True, TEXT_PRIMARY), (rect.x + 18, rect.y + 16))

    layout = spare_tile_panel_layout(rect)
    draw_tile(surface, layout.tile_rect, spare_tile)

    button_fill = PANEL_ALT if rotation_enabled else blend_color(PANEL_ALT, DISABLED, 0.7)
    button_text = TEXT_PRIMARY if rotation_enabled else DISABLED
    for button_rect, label in ((layout.left_button, "<"), (layout.right_button, ">")):
        pg.draw.rect(surface, button_fill, button_rect, border_radius=12)
        arrow = title_font.render(label, True, button_text)
        surface.blit(arrow, arrow.get_rect(center=button_rect.center))

    for offset in range(3):
        card = layout.stack_rect.move(offset * 6, -offset * 6)
        pg.draw.rect(surface, (224, 218, 210), card, border_radius=8)
    treasure_surface = _treasure_surface(active_treasure_type, (76, 76))
    if treasure_surface is not None:
        surface.blit(treasure_surface, treasure_surface.get_rect(center=layout.stack_rect.center))


def draw_tile(surface: pg.Surface, rect: pg.Rect, tile: TileView, *, highlight: bool = False) -> None:
    radius = _tile_radius(rect.size)
    shadow = rect.move(0, 2)
    pg.draw.rect(surface, (77, 62, 48, 40), shadow, border_radius=radius)
    image = _rounded_tile_image(tile, rect.size, highlight=highlight)
    surface.blit(image, rect)
    _draw_home_marker(surface, rect, tile)
    treasure_surface = _treasure_surface(tile.treasure_type, (22, 22))
    if treasure_surface is not None:
        badge_rect = treasure_surface.get_rect(topright=(rect.right - 6, rect.y + 6))
        surface.blit(treasure_surface, badge_rect)


def player_color(player: PublicPlayerPayload) -> tuple[int, int, int]:
    piece_color = cast(PlayerColor, player["piece_color"])
    return PLAYER_COLOR_VALUES[piece_color]


def _tile_surface(tile_type: TileType, rotation: int) -> pg.Surface:
    texture = TILE_IMAGES[tile_type.value]
    angle = (-90 * rotation) % 360
    return pg.transform.rotate(texture, angle)


def _treasure_surface(treasure_type: TreasureType | None, size: tuple[int, int]) -> pg.Surface | None:
    if treasure_type is None:
        return None
    return pg.transform.scale(TREASURE_IMAGES[treasure_type.value], size)


def _tile_radius(size: tuple[int, int]) -> int:
    return max(6, min(14, min(size) // 7))


def _rounded_tile_image(tile: TileView, size: tuple[int, int], *, highlight: bool) -> pg.Surface:
    tile_image = pg.transform.scale(_tile_surface(tile.tile_type, tile.rotation), size)
    clipped = pg.Surface(size, pg.SRCALPHA)
    clipped.blit(tile_image, (0, 0))

    if highlight:
        highlight_surface = pg.Surface(size, pg.SRCALPHA)
        highlight_surface.fill((*MOVE_HIGHLIGHT, 70))
        clipped.blit(highlight_surface, (0, 0))

    radius = _tile_radius(size)
    mask = pg.Surface(size, pg.SRCALPHA)
    pg.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius)
    clipped.blit(mask, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
    return clipped


def _draw_home_marker(surface: pg.Surface, rect: pg.Rect, tile: TileView) -> None:
    if tile.home_color is None:
        return
    badge = pg.Rect(rect.x + 8, rect.bottom - 20, 12, 12)
    pg.draw.circle(surface, PLAYER_COLOR_VALUES[tile.home_color], badge.center, 6)
    pg.draw.circle(surface, (247, 239, 224), badge.center, 6, 2)


def _draw_arrow(surface: pg.Surface, arrow: ArrowSpec, *, enabled: bool) -> None:
    shadow = arrow.rect.move(0, 2)
    fill = (214, 186, 144) if enabled else blend_color(PANEL_ALT, DISABLED, 0.7)
    pg.draw.rect(surface, blend_color(fill, (88, 72, 58), 0.35), shadow, border_radius=12)
    pg.draw.rect(surface, fill, arrow.rect, border_radius=12)
    color = (52, 41, 33) if enabled else (118, 112, 106)
    cx, cy = arrow.rect.center
    if arrow.side == InsertionSide.TOP:
        points = [(cx - 7, cy - 2), (cx + 7, cy - 2), (cx, cy + 7)]
    elif arrow.side == InsertionSide.BOTTOM:
        points = [(cx - 7, cy + 2), (cx + 7, cy + 2), (cx, cy - 7)]
    elif arrow.side == InsertionSide.LEFT:
        points = [(cx + 7, cy), (cx - 2, cy - 7), (cx - 2, cy + 7)]
    else:
        points = [(cx - 7, cy), (cx + 2, cy - 7), (cx + 2, cy + 7)]
    pg.draw.polygon(surface, color, points)
