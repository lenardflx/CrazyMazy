# Author: Lenard Felix

from __future__ import annotations

from shared.lib.snapshot import parse_game_snapshot_payload


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


def test_parse_game_snapshot_payload_accepts_viewer_specific_snapshot() -> None:
    payload = make_snapshot_payload()

    parsed = parse_game_snapshot_payload(payload)

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
