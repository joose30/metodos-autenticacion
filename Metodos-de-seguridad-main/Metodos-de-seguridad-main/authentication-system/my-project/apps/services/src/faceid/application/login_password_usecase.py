# Imports corregidos (sin ".." y sin sys.path)
from domain.face_processor import hash_password
from ports.user_repository_port import UserRepositoryPort

class LoginPasswordUseCase:
    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository

    def execute(self, email, password):
        if not email or not password:
            raise ValueError("Email y contraseña requeridos")
            
        hashed_password = hash_password(password)
        user = self.user_repository.find_user_by_credentials(email, hashed_password)
        
        if user:
            return {
                'id': str(user['_id']),
                'email': user['email'],
                'first_name': user.get('first_name', '')
            }
        else:
            raise ValueError("Email o contraseña incorrectos")