from abc import ABC, abstractmethod
from datetime import datetime

class IAppointmentBasic(ABC):

    @abstractmethod
    def AddEvent(self, event_date: datetime, title: str, description: str):
        pass

    @abstractmethod
    def CancelEvent(self, event_date: datetime):
        pass

    @abstractmethod
    def EditEvent(self, event_date: datetime, title: str, description: str):
        pass

    @abstractmethod
    def RefreshCalendar(self, projected_days: int) -> None:
        pass

    @abstractmethod
    def GetAvailableAppointments(self) -> dict:
        pass
