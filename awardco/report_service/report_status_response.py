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
        return cls(
            status=ReportStatus(data['status']),
            taskId=int(data['taskId']),
            errorCode=str(data['errorCode']) if data.get('errorCode') is not None else None,
            message=str(data['message']) if data.get('message') is not None else None,
            paginatedApiBaseUrl=str(data['paginatedApiBaseUrl']) if data.get('paginatedApiBaseUrl') is not None else None,
            totalPages=int(data['totalPages']) if data.get('totalPages') is not None else None,
            downloadUrl=str(data['downloadUrl']) if data.get('downloadUrl') is not None else None,
        )