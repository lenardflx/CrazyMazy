from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pygame as pg

from client.state.runtime_state import BoardShiftAnimation, PlayerMoveAnimation
from client.textures import PLAYER_IMAGES, TILE_IMAGES, TREASURE_IMAGES
from client.ui.controls import Button
from client.ui.theme import ACCENT_DARK, DISABLED, PANEL, PANEL_ALT, PANEL_SHADOW, TEXT_MUTED, TEXT_PRIMARY, MOVE_HIGHLIGHT, blend_color, draw_pixel_rect, font
from shared.types.enums import InsertionSide, PlayerColor, PlayerSkin, TreasureType
from shared.game.tile import Tile
from shared.game.snapshot import SnapshotGameState

# TODO: finish documentation.... this file is annoying

# Color chodes for the Player
PLAYER_COLOR_VALUES = {
    PlayerColor.RED: (210, 74, 74),
    PlayerColor.BLUE: (63, 109, 215),
    PlayerColor.GREEN: (80, 156, 93),
    PlayerColor.YELLOW: (209, 173, 59),
}

# The type for handling clicks on the game board
BoardClick = (
    tuple[Literal["rotate"], int]
    | tuple[Literal["shift"], InsertionSide, int]
    | tuple[Literal["move"], int, int]
    | None
)


@dataclass(slots=True, frozen=True)
class ArrowTarget:
    """Represents a target for an arrow on the game board."""
    rect: pg.Rect
    side: InsertionSide
    index: int


@dataclass(slots=True, frozen=True)
class GameBoardLayout:
    """Represents the layout of the game board."""
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


@dataclass(slots=True, frozen=True)
class TileOverlayAnchors:
    """Precomputed overlay anchor points inside a tile rect."""
    marker_center: tuple[int, int]
    player_centers: dict[PlayerColor, tuple[int, int]]


