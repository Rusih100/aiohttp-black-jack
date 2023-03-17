import typing

from app.store.database.database import Database
from app.store.rabbitmq.rabbitmq import RabbitMQ

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application", service: str):

        match service:
            case "admin-api":
                from app.store.admin.accessor import AdminAccessor
                from app.store.game.accessor import GameAccessor

                self.admins = AdminAccessor(app)
                self.game = GameAccessor(app)

            case "vk-poller":
                from app.store.vk_api.accessor import VkApiAccessor

                self.vk_api = VkApiAccessor(app, is_poller=True)

            case "vk-worker":
                from app.store.bot.accessor import WorkAccessor
                from app.store.bot.manager import BotManager
                from app.store.game.accessor import GameAccessor
                from app.store.vk_api.accessor import VkApiAccessor

                self.game = GameAccessor(app)
                self.bots_manager = BotManager(app)
                self.vk_api = VkApiAccessor(app, is_poller=False)
                self.worker = WorkAccessor(app)


def setup_store(app: "Application", service: str) -> None:

    match service:
        case "admin-api":
            app.database = Database(app)

            app.on_startup.append(app.database.connect)
            app.on_cleanup.append(app.database.disconnect)

        case "vk-poller":
            app.rabbitmq = RabbitMQ(app)

            app.on_startup.append(app.rabbitmq.connect)
            app.on_cleanup.append(app.rabbitmq.disconnect)

        case "vk-worker":
            app.database = Database(app)
            app.rabbitmq = RabbitMQ(app)

            app.on_startup.append(app.database.connect)
            app.on_cleanup.append(app.database.disconnect)
            app.on_startup.append(app.rabbitmq.connect)
            app.on_cleanup.append(app.rabbitmq.disconnect)

    app.store = Store(app, service=service)
