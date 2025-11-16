# Imports corregidos (sin ".." y sin sys.path)
from domain.face_processor import decode_image, get_face_encoding, hash_password
from ports.user_repository_port import UserRepositoryPort
import base64
import pickle

class RegisterUseCase:
    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository

    def execute(self, first_name, email, password, image_data):
        if not email or not password or not first_name or not image_data:
            raise ValueError('Todos los campos son requeridos (email, password, first_name, image)')

        image = decode_image(image_data)
        if image is None:
            raise ValueError("Error al procesar la imagen")

        face_encoding, error = get_face_encoding(image)
        if error:
            raise ValueError(error)
            
        hashed_pass = hash_password(password)
        
        user_id = self.user_repository.save_user(email, hashed_pass, first_name, face_encoding, "faceid")
        return user_id