class BoardView:
    """
    The BoardView is responsible for rendering the game board, including the tiles, players, and UI elements related to the board.
    It draws the current state and is responsible for determining what the player has clicked on when they interact with the board.
    """
    def __init__(self) -> None:
        self.title_font = font(18)
        self.small_font = font(14)
        self.xs_font = font(12)
        self._rotate_left_button: Button | None = None
        self._rotate_right_button: Button | None = None
        self._arrow_buttons: dict[tuple[InsertionSide, int], Button] = {}
        self._pending_click: BoardClick = None
        self._tile_surface_cache: dict[tuple[str, int, tuple[int, int], bool], pg.Surface] = {}
        self._tile_mask_cache: dict[tuple[int, int], pg.Surface] = {}
        self._tile_shadow_cache: dict[tuple[int, int], pg.Surface] = {}
        self._player_pin_cache: dict[tuple[PlayerColor, tuple[int, int]], pg.Surface] = {}
        self._treasure_surface_cache: dict[tuple[str, tuple[int, int]], pg.Surface] = {}

    def layout(self, surface_rect: pg.Rect, board_size: int) -> GameBoardLayout:
        """Calculate the layout of the game board and related UI elements based on the surface size and board size."""

        # Panels for the board, the side UI, the spare tile and the player list
        board_panel = pg.Rect(24, 96, 770, surface_rect.height - 120)
        side_panel = pg.Rect(820, 96, surface_rect.width - 844, surface_rect.height - 120)
        spare_panel = pg.Rect(side_panel.x, side_panel.y, side_panel.width, 236)
        players_panel = pg.Rect(side_panel.x, side_panel.y + 254, side_panel.width, side_panel.height - 254)

        # Calculate the size of each cell on the board based on the available space and the board size, and create rects for each cell and the spare tile.
        cell_size = min((board_panel.width - 64) // board_size, (board_panel.height - 64) // board_size)
        tile_gap = max(1, min(4, round(cell_size * 0.04)))
        board_rect = pg.Rect(board_panel.x + 32, board_panel.y + 32, cell_size * board_size, cell_size * board_size)
        spare_tile_rect = pg.Rect(spare_panel.x + 18, spare_panel.y + 52, 112, 112)

        # Create rects for each cell on the board and for the arrow targets around the board.
        cells = {
            (col, row): pg.Rect(
                board_rect.x + col * cell_size,
                board_rect.y + row * cell_size,
                cell_size - tile_gap,
                cell_size - tile_gap,
            )
            for row in range(board_size)
            for col in range(board_size)
        }
        arrows = self._build_arrows(board_rect, cell_size, board_size)

        # Return the complete layout for board
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

    def draw(
        self,
        surface: pg.Surface,
        layout: GameBoardLayout,
        game_state: SnapshotGameState,
        spare_tile: Tile,
        shift_animation: BoardShiftAnimation | None,
        move_animation: PlayerMoveAnimation | None,
    ) -> None:
        """Draw the game board and related UI elements based on the current game state and animations."""
        self._draw_board(surface, layout, game_state, shift_animation, move_animation)
        self._draw_spare_panel(surface, layout, spare_tile, game_state)

    def resolve_click(self, pos: tuple[int, int], layout: GameBoardLayout, game_state: SnapshotGameState) -> BoardClick:
        """
        Determine what the player has clicked on based on the position of the click, the layout of the board, and the current game state.
        Returns a BoardClick indicating whether the player clicked on a rotate button, an arrow to shift.
        This is done by checking the collision of the click position with the elements on the board.
        """
        # If we currently move, the only clickable elements are the reachable cells on the board.
        if game_state.can_move:
            # Check every cell and if it was clicked and is reachable.
            for (x, y), cell in layout.cells.items():
                if cell.collidepoint(pos) and game_state.is_position_reachable((x, y)):
                    return "move", x, y
        return None

    def handle_control_event(self, event: pg.event.Event, layout: GameBoardLayout, game_state: SnapshotGameState) -> BoardClick:
        self._sync_control_buttons(layout, game_state)
        self._pending_click = None

        if self._rotate_left_button is not None:
            self._rotate_left_button.handle_event(event)
        if self._rotate_right_button is not None:
            self._rotate_right_button.handle_event(event)
        for button in self._arrow_buttons.values():
            button.handle_event(event)

        click = self._pending_click
        self._pending_click = None
        return click

    def _build_arrows(self, board_rect: pg.Rect, cell_size: int, board_size: int) -> list[ArrowTarget]:
        """Build the list of ArrowTargets for the given board layout. Arrows are placed on every odd index along the edges of the board."""
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

    def _is_arrow_clickable(
        self,
        game_state: SnapshotGameState,
        arrow: ArrowTarget,
        shift_animation: BoardShiftAnimation | None = None,
        move_animation: PlayerMoveAnimation | None = None,
    ) -> bool:
        is_blocked = game_state.is_insertion_blocked(arrow.side, arrow.index)
        return (
            not is_blocked
            and game_state.can_shift
            and shift_animation is None
            and move_animation is None
        )

    def _draw_board(
        self,
        surface: pg.Surface,
        layout: GameBoardLayout,
        game_state: SnapshotGameState,
        shift_animation: BoardShiftAnimation | None,
        move_animation: PlayerMoveAnimation | None,
    ) -> None:
        """Draw the game board, including the tiles, players, and arrows. Takes into account the current animations for shifting and moving."""
        draw_pixel_rect(
            surface,
            layout.board_rect.inflate(24, 24),
            PANEL,
            border=ACCENT_DARK,
            shadow=PANEL_SHADOW,
        )

        players_by_position: dict[tuple[int, int], list[PlayerColor]] = {}
        for player in game_state.ordered_players:
            if player.position is None:
                continue
            if move_animation is not None and player.id == move_animation.player_id:
                continue
            players_by_position.setdefault(player.position, []).append(player.piece_color)

        # Tiles
        for position, rect in layout.cells.items():
            tile = game_state.tile_at(position)
            if tile is None:
                continue
            animated_rect = self._animated_rect(rect, position, layout.cell_size, shift_animation)
            self._draw_tile(
                surface,
                animated_rect,
                tile,
                highlight=game_state.is_position_reachable(position),
            )
            self._draw_tile_overlays(
                surface,
                animated_rect,
                players_by_position.get(position, []),
                treasure_type=tile.treasure,
                home_color=game_state.home_color_at(position),
            )

        # The tile that is being shifted out of the board during animation
        if shift_animation is not None:
            self._draw_outgoing_tile(surface, layout, game_state, shift_animation)

        # Only the actively moving player is drawn separately between tiles.
        for player in game_state.ordered_players:
            if player.position is None:
                continue
            if move_animation is not None and player.id == move_animation.player_id:
                self._draw_player_pin(
                    surface,
                    player.piece_color,
                    self._moving_player_center(layout, move_animation, player.piece_color),
                    max_size=max(14, layout.cell_size // 4),
                )
                continue

        for arrow in layout.arrows:
            self._draw_arrow(surface, arrow, enabled=self._is_arrow_clickable(game_state, arrow, shift_animation, move_animation))

    def _draw_spare_panel(
        self,
        surface: pg.Surface,
        layout: GameBoardLayout,
        tile: Tile,
        game_state: SnapshotGameState,
    ) -> None:
        """Draw the spare tile panel, including the current spare tile and the rotate buttons. The rotate buttons are only enabled when the player can shift."""
        self._sync_control_buttons(layout, game_state)
        draw_pixel_rect(surface, layout.spare_panel, PANEL, border=ACCENT_DARK, shadow=PANEL_SHADOW)
        surface.blit(self.title_font.render("Current Tile", True, TEXT_PRIMARY), (layout.spare_panel.x + 18, layout.spare_panel.y + 16))

        self._draw_tile(surface, layout.spare_tile_rect, tile)
        self._draw_tile_overlays(
            surface,
            layout.spare_tile_rect,
            [],
            treasure_type=tile.treasure,
            home_color=None,
        )

        if self._rotate_left_button is not None:
            self._rotate_left_button.draw(surface, self.title_font)
        if self._rotate_right_button is not None:
            self._rotate_right_button.draw(surface, self.title_font)
        self._draw_treasure_stack(surface, layout.treasure_stack_rect, game_state)

    def _draw_treasure_stack(self, surface: pg.Surface, rect: pg.Rect, game_state: SnapshotGameState) -> None:
        viewer = game_state.viewer_player
        remaining = 0 if viewer is None else viewer.remaining_treasure_count
        visible_stack = max(1, min(remaining, 6))
        top_rect = rect

        for offset in range(visible_stack - 1, 0, -1):
            stack_rect = rect.move(-offset * 4, offset * 4)
            self._draw_stack_card(surface, stack_rect, face_up=False)

        self._draw_stack_card(surface, top_rect, face_up=True)
        if game_state.active_treasure_type is not None:
            treasure_surface = self._treasure_surface(game_state.active_treasure_type, (68, 68))
            if treasure_surface is not None:
                surface.blit(treasure_surface, treasure_surface.get_rect(center=(top_rect.centerx, top_rect.centery - 6)))
            self._draw_stack_count(surface, top_rect, remaining)
            return

        self._draw_home_target(surface, top_rect, game_state)

    def _draw_stack_card(self, surface: pg.Surface, rect: pg.Rect, *, face_up: bool) -> None:
        outline_color = blend_color(PANEL_ALT, TEXT_PRIMARY, 0.2)
        fill = PANEL if face_up else blend_color(PANEL_ALT, PANEL, 0.08)
        draw_pixel_rect(
            surface,
            rect,
            fill,
            border=outline_color,
            shadow=blend_color(fill, PANEL_SHADOW, 0.2),
        )

        if face_up:
            return

        inset = rect.inflate(-10, -14)
        draw_pixel_rect(
            surface,
            inset,
            blend_color(PANEL_ALT, TEXT_PRIMARY, 0.08),
            border=blend_color(PANEL_ALT, TEXT_PRIMARY, 0.16),
        )

    def _draw_stack_count(self, surface: pg.Surface, rect: pg.Rect, remaining: int) -> None:
        label = self.xs_font.render("Cards left", True, TEXT_MUTED)
        value = self.small_font.render(str(remaining), True, TEXT_PRIMARY)
        label_pos = label.get_rect(midleft=(rect.x + 12, rect.bottom - 16))
        value_pos = value.get_rect(midright=(rect.right - 12, rect.bottom - 16))
        surface.blit(label, label_pos)
        surface.blit(value, value_pos)

    def _draw_home_target(self, surface: pg.Surface, rect: pg.Rect, game_state: SnapshotGameState) -> None:
        viewer = game_state.viewer_player
        if viewer is None:
            return

        go_label = self.small_font.render("Go", True, TEXT_MUTED)
        home_label = self.title_font.render("HOME", True, PLAYER_COLOR_VALUES[viewer.piece_color])
        go_rect = go_label.get_rect(center=(rect.centerx, rect.centery - 18))
        home_rect = home_label.get_rect(center=(rect.centerx, rect.centery + 10))
        surface.blit(go_label, go_rect)
        surface.blit(home_label, home_rect)

    def _draw_tile(
        self,
        surface: pg.Surface,
        rect: pg.Rect,
        tile: Tile,
        *,
        highlight: bool = False,
    ) -> None:
        """Draw a single tile at the given rect, with optional highlights for the home player and reachable positions."""
        surface.blit(self._tile_shadow_surface(rect.size), rect.move(0, 3))
        surface.blit(self._tile_visual(tile, rect.size, highlight=highlight), rect)

    def _draw_tile_overlays(
        self,
        surface: pg.Surface,
        rect: pg.Rect,
        players: list[PlayerColor],
        *,
        treasure_type: TreasureType | None,
        home_color: PlayerColor | None,
    ) -> None:
        anchors = self._tile_overlay_anchors(rect)

        if treasure_type is not None:
            treasure_surface = self._treasure_surface(
                treasure_type,
                (max(12, round(rect.width * 0.3)), max(12, round(rect.width * 0.3))),
            )
            if treasure_surface is not None:
                surface.blit(treasure_surface, treasure_surface.get_rect(center=anchors.marker_center))

        if home_color is not None:
            radius = max(4, round(rect.width * 0.13))
            pg.draw.circle(surface, PLAYER_COLOR_VALUES[home_color], anchors.marker_center, radius)
            pg.draw.circle(surface, (247, 239, 224), anchors.marker_center, radius, max(1, radius // 3))

        for piece_color in players:
            center = anchors.player_centers[piece_color]
            self._draw_player_pin(surface, piece_color, center, max_size=max(12, round(rect.width * 0.32)))

    def _draw_arrow(self, surface: pg.Surface, arrow: ArrowTarget, *, enabled: bool) -> None:
        button = self._arrow_buttons.get((arrow.side, arrow.index))
        if button is None:
            return
        button.enabled = enabled
        button.draw(surface, self.small_font)

    def _sync_control_buttons(self, layout: GameBoardLayout, game_state: SnapshotGameState) -> None:
        can_shift = game_state.can_shift

        if self._rotate_left_button is None:
            self._rotate_left_button = Button(
                layout.rotate_left_button.copy(),
                "",
                lambda: self._set_pending_click(("rotate", -1)),
                icon="arrow_left",
            )
        else:
            self._rotate_left_button.rect = layout.rotate_left_button.copy()
        self._rotate_left_button.enabled = can_shift

        if self._rotate_right_button is None:
            self._rotate_right_button = Button(
                layout.rotate_right_button.copy(),
                "",
                lambda: self._set_pending_click(("rotate", 1)),
                icon="arrow_right",
            )
        else:
            self._rotate_right_button.rect = layout.rotate_right_button.copy()
        self._rotate_right_button.enabled = can_shift

        synced: dict[tuple[InsertionSide, int], Button] = {}
        for arrow in layout.arrows:
            key = (arrow.side, arrow.index)
            button = self._arrow_buttons.get(key)
            if button is None:
                button = Button(
                    arrow.rect.copy(),
                    "",
                    lambda side=arrow.side, index=arrow.index: self._set_pending_click(("shift", side, index)),
                    icon={
                        InsertionSide.TOP: "arrow_down",
                        InsertionSide.BOTTOM: "arrow_up",
                        InsertionSide.LEFT: "arrow_right",
                        InsertionSide.RIGHT: "arrow_left",
                    }[arrow.side],
                )
            else:
                button.rect = arrow.rect.copy()
            button.enabled = self._is_arrow_clickable(game_state, arrow)
            synced[key] = button
        self._arrow_buttons = synced

    def _set_pending_click(self, click: BoardClick) -> None:
        self._pending_click = click

    def _tile_visual(self, tile: Tile, size: tuple[int, int], *, highlight: bool) -> pg.Surface:
        key = (tile.type.value, tile.orientation.value, size, highlight)
        cached = self._tile_surface_cache.get(key)
        if cached is not None:
            return cached

        tile_image = pg.transform.scale(_tile_surface(tile), size)
        clipped = pg.Surface(size, pg.SRCALPHA)
        clipped.blit(tile_image, (0, 0))
        if highlight:
            highlight_surface = pg.Surface(size, pg.SRCALPHA)
            highlight_surface.fill((*MOVE_HIGHLIGHT, 70))
            clipped.blit(highlight_surface, (0, 0))

        clipped.blit(self._tile_mask_surface(size), (0, 0), special_flags=pg.BLEND_RGBA_MULT)
        self._tile_surface_cache[key] = clipped
        return clipped

    def _tile_mask_surface(self, size: tuple[int, int]) -> pg.Surface:
        cached = self._tile_mask_cache.get(size)
        if cached is not None:
            return cached

        mask = pg.Surface(size, pg.SRCALPHA)
        draw_pixel_rect(mask, mask.get_rect(), (255, 255, 255), border=(255, 255, 255))
        self._tile_mask_cache[size] = mask
        return mask

    def _tile_shadow_surface(self, size: tuple[int, int]) -> pg.Surface:
        cached = self._tile_shadow_cache.get(size)
        if cached is not None:
            return cached

        shadow = pg.Surface(size, pg.SRCALPHA)
        shadow_color = blend_color(PANEL_SHADOW, PANEL, 0.15)
        draw_pixel_rect(shadow, shadow.get_rect(), shadow_color, border=shadow_color)
        self._tile_shadow_cache[size] = shadow
        return shadow

    def _animated_rect(
        self,
        rect: pg.Rect,
        position: tuple[int, int],
        cell_size: int,
        animation: BoardShiftAnimation | None,
    ) -> pg.Rect:
        if animation is None or not self._matches_shift_line(position, animation):
            return rect
        offset = round(cell_size * (1.0 - animation.eased_progress))
        dx, dy = self._travel_vector(animation.side)
        return rect.move(-dx * offset, -dy * offset)

    def _draw_outgoing_tile(
        self,
        surface: pg.Surface,
        layout: GameBoardLayout,
        game_state: SnapshotGameState,
        animation: BoardShiftAnimation,
    ) -> None:
        if game_state.spare_tile is None:
            return
        outgoing_position = self._outgoing_position(game_state.board_size, animation)
        outgoing_rect = layout.cells[outgoing_position].copy()
        offset = round(layout.cell_size * animation.eased_progress)
        dx, dy = self._travel_vector(animation.side)
        self._draw_tile(surface, outgoing_rect.move(dx * offset, dy * offset), game_state.spare_tile)

    def _matches_shift_line(self, position: tuple[int, int], animation: BoardShiftAnimation) -> bool:
        x, y = position
        if animation.side in (InsertionSide.LEFT, InsertionSide.RIGHT):
            return y == animation.index
        return x == animation.index

    def _outgoing_position(self, board_size: int, animation: BoardShiftAnimation) -> tuple[int, int]:
        if animation.side == InsertionSide.LEFT:
            return board_size - 1, animation.index
        if animation.side == InsertionSide.RIGHT:
            return 0, animation.index
        if animation.side == InsertionSide.TOP:
            return animation.index, board_size - 1
        return animation.index, 0

    def _travel_vector(self, side: InsertionSide) -> tuple[int, int]:
        return {
            InsertionSide.LEFT: (1, 0),
            InsertionSide.RIGHT: (-1, 0),
            InsertionSide.TOP: (0, 1),
            InsertionSide.BOTTOM: (0, -1),
        }[side]

    def _moving_player_center(
        self,
        layout: GameBoardLayout,
        animation: PlayerMoveAnimation,
        piece_color: PlayerColor,
    ) -> tuple[int, int]:
        if len(animation.path) < 2:
            return self._player_anchor(layout.cells[animation.path[-1]], piece_color)

        total_segments = len(animation.path) - 1
        scaled_progress = animation.eased_progress * total_segments
        segment_index = min(total_segments - 1, int(scaled_progress))
        segment_progress = scaled_progress - segment_index
        start = self._player_anchor(layout.cells[animation.path[segment_index]], piece_color)
        end = self._player_anchor(layout.cells[animation.path[segment_index + 1]], piece_color)
        return (
            round(start[0] + (end[0] - start[0]) * segment_progress),
            round(start[1] + (end[1] - start[1]) * segment_progress),
        )

    def _tile_overlay_anchors(self, rect: pg.Rect) -> TileOverlayAnchors:
        inset_x = rect.width // 2.5
        inset_y = rect.height // 2.5
        return TileOverlayAnchors(
            marker_center=rect.center,
            player_centers={
                PlayerColor.RED: (rect.left + inset_x, rect.top + inset_y),
                PlayerColor.BLUE: (rect.right - inset_x, rect.top + inset_y),
                PlayerColor.GREEN: (rect.left + inset_x, rect.bottom - inset_y),
                PlayerColor.YELLOW: (rect.right - inset_x, rect.bottom - inset_y),
            },
        )

    def _player_anchor(self, rect: pg.Rect, piece_color: PlayerColor) -> tuple[int, int]:
        return self._tile_overlay_anchors(rect).player_centers[piece_color]

    def _draw_player_pin(
        self,
        surface: pg.Surface,
        piece_color: PlayerColor,
        center: tuple[int, int],
        *,
        max_size: int | None = None,
    ) -> None:
        pin = PLAYER_IMAGES[PlayerSkin.DEFAULT][piece_color]
        if max_size is not None:
            width, height = pin.get_size()
            scale = min(max_size / max(width, 1), max_size / max(height, 1))
            target_size = (
                max(1, round(width * scale)),
                max(1, round(height * scale)),
            )
            pin = self._player_pin(piece_color, target_size)
        surface.blit(pin, pin.get_rect(center=center))

    def _player_pin(self, piece_color: PlayerColor, size: tuple[int, int]) -> pg.Surface:
        key = (piece_color, size)
        cached = self._player_pin_cache.get(key)
        if cached is not None:
            return cached
        pin = pg.transform.scale(PLAYER_IMAGES[PlayerSkin.DEFAULT][piece_color], size)
        self._player_pin_cache[key] = pin
        return pin

    def _treasure_surface(
        self,
        treasure_type: str | TreasureType | None,
        size: tuple[int, int],
    ) -> pg.Surface | None:
        if treasure_type is None:
            return None
        key = treasure_type.value if isinstance(treasure_type, TreasureType) else treasure_type
        cache_key = (key, size)
        cached = self._treasure_surface_cache.get(cache_key)
        if cached is not None:
            return cached
        surface = pg.transform.scale(TREASURE_IMAGES[key], size)
        self._treasure_surface_cache[cache_key] = surface
        return surface


def _tile_surface(tile: Tile) -> pg.Surface:
    return pg.transform.rotate(TILE_IMAGES[tile.type.value], (-90 * tile.orientation.value) % 360)
