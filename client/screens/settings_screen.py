from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from client.screens.menu_screen import MenuScreen
from client.screens.menu_ui import ACCENT_DARK, PANEL_ALT, CheckboxControl, SliderControl

if TYPE_CHECKING:
    from client.screens.scene_manager import SceneManager


class SettingsScreen(MenuScreen):
    SECTION_LAYOUT: list[tuple[str, int]] = [
        ("Sound", 0),
        ("Graphics", 232),
    ]

    CONTROL_LAYOUT: list[int] = [60, 136, 208, 294]

    def __init__(self, surface: pg.Surface, scene_manager: SceneManager) -> None:
        super().__init__(
            surface,
            scene_manager,
            title="Options",
            is_main_menu=False,
        )
        settings = self.scene_manager.client_settings
        self.content_area = pg.Rect(self.content_rect.x, self.content_rect.y + 64, self.content_rect.width, self.content_rect.height - 84)
        control_width = self.content_area.width

        self.controls: list[CheckboxControl | SliderControl] = [
            SliderControl(pg.Rect(0, 92, control_width, 12), "Master Volume", settings.master_volume),
            SliderControl(pg.Rect(0, 166, control_width, 12), "Music Volume", settings.music_volume),
            SliderControl(pg.Rect(0, 240, control_width, 12), "Effects Volume", settings.effects_volume),
            CheckboxControl(pg.Rect(0, 364, control_width, 32), "Fullscreen", settings.fullscreen),
        ]

    def _sync_settings(self) -> None:
        settings = self.scene_manager.client_settings
        settings.master_volume = self.controls[0].value
        settings.music_volume = self.controls[1].value
        settings.effects_volume = self.controls[2].value
        settings.fullscreen = self.controls[3].value

    def _apply_layout(self) -> None:
        left = self.content_area.x
        for control, y in zip(self.controls, self.CONTROL_LAYOUT, strict=False):
            control.rect.x = left
            control.rect.y = self.content_area.y + y

    def handle_content_event(self, event: pg.event.Event) -> None:
        self._apply_layout()
        changed = False
        for control in self.controls:
            if self.content_area.inflate(0, 20).collidepoint(getattr(event, "pos", (-1, -1))):
                changed = control.handle_event(event) or changed

        if changed:
            self._sync_settings()

    def draw_content(self, rect: pg.Rect) -> None:
        super().draw_content(rect)
        self._apply_layout()
        for title, y in self.SECTION_LAYOUT:
            self._draw_section_header(title, y)
        for control in self.controls:
            control.draw(self.surface, self.body_font, self.small_font)

    def _draw_section_header(self, title: str, y: int) -> None:
        header_y = self.content_area.y + y
        label = self.section_font.render(title, True, (44, 31, 24))
        self.surface.blit(label, (self.content_area.x, header_y))
