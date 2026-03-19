from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = Path(__file__).parent.parent / ".env"


class AppSettings(BaseSettings):
    env: Literal["dev", "prod"] = "dev"


class DatabaseSettings(BaseSettings):
    user: str = Field("pickmechat")
    password: str = Field("pickmechat")
    db: str = Field("pickmechat")
    host: str = Field("postgres")
    port: str = Field("5432")

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=ENV_PATH,
        env_prefix="POSTGRES_",
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


class AuthSettings(BaseSettings):
    secret: str
    algorithm: str = Field(default="HS256")
    access_token_ttl: int = Field(default=30)
    refresh_token_ttl: int = Field(default=1440)
    subscription_token_ttl: int = Field(default=30)

    model_config = SettingsConfigDict(
        env_prefix="AUTH_", env_file=ENV_PATH, extra="ignore"
    )


class RealtimeTransportSettings(BaseSettings):
    url: str
    api_key: str

    model_config = SettingsConfigDict(
        env_prefix="CENTRIFUGO_", env_file=ENV_PATH, extra="ignore"
    )


class Settings(BaseSettings):
    """Настройки приложения"""

    database: DatabaseSettings = DatabaseSettings()
    broker: BrokerSettings = BrokerSettings()
    auth: AuthSettings = AuthSettings()
    realtime: RealtimeTransportSettings = RealtimeTransportSettings()
