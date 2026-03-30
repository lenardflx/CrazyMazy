# Architecture

## Repository Sections

The repository is split into four main areas:

- `client/`: Pygame application, local runtime state, UI, and outbound network actions
- `server/`: connection handling, request handlers, service layer, and persistence
- `shared/`: models, event contracts, protocol helpers, snapshot building, and game state logic
- `tests/`: unit and integration-style tests for client, server, and shared logic

## Runtime Direction

The runtime flow is:

1. The client sends an event such as `start_game`, `shift_tile`, `move_player`, `give_up`, or `leave_game`.
2. The server handler resolves the requesting player from the connection.
3. `GameService` validates the action and mutates authoritative state.
4. The server builds and broadcasts a fresh snapshot.
5. The client converts that snapshot into `SnapshotGameState`.
6. The active screen renders the new snapshot.

## Ownership Rules

Use these rules when deciding where code should go.

### `shared/`

Put code here if it is:

- needed by both client and server
- part of the event contract
- part of game rules or board logic
- part of snapshot construction or snapshot parsing

### `server/`

Put code here if it is:

- authoritative mutation of game state
- request validation tied to connected players
- persistence or repository logic
- mapping handler calls to service calls

### `client/`

Put code here if it is:

- screen composition
- UI rendering
- client-local form/runtime state
- sending an already-defined event to the server
