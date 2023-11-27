import asyncio
import json
import logging

from aio_pika.abc import AbstractConnection
from binance import AsyncClient, BinanceSocketManager

from data_loader.data_loader import send_data_to_rabbitmq


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
