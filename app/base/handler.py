import typing
from typing import Awaitable, Callable, List

from app.base.dataclasses.vk import Update

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Handler:
    def __init__(
        self,
        handler_func: Callable[["Update", "Application"], Awaitable[None]],
        commands: List[str] | None = None,
        buttons_payload: List[str] | None = None,
        func: Callable[["Update"], bool] | None = None,
    ):
        self.handler_func = handler_func
        self.commands = commands or []
        self.buttons_payload = buttons_payload or []
        self.func = func

    def can_process(self, update: Update) -> bool:
        raw_command = update.object.message.text

        # Проверка на наличие команды в тексте
        if self.commands:
            command = raw_command.strip()
            if command in self.commands:
                return True

        raw_payload = update.object.message.payload

        # Проверка на payload
        if self.buttons_payload and raw_payload is not None:
            if raw_payload.button in self.buttons_payload:
                return True

        # Проверка по условию в хэндлере
        if self.func is not None:
            try:
                if self.func(update):
                    return True
            except AttributeError:
                pass

        return False
