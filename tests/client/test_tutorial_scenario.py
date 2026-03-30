from __future__ import annotations

from client.tutorial.scenario import (
    TutorialFreeplayStep,
    TutorialMoveStep,
    TutorialNpcStep,
    TutorialRotateStep,
    TutorialShiftStep,
    TutorialTextStep,
    default_tutorial_steps,
)
from shared.types.enums import InsertionSide


def test_default_tutorial_steps_follow_expected_sequence() -> None:
    steps = default_tutorial_steps()

    assert isinstance(steps[0], TutorialTextStep)
    assert isinstance(steps[1], TutorialTextStep)
    assert isinstance(steps[2], TutorialShiftStep)
    assert isinstance(steps[3], TutorialMoveStep)
    assert isinstance(steps[4], TutorialNpcStep)
    assert isinstance(steps[5], TutorialRotateStep)
    assert isinstance(steps[6], TutorialShiftStep)
    assert isinstance(steps[7], TutorialMoveStep)
    assert isinstance(steps[8], TutorialFreeplayStep)

    assert steps[5].direction == 1
    assert steps[6].side == InsertionSide.TOP
    assert steps[6].index == 1
    assert steps[7].position == (2, 0)
