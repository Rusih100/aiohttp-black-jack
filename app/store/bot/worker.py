import asyncio
from asyncio import Future, Task
from logging import getLogger
from typing import Optional

from aiohttp import ClientOSError

from app.store import Store


class Worker:
    def __init__(self, store: Store):
        self.store = store
        self.is_running = False
        self.work_task: Optional[Task] = None
        self.logger = getLogger("worker")

    def _done_callback(self, future: Future):
        if future.exception():
            self.logger.exception("working failed", exc_info=future.exception())

    async def start(self):
        self.work_task = asyncio.create_task(self.work())
        self.work_task.add_done_callback(self._done_callback)
        self.is_running = True

    async def stop(self):
        if self.work_task:
            await asyncio.wait([self.work_task], timeout=60)
        self.is_running = False

    async def work(self):
        while self.is_running:
            try:
                await self.store.worker.work()
                await asyncio.sleep(1)
            except ClientOSError:
                continue
