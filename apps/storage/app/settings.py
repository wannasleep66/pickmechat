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


class S3StorageSettings(BaseSettings):
    endpoint: str
    aws_secret_access_key: str
    aws_access_key_id: str
    port: int
    bucket: str
    secure: bool = False
    region_name: str = "us-east-1"

    model_config = SettingsConfigDict(
        extra="ignore", env_file=ENV_PATH, env_prefix="STORAGE_S3_"
    )


class LocalStorageSettings(BaseSettings):
    path: str

    model_config = SettingsConfigDict(
        extra="ignore", env_file=ENV_PATH, env_prefix="STORAGE_LOCAL_"
    )


class StorageSettings(BaseSettings):
    provider: Literal["local", "s3"]

    s3: S3StorageSettings = S3StorageSettings()
    local: LocalStorageSettings = LocalStorageSettings()

    model_config = SettingsConfigDict(
        extra="ignore", env_file=ENV_PATH, env_prefix="STORAGE_"
    )


class Settings(BaseSettings):
    """Настройки приложения"""

    database: DatabaseSettings = DatabaseSettings()
    storage: StorageSettings = StorageSettings()
