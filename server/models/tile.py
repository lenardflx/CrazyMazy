# Author: Tamay Engin

from sqlmodel import Field, SQLModel

class Tile(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    board_id: int = Field(default=None, foreign_key="board.id")
    treasure_id: int = Field(default=None, foreign_key="treasure.id")
    row: int
    column: int
    orientation: int
    type: int
