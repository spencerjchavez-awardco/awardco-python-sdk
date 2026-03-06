from dataclasses import dataclass, field
from datetime import datetime, date
from .report_id import ReportId
from .timezone import Timezone
from enum import Enum

@dataclass
class ReportFilters:
    filters: dict[str, list[str|None]] | None = None
    metadata_filters: dict[str, list[str|None]] | None = None
    to_metadata_filters: dict[str, list[str|None]] | None = None
    from_metadata_filters: dict[str, list[str|None]] | None = None

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
    report_id: ReportId
    start_date: datetime | date | None = None
    end_date: datetime | date | None = None
    time_range_option: TimeRangeOption | None = None
    selected_columns: list[str] | None = None
    selected_filters: ReportFilters = field(default_factory=ReportFilters)
    timezone: Timezone | None = None
    time_range_date_columns: list[str] | None = None  # TODO: TEST THIS

    def as_dict(self) -> dict:
        filters = self.selected_filters.filters
        from_metadata_filters = self.selected_filters.from_metadata_filters
        to_metadata_filters = self.selected_filters.to_metadata_filters
        metadata_filters = self.selected_filters.metadata_filters

        filters_dict: dict = dict(filters or {})
        if metadata_filters is not None:
            filters_dict['Metadata'] = metadata_filters
        if from_metadata_filters is not None:
            filters_dict['From Metadata'] = from_metadata_filters
        if to_metadata_filters is not None:
            filters_dict['To Metadata'] = to_metadata_filters

        def format_date(dt: datetime | date | None):
            if isinstance(dt, datetime):
                return dt.replace(microsecond=0).isoformat()
            elif isinstance(dt, date):
                return dt.strftime('%Y-%m-%d')
            return ''

        selected_columns = self.selected_columns
        if selected_columns is not None and len(selected_columns) == 0:
            selected_columns = None

        start_date = format_date(self.start_date)
        end_date = format_date(self.end_date)

        request = {
            'reportId': self.report_id.value,
            'startDate': start_date,
            'endDate': end_date,
            'selectedColumns': selected_columns,
            'selectedFilters': filters_dict,
            'timezone': self.timezone.value if self.timezone else Timezone.UTC.value,
            'timeRangeOption': self.time_range_option.value if self.time_range_option is not None else None,
            'timeRangeDateColumns': self.time_range_date_columns,
        }
        request = {k:v for k, v in request.items() if v is not None and v != ''}
        return request

