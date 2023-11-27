import asyncio
import json
import logging

import aio_pika
from aio_pika.abc import AbstractConnection
from binance import AsyncClient, BinanceSocketManager


async def send_data_to_rabbitmq(
    connection: AbstractConnection,
    data: str,
    topic: str,
) -> None:
    logging.info(f"Sending data to RabbitMQ, topic: {topic}")
    try:
        channel = await connection.channel()
        await channel.declare_queue(topic)
        await channel.default_exchange.publish(
            aio_pika.Message(body=bytes(data, "utf-8")),
            routing_key=topic,
        )
    except Exception as e:
        logging.error(f"Error occurred while sending data to RabbitMQ: {str(e)}")


class BinanceHandler:
    def __init__(self, client: AsyncClient, rabbit_connection: AbstractConnection):
        self.rabbit_connection = rabbit_connection
        self.client = client
        self.manager = BinanceSocketManager(self.client)

    async def send_kline(self, currency: str) -> None:
        ts = self.manager.kline_socket(currency, interval="1s")
        async with ts as tscm:
            while True:
                try:
                    res = await tscm.recv()
                    if res.get("e") == "error":
                        logging.warning(
                            f"Error from {currency} kline socket: {res.get('m')}"
                        )
                    else:
                        logging.info(f"Response from {currency} kline socket: {res}")
                        await send_data_to_rabbitmq(
                            self.rabbit_connection,
                            json.dumps(res),
                            "binance",
                        )

                    await asyncio.sleep(4)
                except Exception as e:
                    logging.error(
                        f"Error occurred while processing data from {currency} kline socket: {str(e)}",
                    )
