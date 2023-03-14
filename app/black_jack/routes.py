import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    from app.black_jack.views import GetGameView

    app.router.add_view("/game.get", GetGameView)
