from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from client.screens.menu.menu_screen import MenuScreen
from client.ui.theme import ACCENT, PANEL_ALT, TEXT_MUTED, TEXT_PRIMARY, font, render_text
from client.lang import DisplayMessage, language_service

if TYPE_CHECKING:
    from client.screens.core.scene_manager import SceneManager


class StatsScreen(MenuScreen):
    """Read-only overview of the locally persisted player stats."""

    def __init__(self, surface: pg.Surface, scene_manager: SceneManager) -> None:
        super().__init__(
            surface,
            scene_manager,
            title=language_service.get_message(DisplayMessage.STATS),
            is_main_menu=False,
        )
        self.hero_font = font(34)

    def draw_content(self, rect: pg.Rect) -> None:
        super().draw_content(rect)
        stats = self.scene_manager.client_settings.get_stats()
        rows = [
            (language_service.get_message(DisplayMessage.STATS_GAMES_PLAYED), str(stats.games_played)),
            (language_service.get_message(DisplayMessage.STATS_GAMES_WON), str(stats.games_won)),
            (language_service.get_message(DisplayMessage.STATS_WIN_RATE), f"{stats.win_rate_percent}%"),
            (language_service.get_message(DisplayMessage.STATS_TREASURES), str(stats.treasures_collected)),
            (language_service.get_message(DisplayMessage.STATS_MOVES), str(stats.moves_made)),
        ]

        center_x = self.content_rect.centerx
        top_y = self.content_rect.y + 92

        rate_surface = render_text(self.hero_font, f"{stats.win_rate_percent}%", ACCENT)
        self.surface.blit(rate_surface, rate_surface.get_rect(center=(center_x, top_y + 18)))

        rate_caption = render_text(self.body_font, language_service.get_message(DisplayMessage.STATS_WIN_RATE), TEXT_PRIMARY)
        self.surface.blit(rate_caption, rate_caption.get_rect(center=(center_x, top_y + 58)))

        divider_y = top_y + 98
        list_width = min(520, self.content_rect.width - 60)
        list_left = center_x - list_width // 2
        list_right = center_x + list_width // 2
        pg.draw.line(self.surface, PANEL_ALT, (list_left, divider_y), (list_right, divider_y), 3)

        row_left = list_left
        row_right = list_right
        row_top = divider_y + 22
        row_height = 44
        for index, (label, value) in enumerate(rows):
            row_y = row_top + index * row_height
            row_center_y = row_y + row_height // 2
            if index > 0:
                separator_y = row_y - 8
                pg.draw.line(self.surface, PANEL_ALT, (row_left, separator_y), (row_right, separator_y), 1)

            label_surface = render_text(self.body_font, label, TEXT_PRIMARY)
            value_surface = render_text(self.body_font, value, TEXT_MUTED)
            self.surface.blit(label_surface, label_surface.get_rect(midleft=(row_left, row_center_y)))
            self.surface.blit(value_surface, value_surface.get_rect(midright=(row_right, row_center_y)))
