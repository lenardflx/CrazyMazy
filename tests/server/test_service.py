# Author: Lenard Felix

from __future__ import annotations

from server.db.memory_repo import (
    GameRepositoryInMemory,
    PlayerRepositoryInMemory,
    TileRepositoryInMemory,
    TreasureRepositoryInMemory,
)
from server.service import GameService
from shared.protocol import ErrorCode
from shared.types.enums import GameEndReason, GamePhase, InsertionSide, PlayerLeaveReason, PlayerResult, PlayerStatus, TurnPhase


def make_service() -> GameService:
    return GameService(
        GameRepositoryInMemory(),
        PlayerRepositoryInMemory(),
        TileRepositoryInMemory(),
        TreasureRepositoryInMemory(),
    )


def make_service_without_npc_play() -> GameService:
    return GameService(
        GameRepositoryInMemory(),
        PlayerRepositoryInMemory(),
        TileRepositoryInMemory(),
        TreasureRepositoryInMemory(),
        allow_npc_play=False,
    )


def test_create_lobby_creates_game_and_leader() -> None:
    service = make_service()

    state = service.create_lobby(
        board_size=7,
        leader_display_name=" Ada ",
        connection_id="conn_1",
    )

    assert state.game.board_size == 7
    assert state.player.display_name == "Ada"
    assert state.player.join_order == 0
    assert state.game.leader_player_id == state.player.id


def test_create_lobby_rejects_invalid_board_size() -> None:
    service = make_service()

    try:
        service.create_lobby(8, "Ada", "conn_1")
    except ValueError as exc:
        assert "Invalid board size" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_join_game_assigns_next_slot_automatically() -> None:
    service = make_service()
    created = service.create_lobby(7, "Ada", "conn_1")

    joined = service.join_game(created.game.code.lower(), " Bob ", "conn_2")

    assert joined.game.id == created.game.id
    assert joined.player.display_name == "Bob"
    assert joined.player.join_order == 1
    assert joined.player.piece_color.value == "YELLOW"


def test_create_lobby_persists_public_flag_and_player_limit() -> None:
    service = make_service()

    state = service.create_lobby(
        board_size=7,
        leader_display_name="Ada",
        connection_id="conn_1",
        is_public=True,
        player_limit=3,
    )

    assert state.game.is_public is True
    assert state.game.player_limit == 3


def test_join_game_respects_player_limit() -> None:
    service = make_service()
    created = service.create_lobby(7, "Ada", "conn_1", player_limit=2)
    assert not isinstance(created, Exception)

    joined = service.join_game(created.game.code, "Bob", "conn_2")
    assert joined.player.join_order == 1

    rejected = service.join_game(created.game.code, "Cara", "conn_3")
    assert rejected == ErrorCode.GAME_NOT_JOINABLE


def test_join_public_picks_first_joinable_public_lobby() -> None:
    service = make_service()
    first = service.create_lobby(7, "Ada", "conn_1", is_public=True, player_limit=2)
    second = service.create_lobby(7, "Bea", "conn_2", is_public=True, player_limit=4)

    service.join_game(first.game.code, "Bob", "conn_3")
    joined = service.join_game(None, "Cara", "conn_4", join_public=True)

    assert joined.game.id == second.game.id


def test_join_public_returns_no_public_lobby_when_none_available() -> None:
    service = make_service()

    rejected = service.join_game(None, "Cara", "conn_4", join_public=True)

    assert rejected == ErrorCode.NO_PUBLIC_LOBBY


def test_start_game_requires_a_human_when_npc_play_is_disabled() -> None:
    service = make_service_without_npc_play()
    created = service.create_lobby(7, "Ada", "conn_1")
    service.add_npc(created.player.id)
    service.add_npc(created.player.id)
    service.leave_game(created.player.id, PlayerLeaveReason.LEFT)

    remaining = service.get_game_state(created.game.id)
    assert remaining is not None
    leader = next(player for player in remaining.players if player.id == remaining.game.leader_player_id)

    started = service.start_game(leader.id)

    assert started == ErrorCode.PLAYER_COUNT_INSUFFICIENT


def test_game_ends_when_only_npcs_remain_and_npc_play_is_disabled() -> None:
    service = make_service_without_npc_play()
    created = service.create_lobby(7, "Ada", "conn_1")
    service.add_npc(created.player.id)
    joined = service.join_game(created.game.code, "Bob", "conn_2")
    started = service.start_game(created.player.id)
    assert not isinstance(started, ErrorCode)

    state = service.leave_game(joined.player.id, PlayerLeaveReason.LEFT)

    assert state is not None
    assert state.game.game_phase == GamePhase.POSTGAME
    assert state.game.end_reason == GameEndReason.PLAYERS_LEFT


