import logging

from .report import Report
from .report_request import ReportRequest
from .report_status_response import ReportStatusResponse, ReportStatus
from awardco.awardco_session import AwardcoSession
import asyncio
import math


class ReportService:
    def __init__(self, session: AwardcoSession):
        self._session = session

    async def _queue_and_await_report_completion(self, report_request: ReportRequest, max_wait_time_secs: int, paginate: bool) -> ReportStatusResponse:
        async def get_report_status(task_id: int) -> ReportStatusResponse:
            res = await self._session.get(f"v2/reports/tasks/{task_id}/status")
            res = res.json()
            return ReportStatusResponse.from_dict(res)

        res = await self._session.post(f"v2/reports/{report_request.reportId.value}",
                                       json=report_request.as_dict() | {'paginate': paginate},
                                       headers={'Accept': 'text/csv'})
        res = res.json()
        task_id = res['taskId']
        status_res = None
        status: ReportStatus = ReportStatus.IN_PROGRESS
        i = 0
        total_wait_time = 0.0
        while status == ReportStatus.IN_PROGRESS:
            if total_wait_time >= max_wait_time_secs:
                raise Exception(f'Report failed to generate after {total_wait_time} seconds')
            wait_time = min(math.pow(2, i), 90)  # cap wait time at 90 secs
            wait_time = min(wait_time, max_wait_time_secs - total_wait_time)
            total_wait_time += wait_time
            await asyncio.sleep(wait_time)
            status_res = await get_report_status(task_id)
            status = status_res.status
            logging.info(f'Report status is {status.value} after {total_wait_time} secs')
            i += 1

        assert status_res is not None
        if status != ReportStatus.COMPLETED:
            assert status_res.errorCode is not None and status_res.message is not None
            raise Exception(f'Error while waiting for report: {status_res.message}. Awardco error code: {status_res.errorCode}')

        else:
            # Completed status
            assert status == ReportStatus.COMPLETED
            return status_res

    async def get_report(self, report_request: ReportRequest, max_wait_time_secs: int=60) -> Report:
        report_status = await self._queue_and_await_report_completion(report_request, max_wait_time_secs, True)
        download_url = report_status.paginatedApiBaseUrl
        total_pages = report_status.totalPages
        assert download_url and total_pages is not None and total_pages > 0
        return Report(download_url, total_pages, self._session)
