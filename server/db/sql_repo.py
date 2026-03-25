# Author: Tamay Engin

from uuid import UUID

from server.db import GameRepository
from server.db.repo import PlayerRepository
from shared.models import *

class GameRepositorySQL(GameRepository):
    def find_game_by_id(self, engine, game_id: UUID) -> Game:
        with Session(engine) as session:
            try:
                return session.exec(select(Game).where(Game.id == game_id))[0]
            except Exception as e:
                error = {"status": "error", "message": str(e)}

    def create_game(self, engine, board_size: int, leader_player_id: UUID) -> Game:
        game = Game(board_size, leader_player_id)
        with Session(engine) as session:
            try:
                session.add(game)
                session.commit()
                return game
            except Exception as e:
                error = {"status": "error", "message": str(e)}

    def delete_game(self, engine, game_id: int):
        with Session(engine) as session:
            game = session.exec(select(Game).where(Game.id == id))[0]
            try:
                session.delete(game)
                session.commit()
            except Exception as e:
                error = {"status": "error", "message": str(e)}

    def update_game(self, engine, new_game: Game):
        with Session(engine) as session:
            try:
                session.add(new_game)
                session.commit()
                session.refresh(new_game)
            except Exception as e:
                error = {"status": "error", "message": str(e)}

    def find_by_join_code(self, engine, join_code: str) -> Game:
        with Session(engine) as session:
            try:
                return session.exec(select(Player).where(Game.join_code == join_code))[0]
            except Exception as e:
                error = {"status": "error", "message": str(e)}


class PlayerRepositorySQL(PlayerRepository):
    def create_player(self, engine, display_name: str, connection_id: str) -> Player:
        player = Player(display_name=display_name, connection_id=connection_id)
        with Session(engine) as session:
            try:
                session.add(player)
                session.commit()
                return player
            except Exception as e:
                error = {"status": "error", "message": str(e)}

    def find_by_id(self, engine, id: UUID) -> Player:
        with Session(engine) as session:
            try:
                return session.exec(select(player).where(player.id == id))[0]
            except Exception as e:
                error = {"status": "error", "message": str(e)}

    def update_player(self, engine, player: Player) -> Player:
        with Session(engine) as session:
            try:
                session.add(player)
                session.commit()
                session.refresh(player)
            except Exception as e:
                error = {"status": "error", "message": str(e)}