def test_join_game_rejects_taken_display_name() -> None:
    service = make_service()
    created = service.create_lobby(7, "Ada", "conn_1")

    try:
        service.join_game(created.game.code, " ada ", "conn_2")
    except ValueError as exc:
        assert "Display name already taken" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_join_game_rejects_non_joinable_game() -> None:
    service = make_service()
    created = service.create_lobby(7, "Ada", "conn_1")
    created.game.game_phase = GamePhase.GAME
    service.game_repo.update_game(created.game)

    try:
        service.join_game(created.game.code, "Bob", "conn_2")
    except ValueError as exc:
        assert "Game is not joinable" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_get_connection_state_returns_game_and_player() -> None:
    service = make_service()
    created = service.create_lobby(7, "Ada", "conn_1")

    state = service.get_connection_state("conn_1")

    assert state is not None
    assert state.game.id == created.game.id
    assert state.player.id == created.player.id


def test_get_connection_state_prefers_newest_session_when_connection_id_is_duplicated() -> None:
    service = make_service()
    old = service.create_lobby(7, "Ada", "conn_1")
    new = service.create_lobby(7, "Bea", "conn_1")

    state = service.get_connection_state("conn_1")

    assert state is not None
    assert state.game.id == new.game.id
    assert state.player.id == new.player.id
    assert state.game.id != old.game.id


def test_leave_game_clears_connection_id_even_when_player_was_already_departed() -> None:
    service = make_service()
    created = service.create_lobby(7, "Ada", "conn_1")
    created.player.status = PlayerStatus.DEPARTED
    service.player_repo.update_player(created.player)

    state = service.leave_game(created.player.id, PlayerLeaveReason.LEFT)

    assert state is None
    player = service.player_repo.find_by_id(created.player.id)
    assert player is None or player.connection_id is None


def test_leave_game_transfers_leadership_to_next_active_player() -> None:
    service = make_service()
    created = service.create_lobby(7, "Ada", "conn_1")
    joined = service.join_game(created.game.code, "Bob", "conn_2")

    state = service.leave_game(created.player.id)

    assert state is not None
    assert state.game.leader_player_id == joined.player.id
    former_leader = next(player for player in state.players if player.id == created.player.id)
    assert former_leader.status == PlayerStatus.DEPARTED
    assert former_leader.connection_id is None


def test_leave_game_deletes_empty_game() -> None:
    service = make_service()
    created = service.create_lobby(7, "Ada", "conn_1")

    state = service.leave_game(created.player.id)

    assert state is None
    assert service.find_game(created.game.id) is None


def test_leave_game_moves_active_game_to_postgame_when_one_player_remains() -> None:
    service = make_service()
    created = service.create_lobby(7, "Ada", "conn_1")
    joined = service.join_game(created.game.code, "Bob", "conn_2")
    created.game.game_phase = GamePhase.GAME
    created.game.current_player_id = created.player.id
    service.game_repo.update_game(created.game)

    state = service.leave_game(created.player.id)

    assert state is not None
    assert state.game.game_phase == GamePhase.POSTGAME
    assert state.game.end_reason == GameEndReason.PLAYERS_LEFT
    assert state.game.current_player_id is None
    assert state.game.ended_at is not None
    assert state.game.leader_player_id == joined.player.id


def test_leave_game_moves_active_game_to_postgame_when_everyone_has_left() -> None:
    service = make_service()
    created = service.create_lobby(7, "Ada", "conn_1")
    created.game.game_phase = GamePhase.GAME
    created.game.current_player_id = created.player.id
    service.game_repo.update_game(created.game)

    state = service.leave_game(created.player.id)

    assert state is not None
    assert state.game.game_phase == GamePhase.POSTGAME
    assert state.game.end_reason == GameEndReason.PLAYERS_LEFT
    assert state.game.current_player_id is None
    assert state.game.ended_at is not None
    assert service.find_game(created.game.id) is not None


def test_give_up_turns_player_into_observer_and_ends_two_player_game() -> None:
    service = make_service()
    created = service.create_lobby(7, "Ada", "conn_1")
    joined = service.join_game(created.game.code, "Bob", "conn_2")
    created.game.game_phase = GamePhase.GAME
    created.game.current_player_id = joined.player.id
    service.game_repo.update_game(created.game)

    state = service.give_up(joined.player.id)

    assert state is not None
    observer = next(player for player in state.players if player.id == joined.player.id)
    assert observer.status == PlayerStatus.OBSERVER
    assert observer.connection_id == joined.player.connection_id
    assert state.game.game_phase == GamePhase.POSTGAME
    assert state.game.end_reason == GameEndReason.PLAYERS_LEFT


def test_give_up_turns_player_into_observer_and_passes_turn_when_other_players_remain() -> None:
    service = make_service()
    created = service.create_lobby(7, "Ada", "conn_1")
    joined = service.join_game(created.game.code, "Bob", "conn_2")
    third = service.join_game(created.game.code, "Cara", "conn_3")
    created.game.game_phase = GamePhase.GAME
    created.game.current_player_id = joined.player.id
    service.game_repo.update_game(created.game)

    state = service.give_up(joined.player.id)

    assert state is not None
    observer = next(player for player in state.players if player.id == joined.player.id)
    assert observer.status == PlayerStatus.OBSERVER
    assert observer.connection_id == joined.player.connection_id
    assert state.game.game_phase == GamePhase.GAME
    assert state.game.end_reason is None
    assert state.game.current_player_id == third.player.id


