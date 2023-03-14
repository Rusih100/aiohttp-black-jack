import typing
from typing import Optional

from app.base.base_accessor import BaseAccessor
from app.store.bot.worker import Worker

if typing.TYPE_CHECKING:
    from app.web.app import Application


class WorkAccessor(BaseAccessor):

    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)

        self.worker: Optional[Worker] = None

    async def connect(self, app: "Application"):
        self.worker = Worker(app.store)
        self.logger.info("start working")
        await self.worker.start()

    async def disconnect(self, app: "Application"):
        if self.worker:
            await self.worker.stop()

    async def work(self):
        await self.app.store.bots_manager.handle_updates()
