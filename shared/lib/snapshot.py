# Author: Lenard Felix

from __future__ import annotations

from typing import Any, Mapping

from shared.lib.parse import (
    parse_bool,
    parse_enum,
    parse_int,
    parse_optional_enum,
    parse_optional_int,
    parse_optional_str,
    parse_str,
)
from shared.models import (
    GamePhase,
    InsertionSide,
    PlayerColor,
    PlayerResult,
    PlayerStatus,
    TileType,
    TreasureType,
    TurnPhase,
)
from shared.schema import (
    PositionPayload,
    PublicPlayerPayload,
    RoomSnapshotPayload,
    TilePayload,
    TurnPayload,
    ViewerPayload,
)


def _parse_position(payload: Any) -> PositionPayload | None:
    if payload is None:
        return None
    if not isinstance(payload, dict):
        return None

    x = parse_int(payload.get("x"))
    y = parse_int(payload.get("y"))
    if x is None or y is None:
        return None

    return {"x": x, "y": y}


def _parse_treasure_list(payload: Any) -> list[str] | None:
    if not isinstance(payload, list):
        return None

    treasures: list[str] = []
    for item in payload:
        treasure_type = parse_enum(item, TreasureType)
        if treasure_type is None:
            return None
        treasures.append(treasure_type)
    return treasures


def _parse_tile_payload(payload: Any) -> TilePayload | None:
    if not isinstance(payload, dict):
        return None

    tile_id = parse_str(payload.get("id"))
    tile_type = parse_enum(payload.get("tile_type"), TileType)
    rotation = parse_int(payload.get("rotation"))
    is_spare = parse_bool(payload.get("is_spare"))
    treasure_type = parse_optional_enum(payload.get("treasure_type"), TreasureType)
    row = parse_optional_int(payload.get("row"))
    column = parse_optional_int(payload.get("column"))

    if tile_id is None or tile_type is None:
        return None
    if rotation is None or is_spare is None:
        return None
    if is_spare:
        if row is not None or column is not None:
            return None
    elif row is None or column is None:
        return None

    tile: TilePayload = {
        "id": tile_id,
        "tile_type": tile_type,
        "rotation": rotation,
        "is_spare": is_spare,
        "treasure_type": treasure_type,
    }
    if row is not None:
        tile["row"] = row
    if column is not None:
        tile["column"] = column
    return tile


def _parse_public_player_payload(payload: Any) -> PublicPlayerPayload | None:
    if not isinstance(payload, dict):
        return None

    player_id = parse_str(payload.get("id"))
    display_name = parse_str(payload.get("display_name"))
    status = parse_enum(payload.get("status"), PlayerStatus)
    result = parse_enum(payload.get("result"), PlayerResult)
    placement = parse_optional_int(payload.get("placement"))
    join_order = parse_int(payload.get("join_order"))
    piece_color = parse_enum(payload.get("piece_color"), PlayerColor)
    position = _parse_position(payload.get("position"))
    collected_treasures = _parse_treasure_list(payload.get("collected_treasures"))
    remaining_treasure_count = parse_int(payload.get("remaining_treasure_count"))

    if player_id is None or display_name is None or status is None or result is None or piece_color is None:
        return None
    if join_order is None or collected_treasures is None or remaining_treasure_count is None:
        return None

    return {
        "id": player_id,
        "display_name": display_name,
        "status": status,
        "result": result,
        "placement": placement,
        "join_order": join_order,
        "piece_color": piece_color,
        "position": position,
        "collected_treasures": collected_treasures,
        "remaining_treasure_count": remaining_treasure_count,
    }


def _parse_viewer_payload(payload: Any) -> ViewerPayload | None:
    if not isinstance(payload, dict):
        return None

    player_id = parse_str(payload.get("player_id"))
    is_leader = parse_bool(payload.get("is_leader"))
    is_current_player = parse_bool(payload.get("is_current_player"))
    active_treasure_type = parse_optional_enum(payload.get("active_treasure_type"), TreasureType)
    collected_treasures = _parse_treasure_list(payload.get("collected_treasures"))
    remaining_treasure_count = parse_int(payload.get("remaining_treasure_count"))

    if player_id is None:
        return None
    if is_leader is None or is_current_player is None or collected_treasures is None or remaining_treasure_count is None:
        return None

    return {
        "player_id": player_id,
        "is_leader": is_leader,
        "is_current_player": is_current_player,
        "active_treasure_type": active_treasure_type,
        "collected_treasures": collected_treasures,
        "remaining_treasure_count": remaining_treasure_count,
    }


def _parse_turn_payload(payload: Any) -> TurnPayload | None:
    if not isinstance(payload, dict):
        return None

    current_player_id = parse_optional_str(payload.get("current_player_id"))
    turn_phase = parse_optional_enum(payload.get("turn_phase"), TurnPhase)
    blocked_insertion_side = parse_optional_enum(payload.get("blocked_insertion_side"), InsertionSide)
    blocked_insertion_index = parse_optional_int(payload.get("blocked_insertion_index"))

    return {
        "current_player_id": current_player_id,
        "turn_phase": turn_phase,
        "blocked_insertion_side": blocked_insertion_side,
        "blocked_insertion_index": blocked_insertion_index,
    }


def parse_room_snapshot_payload(payload: Mapping[str, Any]) -> RoomSnapshotPayload | None:
    game_id = parse_str(payload.get("game_id"))
    code = parse_str(payload.get("code"))
    phase = parse_enum(payload.get("phase"), GamePhase)
    revision = parse_int(payload.get("revision"))
    board_size = parse_int(payload.get("board_size"))
    leader_player_id = parse_optional_str(payload.get("leader_player_id"))
    turn = _parse_turn_payload(payload.get("turn"))
    tiles_raw = payload.get("tiles")
    players_raw = payload.get("players")
    viewer_raw = payload.get("viewer")

    if game_id is None or code is None or phase is None or turn is None or revision is None or board_size is None:
        return None
    if not isinstance(tiles_raw, list) or not isinstance(players_raw, list):
        return None

    tiles: list[TilePayload] = []
    for item in tiles_raw:
        tile = _parse_tile_payload(item)
        if tile is None:
            return None
        tiles.append(tile)

    players: list[PublicPlayerPayload] = []
    for item in players_raw:
        player = _parse_public_player_payload(item)
        if player is None:
            return None
        players.append(player)

    if viewer_raw is None:
        viewer = None
    else:
        viewer = _parse_viewer_payload(viewer_raw)
        if viewer is None:
            return None

    return {
        "game_id": game_id,
        "code": code,
        "phase": phase,
        "revision": revision,
        "board_size": board_size,
        "leader_player_id": leader_player_id,
        "turn": turn,
        "tiles": tiles,
        "players": players,
        "viewer": viewer,
    }
