from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from client.screens.core.scene_types import SceneTypes
from client.screens.game.game_screen import GameScreen
from client.screens.game.post_game_screen import PostGameScreen
from client.screens.game.views.board_view import GameBoardLayout
from client.state.runtime_state import GameRuntimeState
from client.tutorial import (
    TutorialFreeplayStep,
    TutorialMoveStep,
    TutorialNpcStep,
    TutorialRotateStep,
    TutorialSession,
    TutorialShiftStep,
    TutorialTextStep,
)
from client.ui.controls import Button
from client.ui.dialogs import ConfirmDialog
from client.ui.theme import ACCENT, PANEL, PANEL_ALT, TEXT_PRIMARY, font
from shared.game.snapshot import SnapshotGameState
from shared.types.enums import GamePhase

if TYPE_CHECKING:
    from client.screens.core.scene_manager import SceneManager


class TutorialScreen(GameScreen):
    """Interactive guided tutorial that transitions into local freeplay."""

    def __init__(self, surface: pg.Surface, scene_manager: SceneManager) -> None:
        super().__init__(surface, scene_manager)
        self.give_up_button = None  # No give-up in tutorial
        if scene_manager.tutorial_session is None:
            scene_manager.tutorial_session = TutorialSession()
        self.session = scene_manager.tutorial_session
        self.body_font = font(18)
        self.continue_button = Button(pg.Rect(0, 0, 120, 40), "Next", self._continue_step, variant="primary")

    @property
    def _game_runtime(self) -> GameRuntimeState:
        """Override to return the tutorial session's runtime state instead of a normal match runtime."""
        return self.session.runtime

    @property
    def _game_snapshot(self) -> SnapshotGameState | None:
        """Override to return the tutorial session's snapshot instead of a normal match snapshot."""
        return self.session.snapshot

    def _confirm_quit(self) -> None:
        """Open a confirmation dialog to confirm if the player really wants to leave the tutorial and return to the main menu."""
        self.dialog = ConfirmDialog(
            self.surface.get_rect(),
            "Leave Tutorial?",
            "Return to the main menu?",
            self._leave_to_menu,
            self._close_dialog,
            confirm_label="Leave",
        )

    def _leave_to_menu(self) -> None:
        """Leave the tutorial and return to the main menu."""
        self.dialog = None
        self.scene_manager.tutorial_session = None
        self.scene_manager.go_to(SceneTypes.MAIN_MENU)

    def _continue_step(self) -> None:
        before = self.session.freeplay_started
        self.session.handle_continue()
        if not before and self.session.freeplay_started:
            self.scene_manager.client_settings.set_tutorial(True)

    def handle_event(self, event: pg.event.Event) -> None:
        if self.dialog is not None:
            self.dialog.handle_event(event)
            return

        self.menu_button.handle_event(event)
        self.continue_button.handle_event(event)

        snapshot = self._game_snapshot
        layout = self._game_layout()
        if snapshot is None or layout is None:
            return
        if self._game_runtime.shift_animation is not None or self._game_runtime.move_animation is not None:
            return
        if event.type != pg.MOUSEBUTTONDOWN or event.button != 1:
            return

        click = self.board_view.resolve_click(event.pos, layout, snapshot)
        self._handle_board_click(click)

    def _handle_board_click(self, click) -> None:
        self.session.handle_board_click(click)

    def update(self, dt: float) -> None:
        self.session.update(dt)
        snapshot = self._game_snapshot
        if snapshot is not None and snapshot.phase == GamePhase.POSTGAME:
            self.scene_manager.go_to(SceneTypes.POST_GAME)

    def _draw_overlay(self, layout: GameBoardLayout) -> None:
        self._draw_step_overlay(layout)
        self._draw_step_highlight(layout)

    def _draw_step_overlay(self, layout: GameBoardLayout) -> None:
        step = self.session.current_step
        if step is None:
            return

        overlay = pg.Rect(self.surface.get_width() - 444, self.surface.get_height() - 170, 420, 140)
        pg.draw.rect(self.surface, PANEL, overlay, border_radius=16)
        pg.draw.rect(self.surface, PANEL_ALT, overlay, width=1, border_radius=16)

        if isinstance(step, (TutorialTextStep, TutorialRotateStep, TutorialShiftStep, TutorialMoveStep, TutorialNpcStep, TutorialFreeplayStep)):
            self._draw_wrapped_text(step.text, overlay.x + 16, overlay.y + 14, overlay.width - 150)

        self.continue_button.enabled = isinstance(step, (TutorialTextStep, TutorialFreeplayStep))
        self.continue_button.label = step.button_label if isinstance(step, (TutorialTextStep, TutorialFreeplayStep)) else "Next"
        self.continue_button.rect = pg.Rect(overlay.right - 130, overlay.bottom - 52, 110, 36)
        if self.continue_button.enabled:
            self.continue_button.draw(self.surface, self.button_font)

    def _draw_step_highlight(self, layout: GameBoardLayout) -> None:
        step = self.session.current_step
        if step is None:
            return

        target: pg.Rect | None = None
        if isinstance(step, TutorialRotateStep):
            target = layout.rotate_right_button if step.direction > 0 else layout.rotate_left_button
        elif isinstance(step, TutorialShiftStep):
            target = next(
                (arrow.rect for arrow in layout.arrows if arrow.side == step.side and arrow.index == step.index),
                None,
            )
        elif isinstance(step, TutorialMoveStep):
            target = layout.cells.get(step.position)

        if target is None:
            return

        highlight = target.inflate(12, 12)
        pg.draw.rect(self.surface, ACCENT, highlight, width=3, border_radius=16)

    def _draw_wrapped_text(self, text: str, x: int, y: int, width: int) -> None:
        words = text.split()
        line = ""
        lines: list[str] = []
        for word in words:
            candidate = word if not line else f"{line} {word}"
            if self.body_font.size(candidate)[0] <= width:
                line = candidate
                continue
            if line:
                lines.append(line)
            line = word
        if line:
            lines.append(line)

        for index, current in enumerate(lines):
            rendered = self.body_font.render(current, True, TEXT_PRIMARY)
            self.surface.blit(rendered, (x, y + index * (self.body_font.get_height() + 4)))


class TutorialPostGameScreen(PostGameScreen):
    """Reuses the normal post-game layout for completed tutorial matches."""

    @property
    def _game_snapshot(self) -> SnapshotGameState | None:
        if self.scene_manager.tutorial_session is None:
            return None
        return self.scene_manager.tutorial_session.snapshot

    def _play_again(self) -> None:
        self.scene_manager.tutorial_session = TutorialSession()
        self.scene_manager.go_to(SceneTypes.TUTORIAL)

    def _leave_post_game(self) -> None:
        self.scene_manager.tutorial_session = None
        self.scene_manager.go_to(SceneTypes.MAIN_MENU)
