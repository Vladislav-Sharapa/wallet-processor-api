from datetime import datetime, timedelta, timezone
import logging
from typing import List, Optional

from taskiq import TaskiqDepends, Context
from app.src.api.depedencies.report import (
    get_file_storage,
    get_report_generator,
    get_report_repository,
)
from app.src.excel.file import file_buffer_generator
from app.src.models.report import Report
from app.src.repositories.report import ReportRepository
from app.src.schemas.report import ReportStatus
from app.src.services.tasks.metrics.metrics_service import MetricsService
from app.src.schemas.transaction_schemas import WeekTransactionAnalyticsModel
from app.src.core import broker
from app.src.core.database import async_session_maker
from app.src.core.config import config
from asyncio import sleep

logger = logging.getLogger(__name__)


def validate_metrics(metrics: WeekTransactionAnalyticsModel):
    for value in metrics.model_dump().values():
        if isinstance(value, (int, float)) and value > 0:
            return True
    return False


async def calculate_transactions_metrics(weeks: int) -> List[dict]:
    """
    Calculate transactions metrics for 52 weeks. If there are no values ​​in the model,
    then the metrics for the week will not be taken in the final response.
    """
    date_end = datetime.now(timezone.utc).date()
    date_start = date_end - timedelta(days=7)
    async with async_session_maker() as session:
        metrics_provider = MetricsService(session)
        result_metrics = []
        for _ in range(weeks):
            metrics = await metrics_provider.calculate_metrics(date_start, date_end)
            if validate_metrics(metrics):
                result_metrics.append(metrics.model_dump())
            date_end -= timedelta(weeks=1)
            date_start -= timedelta(weeks=1)
    return result_metrics


def create_report_object(user_id: int, task_id: str, weeks: int) -> Report:
    return Report(
        user_id=user_id,
        task_id=task_id,
        end_date=datetime.now(timezone.utc).date(),
        start_date=datetime.now(timezone.utc).date() - timedelta(weeks=weeks),
        status=ReportStatus.PROCESSING,
    )


@broker.task
async def prepare_report(
    user_id: int,
    context: Context = TaskiqDepends(),
    report_repository: ReportRepository = TaskiqDepends(get_report_repository),
    report_generator=TaskiqDepends(get_report_generator),
    file_storage=TaskiqDepends(get_file_storage),
) -> Optional[str]:
    weeks = config.analytics.WEEKS

    report = create_report_object(user_id, context.message.task_id, weeks)

    report_db: Report = await report_repository.create(report)
    await report_repository.commit()

    metrics = await calculate_transactions_metrics(weeks)

    await sleep(60)

    try:
        async with file_buffer_generator() as file:
            await report_generator.generate(metrics, file)
            file.seek(0)
            report_name = await file_storage.record(file)
            report_db.report_name = report_name
            report_db.status = ReportStatus.COMPLETED
            return report_name
    except Exception as e:
        report_db.status = ReportStatus.FAILED
        logger.exception(e)
    finally:
        await report_repository.commit()
