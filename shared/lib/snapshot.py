# Author: Lenard Felix

from __future__ import annotations

from typing import Any, Mapping
from uuid import UUID

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
    GameData,
    GamePhase,
    InsertionSide,
    PlayerData,
    PlayerColor,
    PlayerResult,
    PlayerStatus,
    TileData,
    TileType,
    TreasureType,
    TreasureData,
    TurnPhase,
)
from shared.schema import (
    GameSnapshotPayload,
    LastMovePayload,
    LastShiftPayload,
    PositionPayload,
    PublicPlayerPayload,
    TilePayload,
    TurnPayload,
    ViewerPayload,
)
from shared.state.game_state import Board


def _parse_position(payload: Any) -> PositionPayload | None:
    """Parse a raw dict into a ``PositionPayload``, or ``None`` if absent or invalid."""
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
    """Parse a list of raw treasure type strings, or ``None`` if any entry is invalid."""
    if not isinstance(payload, list):
        return None

    treasures: list[str] = []
    for item in payload:
        treasure_type = parse_enum(item, TreasureType)
        if treasure_type is None:
            return None
        treasures.append(treasure_type)
    return treasures


def _parse_position_list(payload: Any) -> list[PositionPayload] | None:
    if not isinstance(payload, list):
        return None

    positions: list[PositionPayload] = []
    for item in payload:
        position = _parse_position(item)
        if position is None:
            return None
        positions.append(position)
    return positions


def _parse_tile_payload(payload: Any) -> TilePayload | None:
    """Parse a raw dict into a ``TilePayload``, or ``None`` if invalid."""
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
    """Parse a raw dict into a ``PublicPlayerPayload``, or ``None`` if required fields are missing."""
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
    """Parse a raw dict into a ``ViewerPayload``, or ``None`` if required fields are missing."""
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
    """Parse a raw dict into a ``TurnPayload``, or ``None`` if the input is not a dict."""
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


def _parse_last_shift_payload(payload: Any) -> LastShiftPayload | None:
    if payload is None:
        return None
    if not isinstance(payload, dict):
        return None

    side = parse_enum(payload.get("side"), InsertionSide)
    index = parse_int(payload.get("index"))
    rotation = parse_int(payload.get("rotation"))
    if side is None or index is None or rotation is None:
        return None
    return {"side": side, "index": index, "rotation": rotation}


def _parse_last_move_payload(payload: Any) -> LastMovePayload | None:
    if payload is None:
        return None
    if not isinstance(payload, dict):
        return None

    player_id = parse_str(payload.get("player_id"))
    path = _parse_position_list(payload.get("path"))
    collected_treasure_type = parse_optional_enum(payload.get("collected_treasure_type"), TreasureType)
    if player_id is None or path is None:
        return None
    return {
        "player_id": player_id,
        "path": path,
        "collected_treasure_type": collected_treasure_type,
    }


def parse_game_snapshot_payload(payload: Mapping[str, Any]) -> GameSnapshotPayload | None:
    """Parse a full game snapshot payload, or ``None`` if any required field is missing or malformed."""
    game_id = parse_str(payload.get("game_id"))
    code = parse_str(payload.get("code"))
    phase = parse_enum(payload.get("phase"), GamePhase)
    revision = parse_int(payload.get("revision"))
    board_size = parse_int(payload.get("board_size"))
    leader_player_id = parse_optional_str(payload.get("leader_player_id"))
    turn = _parse_turn_payload(payload.get("turn"))
    tiles_raw = payload.get("tiles")
    reachable_positions_raw = payload.get("reachable_positions")
    players_raw = payload.get("players")
    viewer_raw = payload.get("viewer")
    last_shift = _parse_last_shift_payload(payload.get("last_shift"))
    last_move = _parse_last_move_payload(payload.get("last_move"))

    if game_id is None or code is None or phase is None or turn is None or revision is None or board_size is None:
        return None
    if not isinstance(tiles_raw, list) or not isinstance(players_raw, list):
        return None
    reachable_positions = _parse_position_list(reachable_positions_raw)
    if reachable_positions is None:
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

    snapshot: GameSnapshotPayload = {
        "game_id": game_id,
        "code": code,
        "phase": phase,
        "revision": revision,
        "board_size": board_size,
        "leader_player_id": leader_player_id,
        "turn": turn,
        "tiles": tiles,
        "reachable_positions": reachable_positions,
        "players": players,
        "viewer": viewer,
    }
    if "last_shift" in payload:
        if payload.get("last_shift") is not None and last_shift is None:
            return None
        if last_shift is not None:
            snapshot["last_shift"] = last_shift
    if "last_move" in payload:
        if payload.get("last_move") is not None and last_move is None:
            return None
        if last_move is not None:
            snapshot["last_move"] = last_move
    return snapshot


