import time

from server.db.runtime import game_service
from server.handlers._responses import snapshot_response
from server.network.outgoing import flush_outgoing
from shared.async_scheduler import AsyncScheduler
from shared.protocol import ErrorCode
from shared.types.enums import TurnPhase


class TimeoutScheduler(AsyncScheduler):
    def __init__(self):
        pass

    def tick(self):
        active_games = game_service.find_active_games()
        for game in active_games:
            # we don't want to limit the move duration when this is none
            if game.turn_end_timestamp is None:
                continue

            now = time.time_ns() // 1_000_000
            if now < game.turn_end_timestamp:
                continue

            if game.turn_phase == TurnPhase.SHIFT:
                state = game_service.give_up(game.current_player_id)
                if isinstance(state, ErrorCode):
                    continue # todo handle error here
            else:
                state = game_service.end_turn(game.current_player_id)
                if isinstance(state, ErrorCode):
                    continue # todo handle error here

            outgoing_messages = snapshot_response(state)
            flush_outgoing(outgoing_messages)