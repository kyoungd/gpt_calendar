from unittest import mock, TestCase
from pytz import timezone
import json
import os
import traceback

from gpt_calendar.utility import Utility
from gpt_calendar.calendarAppointmentsFile import CalendarAppointmentsFile
from datetime import datetime, timedelta
from gpt_calendar.util_template import load_template_file
from gpt_calendar.calendarGoogle import CalendarGoogleApi

class TestCalendarAppointment(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.template = 'two-human'
        cls.timezone = 'America/Los_Angeles'
        cls.tf = load_template_file(cls.template)
        cls.calendar = CalendarGoogleApi(
                            cls.tf['google_service_account'], 
                            cls.tf['google_calendar_id'],
                            cls.timezone,
                            cls.tf['business_hours'])
        _, calendar = cls.calendar.CreateAppointmentJsonFile(cls.template)

    def setUp(self):
        self.template = TestCalendarAppointment.template
        self.timezone = TestCalendarAppointment.timezone
        self.query = json.dumps({'template': self.template, 'timezone': self.timezone})
        self.tf = load_template_file(self.template)
        one_date = datetime(2023, 8, 7, 9, 0, 0)
        self.start_date = Utility.TimeZoneAwareDateTime(one_date, self.timezone)
        self.calendar = CalendarAppointmentsFile(self.template, key=self.key)

    def test_IntializeClass(self):
        self.assertTrue(True)

    def test_AddDeleteEvent(self):
        try:
            tomorrow = self.start_date
            self.calendar.AddEvent(tomorrow)
            is_available1 = self.calendar.IsAppointmentAvailable(tomorrow)
            self.assertFalse(is_available1)
            self.calendar.CancelEvent(tomorrow)
            is_available2 = self.calendar.IsAppointmentAvailable(tomorrow)
            self.assertTrue(is_available2)
        except Exception as e:
            print(e)
            traceback.format_exc()
            self.assertTrue(False)
        finally:
            self.calendar.CancelEvent(tomorrow)

    def test_GetCalendar(self):
        try:
            tomorrow = self.start_date
            result = self.calendar.load_calendar()
            self.assertIsNotNone(result)
            self.assertIsInstance(result, dict)
        finally:
            self.calendar.CancelEvent(tomorrow)