def make_game_snapshot_payload(
    game: GameData,
    players: list[PlayerData],
    tiles: list[TileData],
    treasures_by_player: Mapping[UUID, list[TreasureData]],
    *,
    viewer_player_id: str | None,
) -> GameSnapshotPayload:
    """Build a full ``GameSnapshotPayload`` from the current server-side game state."""
    viewer_player = next((player for player in players if str(player.id) == viewer_player_id), None)
    reachable_positions = _reachable_positions_for_viewer(game, viewer_player, tiles)
    snapshot: GameSnapshotPayload = {
        "game_id": str(game.id),
        "code": game.code,
        "phase": game.game_phase,
        "revision": game.revision,
        "board_size": game.board_size,
        "leader_player_id": str(game.leader_player_id) if game.leader_player_id is not None else None,
        "turn": {
            "current_player_id": str(game.current_player_id) if game.current_player_id is not None else None,
            "turn_phase": game.turn_phase,
            "blocked_insertion_side": game.blocked_insertion_side,
            "blocked_insertion_index": game.blocked_insertion_index,
        },
        "tiles": [make_tile_payload(tile) for tile in tiles],
        "reachable_positions": [{"x": x, "y": y} for x, y in reachable_positions],
        "players": [make_public_player_payload(player, treasures_by_player.get(player.id, [])) for player in players],
        "viewer": make_viewer_payload(game, viewer_player, treasures_by_player.get(viewer_player.id, []) if viewer_player is not None else []),
    }
    if game.last_shift_side is not None and game.last_shift_index is not None and game.last_shift_rotation is not None:
        snapshot["last_shift"] = {
            "side": game.last_shift_side,
            "index": game.last_shift_index,
            "rotation": game.last_shift_rotation,
        }
    last_move_path = _parse_position_path(game.last_move_path)
    if game.last_move_player_id is not None and last_move_path:
        snapshot["last_move"] = {
            "player_id": str(game.last_move_player_id),
            "path": [{"x": x, "y": y} for x, y in last_move_path],
            "collected_treasure_type": (
                None if game.last_move_collected_treasure_type is None else game.last_move_collected_treasure_type
            ),
        }
    return snapshot


def _reachable_positions_for_viewer(
    game: GameData,
    viewer_player: PlayerData | None,
    tiles: list[TileData],
) -> list[tuple[int, int]]:
    if viewer_player is None or game.game_phase != GamePhase.GAME:
        return []
    if game.turn_phase != TurnPhase.MOVE or game.current_player_id != viewer_player.id:
        return []
    if viewer_player.position_x is None or viewer_player.position_y is None or not tiles:
        return []

    board = Board.from_tile_data(game, tiles)
    return sorted(board.reachable_positions((viewer_player.position_x, viewer_player.position_y)))


def make_public_player_payload(player: PlayerData, treasures: list[TreasureData]) -> PublicPlayerPayload:
    """Build the public-facing player payload (no private treasure details)."""
    position: PositionPayload | None = None
    if player.position_x is not None and player.position_y is not None:
        position = {"x": player.position_x, "y": player.position_y}
    collected = [treasure.treasure_type.value for treasure in sorted(treasures, key=lambda current: current.order_index) if treasure.collected]
    remaining = sum(1 for treasure in treasures if not treasure.collected)
    return {
        "id": str(player.id),
        "display_name": player.display_name,
        "status": player.status,
        "result": player.result,
        "placement": player.placement,
        "join_order": player.join_order,
        "piece_color": player.piece_color,
        "position": position,
        "collected_treasures": collected,
        "remaining_treasure_count": remaining,
    }


def make_viewer_payload(game: GameData, player: PlayerData | None, treasures: list[TreasureData]) -> ViewerPayload | None:
    """Build the viewer payload for the local player, including private treasure info."""
    if player is None:
        return None
    ordered = sorted(treasures, key=lambda current: current.order_index)
    collected = [treasure.treasure_type.value for treasure in ordered if treasure.collected]
    active_treasure_type = (
        next((treasure.treasure_type.value for treasure in ordered if not treasure.collected), None)
        if player.status == PlayerStatus.ACTIVE
        else None
    )
    return {
        "player_id": str(player.id),
        "is_leader": game.leader_player_id == player.id,
        "is_current_player": player.status == PlayerStatus.ACTIVE and game.current_player_id == player.id,
        "active_treasure_type": active_treasure_type,
        "collected_treasures": collected,
        "remaining_treasure_count": sum(1 for treasure in ordered if not treasure.collected),
    }


def make_tile_payload(tile: TileData) -> TilePayload:
    """Serialise a ``TileData`` model into a ``TilePayload`` dict."""
    payload: TilePayload = {
        "id": str(tile.id),
        "tile_type": tile.tile_type,
        "rotation": tile.rotation,
        "is_spare": tile.is_spare,
        "treasure_type": tile.treasure_type,
    }
    if tile.row is not None:
        payload["row"] = tile.row
    if tile.column is not None:
        payload["column"] = tile.column
    return payload


def _parse_position_path(encoded: str | None) -> list[tuple[int, int]] | None:
    if encoded is None:
        return None
    if encoded == "":
        return []

    path: list[tuple[int, int]] = []
    for segment in encoded.split(";"):
        x_raw, separator, y_raw = segment.partition(",")
        if separator != ",":
            return None
        try:
            path.append((int(x_raw), int(y_raw)))
        except ValueError:
            return None
    return path
