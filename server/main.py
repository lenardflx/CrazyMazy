# Author: Lenard Felix

import socket
import threading

import server.handlers # register handlers
from server.config import ALLOW_NPC_PLAY, HOST, PORT
from server.db.runtime import game_service
from server.handlers._responses import snapshot_response
from server.network.connections import register_connection, unregister_connection
from server.network.dispatch import dispatcher
from server.network.models import RequestContext
from server.network.outgoing import flush_outgoing
from server.schedule.timeout_scheduler import TimeoutScheduler
from shared.events import parse_event
from shared.network import recv_line
from shared.protocol import ErrorCode
from shared.types.enums import PlayerLeaveReason
from shared.utils.ids import new_connection_id

def handle_client(conn: socket.socket, addr: tuple[str, int]) -> None:
    """Handle a client connection and dispatch inbound protocol messages."""
    print(f"[server] {addr} connected")
    buffer = ""
    ctx = RequestContext(conn=conn, addr=addr, connection_id=new_connection_id())
    register_connection(ctx.connection_id, conn)
    try:
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
    finally:
        unregister_connection(ctx.connection_id)
        state = game_service.get_connection_state(ctx.connection_id)
        if state is not None:
            updated = game_service.leave_game(state.player.id, reason=PlayerLeaveReason.LEFT)
            if updated is not None and not isinstance(updated, ErrorCode):
                flush_outgoing(snapshot_response(updated))
                game_service.schedule_npc_turns(updated)
        print(f"[server] {addr} disconnected")


def main() -> None:
    game_service.allow_npc_play = ALLOW_NPC_PLAY
    timeout_scheduler = TimeoutScheduler()
    timeout_scheduler.start(interval=1)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"[server] listening on {HOST}:{PORT} (allow_npc_play={game_service.allow_npc_play})")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    main()
