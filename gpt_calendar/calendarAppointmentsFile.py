import datetime
import pytz
import json
import json
import os
from typing import Union, Any
from .util_convert_timezone import convert_timezone, convert_timezone_list
from .util_template import load_template_file
from .iAppointmentBasic import IAppointmentBasic

class CalendarAppointmentsFile(IAppointmentBasic):
    def __init__(self, template:str, calendar = None, key: str = None):
        self.file_path: str = f"./calendar/{template}.json"
        self.calendar: dict = self.load_calendar() if calendar is None else calendar
        self.tf = load_template_file(template)
        self.template = template
        self.key = key

    def load_calendar(self) -> dict:
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                return data
        else:
            return {}

    def save_calendar(self, calendar: dict = None):
        calendar = self.calendar if calendar is None else calendar
        with open(self.file_path, 'w') as f:
            json.dump(calendar, f, indent=4)

    def split_date_time_zone(self, start_time: datetime) -> tuple:
        # Split the datetime into date and time
        date: str = start_time.strftime('%Y-%m-%d')
        time: str = start_time.strftime('%H:%M')
        timezone: pytz.timezone = start_time.tzinfo
        return date, time, timezone

    def AddEvent(self, event_date: datetime):
        date, time, timezone = self.split_date_time_zone(event_date)
        date, time, _ = convert_timezone(date, time, self.tf['google_calendar_timezone'], timezone)
        # Check if date exists in the dictionary
        if date in self.calendar:
            # Check if time exists in the list of times for that date
            if time in self.calendar[date]:
                self.calendar[date].remove(time)
                self.save_calendar()
                self.UpdateAppointmentCalendar()
                
    def CancelEvent(self, event_date: datetime):
        date, time, timezone = self.split_date_time_zone(event_date)
        date, time, _ = convert_timezone(date, time, self.tf['google_calendar_timezone'], timezone)
        # Check if date exists in the dictionary
        if date in self.calendar:
            if time not in self.calendar[date]:
                self.calendar[date].append(time)
                self.calendar[date].sort()  # Sort the times in ascending order
                self.save_calendar()
                self.UpdateAppointmentCalendar()

    def IsAppointmentAvailable(self, event_date: datetime):
        date, time, timezone = self.split_date_time_zone(event_date)
        date, time, _= convert_timezone(date, time, self.tf['google_calendar_timezone'], timezone)
        calendar = self.load_calendar()
        times = calendar[date]
        if time in times:
            return True
        return False

    def UpdateAppointmentCalendar(self, template: str = None) -> None:
        template = self.template if template is None else template
        self.save_calendar()

    @staticmethod
    def AppointmentCalendar(template, user_tz):
        tf = load_template_file(template)
        app = CalendarAppointmentsFile(template)
        input_json = app.load_calendar()
        result_str = ''
        for onedate, onetimes in input_json.items():
            date, times = convert_timezone_list(onedate, onetimes, tf['google_calendar_timezone'], user_tz)
            dt = datetime.datetime.strptime(date, '%Y-%m-%d')
            day_of_week = dt.strftime('%A')
            times_str = '","'.join(times)
            result_str += f'"{day_of_week}, {date}": "{times_str}"\n'
        return result_str
