from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = Path(__file__).parent.parent / ".env"


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


class Settings(BaseSettings):
    """Настройки приложения"""

    database: DatabaseSettings = DatabaseSettings()
