import typing
from logging import getLogger

from app.store.bot.dispather import Dispatcher
from app.store.vk_api.dataclasses import Update

if typing.TYPE_CHECKING:
    from app.web.app import Application

from app.store.bot.handlers import router


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.queue: list[Update] = []
        self.dispather = Dispatcher(
            app=self.app, router=router, logger=getLogger("handler")
        )

    async def handle_updates(self) -> None:
        updates = self.queue.copy()
        await self.dispather.process_updates(updates=updates)
        self.queue.clear()

    async def add_updates_to_queue(self, updates: list[Update]) -> None:
        self.queue += updates
