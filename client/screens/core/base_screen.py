# Author: Lenard Felix

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
import pygame


class BaseScreen(ABC):
    """Base class for all screens in the game."""
    def __init__(self, surface: pygame.Surface) -> None:
        self.surface = surface

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> Optional[BaseScreen]: 
        """Handle an event and return the new screen if it should change, or None to stay on the current screen."""

    @abstractmethod
    def update(self, dt: float) -> None:
        """Update the screen state from the last frame."""

    @abstractmethod
    def draw(self) -> None:
        """Draw the screen to the surface."""
