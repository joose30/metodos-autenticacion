# Imports corregidos (sin ".." y sin sys.path)
from domain.face_processor import decode_image, get_face_encoding
from ports.user_repository_port import UserRepositoryPort
import face_recognition

class LoginFaceUseCase:
    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository

    def execute(self, image_data):
        if not image_data:
            raise ValueError("No se proporcionó imagen")

        image = decode_image(image_data)
        if image is None:
            raise ValueError("Error al procesar la imagen")
            
        face_encoding, error = get_face_encoding(image)
        if error:
            raise ValueError(error)
            
        users = self.user_repository.get_all_users_with_secret()
        if not users:
            raise ValueError("No hay usuarios registrados con Face ID")

        best_match = None
        best_confidence = 0
        
        for user in users:
            stored_encoding = user['secret_encoding']
            face_distance = face_recognition.face_distance([stored_encoding], face_encoding)[0]
            confidence = (1 - face_distance) * 100
            
            if confidence > 55 and confidence > best_confidence:
                best_confidence = confidence
                best_match = {
                    'id': str(user['_id']),
                    'email': user['email'],
                    'first_name': user['first_name']
                }
        
        if best_match:
            return best_match, round(best_confidence, 2)
        else:
            raise ValueError("Rostro no reconocido. Intenta nuevamente.")