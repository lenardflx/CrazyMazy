from __future__ import annotations

from server.network.models import OutgoingMessage
from shared.network import send_msg


def flush_outgoing(messages: list[OutgoingMessage]) -> None:
    for outgoing in messages:
        send_msg(outgoing.conn, outgoing.msg)
