import typing
from logging import getLogger
from typing import Optional
import json

from aio_pika import RobustChannel, RobustQueue, IncomingMessage

from app.base.base_accessor import BaseAccessor
from app.base.dataclasses.vk import Update

if typing.TYPE_CHECKING:
    from app.web.app import Application


class WorkAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.logger = getLogger("worker")

        self.channel: Optional[RobustChannel] = None
        self.queue: Optional[RobustQueue] = None
        self.queue_name: Optional[str] = None

    async def connect(self, app: "Application"):
        self.logger.info("start working")
        self.channel = app.rabbitmq.channel
        self.queue_name = app.rabbitmq.queue_name

        self.queue = await self.channel.declare_queue(
            name=self.queue_name,
        )

        await self.queue.consume(self.work, no_ack=True)

    async def work(self, message: IncomingMessage) -> None:
        self.logger.info(f"Message from RabbitMQ: {message.body}")
        raw_update = message.body.decode("utf-8")
        raw_update_json = json.loads(raw_update)

        update = Update.parse_update(raw_update_json)

        await self.app.store.bots_manager.handle_update(update)
