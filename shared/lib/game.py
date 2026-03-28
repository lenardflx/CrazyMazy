# Author: Lenard Felix
# TODO: docs

from __future__ import annotations

from typing import Any, Mapping

from shared.lib.parse import (
    parse_enum,
    parse_int,
    parse_optional_enum,
    parse_optional_int,
    parse_optional_str,
    parse_str,
)
from shared.types.enums import GamePhase, InsertionSide, NpcDifficulty, PlayerResult, TileType, TreasureType, TurnPhase
from shared.types.payloads import (
    ClientGameAddNpcPayload,
    ClientGameMovePlayerPayload,
    ClientGameShiftTilePayload,
    GamePlacementPayload,
    PositionPayload,
    ServerGameLeftPayload,
    ServerGameFinishedPayload,
    ServerGamePlayerMovedPayload,
    ServerGameStartedPayload,
    ServerGameTileShiftedPayload,
    ServerGameTurnChangedPayload,
    TilePayload,
)


def _parse_position(payload: Any) -> PositionPayload | None:
    """Parse a raw dict into a ``PositionPayload``, or ``None`` if invalid."""
    if not isinstance(payload, Mapping):
        return None

    x = parse_int(payload.get("x"))
    y = parse_int(payload.get("y"))
    if x is None or y is None:
        return None
    return {"x": x, "y": y}


def _parse_tile(payload: Any) -> TilePayload | None:
    """Parse a raw dict into a ``TilePayload``, or ``None`` if invalid."""
    if not isinstance(payload, Mapping):
        return None

    tile_id = parse_str(payload.get("id"))
    tile_type = parse_enum(payload.get("tile_type"), TileType)
    rotation = parse_int(payload.get("rotation"))
    is_spare_raw = payload.get("is_spare")
    if not isinstance(is_spare_raw, bool):
        return None
    treasure_type = parse_optional_enum(payload.get("treasure_type"), TreasureType)
    row = parse_optional_int(payload.get("row"))
    column = parse_optional_int(payload.get("column"))

    if tile_id is None or tile_type is None or rotation is None:
        return None
    if is_spare_raw:
        if row is not None or column is not None:
            return None
    elif row is None or column is None:
        return None

    parsed: TilePayload = {
        "id": tile_id,
        "tile_type": tile_type,
        "rotation": rotation,
        "is_spare": is_spare_raw,
        "treasure_type": treasure_type,
    }
    if row is not None:
        parsed["row"] = row
    if column is not None:
        parsed["column"] = column
    return parsed


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


def parse_server_game_started_payload(payload: Mapping[str, Any]) -> ServerGameStartedPayload | None:
    """Parse a server game-started broadcast payload, or ``None`` if required fields are missing."""
    game_id = parse_str(payload.get("game_id"))
    revision = parse_int(payload.get("revision"))
    phase = parse_enum(payload.get("phase"), GamePhase)
    current_player_id = parse_optional_str(payload.get("current_player_id"))
    turn_phase = parse_optional_enum(payload.get("turn_phase"), TurnPhase)

    if game_id is None or revision is None or phase is None:
        return None
    return {
        "game_id": game_id,
        "revision": revision,
        "phase": phase,
        "current_player_id": current_player_id,
        "turn_phase": turn_phase,
    }


def parse_server_game_tile_shifted_payload(payload: Mapping[str, Any]) -> ServerGameTileShiftedPayload | None:
    """Parse a server tile-shifted broadcast payload, or ``None`` if required fields are missing."""
    game_id = parse_str(payload.get("game_id"))
    revision = parse_int(payload.get("revision"))
    insertion_side = parse_enum(payload.get("insertion_side"), InsertionSide)
    insertion_index = parse_int(payload.get("insertion_index"))
    tile = _parse_tile(payload.get("tile"))
    current_player_id = parse_optional_str(payload.get("current_player_id"))
    turn_phase = parse_optional_enum(payload.get("turn_phase"), TurnPhase)
    blocked_insertion_side = parse_optional_enum(payload.get("blocked_insertion_side"), InsertionSide)
    blocked_insertion_index = parse_optional_int(payload.get("blocked_insertion_index"))

    if game_id is None or revision is None or insertion_side is None or insertion_index is None or tile is None:
        return None
    return {
        "game_id": game_id,
        "revision": revision,
        "insertion_side": insertion_side,
        "insertion_index": insertion_index,
        "tile": tile,
        "current_player_id": current_player_id,
        "turn_phase": turn_phase,
        "blocked_insertion_side": blocked_insertion_side,
        "blocked_insertion_index": blocked_insertion_index,
    }


