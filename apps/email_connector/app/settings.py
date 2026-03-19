from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = Path(__file__).parent.parent / ".env"


class AppSettings(BaseSettings):
    env: Literal["prod", "dev"] = "dev"

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


class EmailSettings(BaseSettings):
    smtp_host: str
    smtp_port: int = 465
    imap_host: str
    imap_port: int
    user: str
    password: str
    secure: bool = True

    model_config = SettingsConfigDict(
        env_prefix="EMAIL_", env_file=ENV_PATH, extra="ignore"
    )


class Settings(BaseSettings):
    broker: BrokerSettings = BrokerSettings()
    email: EmailSettings = EmailSettings()
