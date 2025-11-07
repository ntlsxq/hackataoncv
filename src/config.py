from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    API_HOST: str
    API_PORT: int

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


class TestSettings(BaseSettings):
    DATABASE_URL: str

    model_config = SettingsConfigDict(env_file=".env.test", env_file_encoding="utf-8")


import os

if os.path.exists(".env.test") and os.environ.get("TESTING") == "1":
    settings = TestSettings()
else:
    settings = Settings()