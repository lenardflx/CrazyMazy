# Author: Raphael Eiden
 
from __future__ import annotations

from shared.types.data import PlayerData, TileData, TreasureData, GameData


class PlayerTable(PlayerData, table=True):
    __tablename__ = 'player'


class TileTable(TileData, table=True):
    __tablename__ = 'tile'


class TreasureTable(TreasureData, table=True):
    __tablename__ = 'treasure'


class GameTable(GameData, table=True):
    __tablename__ = 'game'

