from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    API_HOST: str
    API_PORT: int

    JWT_SECRET: str

    DOMAIN: str

    GOOGLE_AUTH_SECRET: str
    GOOGLE_AUTH_CLIENT_ID: str

    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-flash"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()