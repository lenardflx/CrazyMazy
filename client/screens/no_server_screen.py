# Author: Lenard Felix

from __future__ import annotations
from typing import Optional
import pygame
from client.screens.base_screen import BaseScreen


class NoServerScreen(BaseScreen):
    def handle_event(self, event: pygame.event.Event) -> Optional[BaseScreen]:
        return None

    def update(self, dt: float) -> None:
        pass

    def draw(self) -> None:
        self.surface.fill((30, 30, 30))
        font = pygame.font.SysFont(None, 48)
        text = font.render("Server not reachable", True, (220, 80, 80))
        rect = text.get_rect(center=self.surface.get_rect().center)
        self.surface.blit(text, rect)
