import asyncio
import logging
import os

import aio_pika
from aio_pika.abc import AbstractConnection
from binance import AsyncClient
from dotenv import load_dotenv

from data_loader.handlers.binance import BinanceHandler
from data_loader.handlers.coingecko import CoinGeckoHandler

load_dotenv()

# Configure logging
logging.basicConfig(
    level="INFO",
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

GECKO_KEY = os.environ.get("GECKO_KEY", "")
BINANCE_CURRENCIES = ["BTCRUB", "ETHRUB", "USDTRUB"]
GECKO_CURRENCIES = ["bitcoin", "ethereum", "tether"]
GECKO_VS_CURRENCIES = ["rub"]
RABBITMQ_USER = os.environ.get("RABBITMQ_DEFAULT_USER", "quest")
RABBITMQ_PASS = os.environ.get("RABBITMQ_DEFAULT_PASS", "quest")


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


async def main() -> None:
    logging.info("Running main function")
    rabbit_connection = await aio_pika.connect(
        f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@rabbitmq:5672/",
    )
    binance_client = await AsyncClient.create()
    try:
        coin_handler = CoinGeckoHandler(rabbit_connection)
        binance_handler = BinanceHandler(binance_client, rabbit_connection)

        tasks = [
            binance_handler.send_kline(currency) for currency in BINANCE_CURRENCIES
        ]
        tasks.append(coin_handler.send_price(GECKO_CURRENCIES, GECKO_VS_CURRENCIES))
        await asyncio.gather(*tasks)
    except Exception as e:
        logging.critical(f"Critical error occurred: {str(e)}")
    finally:
        await binance_client.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
