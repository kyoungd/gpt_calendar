from unittest import mock, TestCase
from pytz import timezone
import json
import os

from gpt_calendar.utility import Utility
from gpt_calendar.calendarGoogle import CalendarGoogleApi
from datetime import datetime, timedelta
from gpt_calendar.util_template import load_template_file

class TestCalendarGoogleApi(TestCase):

    def setUp(self):
        self.template = 'two-human'
        self.timezone = 'America/Los_Angeles'
        self.query = json.dumps({'template': self.template, 'timezone': self.timezone})
        self.tf = load_template_file(self.template)
        self.calendar = CalendarGoogleApi(
                            self.tf['google_service_account'], 
                            self.tf['google_calendar_id'],
                            self.timezone,
                            self.tf['business_hours'])
        # RESET THIS TO A NEW FUTURE DATE FOR TESTING.
        one_date = datetime(2023, 8, 7, 9, 0, 0)
        self.start_date = Utility.TimeZoneAwareDateTime(one_date, self.timezone)

    def test_IntializeClass(self):
        self.assertTrue(True)

    def test_AddEvent(self):
        try:
            tomorrow = self.start_date
            event = self.calendar.AddEvent(tomorrow, 'test message three')
            self.assertIsNotNone(event)
        finally:
            if event is not None:
                self.calendar.DeleteEvent(event['id'])

    def test_GetEvents(self):
        try:
            datetime1 = self.start_date + timedelta(minutes=30)
            event1 = self.calendar.AddEvent(datetime1, 'test message test_GetEvents')
            datetime2 = self.start_date + timedelta(minutes=60)
            event2 = self.calendar.AddEvent(datetime2, 'test message test_GetEvents')
            events = self.calendar.GetEventsByDate(self.start_date)
            self.assertEqual(len(events), 2)   # 16 time slot -2
        finally:
            if event1 is not None:
                self.calendar.DeleteEvent(event1['id'])
            if event2 is not None:
                self.calendar.DeleteEvent(event2['id'])

    def test_IsAppointmentAvailable(self):
        try:
            datetime1 = self.start_date + timedelta(minutes=30)
            event1 = self.calendar.AddEvent(datetime1, 'test message test_IsAppointmentAvailable')
            result1 = self.calendar.IsAppointmentAvailable(datetime1)
            self.assertFalse(result1)

            datetime2 = self.start_date + timedelta(minutes=60)
            event2 = self.calendar.AddEvent(datetime2, 'test message test_IsAppointmentAvailable')
            result2 = self.calendar.IsAppointmentAvailable(datetime2)
            self.assertFalse(result2)
        finally:
            if event1 is not None:
                self.calendar.DeleteEvent(event1['id'])
            if event2 is not None:
                self.calendar.DeleteEvent(event2['id'])

    def test_LunchTime_Remote(self):
        self.timezone = 'America/New_York'
        one_date = self.start_date.replace(hour=12, minute=30)
        datetime1 = Utility.LocalizedDateTime(one_date, self.timezone)

        result1 = self.calendar.IsAppointmentAvailable(datetime1)
        self.assertFalse(result1)

        datetime2 = datetime1 + timedelta(hours=2)
        result2 = self.calendar.IsAppointmentAvailable(datetime2)
        self.assertTrue(result2)

    def test_TimeZoneDiff(self):
        today = datetime(2023, 3, 13, 13, 30, 0)
        today4 = Utility.TimeZoneAwareDateTime(today, 'US/Eastern')
        today5 = Utility.LocalizedDateTime(today4, 'US/Pacific')
        self.assertEqual(today5.minute, 30)

    def test_AllAvailableEvents(self):
        try:
            datetime1 = self.start_date + timedelta(minutes=30)
            event1 = self.calendar.AddEvent(datetime1, 'test message test_IsAppointmentAvailable')

            result1 = self.calendar.IsAppointmentAvailable(datetime1)
            self.assertFalse(result1)

            datetime2 = self.start_date + timedelta(minutes=60)
            event2 = self.calendar.AddEvent(datetime2, 'test message test_IsAppointmentAvailable')

            events = self.calendar.GetAvailableAppointmentsByDates2(self.start_date)
            self.assertEqual(len(events), 10)
        finally:
            if event1 is not None:
                self.calendar.DeleteEvent(event1['id'])
            if event2 is not None:
                self.calendar.DeleteEvent(event2['id'])

    def test_GetAvailableAppointmentsForCalendarJson(self):
        try:
            
            # check if file exists.  self.calendar.file_path
            fn = self.calendar.AppointmentFileName(self.template)
            if os.path.exists(fn):
                os.remove(fn)
            self.calendar.CreateAppointmentJsonFile(self.template)
            self.assertTrue(os.path.exists(fn))
            # 
            print('done')
        finally:
            print('done')
