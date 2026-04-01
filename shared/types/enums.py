from enum import Enum, StrEnum


class PlayerStatus(StrEnum):
    """
    Defines the participation status of a player in the current game lifecycle.
    Players that WIN or GIVE UP are considered OBSERVERS, while those that leave the game are DEPARTED.
    """
    ACTIVE = "ACTIVE"
    OBSERVER = "OBSERVER"
    DEPARTED = "DEPARTED"


class PlayerLeaveReason(StrEnum):
    KICKED = "KICKED"
    LEFT = "LEFT"


class PlayerResult(StrEnum):
    """
    Defines the final outcome of a player within the current game loop.
    """
    NONE = "NONE"
    WON = "WON"
    FORFEITED = "FORFEITED"


class PlayerColor(StrEnum):
    """
    Defines the identity of a player's figure on the board.
    """
    RED = "RED"
    BLUE = "BLUE"
    GREEN = "GREEN"
    YELLOW = "YELLOW"


class PlayerSkin(StrEnum):
    """
    Defines the visual skin of a player's figure on the board.
    """
    DEFAULT = "DEFAULT"


class TileType(StrEnum):
    """
    Defines the type of a tile on the board, which determines its shape and how it can be shifted.
    The WALL type is only used for testing purposes and is not part of the actual game mechanics.
    """
    STRAIGHT = "STRAIGHT"
    CORNER = "CORNER"
    T = "T"
    WALL = "WALL" # testing only


class TreasureType(StrEnum):
    """
    Defines the type of treasure printed on a tile, which players need to collect to win the game.
    """
    SKULL = "SKULL"
    SWORD = "SWORD"
    GOLDBAG = "GOLDBAG"
    KEYS = "KEYS"
    EMERALD = "EMERALD"
    ARMOR = "ARMOR"
    BOOK = "BOOK"
    CROWN = "CROWN"
    CHEST = "CHEST"
    CANDLE = "CANDLE"
    MAP = "MAP"
    RING = "RING"
    DRAGON = "DRAGON"
    GHOST = "GHOST"
    BAT = "BAT"
    GOBLIN = "GOBLIN"
    PRINCESS = "PRINCESS"
    GENIE = "GENIE"
    BUG = "BUG"
    OWL = "OWL"
    LIZARD = "LIZARD"
    SPIDER = "SPIDER"
    FLY = "FLY"
    RAT = "RAT"

class TileOrientation(Enum):
    """
    Defines the orientation of a tile on the board.
    """
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


class GamePhase(StrEnum):
    """
    Defines the lifecycle phases of a game.
    """
    PREGAME = "PREGAME"
    GAME = "GAME"
    POSTGAME = "POSTGAME"


class GameEndReason(StrEnum):
    """
    Defines the reason why a game ended once it reaches the POSTGAME phase.
    """
    PLAYERS_LEFT = "PLAYERS_LEFT"
    COMPLETED = "COMPLETED"


class TurnPhase(StrEnum):
    """
    Defines the phases of a player's turn during an active match.
    """
    SHIFT = "SHIFT" # move tile
    MOVE = "MOVE" # move player position


class InsertionSide(StrEnum):
    """
    Defines the possible sides of the board where a tile can be inserted during the SHIFT phase of a turn.
    """
    TOP = "TOP"
    RIGHT = "RIGHT"
    BOTTOM = "BOTTOM"
    LEFT = "LEFT"


class PlayerControllerKind(StrEnum):
    """
    Defines whether a player slot is controlled by a human or by the server.
    """
    HUMAN = "HUMAN"
    NPC = "NPC"


class NpcDifficulty(StrEnum):
    """
    Defines future difficulty presets for NPC-controlled players.
    """
    EASY = "EASY"
    NORMAL = "NORMAL"
    HARD = "HARD"
