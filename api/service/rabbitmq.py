import asyncio
import json
from typing import List, Callable

from aio_pika import IncomingMessage
from aio_pika.abc import AbstractConnection
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker

from models import Course
from schemas import BinanceData, CoinGeckoData


class PikaClient:
    def __init__(
        self,
        connection: AbstractConnection,
        session: async_sessionmaker,
        queue_names: List[str],
        process_callable: Callable,
    ):
        self.connection = connection
        self.queue_names = queue_names
        self.process_callable = process_callable
        self.session = session

    async def consume(self) -> None:
        async with self.connection:
            channel = await self.connection.channel()

            while True:
                for queue_name in self.queue_names:
                    queue = await channel.declare_queue(queue_name, auto_delete=False)
                    handler = await self.get_process_incoming_message(queue_name)
                    await queue.consume(handler)
                    # logger.info(f"Consuming from queue: {queue_name}")
                    await asyncio.sleep(1)

    async def get_process_incoming_message(self, queue: str) -> Callable:
        async def _process_incoming_message(message: IncomingMessage) -> None:
            async with message.process():
                msg = message.body.decode()
                msg = json.loads(msg)
                # logger.info(f"Received message: {msg} in queue: {queue}")
                await self.process_callable(msg, queue, self.session)

        return _process_incoming_message


async def save_data_to_db(
    message: dict,
    queue: str,
    session: async_sessionmaker,
) -> None:
    if queue == "binance":
        await binance_data_save(message, session)
    else:
        await coingecko_data_save(message, session)


async def binance_data_save(message: dict, session: async_sessionmaker) -> None:
    data = BinanceData(**message)
    symbol = data.s
    match symbol:
        case "BTCRUB":
            currency = "BTC"
            vs_currency = "RUB"
        case "ETHUSDT":
            currency = "ETH"
            vs_currency = "USDT"
        case "USDTRUB":
            currency = "USDT"
            vs_currency = "RUB"
    async with session() as db:
        item = Course(
            exchange="binance",
            currency=currency,
            vs_currency=vs_currency,
            rate=data.k.c,
        )
        db.add(item)
        try:
            # logger.info("Trying to commit to database.")
            await db.commit()
            # logger.info("Committed successfully to database.")
        except IntegrityError as e:
            # logger.error(str(e))
            str(e)


async def coingecko_data_save(message: dict, session: async_sessionmaker) -> None:
    data = CoinGeckoData(**message)
    async with session() as db:
        db.add_all(
            [
                Course(
                    exchange="coingecko",
                    currency="BTC",
                    vs_currency="RUB",
                    rate=data.bitcoin.rub,
                ),
                Course(
                    exchange="coingecko",
                    currency="BTC",
                    vs_currency="USD",
                    rate=data.bitcoin.usd,
                ),
                Course(
                    exchange="coingecko",
                    currency="ETH",
                    vs_currency="RUB",
                    rate=data.ethereum.rub,
                ),
                Course(
                    exchange="coingecko",
                    currency="ETH",
                    vs_currency="USD",
                    rate=data.ethereum.usd,
                ),
            ],
        )
        try:
            # logger.info("Trying to commit to database.")
            await db.commit()
            # logger.info("Committed successfully to database.")
        except IntegrityError as e:
            # logger.error(str(e))
            str(e)
