# Author: Lenard Felix

import json
import socket


def send_msg(sock: socket.socket, msg: dict) -> None:
    sock.sendall((json.dumps(msg) + "\n").encode())


def recv_line(buffer: str, sock: socket.socket) -> tuple[dict | None, str]:
    try:
        buffer += sock.recv(4096).decode()
    except BlockingIOError:
        pass
    if "\n" in buffer:
        line, buffer = buffer.split("\n", 1)
        return json.loads(line), buffer
    return None, buffer
