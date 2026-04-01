from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from pygame import Rect, Surface

from client.ui.theme import draw_pixel_rect, PANEL_ERROR, PANEL_ERROR_SHADOW, render_text, font, TEXT_MUTED, \
    TEXT_PRIMARY
from shared.types.enums import InsertionSide, TreasureType
from shared.lib.lobby import VALID_BOARD_SIZES, VALID_INSERT_TIMEOUTS, VALID_MOVE_TIMEOUTS


# TODO: docs after error handling is refactored

class PendingRequest(StrEnum):
    CREATE_LOBBY = "CREATE_LOBBY"
    JOIN_LOBBY = "JOIN_LOBBY"
    START_GAME = "START_GAME"
    ADD_NPC = "ADD_NPC"
    SHIFT_TILE = "SHIFT_TILE"
    MOVE_PLAYER = "MOVE_PLAYER"
    GIVE_UP = "GIVE_UP"
    LEAVE_GAME = "LEAVE_GAME"


@dataclass(slots=True)
class CreateLobbyFormState:
    """Persists form inputs and validation errors for the create-lobby screen across re-renders."""
    player_name: str = ""
    board_size: int = min(VALID_BOARD_SIZES)
    insert_timeout: int = 60 if 60 in VALID_INSERT_TIMEOUTS else max(VALID_INSERT_TIMEOUTS)
    move_timeout: int = 60 if 60 in VALID_INSERT_TIMEOUTS else max(VALID_INSERT_TIMEOUTS)
    is_public: bool = False
    player_limit: int = 4


@dataclass(slots=True)
class JoinLobbyFormState:
    """Persists form inputs and validation errors for the join-lobby screen across re-renders."""
    player_name: str = ""
    join_code: str = ""
    join_public: bool = False


@dataclass(slots=True)
class ErrorPopupAnimation:
    progress: float = 0.0
    """The animation progress in both directions, either for pop up or fade away"""

    stay_time: float = 0.0
    """How long the error message was fully visible to the user"""

    text: str = "Internal error"
    duration: float = 0.5  # seconds
    fade_away_duration = 0.5 # seconds
    stay_duration: float = 5

    _rect: Rect | None = None
    _text_surface: Surface | None = None
    _state: int = 0
    """
    The current phase of the animation, where 0 is the pop-up, 1 is the error message 
    being displayed and 2 is the error message fading away. 
    """

    @property
    def is_finished(self) -> bool:
        return self._state == 2 and self.progress >= 1.0

    @property
    def eased_progress(self) -> float:
        """Returns an ease-out version of the raw progress value for smoother animation."""
        clamped = min(max(self.progress, 0.0), 1.0)
        return 1.0 - (1.0 - clamped) * (1.0 - clamped)

    @property
    def linear_progress(self) -> float:
        return self.progress

    def advance(self, dt: float) -> None:
        """Advance the animation by the given delta time in seconds."""
        # if the animation has no or negative duration, it is instant, so finish immediately
        if self.duration <= 0:
            self.progress = 1.0
            return

        # if the current animation phase is completed, immediately switch to the next
        if self.progress >= 1.0:
            # only change to the next animation state if there is one
            if self._state < 2:
                self._state += 1
                self.progress = 0.0
            else:
                self.progress = 1.0

        # get the current duration based on the current phase of the animation
        current_duration = self.duration
        match self._state:
            case 0: current_duration = self.duration
            case 1: current_duration = self.stay_duration
            case _: current_duration = self.fade_away_duration

        self.progress = min(1.0, self.progress + (dt / current_duration))

    def draw(self, surface: Surface, center: tuple[int, int], max_width: int, max_height: int) -> None:
        current_width = max_width

        # Pop-up phase: growing the rectangle from the center
        if self._state == 0:
            current_width = max(1, int(max_width * self.eased_progress))
        # display state: show the error for the given duration
        elif self._state == 1:
            current_width = max_width
        # pop-out phase: the rect shrinks again
        elif self._state == 2:
            current_width = max(1, int(max_width * (1.0 - self.eased_progress)))

        anchor_x = center[0] - current_width // 2
        anchor_y = center[1] - max_height // 2
        self._rect = Rect(anchor_x, anchor_y, current_width, max_height)

        draw_pixel_rect(surface=surface,
                        rect=self._rect,
                        fill=PANEL_ERROR,
                        border=PANEL_ERROR,
                        shadow=PANEL_ERROR_SHADOW)

        fnt = font(19)
        padding = 16

        # when text is centered, we have padding/2 pixels on each side
        available_width = max(1, max_width - padding)

        words = self.text.split(' ')
        line1, line2 = "", ""

        for word in words:
            if not line1:
                line1 = word
            elif fnt.size(line1 + " " + word)[0] <= available_width:
                line1 += " " + word
            elif not line2:
                line2 = word
            elif fnt.size(line2 + " " + word)[0] <= available_width:
                line2 += " " + word
            else:
                # when there are still too many words, simply drop them
                # and add ... to show there is more content to display
                line2 += "..."
                break

        wrapped_lines = [line for line in (line1, line2) if line]

        original_clip = surface.get_clip()
        surface.set_clip(self._rect)

        line_height = fnt.get_linesize()
        total_height = line_height * len(wrapped_lines)
        start_y = center[1] - total_height // 2

        for i, line in enumerate(wrapped_lines):
            text_surf = render_text(font_obj=fnt, text=line, color=TEXT_PRIMARY)
            text_rect = text_surf.get_rect(centerx=center[0], top=start_y + (i * line_height))
            surface.blit(text_surf, text_rect)

        surface.set_clip(original_clip)


