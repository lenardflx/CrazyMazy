# Server

The server is the authoritative owner of game mutations.

## Main Files

### Entry Point

The file [`../server/main.py`](../server/main.py) starts the server runtime and wires up networking plus repositories.

### Request Handlers

The file [`../server/handlers/game_flow.py`](../server/handlers/game_flow.py) contains the request handlers. Handlers should not contain business rules. It is only an adapter between the network layer and the service layer.

### Service Layer

The [`../server/service.py`](../server/service.py) is the core gameplay orchestration layer. It owns:

- lobby creation and joining
- game start and restart
- shift and move validation
- turn progression
- leader reassignment
- departure handling
- give-up handling
- end-of-game transitions

### Persistence

The file [`../server/db/repo.py`](../server/db/repo.py) defines the abstract `Repo` interface for game data persistence. It contains all nessesary CRUD operations.

The `Repo` interface is implemented by both: 

- [`../server/db/sql_repo.py`](../server/db/sql_repo.py)
- [`../server/db/memory_repo.py`](../server/db/memory_repo.py)

while the MemoryRepo is used for testing, the SqlRepo is used in production and development.

## Request Path

For a normal game action:

1. a client sends an event
2. the handler in [`../server/handlers/game_flow.py`](../server/handlers/game_flow.py) receives it
3. the handler calls the corresponding `GameService` method
4. `GameService` updates repository state
5. the updated state is converted into a snapshot and broadcast

## Where To Change What

### Add or change a gameplay rule

Start in: [`../server/service.py`](../server/service.py)

Potential shared follow-up: [`../shared/state/game_state.py`](../shared/state/game_state.py)

### Add a new network action

Touch:

- event definition in `shared/events/`
- parsing/contract logic in `shared/lib/`
- handler in [`../server/handlers/game_flow.py`](../server/handlers/game_flow.py)
- client sender in [`../client/network/services/`](../client/network/services)

### Change persistence behavior

Touch:

- `server/db/` repository code
