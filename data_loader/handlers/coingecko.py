import asyncio
import json
import logging
from typing import List

import aiohttp
from aio_pika.abc import AbstractConnection

from data_loader.data_loader import GECKO_KEY, send_data_to_rabbitmq


class CoinGeckoHandler:
    def __init__(self, rabbit_connection: AbstractConnection):
        self.rabbit_connection = rabbit_connection
        self.client = aiohttp.ClientSession()
        if GECKO_KEY:
            self.base_url = "https://pro-api.coingecko.com/api/v3/"
            self.headers = {"x_cg_pro_api_key": GECKO_KEY}
        else:
            self.base_url = "https://api.coingecko.com/api/v3/"
            self.headers = {}

    async def send_price(self, ids: List[str], vs_currencies: List[str]) -> None:
        async with self.client as session:
            while True:
                try:
                    params = {
                        "ids": ",".join(ids),
                        "vs_currencies": ",".join(vs_currencies),
                    }
                    response = await session.get(
                        self.base_url + "simple/price",
                        headers=self.headers,
                        params=params,
                    )
                    res = await response.json()
                    if response.status != 200:
                        logging.warning(
                            f"Response from CoinGecko API was not 200: {response.status} "
                            f"{res}",
                        )

                    logging.info(f"Response from CoinGecko API: {res}")
                    await send_data_to_rabbitmq(
                        self.rabbit_connection,
                        json.dumps(res),
                        "gecko",
                    )
                    await asyncio.sleep(5)
                except Exception as e:
                    logging.error(
                        f"Error occurred while processing CoinGecko data: {str(e)}",
                    )
