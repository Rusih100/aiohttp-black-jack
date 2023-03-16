import typing
from logging import Logger
from typing import List, Optional

from app.base.dataclasses.vk import Update
from app.base.handler import Handler

if typing.TYPE_CHECKING:
    from app.base.router import Router
    from app.web.app import Application


class Dispatcher:
    def __init__(
        self,
        app: "Application",
        router: "Router",
        logger: Optional[Logger] = None,
    ):
        self.app = app
        self._message_handlers: List[Handler] = router.handlers
        self.logger = logger

    async def process_update(self, update: Update):
        for handler in self._message_handlers:
            if handler.can_process(update):
                await handler.handler_func(update, self.app)
                self.logger.info(
                    f" {handler.handler_func.__name__} function processed update: {update}"
                )
