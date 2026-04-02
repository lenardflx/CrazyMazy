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
    assert isinstance(steps[2], TutorialTextStep)
    assert isinstance(steps[3], TutorialTextStep)
    assert isinstance(steps[4], TutorialTextStep)
    assert isinstance(steps[5], TutorialShiftStep)
    assert isinstance(steps[6], TutorialMoveStep)
    assert isinstance(steps[7], TutorialNpcStep)
    assert isinstance(steps[8], TutorialRotateStep)
    assert isinstance(steps[9], TutorialShiftStep)
    assert isinstance(steps[10], TutorialMoveStep)
    assert isinstance(steps[11], TutorialFreeplayStep)

    assert steps[8].direction == 1
    assert steps[9].side == InsertionSide.TOP
    assert steps[9].index == 1
    assert steps[10].position == (2, 0)
