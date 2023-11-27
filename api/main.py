from contextlib import asynccontextmanager

import uvicorn
from aio_pika import connect
from fastapi import FastAPI

from config import settings
from db import run_async_upgrade
from service.rabbitmq import PikaClient


def log_incoming_message(message: dict, queue: str):
    print("========================================================")
    print(f"Queue: {queue}. Here we got incoming message {message}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await run_async_upgrade()

    connection = await connect(
        f"amqp://{settings.rabbitmq_default_user}:{settings.rabbitmq_default_pass}@rabbitmq:5672/",
    )
    pika_client = PikaClient(connection, ["gecko", "binance"], log_incoming_message)
    await pika_client.consume()

    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def hello():
    return "hello"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
