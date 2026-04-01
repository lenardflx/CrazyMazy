# CrazyMazy
> Software Engineering, Group 1, Team Spirit

The board game "Das Verrückte Labyrinth" as a multiplayer game built with Python and Pygame.

## Requirements

- Python 3.11+

Setup a virtual Environment:
```shell
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Install dependencies:
```shell
pip install -r requirements.txt
```

## Setup

Copy the `.env.example` file to `.env` and adjust as needed

## Run & Debug

Start server and a single client together:
```shell
make dev
```

Start server with two clients simultaneously:
```shell
make dev2
```

For a custom number of clients, and also Windows users (since the Make command may crash in Windows), use:
```shell
./dev.sh -c <number>
```

## Testing

```shell
pytest
```

## Local Stats

The client keeps a small set of local multiplayer stats in `data/app_data.json`.
They are shown in the main menu through the star button and currently track:

- games played
- games won
- win rate
- treasures collected
- moves made

These stats are derived on the client from incoming multiplayer snapshots and are
meant for personal progress only. They are not authoritative server-side stats.

## Project Structure

```
├── client/      # Pygame GUI client (screens, UI, network, state)
├── server/      # TCP socket server (handlers, game service, db)
├── shared/      # Models, events, protocol, and game logic used by both
├── docs/        # Architecture and gameplay documentation
├── tests/       # Pytest test suite
└── assets/      # Game images and UI assets
```

## Documentation

Start with [docs/README.md](./docs/README.md).
