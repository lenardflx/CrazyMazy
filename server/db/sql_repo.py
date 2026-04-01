# Author: Lenard Felix, Raphael Eiden, Tamay Engin

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar
from uuid import UUID

from sqlmodel import SQLModel, Session, select

from server.db.repo import GameRepository, PlayerRepository, TileRepository, TreasureRepository
from shared.types.enums import GamePhase
from shared.types.enums import NpcDifficulty, PlayerColor, PlayerControllerKind, PlayerStatus
from shared.types.data import GameData, PlayerData, TileData, TreasureData
from shared.table_models import GameTable, PlayerTable, TileTable, TreasureTable

ResultT = TypeVar("ResultT")


class SQLRepository:
    session: Session

    def __init__(self, engine) -> None:
        """Ensure table metadata is materialized for fresh test databases."""
        SQLModel.metadata.create_all(engine)
        self.session = Session(engine)

    def read(self, fn: Callable[[Session], ResultT]) -> ResultT:
        return fn(self.session)

    def write(self, fn: Callable[[Session], ResultT]) -> ResultT:
        result = fn(self.session)
        self.session.commit()
        return result


class GameRepositorySQL(SQLRepository, GameRepository):
    def __init__(self, engine):
        super().__init__(engine)

    def find_by_game_id(self, game_id: UUID) -> GameData | None:
        """Returns the instance of the table Game that has a specific game_id."""
        return self.read(
            lambda session: self.session.get(GameTable, game_id)
        )

    def find_by_join_code(self, join_code: str) -> GameData | None:
        """Returns the instance of the table Game that has a specific join_code."""
        return self.read(
            lambda session: self.session.exec(
                select(GameTable).where(GameTable.code == join_code)
            ).first()
        )

    def list_public_games(self) -> list[GameData]:
        """Returns all instances of the table Game that are set to public and in the pregame phase."""
        return self.read(
            lambda session: list(self.session.exec(
                select(GameTable)
                .where(GameTable.is_public == True)  # noqa: E712
                .where(GameTable.game_phase == GamePhase.PREGAME)
                .order_by(GameTable.created_at)
            ).all())
        )

    def find_active_games(self) -> list[GameData]:
        """Returns all instances of the table Game that are in the game phase."""
        return self.read(
            lambda session: list(self.session.exec(
                select(GameTable)
                .where(GameTable.game_phase == GamePhase.GAME)
                .order_by(GameTable.created_at)
            ).all())
        )

    def create_game(
        self,
        board_size: int,
        leader_player_id: UUID | None = None,
        *,
        is_public: bool = False,
        player_limit: int = 4,
        insert_timeout: int = 0
    ) -> GameData:
        """Creates an instance of the table Game and returns it."""
        def op(session: Session) -> GameData:
            game = GameTable(
                code="0000",
                leader_player_id=leader_player_id,
                board_size=board_size,
                is_public=is_public,
                player_limit=player_limit,
                insert_timeout=insert_timeout
            )
            self.session.add(game)
            self.session.flush()
            self.session.refresh(game)
            return game

        return self.write(op)

    def update_game(self, new_game: GameData) -> GameData:
        """Updates an instance of the table Game and returns it."""
        def op(session: Session) -> GameData:
            db_game = self.session.merge(GameTable.model_validate(new_game))
            self.session.flush()
            self.session.refresh(db_game)
            return db_game

        return self.write(op)

    def delete_game(self, game_id: UUID) -> None:
        """Deletes an instance of the table Game."""
        def op(session: Session) -> None:
            game = self.session.get(GameTable, game_id)
            if game:
                self.session.delete(game)

        self.write(op)


