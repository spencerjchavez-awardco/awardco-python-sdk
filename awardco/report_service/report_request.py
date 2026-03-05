from dataclasses import dataclass, field
from datetime import datetime
from .report_id import ReportId
from .timezone import Timezone
from enum import Enum

@dataclass
class ReportFilters:
    filters: dict[str, list[str|None]] | None = None
    metadataFilters: dict[str, list[str|None]] | None = None
    toMetadataFilters: dict[str, list[str|None]] | None = None
    fromMetadataFilters: dict[str, list[str|None]] | None = None

@dataclass
class TimeRangeOption(Enum):
    TODAY = "today"
    THIS_WEEK = "this week"
    THIS_MONTH = "this month"
    THIS_QUARTER = "this quarter"
    THIS_YEAR = "this year"
    YESTERDAY = "yesterday"
    LAST_WEEK = "last week"
    LAST_MONTH = "last month"
    LAST_QUARTER = "last quarter"
    LAST_YEAR = "last year"
    ALL_TIME = 'all time'
    THIRTY_DAYS_INCLUSIVE = '30 days inclusive'
    NINETY_DAYS_INCLUSIVE = '90 days inclusive'
    CURRENT_PERIOD = "current period"  # Recognition Program Utilization Report only
    PREVIOUS_PERIOD = "previous period"  # Recognition Program Utilization Report only

@dataclass
class ReportRequest:
    reportId: ReportId
    startDate: datetime | None = None
    endDate: datetime | None = None
    timeRangeOption: TimeRangeOption | None = None
    selectedColumns: list[str] | None = None
    selectedFilters: ReportFilters = field(default_factory=ReportFilters)
    timezone: Timezone | None = None
    timeRangeDateColumns: list[str] | None = None  # TODO: TEST THIS

    def as_dict(self):
        filters = self.selectedFilters.filters
        from_metadata_filters = self.selectedFilters.fromMetadataFilters
        to_metadata_filters = self.selectedFilters.toMetadataFilters
        metadata_filters = self.selectedFilters.metadataFilters

        filters_dict: dict = dict(filters or {})
        if metadata_filters is not None:
            filters_dict['Metadata'] = metadata_filters
        if from_metadata_filters is not None:
            filters_dict['From Metadata'] = from_metadata_filters
        if to_metadata_filters is not None:
            filters_dict['To Metadata'] = to_metadata_filters

        # Remove microseconds from startDate and endDate if present
        start_date = self.startDate.replace(microsecond=0) if self.startDate else None
        end_date = self.endDate.replace(microsecond=0) if self.endDate else None

        request = {
            'reportId': self.reportId.value,
            'startDate': start_date.isoformat() if start_date else '',
            'endDate': end_date.isoformat() if end_date else '',
            'selectedColumns': self.selectedColumns if self.selectedColumns else [],
            'selectedFilters': filters_dict,
            'timezone': self.timezone.value if self.timezone else Timezone.UTC.value,
            'timeRangeOption': self.timeRangeOption.value if self.timeRangeOption is not None else ''
        }
        request = {k:v for k, v in request.items() if v != ''}

        return request
