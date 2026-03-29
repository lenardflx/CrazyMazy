# Game Flow

This document describes both the player-facing game flow and how the software supports it from lobby to match end.

## Overview

Players try to:

1. join a lobby
2. start a match with other players
3. shift the maze
4. move through reachable paths
5. collect their assigned treasures in order
6. return to their home corner

The first player to finish that sequence wins.

## Core Concepts

### Board
The board is a square maze made of tiles. Each tile has a shape, an orientation, open/closed sides, and sometimes a treasure.

One tile is always outside the board as the **spare tile**.

### Spare Tile
On each turn, the current player inserts the spare tile at a valid entry point with a chosen orientation. This shifts one row or column and ejects a new spare tile on the opposite side.

Players on the shifted line move with it. If pushed off the board, they wrap around to the opposite side.

### Players
Each player has:

- a display name
- a join order
- a piece color / skin
- a board position
- a match status
- an ordered treasure list

### Treasures
Players only care about their **next uncollected treasure**.

That means:

- landing on a treasure only matters if it is the current target
- collecting all treasures is not enough by itself
- the player must also return home to win

## Match Phases

The game moves through three phases:

- **Lobby**
- **Active Match**
- **Post-Game**

### Lobby
Players create or join a lobby, choose settings such as board size, and wait until enough players are present. The earliest valid leader controls match start.

### Active Match
When the game starts:

- a new board is generated
- players are placed on home corners
- treasures are assigned
- one player becomes the current turn owner

Each turn has two steps:

1. **Shift** the maze
2. **Move** through reachable paths

### Post-Game
The game enters post-game when a player wins or too few active players remain. Results and follow-up choices such as rematch or return to menu are shown here.

## Turn Flow

### 1. Shift
The current player inserts the spare tile, changing the maze before movement.

Effects:

- routes open and close
- players on the shifted row/column are carried along
- immediate reversal of the previous shift is blocked

### 2. Move
After shifting, the same player may move to any reachable tile connected by open paths.

If the destination contains the current target treasure, that treasure is collected and the next one becomes active.

If the player has no treasures left and returns to their home corner, they win and the match ends.

## Special Cases

### Give Up
Giving up means the player stops participating in the current match as an active competitor.
They can still watch the match as a spectator, but they cannot win or interact with the board.

### Leave
A player may leave from lobby, active match, or post-game. Leaving removes them from the session and triggers any required leader or turn cleanup.

### Leader Reassignment
If the leader leaves, leadership passes to the earliest-joined remaining player.

### Turn Reassignment
If the current player leaves during an active match, the turn passes to the next active player.

## End Conditions

The game ends in two main ways:

### Normal Win
A player collects all assigned treasures and returns to their home corner.

### Finish Without Winning
A player can also be done with active participation without being the winner.

Typical examples are:

- they give up and become a spectator while the match continues
- they finish in a placement other than first once the round is resolved

So “finished” and “won” are not the same thing.

### Too Few Active Players
If too many players leave or give up during a match, the game ends early and transitions to post-game.

## Software Model

The software uses an **authoritative server** and **snapshot-driven clients**.

- the **server** owns the true game state and validates actions
- the **client** renders the latest snapshot and sends user intent
- the **shared layer** defines models, events, and board/game-state structures used by both sides

In runtime terms, the flow is:

1. the player performs an action on the client
2. the client sends an event to the server
3. the server validates and updates authoritative state
4. the server broadcasts a new snapshot
5. the client re-renders from that snapshot

This keeps one central rule intact:

- gameplay truth lives on the server
- presentation and input live on the client
