from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import cast

import pygame as pg

from client.state.display_state import ClientDisplayState, TileView
from shared.models import InsertionSide, PlayerColor, PlayerStatus, TileType, TreasureType
from shared.schema import PositionPayload, PublicPlayerPayload
from client.ui.textures import TILE_IMAGES, TREASURE_IMAGES
from client.ui.theme import ACTIVE_OUTLINE, DISABLED, MOVE_HIGHLIGHT, PANEL, PANEL_ALT, TEXT_MUTED, TEXT_PRIMARY, blend_color, font


@dataclass(slots=True)
class ArrowSpec:
    rect: pg.Rect
    side: InsertionSide
    index: int


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
    pg.draw.circle(surface, tile.home_color and {
        "RED": (210, 74, 74),
        "BLUE": (63, 109, 215),
        "GREEN": (80, 156, 93),
        "YELLOW": (209, 173, 59),
    }[tile.home_color.value], badge.center, 6)
    pg.draw.circle(surface, (247, 239, 224), badge.center, 6, 2)


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


def board_layout(rect: pg.Rect, board_size: int) -> tuple[pg.Rect, int, dict[tuple[int, int], pg.Rect], list[ArrowSpec]]:
    cell = min((rect.width - 64) // board_size, (rect.height - 64) // board_size)
    board_rect = pg.Rect(rect.x + 32, rect.y + 32, cell * board_size, cell * board_size)
    cells: dict[tuple[int, int], pg.Rect] = {}
    for row in range(board_size):
        for col in range(board_size):
            cells[(col, row)] = pg.Rect(board_rect.x + col * cell, board_rect.y + row * cell, cell - 4, cell - 4)

    arrows: list[ArrowSpec] = []
    for index in range(1, board_size, 2):
        top_x = board_rect.x + index * cell + cell // 2 - 16
        left_y = board_rect.y + index * cell + cell // 2 - 16
        arrows.append(ArrowSpec(pg.Rect(top_x, board_rect.y - 38, 32, 32), InsertionSide.TOP, index))
        arrows.append(ArrowSpec(pg.Rect(top_x, board_rect.bottom + 6, 32, 32), InsertionSide.BOTTOM, index))
        arrows.append(ArrowSpec(pg.Rect(board_rect.x - 38, left_y, 32, 32), InsertionSide.LEFT, index))
        arrows.append(ArrowSpec(pg.Rect(board_rect.right + 6, left_y, 32, 32), InsertionSide.RIGHT, index))
    return board_rect, cell, cells, arrows


def draw_board(
    surface: pg.Surface,
    rect: pg.Rect,
    display: ClientDisplayState,
    *,
    shift_enabled: bool,
) -> tuple[dict[tuple[int, int], pg.Rect], list[ArrowSpec]]:
    if display.board is None:
        return {}, []
    board_rect, cell, cells, arrows = board_layout(rect, display.board_size)
    pg.draw.rect(surface, PANEL_ALT, board_rect.inflate(20, 20), border_radius=20)
    pg.draw.rect(surface, PANEL, board_rect, border_radius=16)

    for position, tile_rect in cells.items():
        tile = display.board[position[1]][position[0]]
        # TODO: Highlight reachable move tiles once the server exposes authoritative move targets.
        highlight = False
        draw_tile(surface, tile_rect, tile, highlight=highlight)

    for player in display.players:
        position: PositionPayload | None = player["position"]
        if position is None:
            continue
        player_rect = cells[(position["x"], position["y"])]
        color = _player_color(player)
        pg.draw.circle(surface, color, player_rect.center, max(8, cell // 7))

    for arrow in arrows:
        _draw_arrow(surface, arrow, enabled=shift_enabled)
    return cells, arrows


def draw_spare_tile_panel(surface: pg.Surface, rect: pg.Rect, display: ClientDisplayState) -> tuple[pg.Rect, pg.Rect]:
    if display.spare_tile is None:
        return pg.Rect(0, 0, 0, 0), pg.Rect(0, 0, 0, 0)
    pg.draw.rect(surface, PANEL, rect, border_radius=20)
    title_font = font(18, bold=True)
    surface.blit(title_font.render("Current Tile", True, TEXT_PRIMARY), (rect.x + 18, rect.y + 16))
    tile_rect = pg.Rect(rect.x + 18, rect.y + 52, 112, 112)
    draw_tile(surface, tile_rect, display.spare_tile)
    left_button = pg.Rect(tile_rect.x, tile_rect.bottom + 16, 52, 40)
    right_button = pg.Rect(tile_rect.right - 52, tile_rect.bottom + 16, 52, 40)
    for button_rect, label in ((left_button, "<"), (right_button, ">")):
        pg.draw.rect(surface, PANEL_ALT, button_rect, border_radius=12)
        arrow = title_font.render(label, True, TEXT_PRIMARY)
        surface.blit(arrow, arrow.get_rect(center=button_rect.center))

    stack_rect = pg.Rect(rect.right - 136, rect.y + 52, 100, 140)
    for offset in range(3):
        card = stack_rect.move(offset * 6, -offset * 6)
        pg.draw.rect(surface, (224, 218, 210), card, border_radius=8)
    treasure_surface = _treasure_surface(display.active_treasure_type, (76, 76))
    if treasure_surface is not None:
        surface.blit(treasure_surface, treasure_surface.get_rect(center=stack_rect.center))
    return left_button, right_button


def draw_player_rows(surface: pg.Surface, rect: pg.Rect, players: Sequence[PublicPlayerPayload], *, active_player_id: str | None, post_game: bool = False) -> None:
    row_font = font(16)
    name_font = font(17, bold=True)
    for index, player in enumerate(players):
        row = pg.Rect(rect.x, rect.y + index * 72, rect.width, 60)
        left = player["status"] == PlayerStatus.DEPARTED
        spectator = player["status"] == PlayerStatus.OBSERVER
        fill = PANEL if not (left or spectator) else (213, 213, 213)
        if player["id"] == active_player_id:
            fill = blend_color(PANEL, ACTIVE_OUTLINE, 0.18)
        pg.draw.rect(surface, fill, row, border_radius=16)
        x = row.x + 14
        pg.draw.circle(surface, _player_color(player), (x + 10, row.centery), 9)
        x += 28
        if player["placement"] is not None:
            placement = name_font.render(f"{player['placement']}.", True, TEXT_MUTED)
            surface.blit(placement, (x, row.y + 18))
            x += 32
        name = name_font.render(player["display_name"], True, TEXT_PRIMARY if not left else TEXT_MUTED)
        surface.blit(name, (x, row.y + 10))
        card_x = row.x + 180
        unlocked = len(player["collected_treasures"])
        for card_index in range(6):
            card = pg.Rect(card_x + card_index * 34, row.y + 12, 24, 36)
            color = (230, 205, 130) if card_index < unlocked else (155, 120, 92)
            if left or spectator:
                color = DISABLED
            pg.draw.rect(surface, color, card, border_radius=4)
        if left or spectator:
            status = row_font.render("Left" if left else "Spectator", True, TEXT_MUTED)
            surface.blit(status, (row.right - 90, row.y + 20))
        elif post_game and player["placement"] is not None:
            status = row_font.render("Finished", True, TEXT_MUTED)
            surface.blit(status, (row.right - 92, row.y + 20))


def _player_color(player: PublicPlayerPayload) -> tuple[int, int, int]:
    piece_color = cast(PlayerColor, player["piece_color"])
    return {
        PlayerColor.RED: (210, 74, 74),
        PlayerColor.BLUE: (63, 109, 215),
        PlayerColor.GREEN: (80, 156, 93),
        PlayerColor.YELLOW: (209, 173, 59),
    }[piece_color]
