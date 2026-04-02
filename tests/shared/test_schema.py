# Author: Lenard Felix

from __future__ import annotations

from shared.lib.snapshot import parse_game_snapshot_payload
from shared.game.snapshot import SnapshotGameState


def make_snapshot_payload() -> dict[str, object]:
    return {
        "game_id": "550e8400-e29b-41d4-a716-446655440000",
        "code": "GAME-1",
        "phase": "GAME",
        "revision": 7,
        "board_size": 7,
        "is_public": False,
        "player_limit": 4,
        "leader_player_id": "550e8400-e29b-41d4-a716-446655440001",
        "turn": {
            "current_player_id": "550e8400-e29b-41d4-a716-446655440001",
            "turn_phase": "MOVE",
            "turn_end_timestamp": None,
            "server_now_timestamp": None,
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
                "controller_kind": "HUMAN",
                "npc_difficulty": None,
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
                "controller_kind": "HUMAN",
                "npc_difficulty": None,
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
            "active_treasure_type": "OWL",
        },
    }


def test_parse_game_snapshot_payload_accepts_viewer_specific_snapshot() -> None:
    payload = make_snapshot_payload()

    parsed = parse_game_snapshot_payload(payload)

    assert parsed is not None
    assert parsed == payload


def test_parse_game_snapshot_payload_rejects_non_spare_tile_without_position() -> None:
    payload = make_snapshot_payload()
    tiles = payload["tiles"]
    assert isinstance(tiles, list)
    tile = tiles[0]
    assert isinstance(tile, dict)
    tile.pop("row")

    assert parse_game_snapshot_payload(payload) is None


def test_parse_game_snapshot_payload_strips_hidden_player_fields() -> None:
    payload = make_snapshot_payload()
    players = payload["players"]
    assert isinstance(players, list)
    player = players[0]
    assert isinstance(player, dict)
    player["active_treasure_type"] = "OWL"

    parsed = parse_game_snapshot_payload(payload)

    assert parsed is not None
    assert "active_treasure_type" not in parsed["players"][0]


def test_parse_game_snapshot_payload_rejects_invalid_reachable_positions() -> None:
    payload = make_snapshot_payload()
    payload["reachable_positions"] = [{"x": 1}]

    assert parse_game_snapshot_payload(payload) is None


def test_snapshot_game_state_allows_pregame_without_board_tiles() -> None:
    payload = make_snapshot_payload()
    payload["phase"] = "PREGAME"
    payload["tiles"] = []
    payload["reachable_positions"] = []

    game_state = SnapshotGameState.from_snapshot(payload)

    assert game_state.phase.value == "PREGAME"
    assert game_state.board is None
    assert game_state.spare_tile is None


def test_snapshot_game_state_rejects_active_game_without_board_tiles() -> None:
    payload = make_snapshot_payload()
    payload["phase"] = "GAME"
    payload["tiles"] = []
    payload["reachable_positions"] = []

    try:
        SnapshotGameState.from_snapshot(payload)
    except ValueError as exc:
        assert str(exc) == "Active game snapshot is missing board tiles"
    else:
        raise AssertionError("Expected active game snapshots without tiles to be rejected")


def test_snapshot_game_state_uses_spectating_prompt_for_observer_viewer() -> None:
    payload = make_snapshot_payload()
    players = payload["players"]
    assert isinstance(players, list)
    viewer_player = players[0]
    assert isinstance(viewer_player, dict)
    viewer_player["status"] = "OBSERVER"

    viewer = payload["viewer"]
    assert isinstance(viewer, dict)
    viewer["is_current_player"] = False
    viewer["active_treasure_type"] = None

    game_state = SnapshotGameState.from_snapshot(payload)

    assert game_state.viewer_is_spectator is True


def test_snapshot_game_state_parses_last_shift_metadata() -> None:
    payload = make_snapshot_payload()
    payload["last_shift"] = {
        "side": "LEFT",
        "index": 3,
        "rotation": 2,
    }

    game_state = SnapshotGameState.from_snapshot(payload)

    assert game_state.last_shift is not None
    assert game_state.last_shift.side.value == "LEFT"
    assert game_state.last_shift.index == 3
    assert game_state.last_shift.rotation == 2


def test_snapshot_game_state_parses_last_move_metadata() -> None:
    payload = make_snapshot_payload()
    payload["last_move"] = {
        "player_id": "550e8400-e29b-41d4-a716-446655440001",
        "path": [
            {"x": 1, "y": 2},
            {"x": 1, "y": 3},
            {"x": 2, "y": 3},
        ],
        "collected_treasure_type": "BOOK",
    }

    game_state = SnapshotGameState.from_snapshot(payload)

    assert game_state.last_move is not None
    assert game_state.last_move.player_id == "550e8400-e29b-41d4-a716-446655440001"
    assert game_state.last_move.path == [(1, 2), (1, 3), (2, 3)]
    assert game_state.last_move.collected_treasure_type.value == "BOOK"
