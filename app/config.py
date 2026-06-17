"""Application settings loaded from environment / .env file."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    telegram_bot_token: str
    admin_password: str = "admin"
    session_secret: str = "change-this-to-a-long-random-string"
    database_url: str = "sqlite+aiosqlite:///./leads.db"
    web_host: str = "0.0.0.0"
    web_port: int = 8000


settings = Settings()
