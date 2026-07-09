from io import StringIO
from csv import DictReader
from typing import AsyncGenerator

from awardco.awardco_session import AwardcoSession
from awardco.utils import wrap_async

class Report:

    def __init__(self, csv_download_url: str, total_pages: int, task_id: int, awardco_session: AwardcoSession):
        self._download_url = csv_download_url
        self._total_pages = total_pages
        self._awardco_session = awardco_session
        self._task_id = task_id

    # TODO: Add a key() function that returns only the report keys.
    # TODO: When requesting large timeframes, automatically split them into smaller ones to prevent Awardco API failures?

    async def get_report_page_as_csv(self, page) -> str:
        res = await self._awardco_session.get(self._download_url, params={'page': page})
        assert res.headers['content-type'] == 'text/csv', 'Report required to be in CSV format.'
        csv_text = res.text.strip('\ufeff')
        return csv_text

    async def iter_rows_async(self) -> AsyncGenerator[dict[str, str], None]:
        for i in range(self._total_pages):
            report_csv = await self.get_report_page_as_csv(i + 1)
            reader = DictReader(StringIO(report_csv))
            for row in reader:
                yield row

    async def iter_pages_async(self) -> AsyncGenerator[list[dict[str, str]], None]:
        for i in range(self._total_pages):
            report_csv = await self.get_report_page_as_csv(i + 1)
            reader = DictReader(StringIO(report_csv))
            yield list(reader)

    async def all_rows_async(self) -> list[dict[str,str]]:
        rows = []
        async for row in self.iter_rows_async():  # Speed could be improved by fetching each row on a separate thread
            rows.append(row)
        return rows

    def all_rows(self) -> list[dict[str, str]]:
        return wrap_async(self.all_rows_async())
