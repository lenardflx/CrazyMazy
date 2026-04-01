from __future__ import annotations

from dataclasses import dataclass

from shared.types.enums import InsertionSide
from client.lang import DisplayMessage, language_service


@dataclass(slots=True, frozen=True)
class TutorialTextStep:
    """Shows explanatory text and advances when the player presses the continue button."""

    text: str
    button_label: str = language_service.get_message(DisplayMessage.TUTORIAL_NEXT)


@dataclass(slots=True, frozen=True)
class TutorialRotateStep:
    """Requires the player to rotate the spare tile in the given direction."""

    text: str
    direction: int


@dataclass(slots=True, frozen=True)
class TutorialShiftStep:
    """Requires the player to insert the spare tile at a specific board edge and index."""

    text: str
    side: InsertionSide
    index: int


@dataclass(slots=True, frozen=True)
class TutorialMoveStep:
    """Requires the player to move to a specific board position."""

    text: str
    position: tuple[int, int]


@dataclass(slots=True, frozen=True)
class TutorialNpcStep:
    """Pauses the script while the tutorial NPC performs its scripted turn."""

    text: str


@dataclass(slots=True, frozen=True)
class TutorialFreeplayStep:
    """Ends the guided sequence and lets the player continue the match in freeplay."""

    text: str
    button_label: str = language_service.get_message(DisplayMessage.TUTORIAL_PLAY)


TutorialStep = (
    TutorialTextStep
    | TutorialRotateStep
    | TutorialShiftStep
    | TutorialMoveStep
    | TutorialNpcStep
    | TutorialFreeplayStep
)

def default_tutorial_steps() -> list[TutorialStep]:
    """Return the default ordered sequence of guided tutorial steps."""
    return [
        TutorialTextStep(
            language_service.get_message(DisplayMessage.TUTORIAL_TEXT_01)
        ),
        TutorialTextStep(
            language_service.get_message(DisplayMessage.TUTORIAL_TEXT_02)
        ),
        TutorialTextStep(
            language_service.get_message(DisplayMessage.TUTORIAL_TEXT_03)  
        ),
        TutorialTextStep(
            language_service.get_message(DisplayMessage.TUTORIAL_TEXT_04)
        ),
        TutorialTextStep(
            language_service.get_message(DisplayMessage.TUTORIAL_TEXT_05)
        ),

        # Cycle 1 — shift somewhere, stay put to show moving is optional
        TutorialShiftStep(
            language_service.get_message(DisplayMessage.TUTORIAL_TEXT_06) +
            language_service.get_message(DisplayMessage.TUTORIAL_TEXT_07),
            side=InsertionSide.LEFT,
            index=3,
        ),
        TutorialMoveStep(
            language_service.get_message(DisplayMessage.TUTORIAL_TEXT_08),
            position=(0, 0),
        ),
        TutorialNpcStep(
            language_service.get_message(DisplayMessage.TUTORIAL_TEXT_09),
        ),

        # Cycle 2 — rotate + shift to unlock the treasure, then collect it
        TutorialRotateStep(
            language_service.get_message(DisplayMessage.TUTORIAL_TEXT_10),
            direction=1,
        ),
        TutorialShiftStep(
            language_service.get_message(DisplayMessage.TUTORIAL_TEXT_11),
            side=InsertionSide.TOP,
            index=1,
        ),
        TutorialMoveStep(
            language_service.get_message(DisplayMessage.TUTORIAL_TEXT_12),
            position=(2, 0),
        ),

        TutorialFreeplayStep(
            language_service.get_message(DisplayMessage.TUTORIAL_TEXT_13),
            button_label="Start",
        ),
    ]
