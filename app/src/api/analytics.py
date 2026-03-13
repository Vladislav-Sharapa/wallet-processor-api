from fastapi import APIRouter, Depends

from app.src.api.depedencies.analytic import get_analytic_service
from app.src.core.permissions import AdminPermission, PermissionsDependency
from app.src.schemas.report import ReportTaskResponse
from app.src.services.analytics import AnalyticsService

router = APIRouter(
    prefix="/analytics",
    tags=[
        "analytics",
    ],
    dependencies=[Depends(PermissionsDependency([AdminPermission]))],
)


@router.get(
    path="/transactions/analyze",
)
async def get_transactions_analysis(
    analytic_service: AnalyticsService = Depends(get_analytic_service),
) -> ReportTaskResponse:
    response = await analytic_service.calculate_metrics()

    return response


@router.get(
    path="/transactions/metrics/{task_id}",
)
async def get_transactions_task(
    task_id: str, analytic_service: AnalyticsService = Depends(get_analytic_service)
) -> ReportTaskResponse:
    response = await analytic_service.get_metrics(task_id)

    return response
