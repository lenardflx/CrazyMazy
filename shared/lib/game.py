# Author: Lenard Felix
# TODO: docs

from __future__ import annotations

from typing import Any, Mapping

from shared.lib.parse import (
    parse_bool,
    parse_enum,
    parse_int,
    parse_optional_str,
    parse_str,
)
from shared.types.enums import InsertionSide, NpcDifficulty
from shared.types.payloads import (
    ClientGameAddNpcPayload,
    ClientCreateLobbyPayload,
    ClientGameMovePlayerPayload,
    ClientGameShiftTilePayload,
    ClientJoinGamePayload,
    ServerGameLeftPayload,
)


def parse_client_game_create_lobby_payload(payload: Mapping[str, Any]) -> ClientCreateLobbyPayload | None:
    board_size = parse_int(payload.get("board_size"))
    player_name = parse_str(payload.get("player_name"))
    is_public = parse_bool(payload.get("is_public"))
    player_limit = parse_int(payload.get("player_limit"))
    insert_timeout = parse_int(payload.get("insert_timeout"))
    move_timeout = parse_int(payload.get("move_timeout"))
    if board_size is None or player_name is None or is_public is None or player_limit is None:
        return None
    return {
        "board_size": board_size,
        "player_name": player_name,
        "is_public": is_public,
        "player_limit": player_limit,
        "insert_timeout": insert_timeout,
        "move_timeout": move_timeout,
    }


def parse_client_game_join_payload(payload: Mapping[str, Any]) -> ClientJoinGamePayload | None:
    join_code = parse_optional_str(payload.get("join_code"))
    player_name = parse_str(payload.get("player_name"))
    join_public = parse_bool(payload.get("join_public"))
    if player_name is None or join_public is None:
        return None
    if join_code is not None and not join_code.strip():
        join_code = None
    return {
        "join_code": join_code,
        "player_name": player_name,
        "join_public": join_public,
    }


def parse_client_game_shift_tile_payload(payload: Mapping[str, Any]) -> ClientGameShiftTilePayload | None:
    """Parse a client shift-tile request payload, or ``None`` if any required field is missing."""
    insertion_side = parse_enum(payload.get("insertion_side"), InsertionSide)
    insertion_index = parse_int(payload.get("insertion_index"))
    rotation = parse_int(payload.get("rotation"))

    if insertion_side is None or insertion_index is None or rotation is None:
        return None
    return {
        "insertion_side": insertion_side,
        "insertion_index": insertion_index,
        "rotation": rotation,
    }


def parse_client_game_move_player_payload(payload: Mapping[str, Any]) -> ClientGameMovePlayerPayload | None:
    """Parse a client move-player request payload, or ``None`` if x or y is missing."""
    x = parse_int(payload.get("x"))
    y = parse_int(payload.get("y"))
    if x is None or y is None:
        return None
    return {"x": x, "y": y}


def parse_client_game_add_npc_payload(payload: Mapping[str, Any]) -> ClientGameAddNpcPayload | None:
    """Parse a client add-NPC request payload, or ``None`` if the difficulty is missing."""
    difficulty = parse_enum(payload.get("difficulty"), NpcDifficulty)
    if difficulty is None:
        return None
    return {"difficulty": difficulty}


def parse_server_game_left_payload(payload: Mapping[str, Any]) -> ServerGameLeftPayload | None:
    """Parse a server game-left notification payload, or ``None`` if the reason is missing."""
    reason = parse_str(payload.get("reason"))
    if reason is None:
        return None
    return {"reason": reason}
