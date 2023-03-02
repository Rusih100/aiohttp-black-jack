import typing
from typing import List

from app.store.vk_api.dataclasses import Update

if typing.TYPE_CHECKING:
    from app.store.bot.router import Router
    from app.web.app import Application


class Handler:
    def __init__(self, handler, command: List[str] = None, func=None):
        self.handler = handler
        self.commands: List[str] = command
        self.func = func

    def can_process(self, update: Update) -> bool:
        raw_command = update.object.message.text

        if self.commands is not None and raw_command:
            command = raw_command.strip()
            if command not in self.commands:
                return False

        if self.func is not None and not self.func(update):
            return False

        return True


class Dispatcher:
    def __init__(self, app: "Application", router: "Router"):
        self.app = app
        self._message_handlers: List[Handler] = router.message_hundlers

    async def process_updates(self, updates: list[Update]):
        for update in updates:
            for handler in self._message_handlers:
                if handler.can_process(update):
                    await handler.handler(update, self.app)
                    break
