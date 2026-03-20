from taskiq import TaskiqDepends

from app.src.core.database import get_async_session
from app.src.core.minio import MinioClient
from app.src.excel.report_generator import ReportGenerator
from app.src.repositories.report import ReportRepository
from sqlalchemy.ext.asyncio import AsyncSession


def get_report_repository(
    session: AsyncSession = TaskiqDepends(get_async_session),
) -> ReportRepository:
    return ReportRepository(session)


def get_report_generator() -> ReportGenerator:
    return ReportGenerator()


def get_file_storage() -> MinioClient:
    return MinioClient()
