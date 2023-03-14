import typing
from logging import Logger
from typing import List, Optional

from app.store.bot.handler import Handler
from app.store.vk_api.dataclasses import Update

if typing.TYPE_CHECKING:
    from app.store.bot.router import Router
    from app.web.app import Application


class Dispatcher:
    def __init__(self, app: "Application", router: "Router", logger: Optional[Logger] = None):
        self.app = app
        self._message_handlers: List[Handler] = router.handlers
        self.logger = logger

    async def process_updates(self, updates: list[Update]):
        for update in updates:
            for handler in self._message_handlers:
                if handler.can_process(update):
                    await handler.handler_func(update, self.app)
                    self.logger.info(
                        f" {handler.handler_func.__name__} function processed update: {update}")
