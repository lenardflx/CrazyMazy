# Author: Lenard Felix

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from client.ui.controls import Checkbox, Slider
from client.ui.theme import TEXT_PRIMARY
from client.screens.menu.menu_screen import MenuScreen

if TYPE_CHECKING:
    from client.screens.core.scene_manager import SceneManager


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

        self.volume_sliders = [
            Slider(pg.Rect(0, 92, control_width, 12), "Master Volume", settings.master_volume),
            Slider(pg.Rect(0, 166, control_width, 12), "Music Volume", settings.music_volume),
            Slider(pg.Rect(0, 240, control_width, 12), "Effects Volume", settings.effects_volume),
        ]
        self.fullscreen_checkbox = Checkbox(pg.Rect(0, 364, control_width, 32), "Fullscreen", settings.fullscreen)

    def _sync_settings(self) -> None:
        settings = self.scene_manager.client_settings
        settings.set_master_volume(self.volume_sliders[0].value)
        settings.set_music_volume(self.volume_sliders[1].value)
        settings.set_effects_volume(self.volume_sliders[2].value)
        settings.set_fullscreen(self.fullscreen_checkbox.value)
        #settings.master_volume = self.volume_sliders[0].value
        #settings.music_volume = self.volume_sliders[1].value
        #settings.effects_volume = self.volume_sliders[2].value
        #settings.fullscreen = self.fullscreen_checkbox.value

    def _apply_layout(self) -> None:
        left = self.content_area.x
        controls: list[Slider | Checkbox] = [*self.volume_sliders, self.fullscreen_checkbox]
        for control, y in zip(controls, self.CONTROL_LAYOUT, strict=False):
            control.rect.x = left
            control.rect.y = self.content_area.y + y

    def handle_content_event(self, event: pg.event.Event) -> None:
        self._apply_layout()
        changed = False
        pointer_in_content = self.content_area.inflate(0, 20).collidepoint(getattr(event, "pos", (-1, -1)))
        for slider in self.volume_sliders:
            if pointer_in_content:
                changed = slider.handle_event(event) or changed
        if pointer_in_content:
            changed = self.fullscreen_checkbox.handle_event(event) or changed

        if changed:
            self._sync_settings()

    def draw_content(self, rect: pg.Rect) -> None:
        super().draw_content(rect)
        self._apply_layout()
        for title, y in self.SECTION_LAYOUT:
            self._draw_section_header(title, y)
        for slider in self.volume_sliders:
            slider.draw(self.surface, self.body_font, self.small_font)
        self.fullscreen_checkbox.draw(self.surface, self.body_font)

    def _draw_section_header(self, title: str, y: int) -> None:
        header_y = self.content_area.y + y
        label = self.section_font.render(title, True, TEXT_PRIMARY)
        self.surface.blit(label, (self.content_area.x, header_y))
