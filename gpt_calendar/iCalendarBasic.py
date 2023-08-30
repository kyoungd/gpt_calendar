from abc import ABC, abstractmethod
from datetime import datetime

class ICalendarBasic(ABC):

    @property
    def Timezone(self):
        pass

    @property
    def CalType(self):
        pass

    @abstractmethod
    def AddEvent(self, start_time, description):
        pass

    @abstractmethod
    def GetEvent(self, event_id):
        pass

    @abstractmethod
    def DeleteEvent(self, event_id):
        pass

    @abstractmethod
    def IsAppointmentAvailable(self, event_at: datetime) -> bool:
        pass

    @abstractmethod
    def GetAvailableAppointmentsByDates2(self, start_date: datetime, end_date: datetime = None) ->  list:
        pass

    @abstractmethod
    def CreateAppointmentJsonFile(self, template: str, projected_days: int = 60):
        pass

