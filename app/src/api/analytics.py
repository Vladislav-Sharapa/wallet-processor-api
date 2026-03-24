from fastapi import APIRouter, Depends

from app.src.api.depedencies.analytic import get_analytic_service
from app.src.api.depedencies.auth import get_current_user_id
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
    path="/transactions/report/create",
)
async def get_transactions_analysis(
    user_id: int = Depends(get_current_user_id),
    analytic_service: AnalyticsService = Depends(get_analytic_service),
) -> ReportTaskResponse:
    response = await analytic_service.calculate_metrics(user_id)

    return response


@router.get(
    path="/transactions/report/download/{task_id}",
)
async def get_report_download_link(
    task_id: str,
    user_id: int = Depends(get_current_user_id),
    analytic_service: AnalyticsService = Depends(get_analytic_service),
) -> ReportTaskResponse:
    response = await analytic_service.get_report_url(task_id, user_id)

    return response


@router.get(path="/transactions/reports/list")
async def get_reports_list(
    user_id: int = Depends(get_current_user_id),
    analytic_service: AnalyticsService = Depends(get_analytic_service),
):
    reports = await analytic_service.get_reports_list(user_id)

    return reports
