import time
from abc import abstractmethod, ABC
import asyncio
from threading import Thread


class AsyncScheduler(ABC):

    @abstractmethod
    def tick(self): ...

    async def _task_loop(self, interval):
        """

        :param interval:        in seconds
        :return:
        """
        try:
            while True:
                self.tick()
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            print("[Background] Task loop cancelled.")

    async def _internal_scheduler(self, interval, total_duration):
        print(f"[Background] Scheduler started. Running for {total_duration}s...")

        try:
            # wait_for acts as the automatic kill-switch
            await asyncio.wait_for(self._task_loop(interval), timeout=total_duration)
        except asyncio.TimeoutError:
            print("[Background] Duration reached. Stopping scheduler automatically.")
        except Exception as e:
            print(f"[Background] Error: {e}")

    def start(self, interval, total_duration=None) -> Thread:
        bg_thread = Thread(
            target=lambda: asyncio.run(self._internal_scheduler(interval, total_duration)),
            daemon=True
        )
        bg_thread.start()
        return bg_thread