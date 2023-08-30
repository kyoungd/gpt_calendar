from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .iCalendarBasic import ICalendarBasic
from .iAppointmentBasic import IAppointmentBasic
from .calendarAppointmentsFile import CalendarAppointmentsFile
from .calendarGoogle import CalendarGoogleApi
from .util_template import load_template_file

@dataclass
class AppointmentHandler(IAppointmentBasic):
    template: str

    def __post_init__(self):
        self.calendarFile: CalendarAppointmentsFile = CalendarAppointmentsFile(self.template)
        self.calendar: ICalendarBasic = self.get_google_calendar(self.template)

    def get_google_calendar(self, template: str) -> ICalendarBasic:
        template_data: Any = load_template_file(template)
        json_credential: str = template_data['google_service_account']
        calendar_id: str = template_data['google_calendar_id']
        local_tz: str = template_data['google_calendar_timezone']
        business_hours:list[str] = template_data['business_hours']
        calendar: ICalendarBasic = CalendarGoogleApi(json_credential=json_credential, calendar_id=calendar_id, local_tz=local_tz, business_hours=business_hours)
        return calendar

    def AddEvent(self, event_date: datetime, title: str, description: str):
        self.calendarFile.AddEvent(event_date)
        self.calendar.AddEvent(event_date, description)

    def CancelEvent(self, event_date: datetime):
        self.calendarFile.CancelEvent(event_date)
        self.calendar.CancelEvent(event_date)

    def EditEvent(self, event_date: datetime, title: str, description: str):
        self.calendar.EditEvent(event_date, description)

    def RefreshCalendar(self, projected_days: int) -> None:
        projected_days = projected_days if projected_days is not None else 60
        self.calendar.CreateAppointmentJsonFile(self.templat, projected_days)

    def GetAvailableAppointments(self) -> dict:
        cal = self.calendarFile.load_calendar()
        return cal
