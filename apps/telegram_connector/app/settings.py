from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = Path(__file__).parent.parent / ".env"


class AppSettings(BaseSettings):
    env: Literal["dev", "prod"] = "dev"

    model_config = SettingsConfigDict(
        env_prefix="APP_", env_file=ENV_PATH, extra="ignore"
    )


class BrokerSettings(BaseSettings):
    user: str
    password: str
    host: str
    port: str

    @property
    def url(self) -> str:
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}"

    model_config = SettingsConfigDict(
        env_prefix="BROKER_", env_file=ENV_PATH, extra="ignore"
    )


class BotSettings(BaseSettings):
    token: str

    model_config = SettingsConfigDict(
        env_prefix="TELEGRAM_", env_file=ENV_PATH, extra="ignore"
    )


class Settings(BaseSettings):
    broker: BrokerSettings = BrokerSettings()
    bot: BotSettings = BotSettings()
