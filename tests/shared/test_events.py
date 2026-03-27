# Author: Lenard Felix

from __future__ import annotations

from shared.events import (
    ClientGameEndTurnEvent,
    ClientJoinGameEvent,
    ClientGameMovePlayerEvent,
    ClientGameShiftTileEvent,
    ClientGameStartEvent,
    ServerGameFinishedEvent,
    ServerGamePlayerMovedEvent,
    ServerGameSnapshotEvent,
    ServerGameStartedEvent,
    ServerGameTileShiftedEvent,
    ServerGameTurnChangedEvent,
    ServerResponseErrorEvent,
    parse_event,
)
from shared.protocol import make_message


def make_snapshot_payload() -> dict[str, object]:
    return {
        "game_id": "550e8400-e29b-41d4-a716-446655440000",
        "code": "GAME-1",
        "phase": "GAME",
        "revision": 7,
        "board_size": 7,
        "leader_player_id": "550e8400-e29b-41d4-a716-446655440001",
        "turn": {
            "current_player_id": "550e8400-e29b-41d4-a716-446655440001",
            "turn_phase": "MOVE",
            "blocked_insertion_side": "LEFT",
            "blocked_insertion_index": 3,
        },
        "tiles": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440010",
                "row": 0,
                "column": 0,
                "tile_type": "CORNER",
                "rotation": 1,
                "is_spare": False,
                "treasure_type": "BOOK",
            },
            {
                "id": "550e8400-e29b-41d4-a716-446655440011",
                "tile_type": "T",
                "rotation": 2,
                "is_spare": True,
                "treasure_type": None,
            },
        ],
        "reachable_positions": [
            {"x": 1, "y": 2},
            {"x": 1, "y": 3},
        ],
        "players": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "display_name": "Ada",
                "status": "ACTIVE",
                "result": "NONE",
                "placement": None,
                "join_order": 0,
                "piece_color": "RED",
                "position": {"x": 1, "y": 2},
                "collected_treasures": ["BOOK"],
                "remaining_treasure_count": 1,
            },
            {
                "id": "550e8400-e29b-41d4-a716-446655440002",
                "display_name": "Linus",
                "status": "ACTIVE",
                "result": "NONE",
                "placement": None,
                "join_order": 1,
                "piece_color": "BLUE",
                "position": {"x": 4, "y": 5},
                "collected_treasures": [],
                "remaining_treasure_count": 2,
            },
        ],
        "viewer": {
            "player_id": "550e8400-e29b-41d4-a716-446655440001",
            "is_leader": True,
            "is_current_player": True,
            "active_treasure_type": "OWL",
            "collected_treasures": ["BOOK"],
            "remaining_treasure_count": 1,
        },
    }


def test_event_to_message_uses_event_id_and_payload() -> None:
    event = ClientJoinGameEvent(
        message_id="msg_custom",
        join_code="GAME",
        player_name="Ada",
    )

    msg = event.to_message()

    assert msg["id"] == "msg_custom"
    assert msg["type"] == ClientJoinGameEvent.message_type
    assert msg["payload"] == {
        "join_code": "GAME",
        "player_name": "Ada",
    }


def test_event_generates_message_id_by_default() -> None:
    event = ClientJoinGameEvent(
        join_code="GAME",
        player_name="Ada",
    )

    assert event.message_id.startswith("msg_")


def test_parse_event_returns_join_event_for_valid_message() -> None:
    event = parse_event(
        make_message(
            ClientJoinGameEvent.message_type,
            {"join_code": " GAME ", "player_name": " Ada "},
        )
    )

    assert isinstance(event, ClientJoinGameEvent)
    assert event.join_code == "GAME"
    assert event.player_name == "Ada"


def test_parse_event_returns_none_for_unknown_message_type() -> None:
    assert parse_event(make_message("unknown.event")) is None


def test_parse_event_returns_none_for_invalid_join_payload() -> None:
    assert parse_event(
        make_message(ClientJoinGameEvent.message_type, {"game_id": "GAME-1"})
    ) is None


def test_parse_event_returns_snapshot_event_for_snapshot_message() -> None:
    payload = make_snapshot_payload()
    event = parse_event(make_message(ServerGameSnapshotEvent.message_type, payload))

    assert isinstance(event, ServerGameSnapshotEvent)
    assert event.payload == payload


def test_parse_event_returns_error_event_for_error_message() -> None:
    event = parse_event(
        make_message(
            ServerResponseErrorEvent.message_type,
            {"code": "GAME_NOT_FOUND", "message": "missing"},
        )
    )

    assert isinstance(event, ServerResponseErrorEvent)
    assert event.code == "GAME_NOT_FOUND"
    assert event.message == "missing"


