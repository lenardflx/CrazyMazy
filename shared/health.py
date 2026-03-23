# Author: Lenard Felix

PING = "ping"
PONG = "pong"


def make_ping() -> dict:
    return {"type": PING}


def make_pong() -> dict:
    return {"type": PONG}


def is_ping(msg: dict) -> bool:
    return msg.get("type") == PING


def is_pong(msg: dict) -> bool:
    return msg.get("type") == PONG
