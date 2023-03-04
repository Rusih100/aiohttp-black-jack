import typing
from typing import Awaitable, Callable, List

from app.store.vk_api.dataclasses import Update

if typing.TYPE_CHECKING:
    from app.store.bot.router import Router
    from app.web.app import Application


class Handler:
    def __init__(
        self,
        handler_func: Callable[["Update", "Application"], Awaitable[None]],
        commands: List[str] | None = None,
        func: Callable[["Update"], bool] | None = None,
    ):
        self.handler_func = handler_func
        self.commands = commands if commands else []
        self.func = func

    def can_process(self, update: Update) -> bool:
        raw_command = update.object.message.text

        # Проверка на наличие команды в тексте
        if self.commands:
            command = raw_command.strip()
            if command not in self.commands:
                return False

        # Проверка по условию в хэндлере
        if self.func is not None and not self.func(update):
            return False

        return True


class Dispatcher:
    def __init__(self, app: "Application", router: "Router"):
        self.app = app
        self._message_handlers: List[Handler] = router.handlers

    async def process_updates(self, updates: list[Update]):
        for update in updates:
            for handler in self._message_handlers:
                if handler.can_process(update):
                    await handler.handler_func(update, self.app)
                    break
