import typing
from logging import getLogger

from app.base.dataclasses.vk import Update
from app.base.dispather import Dispatcher

if typing.TYPE_CHECKING:
    from app.web.app import Application

from app.store.bot.handlers import router


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.dispather = Dispatcher(
            app=self.app, router=router, logger=getLogger("handler")
        )

    async def handle_update(self, update: Update) -> None:
        await self.dispather.process_update(update)
