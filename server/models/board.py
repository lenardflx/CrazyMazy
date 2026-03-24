# Author: Tamay Engin

from sqlmodel import Field, SQLModel

class Board(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    game_id: int = Field(foreign_key="game.id")
