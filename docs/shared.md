# Shared Layer

The `shared/` package is the contract between client and server. It defines the game schema, state representation, and serialization rules.

## Main Files

### Models

The file [`../shared/models.py`](../shared/models.py) contains enum types as well as database models.

### Events

The file [`../shared/events/`](../shared/events) defines the event classes exchanged between client and server.

### Snapshot Construction

The file [`../shared/lib/snapshot.py`](../shared/lib/snapshot.py) builds the client-facing snapshot payload.

### Runtime Game State

The file [`../shared/state/game_state.py`](../shared/state/game_state.py) is the most important shared runtime module. It contains board logic and game rules, as well as the server-side `GameState` and client-side `SnapshotGameState` classes.

## Important Classes

### `Board`

`Board` owns board-level runtime behavior:

- shifting rows and columns
- spare tile handling
- movement validation
- reachable-position calculation

### `GameState`

`GameState` is the server-side assembled state object used by the service layer.

It combines:

- `GameData`
- players
- board
- treasures by player

### `SnapshotGameState`

`SnapshotGameState` is the client-facing parsed snapshot.

It exposes convenience helpers so client screens do not need to recompute simple rules:

- `ordered_players`
- `viewer_turn`
- `can_shift`
- `can_move`
- `turn_prompt`
- `spare_tile`
- `rotated_spare_tile(...)`
- `home_color_at(...)`

That is intentional, so that the client can be a thin rendering layer without game logic.
