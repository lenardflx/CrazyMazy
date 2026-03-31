from server.db import game_service
from shared.async_scheduler import AsyncScheduler


class TimeoutScheduler(AsyncScheduler):
    def __init__(self):
        pass

    def tick(self):
        active_games = game_service.find_active_games()
        for game in active_games:

            game.turn_start_timestamp