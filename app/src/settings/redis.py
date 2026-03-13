from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSetting(BaseSettings):
    REDIS_USER: str
    REDIS_USER_PASSWORD: str
    REDIS_HOST: str
    REDIS_PORT: str = 6380
    TTL_PASSWORD_ATTEMPS: int = 3600
    TTL_PASSWORD_RESET_CODE: int = 120

    @property
    def url(self):
        return f"redis://{self.REDIS_USER}:{self.REDIS_USER_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )
