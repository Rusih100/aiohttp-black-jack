from typing import Optional

from aiohttp.web import (
    Application as AiohttpApplication,
    Request as AiohttpRequest,
    View as AiohttpView,
)
from aiohttp_apispec import setup_aiohttp_apispec
from aiohttp_session import setup as session_setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from app.admin.models import Admin
from app.store import Store, setup_store
from app.store.database.database import Database
from app.store.rabbitmq.rabbitmq import RabbitMQ
from app.web.config import Config, setup_config
from app.web.logger import setup_logging
from app.web.middlewares import setup_middlewares
from app.web.routes import setup_routes


class Application(AiohttpApplication):
    config: Optional[Config] = None
    store: Optional[Store] = None
    database: Optional[Database] = None
    rabbitmq: Optional[RabbitMQ] = None


class Request(AiohttpRequest):
    admin: Optional[Admin] = None

    @property
    def app(self) -> Application:
        return super().app()


class View(AiohttpView):
    @property
    def request(self) -> Request:
        return super().request

    @property
    def database(self):
        return self.request.app.database

    @property
    def store(self) -> Store:
        return self.request.app.store

    @property
    def data(self) -> dict:
        return self.request.get("data", {})


def setup_admin_api(app: Application) -> None:
    session_setup(
        app=app, storage=EncryptedCookieStorage(app.config.session.key)
    )
    setup_routes(app=app)
    setup_aiohttp_apispec(
        app=app,
        version="v0.0.1",
        title="AIOHTTP Black Jack",
        url="/docs/json",
        swagger_path="/docs",
    )


def setup_app(config_path: str, service: str) -> Application:
    app = Application()

    setup_logging(app=app)
    setup_config(app=app, config_path=config_path)

    match service:
        case "admin-api":
            setup_admin_api(app=app)

    setup_middlewares(app=app, service=service)
    setup_store(app=app, service=service)
    return app
