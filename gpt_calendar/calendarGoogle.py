from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from pytz import timezone
import json
from typing import Union, Any, Tuple, Dict
import dateutil
from pandas.tseries.holiday import USFederalHolidayCalendar
from gpt_utility import LOG_EXCEPTION_CLASS, log_exception_line
from .utility import Utility
from .iCalendarBasic import ICalendarBasic


# Define the scope of the Google Calendar API that we want to access
SCOPES = ['https://www.googleapis.com/auth/calendar']
# Path to the service account credentials file
CALENDAR_ID='9caaa4cc1ff954c4f433ec3ead26c714e1a9e022a8af0ac1c1fa6a2c6a95a273@group.calendar.google.com'

# google calendar API.  Add, delete, update, and query calendar events
# https://developers.google.com/calendar/api/v3/reference/events

# @LOG_EXCEPTION_CLASS
class CalendarGoogleApi(ICalendarBasic):
    
    def __init__(self, json_credential: Any, calendar_id: str, local_tz: Union[str, timezone], business_hours:list):
        try:
            # creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            creds = service_account.Credentials.from_service_account_info(json_credential, scopes=SCOPES)
            self.service = build('calendar', 'v3', credentials=creds)
            self.calendar_id = calendar_id
            self.local_timezone = timezone(local_tz) if isinstance(local_tz, str) else local_tz
            self.business_hours = business_hours
            print('Successfully authenticated and created a service object for the Google Calendar API!')
        except HttpError as error:
            print(f'An error occurred while building the service object: {error}')

    # kyd - export
    def AddEvent(self, start_time, description):
        # add event to calendar
        end_time = start_time + timedelta(minutes=30)
        event = {
            'summary': 'inquery call back',
            'location': 'phone',
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': start_time.tzinfo.zone,
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': end_time.tzinfo.zone,
            },
            'reminders': {
                'useDefault': True,
            },
        }
        try:
            event = self.service.events().insert(calendarId=self.calendar_id, body=event).execute()
            print(f'Event created: {event.get("htmlLink")}')
            return event
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None

    def GetEvent(self, event_id):
        try:
            # Retrieve the event from the user's calendar
            event = self.service.events().get(calendarId=self.calendar_id, eventId=event_id).execute()
            # Print the summary and start time of the event
            print('Event summary:', event['summary'])
            print('Event start time:', event['start']['dateTime'])
            return event
        except HttpError as error:
            # Handle errors that may occur during the API request
            print(f'An error occurred: {error}')
            return None

    def DeleteEvent(self, event_id):
        try:
            self.service.events().delete(calendarId=self.calendar_id, eventId=event_id).execute()
            print(f'Event deleted: {event_id}')
        except HttpError as error:
            print(f'An error occurred: {error}')

    def GetEventsByDate(self, event_date: datetime) -> bool:
        return self.GetEventsByDates(event_date, event_date)

    TimeZone = property(lambda self: self.local_timezone)

    def IsBusinessHours(self, event_date: datetime, validHours: list[str] = None) -> bool:
        # valid_hours = ['08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30']
        # Extract the time from event_date and format it as a string in the format HH:MM
        validHours = self.business_hours if validHours is None else validHours
        event_time = event_date.strftime("%H:%M")
        return event_time in validHours

    # kyd - export
    # there was some issues with how google calendar keeps its data.
    # it had to be converted to a string to compare properly.
    # and date/time converted to the local time.
    def IsAppointmentAvailable(self, event_at: datetime) -> bool:
        event_date = Utility.LocalizedDateTime(event_at, self.local_timezone)
        if Utility.IsHoliday(event_date):
            return False
        if Utility.IsWeekend(event_date):
            return False
        if not self.IsBusinessHours(event_date):
            return False
        events = self.GetAvailableAppointmentsByDates2(event_date)
        if events is None or len(events) <= 0:
            return False
        event_dt = event_date.strftime("%Y-%m-%dT%H:%M:%S%z")
        for event in events:
            if event == event_dt:
                return True
        return False

    def GetAllAvailableEventsByDates(self, start_date: datetime, end_date: datetime = None) -> list:
        start_dt = Utility.LocalizedDateTime(start_date, self.TimeZone)
        end_date1 = start_dt if end_date is None else end_date
        end_dt = Utility.LocalizedDateTime(end_date1, self.TimeZone)
        # Define the start and end times for the given date

        # Define the duration of the time slots (in minutes)
        slot_duration = 30

        # Create a list of all 30-minute time slots during business hours
        available_slots = []
        start = Utility.LocalizedDateTime(datetime.combine(start_dt, datetime.min.time()), self.TimeZone)
        end = Utility.LocalizedDateTime(datetime.combine(end_dt, datetime.max.time()), self.TimeZone)

        # Iterate through each 30-minute time slot within business hours on the given date
        while start + timedelta(minutes=slot_duration) <= end:
            if Utility.IsWeekend(start):
                start += timedelta(minutes=slot_duration)
                continue
            if Utility.IsHoliday(start):
                start += timedelta(minutes=slot_duration)
                continue
            if not self.IsBusinessHours(start):
                start += timedelta(minutes=slot_duration)
                continue
            available_slots.append(start.strftime('%Y-%m-%dT%H:%M:%S%z'))
            start += timedelta(minutes=slot_duration)

        return available_slots

    def GetEventsByDates(self, start_date: datetime, end_date: datetime) -> list:
        local_start_date = Utility.LocalizedDateTime(start_date, self.local_timezone)
        local_end_date = Utility.LocalizedDateTime(end_date, self.local_timezone)

        start_time = self.local_timezone.localize(datetime.combine(local_start_date, datetime.min.time())).isoformat()
        end_time = self.local_timezone.localize(datetime.combine(local_end_date, datetime.max.time())).isoformat()
        # Get all events for the given date
        events_result = self.service.events().list(calendarId=self.calendar_id, timeMin=start_time, timeMax=end_time, singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])
        appointments = [event['start']['dateTime'] for event in events]
        return appointments

    def convert_schedule(self, schedule):
        dates_dict = {}
        for date_time in schedule:
            date_str, time_str = date_time.split("T")
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            time_obj = datetime.strptime(time_str[:8], "%H:%M:%S")
            if date_str not in dates_dict:
                dates_dict[date_str] = [time_obj.strftime("%H:%M:%S")]
            else:
                dates_dict[date_str].append(time_obj.strftime("%H:%M:%S"))
        return dates_dict

    def GetAvailableAppointmentsByDates(self, start_date: datetime, end_date: datetime = None) -> list:
        end_date = start_date if end_date is None else end_date
        available_slots = self.GetAllAvailableEventsByDates(start_date, end_date)
        appointments = self.GetEventsByDates(start_date, end_date)
        data = [slot for slot in available_slots if slot not in appointments]
        return self.convert_schedule(data)


    def convertToStandard(self, schedule):
        dates_dict = []
        for date_time in schedule:
            dt = dateutil.parser.parse(date_time)
            date_str = dt.strftime('%Y-%m-%dT%H:%M:%S%z')
            dates_dict.append(date_str)
        return dates_dict

    # kyd - export
    def GetAvailableAppointmentsByDates2(self, start_date: datetime, end_date: datetime = None) -> list:
        end_date = start_date if end_date is None else end_date
        available_slots = self.GetAllAvailableEventsByDates(start_date, end_date)
        appointments = self.GetEventsByDates(start_date, end_date)
        available_slots = self.convertToStandard(available_slots)
        appointments = self.convertToStandard(appointments)
        data = [slot for slot in available_slots if slot not in appointments]
        return data

    def group_times_by_date(self, times):
        # Initialize an empty dictionary to hold the result.
        result = {}

        # Process each timestamp in the input list.
        for time in times:
            # Parse the timestamp into a datetime object.
            dt = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S%z")

            # Convert the date and time to strings.
            date_str = dt.strftime("%Y-%m-%d")
            time_str = dt.strftime("%H:%M")

            # If this date isn't in the result yet, add it with an empty list.
            if date_str not in result:
                result[date_str] = []

            # Append the time to the list for this date.
            result[date_str].append(time_str)

        # Convert the result to JSON and return it.
        return result

    def GetAvailableAppointmentsForCalendarJson(self, projected_days: int = 60) -> dict:
        start_date = datetime.now(self.local_timezone)
        end_date = start_date + timedelta(days=projected_days)
        available_slots = self.GetAvailableAppointmentsByDates2(start_date, end_date)
        available_dt = self.group_times_by_date(available_slots)
        return available_dt

    def AppointmentFileName(self, template):
        return f"./calendar/{template}.json"

    def CreateAppointmentJsonFile(self, template: str, projected_days: int = 60) -> Tuple[str, Dict]:
        appointmentsJson = self.GetAvailableAppointmentsForCalendarJson(projected_days)
        file_path = self.AppointmentFileName(template)
        with open(file_path, 'w') as f:
            json.dump(appointmentsJson, f, indent=4)
        return file_path, appointmentsJson

