# Author: Tamay Engin

from sqlmodel import Field, SQLModel
from enum import StrEnum

class TreasureType(StrEnum):
    BOOK = "BOOK"
    OWL = "OWL"
    # TODO: add other Treasures

class Treasure(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # The player who needs collect this treasure
    player_id: uuid.UUID = Field(default=None, foreign_key="player.id", index=True)

    # The type of treasure
    treasure_type: TreasureType

    # Order of this target card in the players treasure sequence
    order_index: int = Field(index=True)

    # Whether this treasure has already been collected
    collected: bool = Field(default=False, index=True)

    # When this treasure was collected
    collected_at: Optional[datetime] = Field(default=None)
