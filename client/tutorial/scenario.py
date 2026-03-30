from __future__ import annotations

from dataclasses import dataclass

from shared.types.enums import InsertionSide


@dataclass(slots=True, frozen=True)
class TutorialTextStep:
    """Shows explanatory text and advances when the player presses the continue button."""

    text: str
    button_label: str = "Next"


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
    button_label: str = "Play"


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
            "Welcome! This tutorial will teach you the basics of the game."
        ),
        TutorialTextStep(
            "Each turn, you have to insert the spare tile into the board to shift a row or column and move your player"
        ),
        TutorialTextStep(
            "Your goal is to collect all your treasures and return to your starting corner."    
        ),
        TutorialTextStep(
            "On the right, you can see the spare tile that will be inserted on your turn. You can rotate it before inserting. "
        ),
        TutorialTextStep(
            "Next to the spare tile, you can see your current target treasure. Collect it to move on to the next one."
        ),

        # Cycle 1 — shift somewhere, stay put to show moving is optional
        TutorialShiftStep(
            "Insert the spare tile from the left at row 3. "
            "Your treasure is not reachable yet — watch how the tiles shift.",
            side=InsertionSide.LEFT,
            index=3,
        ),
        TutorialMoveStep(
            "You can always stay on your current tile. Click it to end your turn without moving.",
            position=(0, 0),
        ),
        TutorialNpcStep(
            "The opponent takes their turn now.",
        ),

        # Cycle 2 — rotate + shift to unlock the treasure, then collect it
        TutorialRotateStep(
            "Rotate the spare tile once to the right so it opens a path eastward.",
            direction=1,
        ),
        TutorialShiftStep(
            "Insert from the top at column 1. This connects your starting corner to your treasure.",
            side=InsertionSide.TOP,
            index=1,
        ),
        TutorialMoveStep(
            "Move east to collect your treasure.",
            position=(2, 0),
        ),

        TutorialFreeplayStep(
            "Well done! Now try to collect all your remaining treasures, and return to your starting corner to win the game.",
            button_label="Start",
        ),
    ]
