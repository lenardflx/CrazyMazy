# Author: Lenard Felix, Raphael Eiden

from __future__ import annotations

import copy

import pygame as pg

from client.network.services.lobby_service import LobbyService
from client.state.runtime_state import TreasureCollectAnimation
from client.textures import PLAYER_IMAGES, TREASURE_IMAGES
from client.ui import Button
from client.ui.theme import ACTIVE_OUTLINE, DISABLED, PANEL, PANEL_ALT, TEXT_MUTED, TEXT_PRIMARY, blend_color, font
from shared.game.snapshot import SnapshotGameState, SnapshotPlayerState
from shared.types.enums import GamePhase, PlayerControllerKind, PlayerSkin, TreasureType


class PlayerPanelView:
    """
    Renders the list of players in the game, showing their name, piece color, and progress (or placement in post-game).
    Used both during the game (sidebar) and on the post-game screen.
    """

    def __init__(self, container: pg.Rect, lobby_service: LobbyService) -> None:
        # each button is reserved for a specific player
        self.container = container
        self.lobby_service = lobby_service
        self.kick_buttons: dict[str, Button] = {}

    def handle_player_panel_event(self, event: pg.event.Event):
        for player_id, button in self.kick_buttons.items():
            button.handle_event(event)

    def draw(
        self,
        surface: pg.Surface,
        rect: pg.Rect,
        game_state: SnapshotGameState,
        *,
        post_game: bool = False,
        treasure_animation: TreasureCollectAnimation | None = None,
        pending_collect: tuple[str, TreasureType] | None = None,
    ) -> None: # TODO: better docs
        """Draw one row per player inside the given rect.

        :param rect: The bounding area to fill with player rows.
        :param post_game: If True, only players with a final placement are shown.
        """
        players = game_state.ordered_players
        if post_game:
            players = [player for player in players if player.placement is not None]
        if not players:
            return

        is_lobby = game_state.phase == GamePhase.PREGAME
        gap = 10
        preferred_row_height = 58
        min_row_height = 48
        max_fit_height = (rect.height - gap * max(0, len(players) - 1)) // len(players)
        # Keep row sizing stable across 2-4 players and only shrink when the panel would overflow.
        row_height = max(min_row_height, min(preferred_row_height, max_fit_height))
        y = rect.y

        inactive_players = list(self.kick_buttons.keys())
        for player in players:
            if str(player.id) in inactive_players: inactive_players.remove(str(player.id))

            row = pg.Rect(rect.x, y, rect.width, row_height)
            y += row_height + gap
            row_surface = pg.Surface(row.size, pg.SRCALPHA)

            fill = PANEL if not player.is_inactive else blend_color(PANEL, DISABLED, 0.35)
            if player.id == game_state.current_player_id:
                fill = blend_color(PANEL, ACTIVE_OUTLINE, 0.18)
            elif player.id == game_state.viewer_id:
                fill = blend_color(PANEL, PANEL_ALT, 0.22)
            pg.draw.rect(row_surface, fill, row_surface.get_rect(), border_radius=16)

            pin = PLAYER_IMAGES[PlayerSkin.DEFAULT][player.piece_color]
            pin_rect = pin.get_rect(midleft=(14, row_surface.get_rect().centery))
            row_surface.blit(pin, pin_rect)

            if player.placement is not None:
                placement_font = font(18)
                placement = placement_font.render(f"{player.placement}.", True, TEXT_MUTED)
                placement_y = row_surface.get_rect().centery - placement.get_height() // 2
                row_surface.blit(placement, (pin_rect.right + 10, placement_y))
                name_x = pin_rect.right + 40
            else:
                name_x = pin_rect.right + 12

            name_font = font(17)
            name = name_font.render(player.display_name, True, TEXT_PRIMARY if not player.is_departed else TEXT_MUTED)
            name_y = row_surface.get_rect().centery - name.get_height() // 2
            row_surface.blit(name, (name_x, name_y))

            meta = self._inline_meta(player, game_state) if is_lobby else None
            if meta:
                meta_font = font(14)
                meta_surface = meta_font.render(f"({meta})", True, TEXT_MUTED)
                meta_x = name_x + name.get_width() + 8
                row_surface.blit(meta_surface, (meta_x, row_surface.get_rect().centery - meta_surface.get_height() // 2))

                # only draw kick button when the current player is the leader
                # and the button is not rendered for themselves
                if player.id != game_state.leader_player_id and game_state.viewer_id == game_state.leader_player_id:
                    self._draw_kick_button(surface=row_surface,
                                           row=row_surface.get_rect(),
                                           x_offset=self.container.left,
                                           y_offset=y - row_height - gap,
                                           player=player)

            elif not is_lobby:
                self._draw_progress(
                    row_surface,
                    player,
                    row_surface.get_width() - 14,
                    row_surface.get_rect(),
                    treasure_animation=treasure_animation,
                    pending_collect=pending_collect,
                )

            if player.is_inactive:
                row_surface.set_alpha(128)
            surface.blit(row_surface, row.topleft)

        if len(inactive_players) > 0: self.kick_buttons.clear()


    def _draw_kick_button(self,
                          surface: pg.Surface,
                          row: pg.Rect,
                          x_offset: int,
                          y_offset: int,
                          player: SnapshotPlayerState):
        if player.id not in self.kick_buttons:
            kick_button_height = 29
            rect = pg.Rect(row.right - 100, row.centery - kick_button_height // 2, 80, kick_button_height)
            abs_rect = pg.Rect(row.right + x_offset - 100, y_offset + row.centery - kick_button_height // 2, 80, kick_button_height)
            button = Button(rect=rect, label="KICK", on_click=lambda: self.lobby_service.kick_player(player.id), variant="primary", abs_rect=abs_rect)
            self.kick_buttons[player.id] = button
        self.kick_buttons[player.id].draw(surface, font(20))

    def _draw_progress(
        self,
        surface: pg.Surface,
        player: SnapshotPlayerState,
        right: int,
        row: pg.Rect,
        *,
        treasure_animation: TreasureCollectAnimation | None,
        pending_collect: tuple[str, TreasureType] | None,
    ) -> None:
        """Draw a row of six treasure cards, revealing collected treasure icons.

        :param right: The right edge x-coordinate to align the card strip against.
        :param row: The full player row rect, used to vertically center the cards.
        """
        unlocked = player.collected_treasure_count
        animated_index = _animated_collect_index(player, treasure_animation)
        pending_index = _pending_collect_index(player, pending_collect)
        flip_progress = 0.0 if treasure_animation is None else treasure_animation.eased_progress
        card_h = row.height - 18
        card_w = max(12, int(round(card_h * 0.68)))
        gap = 4
        total_w = card_w * 6 + gap * 5
        card_x = max(row.x + 170, right - total_w)
        for card_index in range(6):
            card = pg.Rect(card_x + card_index * (card_w + gap), row.y + (row.height - card_h) // 2, card_w, card_h)
            collected_treasure = player.collected_treasures[card_index] if card_index < unlocked else None
            is_flipping = animated_index == card_index
            if pending_index == card_index and animated_index is None:
                collected_treasure = None
            self._draw_progress_card(
                surface,
                card,
                treasure_type=collected_treasure,
                is_inactive=player.is_inactive,
                is_flipping=is_flipping,
                flip_progress=flip_progress,
            )

    def _draw_progress_card(
        self,
        surface: pg.Surface,
        rect: pg.Rect,
        *,
        treasure_type: TreasureType | None,
        is_inactive: bool,
        is_flipping: bool,
        flip_progress: float,
    ) -> None:
        card_rect = rect.copy()
        outline_color = blend_color(PANEL_ALT, TEXT_PRIMARY, 0.2)
        face_fill = PANEL
        back_fill = blend_color(PANEL_ALT, PANEL, 0.08)

        if is_flipping:
            scale = abs(1.0 - 2.0 * flip_progress)
            card_rect.width = max(2, round(rect.width * max(0.08, scale)))
            card_rect.center = rect.center
            showing_front = flip_progress >= 0.5
        else:
            showing_front = treasure_type is not None

        fill = face_fill if showing_front and treasure_type is not None else back_fill
        shadow = blend_color(fill, (76, 58, 42), 0.12)
        pg.draw.rect(surface, shadow, card_rect.move(0, 2), border_radius=5)
        pg.draw.rect(surface, fill if not is_inactive else blend_color(fill, DISABLED, 0.45), card_rect, border_radius=5)
        pg.draw.rect(surface, outline_color if not is_inactive else DISABLED, card_rect, width=1, border_radius=5)

        if not showing_front or treasure_type is None:
            inset = card_rect.inflate(-4, -6)
            pg.draw.rect(surface, blend_color(PANEL_ALT, TEXT_PRIMARY, 0.08), inset, border_radius=3)
            return

        icon_width = max(2, card_rect.width - 10)
        icon_height = max(8, min(card_rect.height - 12, rect.width - 6))
        icon = _treasure_icon(treasure_type, (icon_width, icon_height))
        if icon is not None:
            icon_rect = icon.get_rect(center=card_rect.center)
            surface.blit(icon, icon_rect)

    def _inline_meta(self, player: SnapshotPlayerState, game_state: SnapshotGameState) -> str | None:
        """Build a short parenthetical tag string for the lobby player row (e.g. "You, Leader", "Hard NPC").
        Returns None if no tags apply.
        """
        tags: list[str] = []
        if player.id == game_state.viewer_id:
            tags.append("You")
        if player.controller == PlayerControllerKind.NPC:
            tags.append("NPC" if player.npc_difficulty is None else f"{player.npc_difficulty.title()} NPC")
        if player.id == (game_state.leader_player_id or ""):
            tags.append("Leader")
        return ", ".join(tags) if tags else None


def _treasure_icon(treasure_type: TreasureType | None, size: tuple[int, int]) -> pg.Surface | None:
    if treasure_type is None:
        return None
    return pg.transform.scale(TREASURE_IMAGES[treasure_type.value], size)


def _animated_collect_index(
    player: SnapshotPlayerState,
    treasure_animation: TreasureCollectAnimation | None,
) -> int | None:
    if treasure_animation is None or treasure_animation.player_id != player.id:
        return None
    try:
        return player.collected_treasures.index(treasure_animation.treasure_type)
    except ValueError:
        return None


def _pending_collect_index(
    player: SnapshotPlayerState,
    pending_collect: tuple[str, TreasureType] | None,
) -> int | None:
    if pending_collect is None or pending_collect[0] != player.id:
        return None
    try:
        return player.collected_treasures.index(pending_collect[1])
    except ValueError:
        return None
