# Author: Lenard Felix

import socket
import threading

import server.handlers
from server.config import HOST, PORT
from server.network.dispatch import dispatcher
from server.network.models import OutgoingMessage, RequestContext
from shared.events import parse_event
from shared.network import recv_line, send_msg
from shared.utils.ids import new_connection_id


def flush_outgoing(messages: list[OutgoingMessage]) -> None:
    for outgoing in messages:
        send_msg(outgoing.conn, outgoing.msg)


def handle_client(conn: socket.socket, addr: tuple[str, int]) -> None:
    """Handle a client connection and dispatch inbound protocol messages."""
    print(f"[server] {addr} connected")
    buffer = ""
    ctx = RequestContext(conn=conn, addr=addr, connection_id=new_connection_id())
    with conn:
        while True:
            try:
                msg, buffer = recv_line(buffer, conn)
                if msg is None:
                    continue
                event = parse_event(msg)
                if event is None:
                    continue
                outgoing = dispatcher.dispatch(ctx, event)
                if outgoing is not None:
                    flush_outgoing(outgoing)
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
