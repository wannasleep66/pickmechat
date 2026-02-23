from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = Path(__file__).parent.parent / ".env"


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
    host: str
    port: int = 465
    user: str
    password: str
    secure: bool = True

    model_config = SettingsConfigDict(
        env_prefix="EMAIL_", env_file=ENV_PATH, extra="ignore"
    )


class Settings(BaseSettings):
    broker: BrokerSettings = BrokerSettings()
    email: EmailSettings = EmailSettings()