class PlayerRepositorySQL(SQLRepository, PlayerRepository):
    def __init__(self, engine):
        super().__init__(engine)

    def create_player(
        self,
        display_name: str,
        connection_id: str | None,
        game_id: UUID,
        join_order: int,
        piece_color: PlayerColor,
        controller_kind: PlayerControllerKind = PlayerControllerKind.HUMAN,
        npc_difficulty: NpcDifficulty | None = None,
    ) -> PlayerData:
        """Creates an instance of the table Game and returns it."""
        def op(session: Session) -> PlayerData:
            player = PlayerTable(
                display_name=display_name,
                connection_id=connection_id,
                game_id=game_id,
                join_order=join_order,
                piece_color=piece_color,
                controller_kind=controller_kind,
                npc_difficulty=npc_difficulty,
            )
            self.session.add(player)
            self.session.flush()
            self.session.refresh(player)
            return player

        return self.write(op)

    def find_by_id(self, player_id: UUID) -> PlayerData | None:
        """Returns the instance of the table Player that has a specific player_id."""
        return self.read(lambda session: self.session.get(PlayerTable, player_id))

    def find_by_connection_id(self, connection_id: str) -> PlayerData | None:
        """Returns the instance of the table Player that has a specific connection_id."""
        candidates = self.read(
            lambda session: list(
                self.session.exec(
                    select(PlayerTable).where(PlayerTable.connection_id == connection_id)
                ).all()
            )
        )
        if not candidates:
            return None
        # Prefer the most recent live session when stale rows still carry the same connection id.
        return sorted(
            candidates,
            key=lambda player: (
                player.status == PlayerStatus.DEPARTED,
                -player.created_at.timestamp(),
            ),
        )[0]

    def list_by_game_id(self, game_id: UUID) -> list[PlayerData]:
        """Returns all instances of the table Player that have a specific game_id"""
        return self.read(
            lambda session: list(
                self.session.exec(
                    select(PlayerTable).where(PlayerTable.game_id == game_id)
                ).all()
            )
        )

    def update_player(self, player: PlayerData) -> PlayerData:
        """Updates an instance of the table Player and returns it."""
        def op(session: Session) -> PlayerData:
            db_player = self.session.merge(PlayerTable.model_validate(player))
            self.session.flush()
            self.session.refresh(db_player)
            return db_player

        return self.write(op)

    def delete_player(self, player_id: UUID) -> None:
        """Deletes an instance of the table Player."""
        def op(session: Session) -> None:
            player = self.session.get(PlayerTable, player_id)
            if player:
                self.session.delete(player)

        self.write(op)



class TileRepositorySQL(SQLRepository, TileRepository):
    def __init__(self, engine):
        super().__init__(engine)

    def create_tile(self, tile: TileData) -> TileData:
        """Creates an instance of the table Tile and returns it."""
        def op(session: Session) -> TileData:
            db_tile = TileTable.model_validate(tile)
            self.session.add(db_tile)
            self.session.flush()
            self.session.refresh(db_tile)
            return db_tile

        return self.write(op)

    def find_by_id(self, tile_id: UUID) -> TileData | None:
        """Returns the instance of the table Tile that has a specific tile_id."""
        return self.read(lambda session: self.session.get(TileTable, tile_id))

    def list_by_game_id(self, game_id: UUID) -> list[TileData]:
        """Returns all instances of the table Tile that have a specific game_id"""
        return self.read(
            lambda session: list(
                self.session.exec(select(TileTable).where(TileTable.game_id == game_id)).all()
            )
        )

    def update_tile(self, tile: TileData) -> TileData:
        """Updates an instance of the table Tile and returns it."""
        def op(session: Session) -> TileData:
            db_tile = self.session.merge(TileTable.model_validate(tile))
            self.session.flush()
            self.session.refresh(db_tile)
            return db_tile

        return self.write(op)

    def delete_tile(self, tile_id: UUID) -> None:
        """Deletes an instance of the table Tile."""
        def op(session: Session) -> None:
            tile = self.session.get(TileTable, tile_id)
            if tile:
                self.session.delete(tile)

        self.write(op)


class TreasureRepositorySQL(SQLRepository, TreasureRepository):
    def __init__(self, engine):
        super().__init__(engine)

    def create_treasure(self, treasure: TreasureData) -> TreasureData:
        """Creates an instance of the table Treasure and returns it."""
        def op(session: Session) -> TreasureData:
            db_treasure = TreasureTable.model_validate(treasure)
            self.session.add(db_treasure)
            self.session.flush()
            self.session.refresh(db_treasure)
            return db_treasure

        return self.write(op)

    def find_by_id(self, treasure_id: UUID) -> TreasureData | None:
        """Returns the instance of the table Treasure that has a specific treasure_id."""
        return self.read(lambda session: self.session.get(TreasureTable, treasure_id))

    def list_by_player_id(self, player_id: UUID) -> list[TreasureData]:
        """Returns all instances of the table Treasure that have a specific player_id"""
        return self.read(
            lambda session: list(
                self.session.exec(
                    select(TreasureTable).where(TreasureTable.player_id == player_id)
                ).all()
            )
        )

    def update_treasure(self, treasure: TreasureData) -> TreasureData:
        """Updates an instance of the table Treasure and returns it."""
        def op(session: Session) -> TreasureData:
            db_treasure = self.session.merge(TreasureTable.model_validate(treasure))
            self.session.flush()
            self.session.refresh(db_treasure)
            return db_treasure

        return self.write(op)

    def delete_treasure(self, treasure_id: UUID) -> None:
        """Deletes an instance of the table Treasure."""
        def op(session: Session) -> None:
            treasure = self.session.get(TreasureTable, treasure_id)
            if treasure:
                self.session.delete(treasure)

        self.write(op)
        
