from app.base.router import Router
from app.store.bot.handlers import (
    help_command,
    start_command,
    start_game_command,
    stop_game_command,
)

router = Router(
    help_command.router,
    start_command.router,
    start_game_command.router,
    stop_game_command.router,
)
