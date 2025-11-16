# Imports corregidos (sin ".." y sin sys.path)
from ports.user_repository_port import UserRepositoryPort

class UserManagementUseCase:
    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository

    def get_all_users(self):
        return self.user_repository.get_all_users()

    def delete_user(self, user_id: str):
        return self.user_repository.delete_user_by_id(user_id)