def test_parse_event_returns_game_start_event_for_empty_payload() -> None:
    event = parse_event(make_message(ClientGameStartEvent.message_type, {}))

    assert isinstance(event, ClientGameStartEvent)


def test_parse_event_returns_shift_tile_event_for_valid_message() -> None:
    event = parse_event(
        make_message(
            ClientGameShiftTileEvent.message_type,
            {"insertion_side": "LEFT", "insertion_index": 3, "rotation": 2},
        )
    )

    assert isinstance(event, ClientGameShiftTileEvent)
    assert event.insertion_side == "LEFT"
    assert event.insertion_index == 3
    assert event.rotation == 2


def test_parse_event_returns_move_player_event_for_valid_message() -> None:
    event = parse_event(
        make_message(
            ClientGameMovePlayerEvent.message_type,
            {"x": 4, "y": 5},
        )
    )

    assert isinstance(event, ClientGameMovePlayerEvent)
    assert event.x == 4
    assert event.y == 5


def test_parse_event_returns_end_turn_event_for_empty_payload() -> None:
    event = parse_event(make_message(ClientGameEndTurnEvent.message_type, {}))

    assert isinstance(event, ClientGameEndTurnEvent)


def test_parse_event_returns_server_game_started_event_for_valid_message() -> None:
    event = parse_event(
        make_message(
            ServerGameStartedEvent.message_type,
            {
                "game_id": "550e8400-e29b-41d4-a716-446655440000",
                "revision": 8,
                "phase": "GAME",
                "current_player_id": "550e8400-e29b-41d4-a716-446655440001",
                "turn_phase": "SHIFT",
            },
        )
    )

    assert isinstance(event, ServerGameStartedEvent)
    assert event.payload["turn_phase"] == "SHIFT"


def test_parse_event_returns_server_game_tile_shifted_event_for_valid_message() -> None:
    event = parse_event(
        make_message(
            ServerGameTileShiftedEvent.message_type,
            {
                "game_id": "550e8400-e29b-41d4-a716-446655440000",
                "revision": 9,
                "insertion_side": "LEFT",
                "insertion_index": 3,
                "tile": {
                    "id": "550e8400-e29b-41d4-a716-446655440010",
                    "tile_type": "STRAIGHT",
                    "rotation": 1,
                    "is_spare": True,
                    "treasure_type": None,
                },
                "current_player_id": "550e8400-e29b-41d4-a716-446655440001",
                "turn_phase": "MOVE",
                "blocked_insertion_side": "RIGHT",
                "blocked_insertion_index": 3,
            },
        )
    )

    assert isinstance(event, ServerGameTileShiftedEvent)
    assert event.payload["tile"]["tile_type"] == "STRAIGHT"


def test_parse_event_returns_server_game_player_moved_event_for_valid_message() -> None:
    event = parse_event(
        make_message(
            ServerGamePlayerMovedEvent.message_type,
            {
                "game_id": "550e8400-e29b-41d4-a716-446655440000",
                "revision": 10,
                "player_id": "550e8400-e29b-41d4-a716-446655440001",
                "position": {"x": 4, "y": 5},
                "active_treasure_type": "OWL",
                "collected_treasure_type": "BOOK",
                "remaining_treasure_count": 0,
            },
        )
    )

    assert isinstance(event, ServerGamePlayerMovedEvent)
    assert event.payload["position"] == {"x": 4, "y": 5}


def test_parse_event_returns_server_game_turn_changed_event_for_valid_message() -> None:
    event = parse_event(
        make_message(
            ServerGameTurnChangedEvent.message_type,
            {
                "game_id": "550e8400-e29b-41d4-a716-446655440000",
                "revision": 11,
                "current_player_id": "550e8400-e29b-41d4-a716-446655440002",
                "turn_phase": "SHIFT",
                "blocked_insertion_side": "LEFT",
                "blocked_insertion_index": 5,
            },
        )
    )

    assert isinstance(event, ServerGameTurnChangedEvent)
    assert event.payload["current_player_id"] == "550e8400-e29b-41d4-a716-446655440002"


def test_parse_event_returns_server_game_finished_event_for_valid_message() -> None:
    event = parse_event(
        make_message(
            ServerGameFinishedEvent.message_type,
            {
                "game_id": "550e8400-e29b-41d4-a716-446655440000",
                "revision": 12,
                "winner_player_id": "550e8400-e29b-41d4-a716-446655440001",
                "placements": [
                    {
                        "player_id": "550e8400-e29b-41d4-a716-446655440001",
                        "result": "WON",
                        "placement": 1,
                    },
                    {
                        "player_id": "550e8400-e29b-41d4-a716-446655440002",
                        "result": "FORFEITED",
                        "placement": 2,
                    },
                ],
            },
        )
    )

    assert isinstance(event, ServerGameFinishedEvent)
    assert event.payload["placements"][0]["result"] == "WON"
