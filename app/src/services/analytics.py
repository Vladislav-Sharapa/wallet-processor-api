from sqlalchemy.ext.asyncio import AsyncSession
from app.src.core.minio import MinioClient
from app.src.exceptions.report import (
    FileNotBelongsToUserException,
    NoDataFromServerException,
    TaskNotExistOrProcessedException,
)
from app.src.models.report import Report
from app.src.repositories.report import ReportRepository
from app.src.schemas.report import ReportResponse, ReportStatus, ReportTaskResponse
from app.src.services.tasks.metrics.metrics_calculator import prepare_report


class AnalyticsService:
    def __init__(self, session: AsyncSession, file_storage: MinioClient):
        self.__session = session
        self.__file_storage = file_storage
        self.__report_repository = ReportRepository(self.__session)

    async def calculate_metrics(self, user_id: int) -> ReportTaskResponse:
        task = await prepare_report.kiq(user_id=user_id)

        response = ReportTaskResponse(task_id=task.task_id, status=ReportStatus.PENDING)

        return response

    async def get_report_url(self, task_id: str, user_id: int):
        report_url = None

        try:
            report_db: Report = await self.__report_repository.get_report_by_task_id(
                task_id
            )
            if not report_db:
                raise TaskNotExistOrProcessedException
            if report_db.user_id != user_id:
                raise FileNotBelongsToUserException
            if report_db.report_name:
                report_url = await self.__file_storage.get_file_url(
                    report_db.report_name
                )
        except Exception:
            raise NoDataFromServerException

        return ReportTaskResponse(
            task_id=task_id, status=report_db.status, payload=report_url
        )

    async def get_reports_list(self, user_id):
        reports = await self.__report_repository.get_reports_list(user_id)

        return [ReportResponse.model_validate(report) for report in reports]
