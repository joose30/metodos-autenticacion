from abc import ABC, abstractmethod

class UserRepositoryPort(ABC):
    @abstractmethod
    def save_user(self, email: str, secret: str, password: str):
        pass

    @abstractmethod
    def get_secret_by_email(self, email: str) -> str:
        pass