import asyncio
from typing import TYPE_CHECKING, Optional

import aiormq
from aio_pika import (
    Message,
    RobustChannel,
    RobustConnection,
    RobustQueue,
    connect_robust,
)

if TYPE_CHECKING:
    from app.web.app import Application


class RabbitMQ:
    def __init__(self, app: "Application"):
        self.app = app

        self._connection: Optional[RobustConnection] = None
        self.channel: Optional[RobustChannel] = None
        self.queue: Optional[RobustQueue] = None
        self.queue_name: Optional[str] = None

    async def connect(self, *_: list, **__: dict) -> None:
        config = self.app.config.rabbitmq
        self.queue_name = config.queue

        try:
            self._connection = await connect_robust(
                host=config.host,
                port=config.port,
                login=config.user,
                password=config.password,
            )
        except aiormq.exceptions.AMQPConnectionError:
            await asyncio.sleep(5)
            await self.connect(*_, **__)

        self.channel = await self._connection.channel()
        self.queue = await self.channel.declare_queue(self.queue_name)

    async def disconnect(self, *_: list, **__: dict) -> None:
        if self.channel:
            await self.channel.close()
        if self._connection:
            await self._connection.close()

    async def publish_message(self, message: str) -> None:
        await self.channel.default_exchange.publish(
            message=Message(body=message.encode("utf-8")),
            routing_key=self.queue_name,
        )
