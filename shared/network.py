# Author: Lenard Felix

from __future__ import annotations

import json
from typing import Protocol

from shared.protocol import Message, parse_message


class SupportsSendall(Protocol):
    """
    This trait acts as a type placeholder for any socket as any socket
    supports the `sendall` method. We use this for type safety in the
    `send_msg` method to ensure that the provided socket argument
    actually supports the `sendall` operation.
    """
    def sendall(self, data: bytes | bytearray | memoryview, flags: int = 0, /) -> None: ...


class SupportsRecv(Protocol):
    """
    This trait acts as a type placeholder for any socket supporting the `recv`
    method. This class only serves type safety purposes to avoid using a full socket
    class.
    """
    def recv(self, bufsize: int, flags: int = 0, /) -> bytes: ...


def send_msg(sock: SupportsSendall, msg: Message) -> None:
    """
    Takes a message object and sends it to all connections known to
    the given socket. This is equivalent to a broadcast to all connected
    clients.

    After transmitting the message, a new line is written to the socket channel
    to separate the messages from each other.

    :param sock:    The socket to send the message to
    :param msg:     The message to send
    """
    sock.sendall((json.dumps(msg) + "\n").encode())


def recv_line(buffer: str, sock: SupportsRecv) -> tuple[Message | None, str]:
    """
    Reads a line from the socket and appends it to the current buffer.
    If a new line is received, a full message is read and parsed to be returned along
    the buffer.

    :param buffer:  The currently known buffer content
    :param sock:    The socket to read the message from
    :return:        None if no complete message is read and a `Message` object if a full line is received.
    """
    try:
        buffer += sock.recv(4096).decode()
    except BlockingIOError:
        pass
    # when a new line is detected, split the data as we are viewing
    # two different messages.
    if "\n" in buffer:
        line, buffer = buffer.split("\n", 1)
        raw = json.loads(line)
        return parse_message(raw), buffer
    return None, buffer
