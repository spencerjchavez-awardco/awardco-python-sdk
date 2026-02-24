from io import StringIO
from typing import AsyncGenerator
from .report_request import ReportRequest
from .report_status_response import ReportStatusResponse, ReportStatus
from awardco.awardco_session import AwardcoSession
import pandas as pd
import asyncio
import math

class ReportService:
    def __init__(self, session: AwardcoSession):
        self.session = session

    async def _queue_and_await_report_completion(self, report_request: ReportRequest, max_wait_time_secs: int, paginate: bool) -> ReportStatusResponse:
        async def get_report_status(task_id) -> ReportStatusResponse:
            res = await self.session.get(f"v2/reports/tasks/{task_id}/status")
            res = res.json()
            return ReportStatusResponse.from_dict(res)

        res = await self.session.post(f"v2/reports/{report_request.reportId.value}",
            json=report_request.as_dict() | {'paginate': paginate},
            headers={'Accept': 'text/csv'})

        res = res.json()
        task_id = res['taskId']
        status_res = None
        status: ReportStatus = ReportStatus.IN_PROGRESS
        i = 0
        total_wait_time = 0
        while status == ReportStatus.IN_PROGRESS:
            if total_wait_time >= max_wait_time_secs:
                raise Exception(f'Report failed to generate after {total_wait_time} seconds')
            wait_time = math.pow(2, i)
            wait_time = max(wait_time, total_wait_time - max_wait_time_secs)
            total_wait_time += wait_time
            await asyncio.sleep(wait_time)
            status_res = await get_report_status(task_id)
            status = status_res.status
            i += 1

        assert status_res is not None
        if status != ReportStatus.COMPLETED:
            assert status_res.errorCode is not None and status_res.message is not None
            raise Exception(f'Error while waiting for report: {status_res.message}. Awardco error code: {status_res.errorCode}')

        else:
            # Completed status
            assert status == ReportStatus.COMPLETED
            return status_res

    async def get_report(self, report_request: ReportRequest, max_wait_time_secs: int=60) -> pd.DataFrame:
        report_status = await self._queue_and_await_report_completion(report_request, max_wait_time_secs, False)
        assert report_status.downloadUrl
        res = await self.session.get(report_status.downloadUrl)
        assert res.headers['content-type'] == 'text/csv'
        csv_text = res.text
        return pd.read_csv(StringIO(csv_text), dtype='str')

    async def get_paginated_report(self, report_request: ReportRequest, max_wait_time_secs: int=60) -> AsyncGenerator[pd.DataFrame, None]:
        async def get_report_page_as_csv(url, page) -> str:
            res = await self.session.get(url, params={'page': page})
            assert res.headers['content-type'] == 'text/csv'
            csv_text = res.text
            return csv_text

        report_status = await self._queue_and_await_report_completion(report_request, max_wait_time_secs, True)
        download_url = report_status.paginatedApiBaseUrl
        total_pages = report_status.totalPages
        assert download_url and total_pages > 0
        for i in range(total_pages):
            report_csv = await get_report_page_as_csv(download_url, i + 1)
            yield pd.read_csv(StringIO(report_csv), dtype=str)

