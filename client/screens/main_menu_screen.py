# Author: Lenard Felix

from __future__ import annotations
from typing import Optional
import pygame
from client.screens.base_screen import BaseScreen


class MainMenuScreen(BaseScreen):
    def handle_event(self, event: pygame.event.Event) -> Optional[BaseScreen]:
        return None

    def update(self, dt: float) -> None:
        pass

    def draw(self) -> None:
        self.surface.fill((20, 20, 40))
        font = pygame.font.SysFont(None, 64)
        text = font.render("Hello World", True, (255, 255, 255))
        rect = text.get_rect(center=self.surface.get_rect().center)
        self.surface.blit(text, rect)
