from typing import List

from app.store.bot.dispather import Handler


class Router:
    def __init__(self):
        self._message_handlers: List[Handler] = []

    def message_handler(self, commands: List[str] = None, func=None):
        def decorator(handler):
            handler_object = Handler(
                handler=handler, command=commands, func=func
            )
            self._message_handlers.append(handler_object)
            return handler

        return decorator

    @property
    def message_hundlers(self):
        return self._message_handlers