def test_move_player_stores_last_move_path_and_collected_treasure() -> None:
    service = make_service()
    created = service.create_lobby(7, "Ada", "conn_1")
    service.join_game(created.game.code, "Bob", "conn_2")
    started = service.start_game(created.player.id)
    current_player = next(player for player in started.players if player.id == started.game.current_player_id)
    assert current_player.position_x is not None
    assert current_player.position_y is not None

    game = service.find_game(started.game.id)
    assert game is not None
    game.turn_phase = TurnPhase.MOVE
    service.game_repo.update_game(game)

    active_treasure = service.treasure_repo.list_by_player_id(current_player.id)[0]
    tile = next(
        tile
        for tile in service.tile_repo.list_by_game_id(started.game.id)
        if tile.column == current_player.position_x and tile.row == current_player.position_y
    )
    tile.treasure_type = active_treasure.treasure_type
    service.tile_repo.update_tile(tile)

    state = service.move_player(current_player.id, current_player.position_x, current_player.position_y)

    assert state.game.last_move_player_id == current_player.id
    assert state.game.last_move_path == f"{current_player.position_x},{current_player.position_y}"
    assert state.game.last_move_collected_treasure_type == active_treasure.treasure_type


def test_move_player_win_assigns_postgame_placements_to_other_players() -> None:
    service = make_service()
    created = service.create_lobby(7, "Ada", "conn_1")
    joined = service.join_game(created.game.code, "Bob", "conn_2")
    started = service.start_game(created.player.id)

    game = service.find_game(started.game.id)
    assert game is not None
    game.current_player_id = created.player.id
    game.turn_phase = TurnPhase.MOVE
    service.game_repo.update_game(game)

    for treasure in service.treasure_repo.list_by_player_id(created.player.id):
        treasure.collected = True
        service.treasure_repo.update_treasure(treasure)

    winner = service.player_repo.find_by_id(created.player.id)
    assert winner is not None
    assert winner.position_x is not None
    assert winner.position_y is not None

    state = service.move_player(winner.id, winner.position_x, winner.position_y)

    assert state.game.game_phase == GamePhase.POSTGAME
    players = {player.id: player for player in state.players}
    assert players[created.player.id].placement == 1
    assert players[created.player.id].result == PlayerResult.WON
    assert players[joined.player.id].placement == 2


def test_end_turn_preserves_blocked_insertion_for_next_player() -> None:
    service = make_service()
    created = service.create_lobby(7, "Ada", "conn_1")
    joined = service.join_game(created.game.code, "Bob", "conn_2")
    started = service.start_game(created.player.id)

    game = service.find_game(started.game.id)
    assert game is not None
    game.current_player_id = created.player.id
    game.turn_phase = TurnPhase.MOVE
    game.blocked_insertion_side = InsertionSide.LEFT
    game.blocked_insertion_index = 3
    service.game_repo.update_game(game)

    state = service.end_turn(created.player.id)

    assert state.game.current_player_id == joined.player.id
    assert state.game.turn_phase == TurnPhase.SHIFT
    assert state.game.blocked_insertion_side == InsertionSide.LEFT
    assert state.game.blocked_insertion_index == 3


def test_give_up_preserves_blocked_insertion_when_turn_passes() -> None:
    service = make_service()
    created = service.create_lobby(7, "Ada", "conn_1")
    joined = service.join_game(created.game.code, "Bob", "conn_2")
    third = service.join_game(created.game.code, "Cara", "conn_3")
    created.game.game_phase = GamePhase.GAME
    created.game.current_player_id = joined.player.id
    created.game.turn_phase = TurnPhase.MOVE
    created.game.blocked_insertion_side = InsertionSide.TOP
    created.game.blocked_insertion_index = 1
    service.game_repo.update_game(created.game)

    state = service.give_up(joined.player.id)

    assert state is not None
    assert state.game.current_player_id == third.player.id
    assert state.game.turn_phase == TurnPhase.SHIFT
    assert state.game.blocked_insertion_side == InsertionSide.TOP
    assert state.game.blocked_insertion_index == 1


def test_give_up_ending_game_assigns_postgame_placements_to_all_remaining_players() -> None:
    service = make_service()
    created = service.create_lobby(7, "Ada", "conn_1")
    joined = service.join_game(created.game.code, "Bob", "conn_2")
    created.game.game_phase = GamePhase.GAME
    created.game.current_player_id = joined.player.id
    service.game_repo.update_game(created.game)

    state = service.give_up(joined.player.id)

    assert state is not None
    assert state.game.game_phase == GamePhase.POSTGAME
    players = {player.id: player for player in state.players}
    assert players[created.player.id].placement == 1
    assert players[created.player.id].result == PlayerResult.WON
    assert players[joined.player.id].placement == 2
    assert players[joined.player.id].result == PlayerResult.FORFEITED
