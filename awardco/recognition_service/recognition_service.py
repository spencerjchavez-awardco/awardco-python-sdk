from io import StringIO

from .bulk_recognition import BulkRecognition
from awardco.awardco_session import AwardcoSession
from csv import DictWriter

class RecognitionService:

    def __init__(self, session: AwardcoSession):
        self.session = session

    async def bulk_recognize(self, recognitions: list[BulkRecognition]):
        if len(recognitions) == 0:
            return
        keys = list(recognitions[0].as_dict().keys())
        csv_contents = StringIO()
        writer = DictWriter(csv_contents, fieldnames=keys)
        writer.writeheader()
        writer.writerows([r.as_dict() for r in recognitions])
        await self.session.post('bulk-recognize/upload', files={'file': ('bulk-recognitions.csv', csv_contents.getvalue(), 'text/csv')})
