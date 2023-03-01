import asyncio
from asyncio import Future, Task
from logging import getLogger
from typing import Optional

from aiohttp import ClientOSError

from app.store import Store


class Poller:
    def __init__(self, store: Store):
        self.store = store
        self.is_running = False
        self.poll_task: Optional[Task] = None
        self.logger = getLogger("poller")

    def _done_callback(self, future: Future):
        if future.exception():
            self.logger.exception("polling failed", exc_info=future.exception())

    async def start(self):
        self.poll_task = asyncio.create_task(self.poll())
        self.poll_task.add_done_callback(self._done_callback)
        self.is_running = True

    async def stop(self):
        self.is_running = False
        if self.poll_task:
            await asyncio.wait([self.poll_task], timeout=60)

    async def poll(self):
        while self.is_running:
            try:
                await self.store.vk_api.poll()
            except ClientOSError:
                continue
