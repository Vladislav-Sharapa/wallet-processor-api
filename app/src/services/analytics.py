from fastapi.responses import JSONResponse

from app.src.schemas.report import ReportStatus, ReportTaskResponse
from app.src.services.tasks.metrics.metrics_calculator import (
    calculate_transactions_metrics,
)
from app.src.core import broker
from taskiq_redis.exceptions import ResultIsMissingError
from fastapi import status


class AnalyticsService:
    async def calculate_metrics(self) -> ReportTaskResponse:
        task = await calculate_transactions_metrics.kiq()
        response = ReportTaskResponse(task_id=task.task_id, status=ReportStatus.PENDING)

        return response

    async def get_metrics(self, task_id: str):
        try:
            result = await broker.result_backend.get_result(task_id)

        except ResultIsMissingError:
            return JSONResponse(
                content={"detail": "The task does not exist or is being processed"}
            )
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"msg": "Failed to return data from server", "detail": str(e)},
            )
        return ReportTaskResponse(
            task_id=task_id, status=ReportStatus.COMPLETED, payload=result
        )
