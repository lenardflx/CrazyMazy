# Author: Tamay Engin

from uuid import UUID

from sqlmodel import select

from server.db import GameRepository
from server.db.repo import PlayerRepository
from server.db.engine import get_session
from shared.models import *
from shared.table_models import GameTable


class GameRepositorySQL(GameRepository):
    def find_game_by_id(self, game_id: UUID) -> Optional[GameData]:
        session = get_session
        try:
            return session.exec(select(GameTable).where(GameTable.id == game_id))[0]
        except Exception as e:
            error = {"status": "error", "message": str(e)}

    def create_game(self, board_size: int, leader_player_id: UUID) -> Optional[GameData]:
        game = GameData(board_size=board_size, leader_player_id=leader_player_id, )
        try:
            session = get_session()
            session.add(game)
            session.commit()
            return game
        except Exception as e:
            error = {"status": "error", "message": str(e)}

    def delete_game(self, game_id: int):
        # game = session.exec(select(Game).where(Game.id == id))[0]
        # try:
        #     session = get_session()
        #     session.delete(game)
        #     session.commit()
        # except Exception as e:
        #     error = {"status": "error", "message": str(e)}
        pass

    def update_game(self, new_game: GameData):
        try:
            session = get_session()
            session.add(new_game)
            session.commit()
            session.refresh(new_game)
        except Exception as e:
            error = {"status": "error", "message": str(e)}

    def find_by_join_code(self, join_code: str) -> Optional[GameData]:
        try:
            session = get_session()
            return session.exec(select(GameTable).where(GameTable.join_code == join_code))[0]
        except Exception as e:
            error = {"status": "error", "message": str(e)}


class PlayerRepositorySQL(PlayerRepository):
    def create_player(self, display_name: str, connection_id: str) -> PlayerData:
        # player = Player(display_name=display_name, connection_id=connection_id)
        # try:
        #     session = get_session()
        #     session.add(player)
        #     session.commit()
        #     return player
        # except Exception as e:
        #     error = {"status": "error", "message": str(e)}
        pass

    def find_by_id(self, id: UUID) -> Optional[PlayerData]:
        # try:
        #     session = get_session()
        #     return session.exec(select(player).where(player.id == id))[0]
        # except Exception as e:
        #     error = {"status": "error", "message": str(e)}
        pass

    def update_player(self, player: PlayerData) -> Optional[PlayerData]:
        try:
            session = get_session()
            session.add(player)
            session.commit()
            session.refresh(player)
        except Exception as e:
            error = {"status": "error", "message": str(e)}
