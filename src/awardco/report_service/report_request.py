from dataclasses import dataclass, asdict
from datetime import datetime
from .report_id import ReportId
from .timezone import Timezone
from enum import Enum

@dataclass
class ReportFilters:
    filters: dict[str, list[str]] | None = None
    metadataFilters: dict[str, list[str]] | None = None
    toMetadataFilters: dict[str, list[str]] | None = None
    fromMetadataFilters: dict[str, list[str]] | None = None

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
    selectedFilters: ReportFilters | None = None
    timezone: Timezone = None
    timeRangeDateColumns: list[str] | None = None  # TODO: TEST THIS

    def __post_init__(self):
        if self.selectedFilters is None:
            self.selectedFilters = ReportFilters()
        if self.timezone is None:
            self.timezone = Timezone.UTC

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

        return {
            'reportId': self.reportId.value,
            'startDate': self.startDate,
            'endDate': self.endDate,
            'selectedColumns': self.selectedColumns,
            'selectedFilters': filters_dict,
            'timezone': self.timezone.value,
            'timeRangeOption': None if self.timeRangeOption is None else self.timeRangeOption.value
        }
