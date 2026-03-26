# Author: Lenard Felix, Raphael Eiden, Tamay Engin

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar
from uuid import UUID

from sqlmodel import Session, select

from server.db.repo import GameRepository, PlayerRepository, TileRepository, TreasureRepository
from shared.models import GameData, PlayerColor, PlayerData, TileData, TreasureData
from shared.table_models import GameTable, PlayerTable, TileTable, TreasureTable

ResultT = TypeVar("ResultT")


class SQLRepository:
    def read(self, fn: Callable[[Session], ResultT]) -> ResultT:
        return fn(self.session)

    def write(self, fn: Callable[[Session], ResultT]) -> ResultT:
        result = fn(self.session)
        self.session.commit()
        return result


class GameRepositorySQL(SQLRepository, GameRepository):
    def __init__(self, engine):
        self.session = Session(engine)

    def find_by_game_id(self, game_id: UUID) -> GameData | None:
        return self.read(
            lambda session: self.session.get(GameTable, game_id)
        )

    def find_by_join_code(self, join_code: str) -> GameData | None:
        return self.read(
            lambda session: self.session.exec(
                select(GameTable).where(GameTable.code == join_code)
            ).first()
        )

    def create_game(self, board_size: int, leader_player_id: UUID | None = None) -> GameData:
        def op(session: Session) -> GameData:
            game = GameTable(
                code="0000",
                leader_player_id=leader_player_id,
                board_size=board_size,
            )
            self.session.add(game)
            self.session.flush()
            self.session.refresh(game)
            return game

        return self.write(op)

    def update_game(self, new_game: GameData) -> GameData:
        def op(session: Session) -> GameData:
            db_game = self.session.merge(GameTable.model_validate(new_game))
            self.session.flush()
            self.session.refresh(db_game)
            return db_game

        return self.write(op)

    def delete_game(self, game_id: UUID) -> None:
        def op(session: Session) -> None:
            game = self.session.get(GameTable, game_id)
            if game:
                self.session.delete(game)

        self.write(op)


class PlayerRepositorySQL(SQLRepository, PlayerRepository):
    def __init__(self, engine):
        self.session = Session(engine)

    def create_player(
        self,
        display_name: str,
        connection_id: str,
        game_id: UUID,
        join_order: int,
        piece_color: PlayerColor,
    ) -> PlayerData:
        def op(session: self.Session) -> PlayerData:
            player = PlayerTable(
                display_name=display_name,
                connection_id=connection_id,
                game_id=game_id,
                join_order=join_order,
                piece_color=piece_color,
            )
            self.session.add(player)
            self.session.flush()
            self.session.refresh(player)
            return player

        return self.write(op)

    def find_by_id(self, player_id: UUID) -> PlayerData | None:
        return self.read(lambda session: self.session.get(PlayerTable, player_id))

    def find_by_connection_id(self, connection_id: str) -> PlayerData | None:
        return self.read(
            lambda session: self.session.exec(
                select(PlayerTable).where(PlayerTable.connection_id == connection_id)
            ).first()
        )

    def list_by_game_id(self, game_id: UUID) -> list[PlayerData]:
        return self.read(
            lambda session: list(
                self.session.exec(
                    select(PlayerTable).where(PlayerTable.game_id == game_id)
                ).all()
            )
        )

    def update_player(self, player: PlayerData) -> PlayerData:
        def op(session: Session) -> PlayerData:
            db_player = self.session.merge(PlayerTable.model_validate(player))
            self.session.flush()
            self.session.refresh(db_player)
            return db_player

        return self.write(op)


class TileRepositorySQL(SQLRepository, TileRepository):
    def __init__(self, engine):
        self.session = Session(engine)

    def create_tile(self, tile: TileData) -> TileData:
        def op(session: Session) -> TileData:
            db_tile = TileTable.model_validate(tile)
            self.session.add(db_tile)
            self.session.flush()
            self.session.refresh(db_tile)
            return db_tile

        return self.write(op)

    def find_by_id(self, tile_id: UUID) -> TileData | None:
        return self.read(lambda session: self.session.get(TileTable, tile_id))

    def list_by_game_id(self, game_id: UUID) -> list[TileData]:
        return self.read(
            lambda session: list(
                self.session.exec(select(TileTable).where(TileTable.game_id == game_id)).all()
            )
        )

    def update_tile(self, tile: TileData) -> TileData:
        def op(session: Session) -> TileData:
            db_tile = self.session.merge(TileTable.model_validate(tile))
            self.session.flush()
            self.session.refresh(db_tile)
            return db_tile

        return self.write(op)

    def delete_tile(self, tile_id: UUID) -> None:
        def op(session: Session) -> None:
            tile = self.session.get(TileTable, tile_id)
            if tile:
                self.session.delete(tile)

        self.write(op)


class TreasureRepositorySQL(SQLRepository, TreasureRepository):
    def __init__(self, engine):
        self.session = Session(engine)

    def create_treasure(self, treasure: TreasureData) -> TreasureData:
        def op(session: Session) -> TreasureData:
            db_treasure = TreasureTable.model_validate(treasure)
            self.session.add(db_treasure)
            self.session.flush()
            self.session.refresh(db_treasure)
            return db_treasure

        return self.write(op)

    def find_by_id(self, treasure_id: UUID) -> TreasureData | None:
        return self.read(lambda session: self.session.get(TreasureTable, treasure_id))

    def list_by_player_id(self, player_id: UUID) -> list[TreasureData]:
        return self.read(
            lambda session: list(
                self.session.exec(
                    select(TreasureTable).where(TreasureTable.player_id == player_id)
                ).all()
            )
        )

    def update_treasure(self, treasure: TreasureData) -> TreasureData:
        def op(session: Session) -> TreasureData:
            db_treasure = self.session.merge(TreasureTable.model_validate(treasure))
            self.session.flush()
            self.session.refresh(db_treasure)
            return db_treasure

        return self.write(op)

    def delete_treasure(self, treasure_id: UUID) -> None:
        def op(session: Session) -> None:
            treasure = self.session.get(TreasureTable, treasure_id)
            if treasure:
                self.session.delete(treasure)

        self.write(op)
        
