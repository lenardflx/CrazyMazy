from __future__ import annotations

from server.db.memory_repo import GameRepositoryInMemory, PlayerRepositoryInMemory
from server.service import GameService
from shared.models import GamePhase, PlayerStatus


def make_service() -> GameService:
    return GameService(GameRepositoryInMemory(), PlayerRepositoryInMemory())


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
    assert state.game.admin == state.player.id


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
    assert joined.player.piece_color.value == "BLUE"


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


def test_leave_game_transfers_leadership_to_next_active_player() -> None:
    service = make_service()
    created = service.create_lobby(7, "Ada", "conn_1")
    joined = service.join_game(created.game.code, "Bob", "conn_2")

    state = service.leave_game(created.player.id)

    assert state is not None
    assert state.game.leader_player_id == joined.player.id
    former_leader = next(player for player in state.players if player.id == created.player.id)
    assert former_leader.status == PlayerStatus.LEFT
    assert former_leader.connection_id is None


def test_leave_game_deletes_empty_game() -> None:
    service = make_service()
    created = service.create_lobby(7, "Ada", "conn_1")

    state = service.leave_game(created.player.id)

    assert state is None
    assert service.find_game(created.game.id) is None
