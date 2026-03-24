from datetime import date, datetime
from enum import StrEnum
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ReportStatus(StrEnum):
    PENDING = "pending"
    FAILED = "failed"
    PROCESSING = "processing"
    COMPLETED = "completed"


class ReportTaskResponse(BaseModel):
    task_id: str
    status: ReportStatus
    payload: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ReportResponse(BaseModel):
    task_id: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    report_name: Optional[str]
    created: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
