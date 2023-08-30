from unittest import mock, TestCase
from pytz import timezone
import json
import time
import traceback
from datetime import datetime, timedelta

from app import add_event, edit_event, cancel_event, nightly_refresh, get_available_appointments
from gpt_redis import RedisDataPackage, GetRedisEventKeys, RedisPublisher
from gpt_calendar.calendarAppointmentsFile import CalendarAppointmentsFile

class TestCalendarAppointmentPubSub(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.event_keys = GetRedisEventKeys()
        add_event()
        cancel_event()
        edit_event()
        get_available_appointments()

    def setUp(self):
        nightly_refresh()
        time.sleep(5)
        self.template = "two-human"
        self.event_datetime = datetime(2023, 8, 30, 9, 0, 0, tzinfo=timezone('America/Los_Angeles'))

    def test_AddEvent(self):
        calendarFile1 = CalendarAppointmentsFile(self.template)
        cal1 = calendarFile1.load_calendar()
        data = {'template': self.template, 'data': {'start_time': self.event_datetime, 'description': 'test'}}
        key = TestCalendarAppointmentPubSub.event_keys.events.calendar_add_event
        RedisPublisher.Running(key, data)
        time.sleep(2)
        calendarFile2 = CalendarAppointmentsFile(self.template)
        cal2 = calendarFile2.load_calendar()
        ondate = self.event_datetime.strftime('%Y-%m-%d')
        self.assertGreater(len(cal1[ondate]), len(cal2[ondate]))

