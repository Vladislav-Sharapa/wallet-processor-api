from pydantic_settings import BaseSettings, SettingsConfigDict


class MinioSettings(BaseSettings):
    MINIO_IP_ADDRESS: str
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_S3_PORT: int
    MINIO_DEFAULT_BUCKET: str

    @property
    def url(self):
        return f"{self.MINIO_IP_ADDRESS}:{self.MINIO_S3_PORT}"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )
