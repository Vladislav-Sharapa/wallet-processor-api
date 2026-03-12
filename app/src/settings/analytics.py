from pydantic import PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict


class AnalyticsSettings(BaseSettings):
    WEEKS: PositiveInt = 52

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )
