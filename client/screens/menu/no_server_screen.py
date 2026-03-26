# Author: Lenard Felix

from __future__ import annotations
import pygame
from client.screens.core.base_screen import BaseScreen


class NoServerScreen(BaseScreen):
    def __init__(self, surface: pygame.Surface) -> None:
        super().__init__(surface)

    def handle_event(self, event: pygame.event.Event) -> None:
        del event

    def update(self, dt: float) -> None:
        pass

    def draw(self) -> None:
        self.surface.fill((30, 30, 30))
        font = pygame.font.SysFont(None, 48)
        text = font.render("Server not reachable", True, (220, 80, 80))
        rect = text.get_rect(center=self.surface.get_rect().center)
        self.surface.blit(text, rect)
