# Author: Lenard Felix

import socket

from server.dispatch import dispatcher
from shared.network import send_msg
from shared.protocol import EventType, Message


@dispatcher.handler(EventType.CLIENT_HEALTH_PING)
def handle_ping(conn: socket.socket, msg: Message) -> None:
    send_msg(conn, Message(type=EventType.SERVER_HEALTH_PONG).to_dict())