import typing
from typing import Awaitable, Callable, List

from app.base.dispather import Handler

if typing.TYPE_CHECKING:
    from app.base.dataclasses.vk import Update
    from app.web.app import Application


class Router:
    def __init__(self, *args: "Router"):
        self._message_handlers: List[Handler] = []

        if args:
            for router in args:
                self._message_handlers += router.handlers

    def handler(
        self,
        commands: List[str] | None = None,
        buttons_payload: List[str] | None = None,
        func: Callable[["Update"], bool] | None = None,
    ) -> Callable[
        [Callable[["Update", "Application"], Awaitable[None]]],
        Callable[["Update", "Application"], Awaitable[None]],
    ]:
        def decorator(
            handler_func: Callable[["Update", "Application"], Awaitable[None]]
        ) -> Callable[["Update", "Application"], Awaitable[None]]:
            handler_object = Handler(
                handler_func=handler_func,
                commands=commands,
                func=func,
                buttons_payload=buttons_payload,
            )
            self._message_handlers.append(handler_object)
            return handler_func

        return decorator

    @property
    def handlers(self) -> List[Handler]:
        return self._message_handlers
