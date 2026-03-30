from __future__ import annotations

from shared.protocol import ErrorCode

from client.screens.game.views.board_view import BoardClick
from client.tutorial.match import TutorialMatch
from client.tutorial.scenario import (
    TutorialFreeplayStep,
    TutorialMoveStep,
    TutorialNpcStep,
    TutorialRotateStep,
    TutorialShiftStep,
    TutorialStep,
    TutorialTextStep,
    default_tutorial_steps,
)


class TutorialSession:
    """Coordinates the tutorial script on top of the local tutorial match."""

    def __init__(self) -> None:
        self.match = TutorialMatch()
        self._steps = default_tutorial_steps()
        self._step_index = 0
        self._completed = False
        self.last_error: ErrorCode | None = None

    @property
    def completed(self) -> bool:
        """Return whether all tutorial steps have been completed."""
        return self._completed

    @property
    def current_step(self) -> TutorialStep | None:
        """Return the current tutorial step, or None when the tutorial is finished."""
        if self._step_index >= len(self._steps):
            return None
        return self._steps[self._step_index]

    @property
    def snapshot(self):
        """Expose the current tutorial match snapshot for the screen layer."""
        return self.match.snapshot

    @property
    def runtime(self):
        """Expose the tutorial match runtime state for the screen layer."""
        return self.match.runtime

    @property
    def freeplay_started(self) -> bool:
        """Return whether the guided tutorial has transitioned into freeplay."""
        return self.match.freeplay_started

    def update(self, dt: float) -> None:
        """Advance the tutorial match and move past the NPC step when its scripted turn finishes."""
        current = self.current_step
        npc_enabled = self.freeplay_started or isinstance(current, TutorialNpcStep)
        self.match.update(dt, npc_enabled=npc_enabled)
        if isinstance(current, TutorialNpcStep) and self.match.scripted_npc_turn_done:
            self.match.consume_scripted_npc_turn_done()
            self._advance()

    def handle_continue(self) -> None:
        """Advance tutorial steps that use the continue button and start freeplay when requested."""
        step = self.current_step
        if isinstance(step, TutorialTextStep):
            self._advance()
            return
        if isinstance(step, TutorialFreeplayStep):
            self.match.start_freeplay()
            self._advance()

    def handle_board_click(self, click: BoardClick | None) -> bool:
        """Handle a board interaction for either the guided step or freeplay."""
        if click is None:
            return False

        step = self.current_step
        if isinstance(step, TutorialRotateStep) and click == ("rotate", step.direction):
            self.match.rotate_spare(step.direction)
            self.last_error = None
            self._advance()
            return True

        if isinstance(step, TutorialShiftStep) and click == ("shift", step.side, step.index):
            error = self.match.shift_tile(step.side, step.index)
            if error is None:
                self.last_error = None
                self._advance()
                return True
            self.last_error = error
            return False

        if isinstance(step, TutorialMoveStep) and click == ("move", *step.position):
            error = self.match.move_player(*step.position)
            if error is None:
                self.last_error = None
                self._advance()
                return True
            self.last_error = error
            return False

        if self.freeplay_started:
            match click:
                case ("rotate", direction):
                    self.match.rotate_spare(direction)
                    self.last_error = None
                case ("shift", side, index):
                    error = self.match.shift_tile(side, index)
                    self.last_error = error
                    return error is None
                case ("move", x, y):
                    error = self.match.move_player(x, y)
                    self.last_error = error
                    return error is None
            return False

        # Wrong click during the scripted phase — no error message, just ignore.
        return False

    def _advance(self) -> None:
        self._step_index += 1
        if self._step_index >= len(self._steps):
            self._completed = True
