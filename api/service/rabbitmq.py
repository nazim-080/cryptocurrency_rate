import asyncio
import json
from typing import List

from aio_pika import IncomingMessage
from aio_pika.abc import AbstractConnection


class PikaClient:
    def __init__(
        self,
        connection: AbstractConnection,
        queue_names: List[str],
        process_callable,
    ):
        self.connection = connection
        self.queue_names = queue_names
        self.process_callable = process_callable

    async def consume(self):
        async with self.connection:
            channel = await self.connection.channel()

            while True:
                for queue_name in self.queue_names:
                    queue = await channel.declare_queue(queue_name, auto_delete=False)
                    handler = await self.get_process_incoming_message(queue_name)
                    await queue.consume(handler, no_ack=False)
                    await asyncio.sleep(1)

    async def get_process_incoming_message(self, queue: str):
        async def _process_incoming_message(message: IncomingMessage):
            msg = message.body.decode()
            msg = json.loads(msg)
            self.process_callable(msg, queue)

        return _process_incoming_message
