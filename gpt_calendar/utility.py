import holidays
from datetime import datetime, timedelta
from typing import Union
from pytz import timezone
import dateutil

class Utility:

    @staticmethod
    def LocalizedDateTime(event_date: datetime, local_tz: Union[str, timezone]) -> datetime:
        local_timezone = timezone(local_tz) if isinstance(local_tz, str) else local_tz
        
        if event_date.tzinfo is not None:
            # If event_date has a timezone, convert it to the local timezone
            return event_date.astimezone(local_timezone)
        else:
            # If event_date doesn't have a timezone, localize it to the local timezone
            return local_timezone.localize(event_date)

    @staticmethod
    def IsHoliday(start: datetime) -> bool:
        us_holidays = holidays.UnitedStates()

        # Increment the date until a business day is found
        return start in us_holidays

    @staticmethod
    def IsWeekend(start: datetime) -> bool:
        return start.weekday() >= 5

    def IsBusinessHours(event_date: datetime, validHours: list[str]) -> bool:
        event_time = event_date.strftime("%H:%M")
        return event_time in validHours

    @staticmethod
    def ConvertToDateTime(datetime_str: str, local_tz: str) -> datetime:
        datetime_obj = dateutil.parser.parse(datetime_str)
        event_date = Utility.TimeZoneAwareDateTime(datetime_obj, local_tz)
        return event_date

    @staticmethod
    def TimeZoneAwareDateTime(naive_datetime: datetime, local_tz: Union[str, timezone]) -> datetime:
        local_timezone = timezone(local_tz) if isinstance(local_tz, str) else local_tz
        # Make the datetime object timezone-aware
        aware_datetime = local_timezone.localize(naive_datetime)
        return aware_datetime

