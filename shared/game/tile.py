# Author: Lennart William Owen, Raphael Eiden, Sarah Trapp, Lenard Felix

from __future__ import annotations

from collections import deque

from shared.types.data import TileData
from shared.types.enums import TileOrientation, TileType, TreasureType
from shared.types.payloads import TilePayload


class Tile:
    def __init__(self, type: TileType, orientation: TileOrientation | int, treasure: None | TreasureType = None):
        """
        Represents a single tile on the board.

        Args:
            type: The structural tile type (STRAIGHT, CORNER, T_PIECE, WALL(just for testing)).
            orientation: The current rotation of the tile (NORTH/EAST/SOUTH/WEST).
            treasure: Optional treasure placed on this tile.
        """

        # Basic tile metadata
        self.type = TileType(type)
        self.orientation = TileOrientation(orientation)
        self.treasure = None if treasure is None else TreasureType(treasure)
        
        # Path connectivity in order [N, E, S, W]
        # Example: [1,0,1,0] means open to North + South
        self.path = None

        # Compute initial path layout based on type + orientation
        self.set_paths()

    def set_paths(self) -> None:
        """
        Computes the tile's connectivity (open paths) based on its type and orientation.

        Base patterns are defined for NORTH orientation.
        Then we rotate the deque to match the actual orientation.
        """

        # base path pattern for orientation NORTH
        parse_Tiletype = {TileType.STRAIGHT: [1,0,1,0], # N E S W
                          TileType.CORNER : [1,1,0,0],
                          TileType.T : [1,1,0,1],
                          TileType.WALL : [0,0,0,0]}
        # set exit values for path
        path = deque(parse_Tiletype[self.type])


        # Rotate the connectivity pattern according to orientation
        # TileOrientation.value is 0=N, 1=E, 2=S, 3=W
        path.rotate(TileOrientation(self.orientation).value)

        # Convert deque → list for easier use elsewhere
        self.path = list(path)

    def rotate_left(self):
        """
        Rotates the tile 90° counter-clockwise.

        Updates:
        - orientation
        - path connectivity
        """

        # Decrease orientation index modulo 4
        self.orientation = TileOrientation((self.orientation.value - 1) % 4)

        # Recompute connectivity
        self.set_paths()

    def rotate_right(self):
        """
        Rotates the tile 90° clockwise.

        Updates:
        - orientation
        - path connectivity
        """

        # Increase orientation index modulo 4
        self.orientation = TileOrientation((self.orientation.value + 1) % 4)

        # Recompute connectivity
        self.set_paths()

    @classmethod
    def from_payload(cls, payload: TilePayload) -> "Tile":
        return cls(
            payload["tile_type"],
            payload["rotation"],
            payload["treasure_type"],
        )

    @classmethod
    def from_tile_data(cls, tile: TileData) -> "Tile":
        return cls(tile.tile_type, tile.rotation, tile.treasure_type)
