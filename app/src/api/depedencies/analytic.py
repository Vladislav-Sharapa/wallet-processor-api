from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.src.api.depedencies.report import get_file_storage
from app.src.core.database import get_async_session
from app.src.services.analytics import AnalyticsService


def get_analytic_service(
    session: AsyncSession = Depends(get_async_session),
    file_storage=Depends(get_file_storage),
) -> AnalyticsService:
    return AnalyticsService(session=session, file_storage=file_storage)
