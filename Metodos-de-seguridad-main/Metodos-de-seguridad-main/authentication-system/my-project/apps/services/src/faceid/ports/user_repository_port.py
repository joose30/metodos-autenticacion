from abc import ABC, abstractmethod

class UserRepositoryPort(ABC):
    
    @abstractmethod
    def save_user(self, email, hashed_password, first_name, secret, auth_method):
        pass

    @abstractmethod
    def get_all_users_with_secret(self):
        pass

    @abstractmethod
    def find_user_by_credentials(self, email, hashed_password):
        pass

    @abstractmethod
    def get_all_users(self):
        pass

    @abstractmethod
    def delete_user_by_id(self, user_id: str):
        pass

    @abstractmethod
    def check_db_connection(self):
        pass