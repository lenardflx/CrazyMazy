from __future__ import annotations

import time

from . import _sunfish as sunfish


class WaitingChessGame:
    """
    Lightweight chess game state for the lobby easter egg.

    The player is always white. After each white move the sunfish engine searches for up to
    AI_DELAY seconds (depth-limited to 5) and plays the best move it finds.
    History is stored as a list of sunfish Positions — each entry is from the moving player's
    perspective (sunfish convention), so even-indexed entries are black's view.
    """

    AI_DELAY = 0.35

    def __init__(self) -> None:
        self.reset()

    @property
    def position(self) -> sunfish.Position:
        return self.history[-1]

    @property
    def white_to_move(self) -> bool:
        return len(self.history) % 2 == 1

    def reset(self) -> None:
        """Restart the game from the initial position."""
        self.history = sunfish.initial_history()
        self.selected_square: str | None = None
        self.ai_delay_remaining = 0.0
        self.game_over = False

    def update(self, dt: float) -> None:
        """Tick the AI: counts down the pre-move delay, then runs the sunfish search and applies the best move found."""
        if self.game_over or self.white_to_move:
            return
        self.ai_delay_remaining = max(0.0, self.ai_delay_remaining - dt)
        if self.ai_delay_remaining > 0.0:
            return

        best_move: sunfish.Move | None = None
        started_at = time.time()
        for depth, gamma, score, move in sunfish.Searcher().search(self.history):
            if move is not None and score >= gamma:
                best_move = move
            if time.time() - started_at >= self.AI_DELAY:
                break
            if depth >= 5 and best_move is not None:
                break

        if best_move is None:
            self.game_over = True
            return

        self._apply_move(best_move)

    def click_square(self, square: str) -> None:
        """Handle a board click: select a piece, deselect it, or attempt a move to the target square."""
        if self.game_over or not self.white_to_move:
            return

        legal_moves = self._legal_moves(self.position)
        piece = self.piece_at(square)
        if self.selected_square is None:
            if piece.isupper() and any(move.i == sunfish.parse(square) for move in legal_moves):
                self.selected_square = square
            return

        if square == self.selected_square:
            self.selected_square = None
            return

        source_index = sunfish.parse(self.selected_square)
        destination_index = sunfish.parse(square)
        matching_moves = [move for move in legal_moves if move.i == source_index and move.j == destination_index]
        if not matching_moves:
            if piece.isupper() and any(move.i == destination_index for move in legal_moves):
                self.selected_square = square
            else:
                self.selected_square = None
            return

        move = next((candidate for candidate in matching_moves if candidate.prom == "Q"), matching_moves[0])
        self._apply_move(move)
        if self.game_over:
            return
        self.ai_delay_remaining = self.AI_DELAY

    def _apply_move(self, move: sunfish.Move) -> None:
        """Push a move onto the history and check for game over (no legal replies)."""
        self.history.append(self.position.move(move))
        self.selected_square = None
        if not self._legal_moves(self.position):
            self.game_over = True

    def piece_at(self, square: str) -> str:
        """Return the board character at a square from white's perspective. '.' means empty."""
        position = self.position if self.white_to_move else self.position.rotate()
        return position.board[sunfish.parse(square)]

    def legal_destinations(self) -> set[str]:
        """Return the set of squares the selected piece can legally move to, used for rendering move hints."""
        if self.selected_square is None or self.game_over or not self.white_to_move:
            return set()
        source = sunfish.parse(self.selected_square)
        return {sunfish.render(move.j) for move in self._legal_moves(self.position) if move.i == source}

    def _legal_moves(self, position: sunfish.Position) -> list[sunfish.Move]:
        """Filter pseudo-legal sunfish moves down to moves that do not leave the mover's king capturable."""
        return [move for move in position.gen_moves() if self._is_legal_move(position, move)]

    def _is_legal_move(self, position: sunfish.Position, move: sunfish.Move) -> bool:
        """A move is legal if, after it is made, the opponent cannot immediately capture the mover's king."""
        return not self._opponent_can_capture_king(position.move(move))

    def _opponent_can_capture_king(self, position: sunfish.Position) -> bool:
        """Check whether the side to move in the given position has a pseudo-legal king capture available."""
        for move in position.gen_moves():
            if position.board[move.j] == "k":
                return True
        return False
