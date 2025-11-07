from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    API_HOST: str
    API_PORT: int

    JWT_SECRET: str

    DOMAIN: str

    GOOGLE_AUTH_SECRET: str
    GOOGLE_AUTH_CLIENT_ID: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()