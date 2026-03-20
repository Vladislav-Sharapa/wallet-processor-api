from datetime import timedelta
from io import BytesIO
import logging
import uuid
from app.src.core.config import config
from app.src.exceptions.report import NoDataToRecordInStorage
from minio import Minio

logger = logging.getLogger(__name__)


class MinioClient:
    default_bucket = config.minio.MINIO_DEFAULT_BUCKET

    def __init__(self, minio: Minio | None = None):
        if not minio:
            minio = Minio(
                config.minio.url,
                config.minio.MINIO_ROOT_USER,
                config.minio.MINIO_ROOT_PASSWORD,
                secure=False,
            )
        self.__storage = minio

        if not self.__storage.bucket_exists(self.default_bucket):
            self.__storage.make_bucket(self.default_bucket)

    async def record(self, stream: BytesIO) -> str:
        if not stream:
            raise NoDataToRecordInStorage

        try:
            report_name = self.__generate_report_name()
            self.__storage.put_object(
                self.default_bucket, report_name, stream, stream.getbuffer().nbytes
            )

        except Exception as e:
            logger.exception(e)

        return report_name

    async def get_file_url(self, report_name: str):
        return self.__storage.presigned_get_object(
            self.default_bucket, report_name, expires=timedelta(days=1)
        )

    def __generate_report_name(self) -> str:
        return f"report_{uuid.uuid4()}.xlsx"