@dataclass(slots=True)
class BoardShiftAnimation:
    """Client-side animation state for a board row/column shift. Advanced each frame by the game screen."""

    side: InsertionSide
    index: int
    progress: float = 0.0
    duration: float = 0.18  # seconds

    @property
    def is_finished(self) -> bool:
        return self.progress >= 1.0

    @property
    def eased_progress(self) -> float:
        """Returns an ease-out version of the raw progress value for smoother animation."""
        clamped = min(max(self.progress, 0.0), 1.0)
        return 1.0 - (1.0 - clamped) * (1.0 - clamped)

    def advance(self, dt: float) -> None:
        """Advance the animation by the given delta time in seconds."""
        if self.duration <= 0:
            self.progress = 1.0
            return
        self.progress = min(1.0, self.progress + (dt / self.duration))


@dataclass(slots=True)
class PlayerMoveAnimation:
    """Client-side animation state for a player movement along a path. Advanced each frame by the game screen."""

    player_id: str
    path: list[tuple[int, int]]
    collected_treasure_type: TreasureType | None = None  # Set if the player collected a treasure during this move
    progress: float = 0.0
    duration_per_step: float = 0.16  # seconds per path step

    @property
    def is_finished(self) -> bool:
        return self.progress >= 1.0

    @property
    def eased_progress(self) -> float:
        """Returns an ease-out version of the raw progress value for smoother animation."""
        clamped = min(max(self.progress, 0.0), 1.0)
        return 1.0 - (1.0 - clamped) * (1.0 - clamped)

    @property
    def duration(self) -> float:
        """Total animation duration in seconds, scaled by the number of steps in the path."""
        return max(0.01, max(1, len(self.path) - 1) * self.duration_per_step)

    def advance(self, dt: float) -> None:
        """Advance the animation by the given delta time in seconds."""
        self.progress = min(1.0, self.progress + (dt / self.duration))


@dataclass(slots=True)
class TreasureCollectAnimation:
    """Client-side animation state for a newly collected treasure card in the player sidebar."""

    player_id: str
    treasure_type: TreasureType
    progress: float = 0.0
    duration: float = 0.45

    @property
    def is_finished(self) -> bool:
        return self.progress >= 1.0

    @property
    def eased_progress(self) -> float:
        clamped = min(max(self.progress, 0.0), 1.0)
        return 1.0 - (1.0 - clamped) * (1.0 - clamped)

    def advance(self, dt: float) -> None:
        if self.duration <= 0:
            self.progress = 1.0
            return
        self.progress = min(1.0, self.progress + (dt / self.duration))


@dataclass(slots=True)
class GameRuntimeState:
    """Holds mutable in-game client state that is not derived from the server snapshot."""
    spare_rotation: int = 0  # The current local rotation of the spare tile (0–3)
    shift_animation: BoardShiftAnimation | None = None
    move_animation: PlayerMoveAnimation | None = None
    treasure_collect_animation: TreasureCollectAnimation | None = None


@dataclass(slots=True)
class RuntimeState:
    """
    Top-level mutable client state that lives for the entire session.
    Aggregates form state and in-game state
    """
    create_lobby: CreateLobbyFormState = field(default_factory=CreateLobbyFormState)
    join_lobby: JoinLobbyFormState = field(default_factory=JoinLobbyFormState)
    game: GameRuntimeState = field(default_factory=GameRuntimeState)
