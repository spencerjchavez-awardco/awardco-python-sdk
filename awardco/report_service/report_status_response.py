from enum import Enum
from dataclasses import dataclass, fields


class ReportStatus(Enum):
    IN_PROGRESS = 'in progress'
    COMPLETED = 'completed'
    GENERIC_ERROR = 'error'

@dataclass
class ReportStatusResponse:
    status: ReportStatus
    taskId: int
    errorCode: str | None
    message: str | None
    paginatedApiBaseUrl: str | None
    totalPages: int | None
    downloadUrl: str | None  # used for non-paginated report_service

    @classmethod
    def from_dict(cls, data: dict):
        kwargs = {}
        for f in fields(cls):
            value = data.get(f.name)
            if f.name == 'status' and value is not None:
                value = ReportStatus(value)
            kwargs[f.name] = value
        return cls(**kwargs)
