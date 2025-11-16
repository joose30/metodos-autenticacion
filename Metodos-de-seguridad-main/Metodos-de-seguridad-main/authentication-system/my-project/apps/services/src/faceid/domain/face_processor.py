import cv2
import face_recognition
import numpy as np
import pickle
import base64
import hashlib

def hash_password(password):
    """Hashea una contraseña con SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def decode_image(base64_string):
    """Convierte imagen base64 a formato numpy array y normaliza canales/dtype"""
    if not base64_string:
        print("decode_image: no se recibió cadena base64")
        return None

    try:
        # Acepta data URIs del tipo "data:image/png;base64,...." o raw base64
        if ',' in base64_string:
            payload = base64_string.split(',', 1)[1]
        else:
            payload = base64_string

        img_data = base64.b64decode(payload)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)  # mantener canales para detectar alpha

        if img is None:
            print("decode_image: cv2.imdecode devolvió None (base64 inválido o formato no soportado)")
            return None

        # Asegurar dtype uint8
        if img.dtype != np.uint8:
            try:
                img = img.astype(np.uint8)
            except Exception as e:
                print(f"decode_image: no se pudo convertir dtype a uint8: {e}")
                return None

        # Normalizar canales:
        if img.ndim == 2:
            # imagen en escala de grises -> convertir a BGR
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif img.shape[2] == 4:
            # BGRA -> BGR (descartar canal alpha)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        # si ya es 3 canales (BGR) queda igual

        # Debug: informar dtype/shape antes de devolver
        try:
            print(f"decode_image: salida dtype={img.dtype}, shape={img.shape}, ndim={img.ndim}")
        except Exception:
            pass

        return img
    except (ValueError, base64.binascii.Error) as e:
        print(f"Error decodificando base64: {e}")
        return None
    except Exception as e:
        print(f"Error decodificando imagen: {e}")
        return None

def get_face_encoding(image):
    """Obtiene el encoding facial de una imagen"""
    if image is None:
        return None, "Imagen inválida o nula"

    try:
        # Asegurar que sea uint8 y 3 canales antes de convertir a RGB
        if image.dtype != np.uint8:
            image = image.astype(np.uint8)
        if image.ndim == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        elif image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Asegurar dtype uint8 y contigüidad (face_recognition lo requiere)
        rgb_image = np.ascontiguousarray(rgb_image.astype(np.uint8))

        # Debug: informar estado antes de face_locations
        print(f"get_face_encoding: rgb dtype={rgb_image.dtype}, shape={rgb_image.shape}, contiguous={bool(rgb_image.flags.c_contiguous)}")
    except Exception as e:
        print(f"get_face_encoding: error al preparar/convetir imagen a RGB: {e}")
        return None, "Error al procesar la imagen (tipo de imagen no soportado)"

    try:
        face_locations = face_recognition.face_locations(rgb_image)
    except Exception as e:
        print(f"get_face_encoding: error en face_locations: {e}")
        return None, "Error al detectar rostros"

    if len(face_locations) == 0:
        return None, "No se detectó ningún rostro"
    
    if len(face_locations) > 1:
        return None, "Se detectaron múltiples rostros. Asegúrate de que solo haya una persona"

    try:
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
    except Exception as e:
        print(f"get_face_encoding: error en face_encodings: {e}")
        return None, "No se pudo procesar el rostro"

    if len(face_encodings) == 0:
        return None, "No se pudo procesar el rostro"
    
    return face_encodings[0], None