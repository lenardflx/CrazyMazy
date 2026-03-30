# Author: Lenard Felix

from __future__ import annotations
from abc import ABC, abstractmethod
import pygame

class BaseScreen(ABC):
    """
    Base class for all screens in the game.
    Each screen has to inherit from this class and implement the abstract methods.
    """
    def __init__(self, surface: pygame.Surface) -> None:
        self.surface = surface
        self.error_message: str | None = None

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle a pygame event"""

    @abstractmethod
    def update(self, dt: float) -> None:
        """Update the screen state from the last frame."""

    @abstractmethod
    def draw(self) -> None:
        """Draw the screen to the surface."""
