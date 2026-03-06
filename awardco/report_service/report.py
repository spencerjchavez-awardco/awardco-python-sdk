from io import StringIO
from csv import DictReader
from typing import AsyncGenerator
import asyncio

from awardco.awardco_session import AwardcoSession

class Report:

    def __init__(self, csv_download_url: str, total_pages: int, task_id: int, awardco_session: AwardcoSession):
        self._download_url = csv_download_url
        self._total_pages = total_pages
        self._awardco_session = awardco_session
        self._task_id = task_id

    async def iter_rows(self) -> AsyncGenerator[dict[str, str], None]:
        async def get_report_page_as_csv(url, page) -> str:
            res = await self._awardco_session.get(url, params={'page': page})
            assert res.headers['content-type'] == 'text/csv', 'Report required to be in CSV format.'
            csv_text = res.text.strip('\ufeff')
            return csv_text

        for i in range(self._total_pages):
            report_csv = await get_report_page_as_csv(self._download_url, i + 1)
            reader = DictReader(StringIO(report_csv))
            for row in reader:
                yield row

    async def all_rows(self) -> list[dict[str,str]]:
        rows = []
        async for row in self.iter_rows():
            rows.append(row)
        return rows
