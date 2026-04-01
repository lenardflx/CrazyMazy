# Author: Lenard Felix, Christopher Ionescu

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from client.screens.menu.menu_screen import MenuScreen
from client.state.languages import languages as langs
from client.ui.controls import Button, Checkbox, Slider
from client.ui.theme import TEXT_MUTED, TEXT_PRIMARY, render_text
from client.lang import DisplayMessage, language_service

if TYPE_CHECKING:
    from client.screens.core.scene_manager import SceneManager


class SettingsForm:
    """Reusable settings form used by the menu screen and the in-game overlay."""

    def __init__(
        self,
        surface: pg.Surface,
        scene_manager: SceneManager,
        rect: pg.Rect,
        *,
        body_font: pg.font.Font,
        small_font: pg.font.Font,
        button_font: pg.font.Font,
        label_updater
    ) -> None:
        self.surface = surface
        self.scene_manager = scene_manager
        self.rect = rect
        self.body_font = body_font
        self.small_font = small_font
        self.button_font = button_font
        self.language = langs.ENGLISH
        self._stored_master_volume = 100
        self._build_controls()
        self.reset_from_settings()
        self.label_updater = label_updater

    def _build_controls(self) -> None:
        center_x = self.rect.centerx
        split_gap = 28
        split_slider_width = (self.rect.width - 120 - split_gap) // 2
        top_row_width = split_slider_width * 2 + split_gap
        mute_width = 96
        top_slider_width = top_row_width - mute_width - 16
        master_y = self.rect.y + 64
        music_y = master_y + 78
        settings_y = music_y + 62
        top_row_left = center_x - top_row_width // 2

        self.master_slider = Slider(
            pg.Rect(top_row_left, master_y, top_slider_width, 12),
            language_service.get_message(DisplayMessage.SETTINGS_MASTER_VOLUME),
            100,
        )
        self.mute_button = Button(
            pg.Rect(self.master_slider.rect.right + 16, master_y - 20, 96, 42),
            language_service.get_message(DisplayMessage.SETTINGS_MUTE_SOUND),
            self._toggle_mute,
        )

        split_left = center_x - (split_slider_width * 2 + split_gap) // 2
        self.music_slider = Slider(
            pg.Rect(split_left, music_y, split_slider_width, 12),
            language_service.get_message(DisplayMessage.SETTINGS_MUSIC_VOLUME),
            100,
        )
        self.effects_slider = Slider(
            pg.Rect(split_left + split_slider_width + split_gap, music_y, split_slider_width, 12),
            language_service.get_message(DisplayMessage.SETTINGS_EFFECTS_VOLUME),
            100,
        )

        lower_row_width = top_row_width
        lower_left = center_x - lower_row_width // 2
        language_width = 252
        lower_gap = 20
        fullscreen_width = lower_row_width - language_width - lower_gap
        language_center_x = lower_left + language_width // 2
        fullscreen_x = lower_left + language_width + lower_gap
        display_center_x = fullscreen_x + fullscreen_width // 2
        self.fullscreen_checkbox = Checkbox(
            pg.Rect(display_center_x - 90, settings_y + 44, 180, 32),
            language_service.get_message(DisplayMessage.SETTINGS_FULLSCREEN),
            False,
        )
        self.english_button = Button(
            pg.Rect(language_center_x - 126, settings_y + 44, 120, 42),
            language_service.get_message(DisplayMessage.SETTINGS_ENGLISH),
            lambda: self._set_language(langs.ENGLISH),
            icon="flag_en",
        )
        self.german_button = Button(
            pg.Rect(language_center_x + 6, settings_y + 44, 120, 42),
            language_service.get_message(DisplayMessage.SETTINGS_GERMAN),
            lambda: self._set_language(langs.GERMAN),
            icon="flag_de",
        )
        self._language_label_center = (language_center_x, settings_y)
        self._display_label_center = (display_center_x, settings_y)

    def reset_from_settings(self) -> None:
        settings = self.scene_manager.client_settings
        self.master_slider.value = settings.get_master_volume()
        self.music_slider.value = settings.get_music_volume()
        self.effects_slider.value = settings.get_effects_volume()
        self.fullscreen_checkbox.value = settings.get_fullscreen()
        self.language = settings.get_language()
        self._stored_master_volume = self.master_slider.value or 100
        self._sync_mute_button()
        self._sync_language_buttons()

    def _set_language(self, value: langs) -> None:
        self.language = value
        self._sync_language_buttons()

    def _sync_language_buttons(self) -> None:
        self.english_button.variant = "primary" if self.language == langs.ENGLISH else "secondary"
        self.german_button.variant = "primary" if self.language == langs.GERMAN else "secondary"

    def _sync_mute_button(self) -> None:
        is_muted = self.master_slider.value == 0
        self.mute_button.label = language_service.get_message(DisplayMessage.SETTINGS_UNMUTE_SOUND) if is_muted else language_service.get_message(DisplayMessage.SETTINGS_MUTE_SOUND)
        self.mute_button.variant = "primary" if is_muted else "secondary"

    def _toggle_mute(self) -> None:
        if self.master_slider.value == 0:
            self.master_slider.value = self._stored_master_volume
        else:
            self._stored_master_volume = self.master_slider.value or self._stored_master_volume
            self.master_slider.value = 0
        self._sync_mute_button()

    def apply(self) -> None:
        settings = self.scene_manager.client_settings
        prev_fullscreen = settings.fullscreen
        settings.set_master_volume(self.master_slider.value)
        settings.set_music_volume(self.music_slider.value)
        settings.set_effects_volume(self.effects_slider.value)
        settings.set_language(self.language)
        settings.set_fullscreen(self.fullscreen_checkbox.value)
        self.scene_manager.audio.apply_settings(
            settings.master_volume,
            settings.music_volume,
            settings.effects_volume,
        )
        settings.write_JSON()
        if settings.fullscreen != prev_fullscreen:
            self.scene_manager.apply_fullscreen(settings.fullscreen)
        self.update_labels()

    def handle_event(self, event: pg.event.Event) -> None:
        if self.master_slider.handle_event(event) and self.master_slider.value > 0:
            self._stored_master_volume = self.master_slider.value
        self._sync_mute_button()
        self.music_slider.handle_event(event)
        self.effects_slider.handle_event(event)
        self.fullscreen_checkbox.handle_event(event)
        self.mute_button.handle_event(event)
        self.english_button.handle_event(event)
        self.german_button.handle_event(event)

    def draw(self) -> None:
        self.master_slider.draw(self.surface, self.body_font, self.small_font)
        self.mute_button.draw(self.surface, self.button_font)
        self.music_slider.draw(self.surface, self.body_font, self.small_font)
        self.effects_slider.draw(self.surface, self.body_font, self.small_font)
        display_label = render_text(self.body_font, language_service.get_message(DisplayMessage.SETTINGS_DISPLAY), TEXT_PRIMARY)
        self.surface.blit(display_label, display_label.get_rect(center=self._display_label_center))
        self.fullscreen_checkbox.draw(self.surface, self.body_font)
        language_label = render_text(self.body_font, language_service.get_message(DisplayMessage.SETTINGS_LANGUAGE), TEXT_PRIMARY)
        self.surface.blit(
            language_label,
            language_label.get_rect(center=self._language_label_center),
        )
        self.english_button.draw(self.surface, self.button_font)
        self.german_button.draw(self.surface, self.button_font)

    def update_labels(self) -> None:
        self.fullscreen_checkbox.label = language_service.get_message(DisplayMessage.SETTINGS_FULLSCREEN)
        self.master_slider.label = language_service.get_message(DisplayMessage.SETTINGS_MASTER_VOLUME)
        self.music_slider.label = language_service.get_message(DisplayMessage.SETTINGS_MUSIC_VOLUME)
        self.effects_slider.label = language_service.get_message(DisplayMessage.SETTINGS_EFFECTS_VOLUME)
        
        self.label_updater()


class SettingsScreen(MenuScreen):
    """
    The settings screen. Allows the player to adjust audio, fullscreen, and language preferences.
    Changes are applied only when the Apply button is pressed.
    """

    def __init__(self, surface: pg.Surface, scene_manager: SceneManager) -> None:
        super().__init__(
            surface,
            scene_manager,
            title=language_service.get_message(DisplayMessage.MAIN_MENU_OPTIONS),
            is_main_menu=False,
        )
        form_rect = pg.Rect(
            self.content_rect.x,
            self.content_rect.y + 10,
            self.content_rect.width,
            self.content_rect.height - 110,
        )
        self.form = SettingsForm(
            surface,
            scene_manager,
            form_rect,
            body_font=self.body_font,
            small_font=self.small_font,
            button_font=self.button_font,
            label_updater=self.update_labels
        )
        self.apply_button = Button(
            pg.Rect(self.content_rect.centerx - 90, self.content_rect.bottom - 64, 180, 46),
            language_service.get_message(DisplayMessage.SETTINGS_APPLY),
            self.form.apply,
            variant="primary",
        )

    def handle_content_event(self, event: pg.event.Event) -> None:
        self.form.handle_event(event)
        self.apply_button.handle_event(event)

    def draw_content(self, rect: pg.Rect) -> None:
        super().draw_content(rect)
        self.form.draw()
        self.apply_button.draw(self.surface, self.button_font)

    def update_labels(self):
        self.apply_button.label = language_service.get_message(DisplayMessage.SETTINGS_APPLY)
        self.title = language_service.get_message(DisplayMessage.MAIN_MENU_OPTIONS)
