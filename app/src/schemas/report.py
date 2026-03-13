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
    payload: Optional[list] = None

    model_config = ConfigDict(from_attributes=True)


class ReportResponse(BaseModel):
    url: str
    author: str
