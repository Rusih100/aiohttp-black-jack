import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    from app.blackjack.views import GameInfoView, GameListView, UserListView

    app.router.add_view("/game.get", GameInfoView)
    app.router.add_view("/game.all_current", GameListView)
    app.router.add_view("/user.all", UserListView)
