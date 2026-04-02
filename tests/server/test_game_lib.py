# Author: Lenard Felix

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from server.lib.game import can_join_game, is_valid_board_size, is_valid_join_code, normalize_join_code
from shared.types.enums import GamePhase, PlayerStatus
from shared.types.data import GameData, PlayerData


@dataclass
class FakeGame:
    board_size: int
    game_phase: GamePhase
    player_limit: int


@dataclass
class FakePlayer:
    status: PlayerStatus


def make_game(*, board_size: int = 7, phase: GamePhase = GamePhase.PREGAME, player_limit: int = 4) -> FakeGame:
    return FakeGame(board_size=board_size, game_phase=phase, player_limit=player_limit)


def make_player(*, status: PlayerStatus = PlayerStatus.ACTIVE) -> FakePlayer:
    return FakePlayer(status=status)


def test_is_valid_board_size_accepts_supported_odd_sizes() -> None:
    assert is_valid_board_size(7)
    assert is_valid_board_size(9)
    assert is_valid_board_size(11)
    assert is_valid_board_size(13)
    assert is_valid_board_size(15)


def test_is_valid_board_size_rejects_even_and_out_of_range_sizes() -> None:
    assert not is_valid_board_size(6)
    assert not is_valid_board_size(8)
    assert not is_valid_board_size(16)


def test_normalize_join_code_trims_and_uppercases() -> None:
    assert normalize_join_code(" ab12 ") == "AB12"


def test_is_valid_join_code_accepts_uppercase_letters_numbers_and_dash() -> None:
    assert is_valid_join_code("ab12")
    assert is_valid_join_code("AB12")


def test_is_valid_join_code_rejects_invalid_shape() -> None:
    assert not is_valid_join_code("a")
    assert not is_valid_join_code("ABC")
    assert not is_valid_join_code("ABCDE")
    assert not is_valid_join_code("game 1")
    assert not is_valid_join_code("game_1")
    assert not is_valid_join_code("GAME-1")


def test_can_join_game_accepts_pregame_with_space_available() -> None:
    game = make_game()
    players = [make_player(), make_player()]

    assert can_join_game(cast(GameData, game), cast(list[PlayerData], players))


def test_can_join_game_rejects_invalid_board_size() -> None:
    game = make_game(board_size=8)

    assert not can_join_game(cast(GameData, game), [])


def test_can_join_game_rejects_non_pregame_phase() -> None:
    game = make_game(phase=GamePhase.GAME)

    assert not can_join_game(cast(GameData, game), [])


def test_can_join_game_rejects_full_active_game() -> None:
    game = make_game()
    players = [
        make_player(),
        make_player(),
        make_player(),
        make_player(),
    ]

    assert not can_join_game(cast(GameData, game), cast(list[PlayerData], players))


def test_can_join_game_ignores_left_players_when_counting_capacity() -> None:
    game = make_game()
    players = [
        make_player(),
        make_player(),
        make_player(),
        make_player(status=PlayerStatus.DEPARTED),
    ]

    assert can_join_game(cast(GameData, game), cast(list[PlayerData], players))
