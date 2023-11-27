import asyncio
import logging
from enum import Enum
from typing import List, Optional

from aio_pika import connect
from aio_pika.abc import AbstractConnection
from fastapi import FastAPI, Depends
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from db import run_async_upgrade, get_session, async_session
from models import Course
from schemas import ResponseSchema
from service.rabbitmq import PikaClient, save_data_to_db

app = FastAPI()

logger = logging.getLogger(__name__)
logging.Formatter(
    fmt="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class Exchange(Enum):
    BINANCE = "binance"
    COINGECKO = "coingecko"


class Currency(Enum):
    BTC = "BTC"
    ETH = "ETH"
    USDT = "USDT"


@app.on_event("startup")
async def startup() -> None:
    logger.info("Startup event")
    try:
        await run_async_upgrade()
    except Exception as e:
        logger.critical(f"Couldn't run async upgrade: {e}")

    try:
        connection: AbstractConnection = await connect(
            f"amqp://{settings.rabbitmq_default_user}:{settings.rabbitmq_default_pass}@rabbitmq:5672/",
        )
        pika_client = PikaClient(
            connection,
            async_session,
            ["gecko", "binance"],
            save_data_to_db,
        )
        asyncio.create_task(pika_client.consume())

    except Exception as e:
        logger.critical(f"Couldn't create connection or task: {e}")


#
@app.get("/course")
async def course(
    exchange: Optional[Exchange] = None,
    currency: Optional[Currency] = None,
    db: AsyncSession = Depends(get_session),
) -> List[ResponseSchema]:
    subquery = (
        select(
            Course.exchange,
            Course.currency,
            Course.vs_currency,
            func.max(Course.timestamp).label("max_timestamp"),
        )
        .group_by(Course.exchange, Course.currency, Course.vs_currency)
        .subquery("subquery")
    )

    query = select(Course).join(
        subquery,
        and_(
            Course.exchange == subquery.c.exchange,
            Course.currency == subquery.c.currency,
            Course.vs_currency == subquery.c.vs_currency,
            Course.timestamp == subquery.c.max_timestamp,
        ),
    )
    where_filter = []
    if exchange:
        exchange = exchange.value
        where_filter.append(Course.exchange == exchange)

    if currency:
        currency = currency.value
        where_filter.append(Course.currency == currency)

    if where_filter:
        query = query.where(*where_filter)

    result = await db.scalars(query)
    bn = {
        "exchanger": "binance",
        "courses": [],
    }
    cg = {
        "exchanger": "coingecko",
        "courses": [],
    }
    for i in result.unique().all():
        logger.debug(f"Processing exchange data: {i}")
        if i.exchange == "binance":
            bn["courses"].append(
                {
                    "direction": f"{i.currency}-{i.vs_currency}",
                    "value": i.rate,
                },
            )
        else:
            cg["courses"].append(
                {
                    "direction": f"{i.currency}-{i.vs_currency}",
                    "value": i.rate,
                },
            )
    return [
        ResponseSchema(**exchanger) for exchanger in [bn, cg] if exchanger["courses"]
    ]
