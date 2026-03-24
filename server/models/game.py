# Author: Tamay Engin

from sqlmodel import Field, SQLModel

class Game(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    lobby_code: str 
    board_id: int
    admin: int | None = Field(default=None, foreign_key="player.id")
    finished: bool 
