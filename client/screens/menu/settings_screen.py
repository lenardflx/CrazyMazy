# Author: Lenard Felix

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from client.ui.controls import Checkbox, Slider, Button
from client.ui.theme import TEXT_PRIMARY, render_text
from client.screens.menu.menu_screen import MenuScreen

if TYPE_CHECKING:
    from client.screens.core.scene_manager import SceneManager


class SettingsScreen(MenuScreen):
    """
    The settings (options) screen. Allows the player to adjust master/music/effects volume and toggle fullscreen.
    Changes are applied live to the audio manager and persisted immediately to the JSON settings file.
    """

    SECTION_LAYOUT: list[tuple[str, int, int]] = [
        ("Sound", 0, 0),
        ("Graphics", 0, 240),
        ("Language", 280, 240),
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
        self.language = settings.get_language()

        # Sliders for master, music, effects and language channels
        self.control_sliders = [
            Slider(pg.Rect(0, 92, control_width, 12), "Master Volume", settings.get_master_volume()),
            Slider(pg.Rect(0, 166, control_width, 12), "Music Volume", settings.get_music_volume()),
            Slider(pg.Rect(0, 240, control_width, 12), "Effects Volume", settings.get_effects_volume()),
        ]
        self.fullscreen_checkbox = Checkbox(pg.Rect(0, 324, 128, 32), "Fullscreen", settings.fullscreen)
        # Apply button to explicitly save settings (live changes also auto-save, this makes the intention explicit)
        self.apply_button = Button(
                pg.Rect(860, 580, 120, 46),
                "Apply",
                lambda: self._sync_settings(),
        )

        self.english_button = Button(pg.Rect(520, 500, 120, 46), "English", lambda: self.__set_language(0), variant = "primary" if self.language == 0 else "secondary")
        self.german_button =  Button(pg.Rect(660, 500, 120, 46), "German", lambda: self.__set_language(1), variant = "primary" if self.language == 1 else "secondary")

    def _sync_settings(self) -> None:
        """Read all control values, write them to ClientData, and apply audio and fullscreen changes."""
        settings = self.scene_manager.client_settings
        settings.set_master_volume(self.control_sliders[0].value)
        settings.set_music_volume(self.control_sliders[1].value)
        settings.set_effects_volume(self.control_sliders[2].value)
        settings.set_language(self.language)
        settings.set_fullscreen(self.fullscreen_checkbox.value)
        self.scene_manager.apply_fullscreen(self.fullscreen_checkbox.value)

    def _apply_layout(self) -> None:
        """Position all controls according to CONTROL_LAYOUT. Called each frame so the layout stays correct after window resize."""
        left = self.content_area.x
        controls: list[Slider | Checkbox | Button] = [*self.control_sliders,
                                                        self.fullscreen_checkbox,
                                                        self.apply_button,
                                                        self.english_button,
                                                        self.german_button,]
        
        for control, y in zip(controls, self.CONTROL_LAYOUT, strict=False):
            control.rect.x = left
            control.rect.y = self.content_area.y + y

    def handle_content_event(self, event: pg.event.Event) -> None:
        """Handle control interactions. Live-applies audio settings and persists them on any change."""
        self._apply_layout()
        changed = False
        pointer_in_content = self.content_area.inflate(0, 20).collidepoint(getattr(event, "pos", (-1, -1)))
        
        for slider in self.control_sliders:
            if pointer_in_content:
                changed = slider.handle_event(event) or changed
        if pointer_in_content:
            changed = self.fullscreen_checkbox.handle_event(event) or changed

        self.apply_button.handle_event(event)

        self.english_button.handle_event(event)
        self.german_button.handle_event(event)

        if changed:
            prev_fullscreen = self.scene_manager.client_settings.fullscreen
            settings = self.scene_manager.client_settings
            self.scene_manager.audio.apply_settings(
                settings.master_volume,
                settings.music_volume,
                settings.effects_volume,
            )
            settings.write_JSON()
            if settings.fullscreen != prev_fullscreen:
                self.scene_manager.apply_fullscreen(settings.fullscreen)

    def draw_content(self, rect: pg.Rect) -> None:
        """Draw section headers and all controls."""
        super().draw_content(rect)
        self._apply_layout()
        for title, x, y in self.SECTION_LAYOUT:
            self._draw_section_header(title, x, y)
        for slider in self.control_sliders:
            slider.draw(self.surface, self.body_font, self.small_font)
        self.fullscreen_checkbox.draw(self.surface, self.body_font)
        self.apply_button.draw(self.surface, self.button_font)
        self.english_button.draw(self.surface, self.button_font)
        self.german_button.draw(self.surface, self.button_font)

    def _draw_section_header(self, title: str, x: int, y: int) -> None:
        """Render a bold section label at the given vertical offset within the content area.

        :param y: Offset in pixels from the top of the content area.
        """
        header_x = self.content_area.x + x
        header_y = self.content_area.y + y
        label = render_text(self.section_font, title, TEXT_PRIMARY)
        self.surface.blit(label, (header_x, header_y))

    #Ändere Sprache
    def __set_language(self, val):
        self.language = val
        self.english_button.variant = "primary" if self.language == 0 else "secondary"
        self.german_button.variant = "primary" if self.language == 1 else "secondary"
