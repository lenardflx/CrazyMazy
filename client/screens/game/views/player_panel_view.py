from __future__ import annotations

import pygame as pg

from client.textures import PLAYER_IMAGES
from client.ui.theme import ACTIVE_OUTLINE, DISABLED, PANEL, PANEL_ALT, TEXT_MUTED, TEXT_PRIMARY, blend_color, font
from shared.game.snapshot import SnapshotGameState, SnapshotPlayerState
from shared.types.enums import GamePhase, PlayerControllerKind, PlayerSkin


class PlayerPanelView:
    def draw(
        self,
        surface: pg.Surface,
        rect: pg.Rect,
        game_state: SnapshotGameState,
        *,
        post_game: bool = False,
    ) -> None:
        players = game_state.ordered_players
        if post_game:
            players = [player for player in players if player.placement is not None]
        if not players:
            return

        is_lobby = game_state.phase == GamePhase.PREGAME
        gap = 12
        row_height = min(68, max(48, (rect.height - gap * max(0, len(players) - 1)) // len(players)))
        y = rect.y

        for player in players:
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
                placement_font = font(18, bold=True)
                placement = placement_font.render(f"{player.placement}.", True, TEXT_MUTED)
                placement_y = row_surface.get_rect().centery - placement.get_height() // 2
                row_surface.blit(placement, (pin_rect.right + 10, placement_y))
                name_x = pin_rect.right + 40
            else:
                name_x = pin_rect.right + 12

            name_font = font(17, bold=True)
            name = name_font.render(player.display_name, True, TEXT_PRIMARY if not player.is_departed else TEXT_MUTED)
            name_y = row_surface.get_rect().centery - name.get_height() // 2
            row_surface.blit(name, (name_x, name_y))

            meta = self._inline_meta(player, game_state) if is_lobby else None
            if meta:
                meta_font = font(14)
                meta_surface = meta_font.render(f"({meta})", True, TEXT_MUTED)
                meta_x = name_x + name.get_width() + 8
                row_surface.blit(meta_surface, (meta_x, row_surface.get_rect().centery - meta_surface.get_height() // 2))
            elif not is_lobby:
                self._draw_progress(row_surface, player, row_surface.get_width() - 14, row_surface.get_rect())

            if player.is_inactive:
                row_surface.set_alpha(128)
            surface.blit(row_surface, row.topleft)

    def _draw_progress(self, surface: pg.Surface, player: SnapshotPlayerState, right: int, row: pg.Rect) -> None:
        unlocked = player.collected_treasure_count
        card_w = 18
        gap = 8
        total_w = card_w * 6 + gap * 5
        card_x = max(row.x + 170, right - total_w)
        for card_index in range(6):
            card = pg.Rect(card_x + card_index * (card_w + gap), row.y + 14, card_w, row.height - 28)
            color = (230, 205, 130) if card_index < unlocked else (155, 120, 92)
            if player.is_inactive:
                color = DISABLED
            pg.draw.rect(surface, color, card, border_radius=5)

    def _inline_meta(self, player: SnapshotPlayerState, game_state: SnapshotGameState) -> str | None:
        tags: list[str] = []
        if player.id == game_state.viewer_id:
            tags.append("You")
        if player.controller == PlayerControllerKind.NPC:
            tags.append("NPC" if player.npc_difficulty is None else f"{player.npc_difficulty.title()} NPC")
        if player.id == (game_state.leader_player_id or ""):
            tags.append("Leader")
        return ", ".join(tags) if tags else None
