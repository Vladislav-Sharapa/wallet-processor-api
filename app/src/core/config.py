from app.src.settings.analytics import AnalyticsSettings
from app.src.settings.application import ApplicationSetting
from app.src.settings.auth import AuthSetting
from app.src.settings.broker import RabbitMQSettings
from app.src.settings.database import PostgreSQLSetting, PostgreSQLTestSettings
from app.src.settings.email import EmailSetting
from app.src.settings.minio import MinioSettings
from app.src.settings.redis import RedisSetting


class Config:
    database: PostgreSQLSetting = PostgreSQLSetting()
    database_test: PostgreSQLTestSettings = PostgreSQLTestSettings()
    application: ApplicationSetting = ApplicationSetting()
    auth: AuthSetting = AuthSetting()
    redis: RedisSetting = RedisSetting()
    broker: RabbitMQSettings = RabbitMQSettings()
    analytics: AnalyticsSettings = AnalyticsSettings()
    email: EmailSetting = EmailSetting()
    minio: MinioSettings = MinioSettings()


config = Config()
