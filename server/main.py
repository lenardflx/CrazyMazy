# Author: Lenard Felix

import socket
import threading

from server.config import HOST, PORT
from shared.health import is_ping, make_pong
from shared.network import recv_line, send_msg


def handle_client(conn: socket.socket, addr: tuple) -> None:
    """Handle a client connection, including the initial handshake and responding to pings."""
    print(f"[server] {addr} connected")
    buffer = ""
    with conn:
        while True:
            try:
                msg, buffer = recv_line(buffer, conn)
                if msg is None:
                    continue
                if is_ping(msg):
                    send_msg(conn, make_pong())
            except OSError:
                break
    print(f"[server] {addr} disconnected")


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"[server] listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    main()
