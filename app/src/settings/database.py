from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgreSQLSetting(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int
    POSTGRES_HOST: str

    @property
    def url(self):
        # postgresql+psycopg://db_user:db:pass@db_host:db_port/db_name
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )
