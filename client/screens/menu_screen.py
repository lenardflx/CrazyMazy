from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Optional

import pygame as pg

from client.screens.base_screen import BaseScreen
from client.screens.menu_ui import ACCENT_DARK, PANEL, TEXT_MUTED, TEXT_PRIMARY, MenuButton
from client.screens.scene_types import SceneTypes

if TYPE_CHECKING:
    from client.screens.scene_manager import SceneManager


BACKGROUND_COLOR = (76, 96, 122)
ButtonTarget = SceneTypes | Callable[[], None]
ButtonSpec = tuple[str, ButtonTarget, str]


class MenuScreen(BaseScreen):
    def __init__(
        self,
        surface: pg.Surface,
        scene_manager: SceneManager,
        *,
        title: str,
        is_main_menu: bool = False,
        buttons: list[ButtonSpec] | None = None,
        message: str = "",
    ) -> None:
        super().__init__(surface)
        self.scene_manager = scene_manager
        self.title = title
        self.is_main_menu = is_main_menu
        self.message = message
        self._requested_scene: SceneTypes | None = None

        self.title_font = pg.font.SysFont("verdana", 42, bold=True)
        self.section_font = pg.font.SysFont("verdana", 24, bold=True)
        self.body_font = pg.font.SysFont("verdana", 18)
        self.small_font = pg.font.SysFont("verdana", 16)
        self.button_font = pg.font.SysFont("verdana", 20, bold=True)

        width, height = self.surface.get_size()
        self.card_rect = pg.Rect(width // 2 - 430, 120, 860, height - 180)
        self.content_rect = self.card_rect.inflate(-56, -56)
        self.back_button = None
        self.buttons: list[MenuButton] = []
        if not self.is_main_menu:
            self.back_button = MenuButton(
                pg.Rect(42, 34, 120, 46),
                "Back",
                lambda: self._request_scene(SceneTypes.MAIN_MENU),
            )
        if buttons:
            self._build_buttons(buttons)

    def _build_buttons(self, specs: list[ButtonSpec]) -> None:
        button_width = 320
        button_height = 56
        gap = 74
        left = self.surface.get_width() // 2 - button_width // 2
        start_y = 240 if self.is_main_menu else self.content_rect.y + 120
        self.buttons = []
        for index, (label, target, variant) in enumerate(specs):
            rect = pg.Rect(left, start_y + index * gap, button_width, button_height)
            action = (
                (lambda scene=target: self._request_scene(scene))
                if isinstance(target, SceneTypes)
                else target
            )
            self.buttons.append(MenuButton(rect, label, action, variant=variant))

    def _request_scene(self, scene: SceneTypes) -> None:
        self._requested_scene = scene

    def handle_event(self, event: pg.event.Event) -> Optional[BaseScreen]:
        if self.back_button is not None:
            self.back_button.handle_event(event)
            if self._requested_scene is not None:
                next_screen = self.scene_manager.switch_scene(self._requested_scene, self.surface)
                self._requested_scene = None
                return next_screen

        self.handle_content_event(event)
        if self._requested_scene is not None:
            next_screen = self.scene_manager.switch_scene(self._requested_scene, self.surface)
            self._requested_scene = None
            return next_screen
        return None

    def update(self, dt: float) -> None:
        del dt

    def draw(self) -> None:
        self.surface.fill(BACKGROUND_COLOR)
        # TODO: replace the flat fill with the final menu background image.

        if self.back_button is not None:
            self.back_button.draw(self.surface, self.button_font)

        if not self.is_main_menu:
            shadow_rect = self.card_rect.move(0, 4)
            pg.draw.rect(self.surface, (64, 81, 104), shadow_rect, border_radius=28)
            pg.draw.rect(self.surface, PANEL, self.card_rect, border_radius=28)
            pg.draw.rect(self.surface, (196, 202, 210), self.card_rect, width=1, border_radius=28)
            self.draw_content(self.content_rect)
        else:
            self.draw_content(self.surface.get_rect())

    def handle_content_event(self, event: pg.event.Event) -> None:
        for button in self.buttons:
            button.handle_event(event)

    def draw_content(self, rect: pg.Rect) -> None:
        if self.is_main_menu:
            title = self.title_font.render(self.title, True, TEXT_PRIMARY)
            self.surface.blit(title, title.get_rect(center=(rect.centerx, 130)))
        else:
            title = self.title_font.render(self.title, True, TEXT_PRIMARY)
            self.surface.blit(title, (self.content_rect.x, self.content_rect.y))

        if self.message:
            text = self.body_font.render(self.message, True, TEXT_MUTED)
            if self.is_main_menu:
                self.surface.blit(text, text.get_rect(center=(rect.centerx, rect.centery + 18)))
            else:
                self.surface.blit(text, (self.content_rect.x, self.content_rect.y + 56))

        for button in self.buttons:
            button.draw(self.surface, self.button_font)
