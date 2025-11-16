from abc import ABC, abstractmethod

class SMSServicePort(ABC):
    @abstractmethod
    def send_otp(self, phone_number: str, otp: str) -> bool:
        pass