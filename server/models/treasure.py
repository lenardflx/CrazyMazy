# Author: Tamay Engin

from sqlmodel import Field, SQLModel

class Treasure(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    player_id: int = Field(default=None, foreign_key="user.id")
    collected: bool
    order: int
    type: int
