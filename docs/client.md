# Client

The client renders server snapshots and sends user intent back to the server.

## Main Areas

### Scene Management

- [`client/screens/core/scene_manager.py`](../client/screens/core/scene_manager.py)
- [`client/screens/core/transport_sync.py`](../client/screens/core/transport_sync.py)
- [`client/screens/core/screen_factory.py`](../client/screens/core/screen_factory.py)

Responsibilities:

- own the active screen
- sync network transport state into `SnapshotGameState`
- switch scenes based on server snapshots

### Game Screens

- [`client/screens/game/game_screen.py`](../client/screens/game/game_screen.py)
- [`client/screens/game/post_game_screen.py`](../client/screens/game/post_game_screen.py)
- [`client/screens/game/views/board_view.py`](../client/screens/game/views/board_view.py)
- [`client/screens/game/views/player_panel_view.py`](../client/screens/game/views/player_panel_view.py)

Responsibilities:

- `GameScreen`: orchestration, dialog flow, and dispatching selected actions
- `BoardView`: board layout, board rendering, spare-tile panel rendering, and click resolution
- `PlayerPanelView`: player sidebar rendering

- `PostGameScreen`: post-game layout and action buttons

### Menu and Lobby Screens

- [`client/screens/menu/`](../client/screens/menu)
- [`client/screens/lobby/`](../client/screens/lobby)

`MenuScreen` provides a reusable base for non-match screens.

### Outbound Network Actions

- [`client/network/services/lobby_service.py`](../client/network/services/lobby_service.py)
- [`client/network/services/game_service.py`](../client/network/services/game_service.py)

These services package user intent into event sends:

- create lobby
- join lobby
- start game
- shift tile
- move player
- give up
- leave game

It also updates local runtime error and pending-request state.

### Local Runtime State

- [`client/state/runtime_state.py`](../client/state/runtime_state.py)
- [`client/state/settings.py`](../client/state/settings.py)

`RuntimeState` is not authoritative game state. It only stores client-local UI state such as:

- pending requests
- current error target
- form errors
- spare-tile preview rotation

## How The Active Match Screen Works

1. `SceneManager` exposes the current `SnapshotGameState`
2. `GameScreen` asks `BoardView` for a layout and click resolution
3. `GameScreen` turns a resolved click into a network action
4. the next server snapshot updates the rendered state

This means:

- the client does not decide whether a move is valid in the authoritative sense
- the client may show likely-valid UI based on the snapshot
- the server still validates everything

## Where To Edit

### Change visual board rendering

- [`client/screens/game/views/board_view.py`](../client/screens/game/views/board_view.py)

### Change player sidebar visuals

- [`client/screens/game/views/player_panel_view.py`](../client/screens/game/views/player_panel_view.py)

### Change what happens when a user clicks a game control

- [`client/screens/game/game_screen.py`](../client/screens/game/game_screen.py)
- possibly [`client/network/services/game_service.py`](../client/network/services/game_service.py)

### Change screen routing after snapshots

- [`client/screens/core/transport_sync.py`](../client/screens/core/transport_sync.py)
