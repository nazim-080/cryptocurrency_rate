import asyncio
import logging
import os

import aio_pika
from binance import AsyncClient
from dotenv import load_dotenv

from handlers.binance import BinanceHandler
from handlers.coingecko import CoinGeckoHandler

load_dotenv()

# Configure logging
logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


BINANCE_CURRENCIES = ["BTCRUB", "ETHUSDT", "USDTRUB"]
GECKO_CURRENCIES = ["bitcoin", "ethereum", "tether"]
GECKO_VS_CURRENCIES = ["rub", "usd"]
RABBITMQ_USER = os.environ.get("RABBITMQ_DEFAULT_USER", "quest")
RABBITMQ_PASS = os.environ.get("RABBITMQ_DEFAULT_PASS", "quest")


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
