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
        self.logger = getLogger("handler")
        self.dispather = Dispatcher(app=self.app, router=router)

    async def handle_updates(self, updates: list[Update]):
        await self.dispather.process_updates(updates=updates)
