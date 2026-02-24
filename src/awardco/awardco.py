from .report_service import ReportService
from .awardco_session import AwardcoSession

class Awardco:

    def __init__(self, api_key, base_url='https://api.awardco.com/api/'):
        self.session = AwardcoSession(
            api_key=api_key,
            base_url=base_url,
        )
        self.report_service = ReportService(self.session)
