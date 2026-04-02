# Author: Lenard Felix, Raphael Eiden

from __future__ import annotations
from abc import ABC, abstractmethod
import pygame

from client.config import WINDOW_HEIGHT
from client.state.runtime_state import ErrorPopupAnimation


class BaseScreen(ABC):
    """
    Base class for all screens in the game.
    Each screen has to inherit from this class and implement the abstract methods.
    """
    def __init__(self, surface: pygame.Surface) -> None:
        self.surface = surface

        # text field reserved for an error message. Can be rendered
        # optionally in the `draw` method.
        self.error_message: str | None = None
        self._current_error: int = 0
        self._seen_error_version: int = 0
        self.error_animation: ErrorPopupAnimation | None = None

    def set_error_message(self, error_message: str) -> None:
        self.error_message = error_message
        self._current_error += 1
        scene_manager = getattr(self, "scene_manager", None)
        if scene_manager is not None:
            scene_manager.audio.play_sfx("error")

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle a pygame event"""

    def update(self, dt: float) -> None:
        """Update the screen state from the last frame."""
        if self.error_animation is not None:
            self.error_animation.advance(dt)
            if self.error_animation.is_finished:
                self.error_animation = None

    def draw(self) -> None:
        """Draw the screen to the surface."""
        if self._seen_error_version < self._current_error and (self.error_animation is None or self.error_animation.text != self.error_message):
            self.error_animation = ErrorPopupAnimation(text=self.error_message)
            self._seen_error_version = self._current_error
        if self.error_animation is not None:
            self.error_animation.draw(self.surface,
                                      (self.surface.get_width() - 175, WINDOW_HEIGHT - 50),
                                      300,
                                      50)