def parse_server_game_player_moved_payload(payload: Mapping[str, Any]) -> ServerGamePlayerMovedPayload | None:
    """Parse a server player-moved broadcast payload, or ``None`` if required fields are missing."""
    game_id = parse_str(payload.get("game_id"))
    revision = parse_int(payload.get("revision"))
    player_id = parse_str(payload.get("player_id"))
    position = _parse_position(payload.get("position"))
    active_treasure_type = parse_optional_enum(payload.get("active_treasure_type"), TreasureType)
    collected_treasure_type = parse_optional_enum(payload.get("collected_treasure_type"), TreasureType)
    remaining_treasure_count = parse_int(payload.get("remaining_treasure_count"))

    if game_id is None or revision is None or player_id is None or position is None or remaining_treasure_count is None:
        return None
    return {
        "game_id": game_id,
        "revision": revision,
        "player_id": player_id,
        "position": position,
        "active_treasure_type": active_treasure_type,
        "collected_treasure_type": collected_treasure_type,
        "remaining_treasure_count": remaining_treasure_count,
    }


def parse_server_game_turn_changed_payload(payload: Mapping[str, Any]) -> ServerGameTurnChangedPayload | None:
    """Parse a server turn-changed broadcast payload, or ``None`` if required fields are missing."""
    game_id = parse_str(payload.get("game_id"))
    revision = parse_int(payload.get("revision"))
    current_player_id = parse_optional_str(payload.get("current_player_id"))
    turn_phase = parse_optional_enum(payload.get("turn_phase"), TurnPhase)
    blocked_insertion_side = parse_optional_enum(payload.get("blocked_insertion_side"), InsertionSide)
    blocked_insertion_index = parse_optional_int(payload.get("blocked_insertion_index"))

    if game_id is None or revision is None:
        return None
    return {
        "game_id": game_id,
        "revision": revision,
        "current_player_id": current_player_id,
        "turn_phase": turn_phase,
        "blocked_insertion_side": blocked_insertion_side,
        "blocked_insertion_index": blocked_insertion_index,
    }


def _parse_game_placement(payload: Any) -> GamePlacementPayload | None:
    """Parse a single placement entry from a finished-game payload, or ``None`` if invalid."""
    if not isinstance(payload, Mapping):
        return None
    player_id = parse_str(payload.get("player_id"))
    result = parse_enum(payload.get("result"), PlayerResult)
    placement = parse_optional_int(payload.get("placement"))
    if player_id is None or result is None:
        return None
    return {"player_id": player_id, "result": result, "placement": placement}


def parse_server_game_finished_payload(payload: Mapping[str, Any]) -> ServerGameFinishedPayload | None:
    """Parse a server game-finished broadcast payload, or ``None`` if required fields are missing."""
    game_id = parse_str(payload.get("game_id"))
    revision = parse_int(payload.get("revision"))
    winner_player_id = parse_optional_str(payload.get("winner_player_id"))
    placements_raw = payload.get("placements")
    if game_id is None or revision is None or not isinstance(placements_raw, list):
        return None

    placements: list[GamePlacementPayload] = []
    for item in placements_raw:
        placement = _parse_game_placement(item)
        if placement is None:
            return None
        placements.append(placement)

    return {
        "game_id": game_id,
        "revision": revision,
        "winner_player_id": winner_player_id,
        "placements": placements,
    }


def parse_server_game_left_payload(payload: Mapping[str, Any]) -> ServerGameLeftPayload | None:
    """Parse a server game-left notification payload, or ``None`` if the reason is missing."""
    reason = parse_str(payload.get("reason"))
    if reason is None:
        return None
    return {"reason": reason}
