# Author: Tamay Engin

from sqlmodel import Field, SQLModel

class Player(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    game_id: int = Field(default=None, foreign_key="game.id")
    role: int
    active: bool
    position_x: int
    position_y: int
    game_id: int = Field(default=None, foreign_key="game.id")
    order: int
    score: int
