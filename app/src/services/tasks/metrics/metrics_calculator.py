from datetime import datetime, timedelta, timezone
from typing import List

from app.src.services.tasks.metrics.metrics_service import MetricsService
from app.src.schemas.transaction_schemas import WeekTransactionAnalyticsModel
from app.src.core import broker
from app.src.core.database import async_session_maker
from app.src.core.config import config


def validate_metrics(metrics: WeekTransactionAnalyticsModel):
    for value in metrics.model_dump().values():
        if isinstance(value, (int, float)) and value > 0:
            return True
    return False


@broker.task
async def calculate_transactions_metrics() -> List[dict]:
    """
    Calculate transactions metrics for 52 weeks. If there are no values ​​in the model,
    then the metrics for the week will not be taken in the final response.
    """
    weeks = config.analytics.WEEKS

    date_end = datetime.now(timezone.utc).date()
    date_start = date_end - timedelta(days=7)
    async with async_session_maker() as session:
        metrics_provider = MetricsService(session)
        result_metrics = []
        for _ in range(weeks):
            metrics = await metrics_provider.calculate_metrics(date_start, date_end)
            if validate_metrics(metrics):
                result_metrics.append(
                    {
                        "start_date": date_start,
                        "end_date": date_end,
                        "metrics": metrics.model_dump(),
                    }
                )
            date_end -= timedelta(weeks=1)
            date_start -= timedelta(weeks=1)
    return result_metrics
