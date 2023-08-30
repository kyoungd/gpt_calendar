import json
from gpt_redis import RedisSubscriber, GetRedisEventKeys, RedisPublishReturn
from gpt_calendar.appointment_handler import AppointmentHandler

event_keys = GetRedisEventKeys()

# sample: dict = {
#     'template': 'two-human',
#     'return_key': 'abd1-12fe-334a-2985'
#     'start_time': '2021-08-07T09:00:00-07:00',
#     'description': 'sample'
# }

def parse_package(block: str) -> tuple:
    package = json.loads(block)
    data = package['data']
    template = data['template']
    data_package = data['data']
    return template, data_package

def add_event() -> None:
    def _callback(package: str):
        template, data = parse_package(package)
        start_time = data['start_time']
        description = data['description']
        handler = AppointmentHandler(template)
        handler.AddEvent(start_time, title="", description=description)

    name = event_keys.subscriptions.calendar_add_event
    channels = event_keys.events.calendar_add_event
    app = RedisSubscriber(subscription_name=name, channels=channels, callback=_callback)
    app.start()

def edit_event() -> None:
    def _callback(package: str):
        template, data = parse_package(package)
        start_time = data['start_time']
        description = data['description']
        handler = AppointmentHandler(template)
        handler.AddEvent(start_time, title="", description=description)

    name = event_keys.subscriptions.calendar_edit_event
    channels = event_keys.events.calendar_edit_event
    app = RedisSubscriber(subscription_name=name, channels=channels, callback=_callback)
    app.start()

def cancel_event() -> None:
    def _callback(package: str):
        template, data = parse_package(package)
        start_time = data['start_time']
        handler = AppointmentHandler(template)
        handler.CancelEvent(start_time)

    name = event_keys.subscriptions.calendar_cancel_event
    channels = event_keys.events.calendar_cancel_event
    app = RedisSubscriber(subscription_name=name, channels=channels, callback=_callback)
    app.start()

def nightly_refresh() -> None:
    def _callback(package: str):
        template, _ = parse_package(package)
        handler = AppointmentHandler(template)
        handler.RefreshCalendar(projected_days=60)
    name = event_keys.subscriptions.calendar_nightly_refresh
    channels = event_keys.events.calendar_nightly_refresh
    app = RedisSubscriber(subscription_name=name, channels=channels, callback=_callback)
    app.start()

def get_available_appointments() -> None:
    def _callback(package: dict):
        handler = AppointmentHandler(package)
        appointments = handler.GetAvailableAppointments()
        print(appointments)
    name = event_keys.subscriptions.calendar_get_available_appointments
    channels = event_keys.events.calendar_get_available_appointments
    app = RedisPublishReturn(sub_callback=name, channels=channels, callback=_callback)
    app.start()

if __name__ == "__main__":
    add_event()
    cancel_event()
    edit_event()
    nightly_refresh()
    get_available_appointments()
    while True:
        pass
