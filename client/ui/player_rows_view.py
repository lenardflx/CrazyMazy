from __future__ import annotations

from collections.abc import Sequence

import pygame as pg

from client.ui.game_board_view import player_color
from client.ui.theme import ACTIVE_OUTLINE, DISABLED, PANEL, TEXT_MUTED, TEXT_PRIMARY, blend_color, font
from shared.models import PlayerStatus
from shared.schema import PublicPlayerPayload

# TODO: layout sucks. 

def draw_player_rows(
    surface: pg.Surface,
    rect: pg.Rect,
    players: Sequence[PublicPlayerPayload],
    *,
    active_player_id: str | None,
    post_game: bool = False,
) -> None:
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
        pg.draw.circle(surface, player_color(player), (x + 10, row.centery), 9)
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
