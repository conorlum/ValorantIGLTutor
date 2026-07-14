from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://valorant:valorant@localhost:5432/valorant_igl_tutor"
    session_secret: str = "dev-only-change-me"


settings = Settings()
