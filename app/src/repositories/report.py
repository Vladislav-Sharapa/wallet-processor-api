from typing import List

from sqlalchemy import select

from app.src.core.repository import SQLAlchemyRepository
from app.src.models.report import Report
from app.src.schemas.report import ReportStatus


class ReportRepository(SQLAlchemyRepository):
    model = Report

    async def get_report_by_task_id(self, task_id: str) -> Report:
        query = select(Report).filter(Report.task_id == task_id)
        query_result = await self.session.execute(query)

        return query_result.scalar()

    async def get_reports_list(self, user_id: int) -> List[Report]:
        query = select(Report).filter(
            Report.user_id == user_id, Report.status == ReportStatus.COMPLETED
        )
        query_result = await self.session.execute(query)

        return query_result.scalars().all()
