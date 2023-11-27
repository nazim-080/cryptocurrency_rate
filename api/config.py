from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path.cwd().parent / ".env",
        env_file_encoding="utf-8",
    )

    gecko_key: str
    binance_currencies: list
    gecko_currencies: list
    gecko_vs_currencies: list
    rabbitmq_default_user: str
    rabbitmq_default_pass: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: str


settings = Settings()
