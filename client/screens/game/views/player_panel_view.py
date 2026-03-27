from __future__ import annotations

import pygame as pg

from client.screens.game.views.board_view import player_color
from client.ui.theme import ACTIVE_OUTLINE, DISABLED, PANEL, TEXT_MUTED, TEXT_PRIMARY, blend_color, font
from shared.game.snapshot import SnapshotGameState


class PlayerPanelView:
    def draw(
        self,
        surface: pg.Surface,
        rect: pg.Rect,
        game_state: SnapshotGameState,
        *,
        post_game: bool = False,
    ) -> None:
        row_font = font(16)
        name_font = font(17, bold=True)

        for index, player in enumerate(game_state.ordered_players):
            row = pg.Rect(rect.x, rect.y + index * 72, rect.width, 60)
            fill = PANEL if not player.is_inactive else (213, 213, 213)
            if player.id == game_state.current_player_id:
                fill = blend_color(PANEL, ACTIVE_OUTLINE, 0.18)
            pg.draw.rect(surface, fill, row, border_radius=16)

            x = row.x + 14
            pg.draw.circle(surface, player_color(player), (x + 10, row.centery), 9)
            x += 28

            if player.placement is not None:
                placement = name_font.render(f"{player.placement}.", True, TEXT_MUTED)
                surface.blit(placement, (x, row.y + 18))
                x += 32

            name = name_font.render(player.display_name, True, TEXT_PRIMARY if not player.is_departed else TEXT_MUTED)
            surface.blit(name, (x, row.y + 10))

            card_x = row.x + 180
            unlocked = player.collected_treasure_count
            for card_index in range(6):
                card = pg.Rect(card_x + card_index * 34, row.y + 12, 24, 36)
                color = (230, 205, 130) if card_index < unlocked else (155, 120, 92)
                if player.is_inactive:
                    color = DISABLED
                pg.draw.rect(surface, color, card, border_radius=4)

            status = player.sidebar_status(post_game=post_game)
            if status:
                status_surface = row_font.render(status, True, TEXT_MUTED)
                surface.blit(status_surface, (row.right - 92, row.y + 20))
