from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import face_recognition
import mysql.connector
from mysql.connector import Error
import numpy as np
import pickle
import base64
from datetime import datetime
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuración de la base de datos MySQL
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'faceid'),
    'port': int(os.getenv('DB_PORT', 3306))
}

def get_db_connection():
    """Crea una conexión a MySQL"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None

def hash_password(password):
    """Hashea una contraseña con SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def decode_image(base64_string):
    """Convierte imagen base64 a formato numpy array"""
    try:
        img_data = base64.b64decode(base64_string.split(',')[1])
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"Error decodificando imagen: {e}")
        return None

def get_face_encoding(image):
    """Obtiene el encoding facial de una imagen"""
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_image)
    
    if len(face_locations) == 0:
        return None, "No se detectó ningún rostro"
    
    if len(face_locations) > 1:
        return None, "Se detectaron múltiples rostros. Asegúrate de que solo haya una persona"
    
    face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
    
    if len(face_encodings) == 0:
        return None, "No se pudo procesar el rostro"
    
    return face_encodings[0], None

@app.route('/api/register', methods=['POST'])
def register():
    """Registra un nuevo usuario con reconocimiento facial"""
    connection = None
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        image_data = data.get('image')
        
        # Validar campos requeridos
        if not email or not password or not first_name or not image_data:
            return jsonify({
                'success': False, 
                'message': 'Todos los campos son requeridos (email, password, first_name, image)'
            }), 400
        
        # Decodificar imagen
        image = decode_image(image_data)
        if image is None:
            return jsonify({'success': False, 'message': 'Error al procesar la imagen'}), 400
        
        # Obtener encoding facial
        face_encoding, error = get_face_encoding(image)
        if error:
            return jsonify({'success': False, 'message': error}), 400
        
        # Serializar encoding facial (convertir a texto base64 para TEXT)
        secret = base64.b64encode(pickle.dumps(face_encoding)).decode('utf-8')
        
        # Hashear contraseña
        hashed_password = hash_password(password)
        
        # Conectar a la base de datos
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        
        cursor = connection.cursor()
        
        try:
            # Insertar usuario
            query = '''
                INSERT INTO users (email, password, first_name, secret) 
                VALUES (%s, %s, %s, %s)
            '''
            cursor.execute(query, (email, hashed_password, first_name, secret))
            connection.commit()
            
            user_id = cursor.lastrowid
            
            return jsonify({
                'success': True,
                'message': f'Usuario {first_name} registrado exitosamente',
                'userId': user_id
            }), 201
            
        except mysql.connector.IntegrityError:
            return jsonify({
                'success': False,
                'message': 'El email ya está registrado'
            }), 409
            
    except Exception as e:
        print(f"Error en registro: {e}")
        return jsonify({'success': False, 'message': f'Error del servidor: {str(e)}'}), 500
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/login/face', methods=['POST'])
def login_face():
    """Autentica un usuario por reconocimiento facial"""
    connection = None
    try:
        data = request.json
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'success': False, 'message': 'No se proporcionó imagen'}), 400
        
        # Decodificar imagen
        image = decode_image(image_data)
        if image is None:
            return jsonify({'success': False, 'message': 'Error al procesar la imagen'}), 400
        
        # Obtener encoding facial
        face_encoding, error = get_face_encoding(image)
        if error:
            return jsonify({'success': False, 'message': error}), 400
        
        # Conectar a la base de datos
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT id, email, first_name, secret FROM users')
        users = cursor.fetchall()
        
        if not users:
            return jsonify({
                'success': False,
                'message': 'No hay usuarios registrados'
            }), 404
        
        # Comparar con todos los usuarios
        best_match = None
        best_confidence = 0
        
        for user in users:
            try:
                # Deserializar encoding facial desde base64
                stored_encoding = pickle.loads(base64.b64decode(user['secret']))
                
                # Calcular distancia facial
                face_distance = face_recognition.face_distance([stored_encoding], face_encoding)[0]
                confidence = (1 - face_distance) * 100
                
                # Umbral de confianza: 55%
                if confidence > 55 and confidence > best_confidence:
                    best_confidence = confidence
                    best_match = {
                        'id': user['id'],
                        'email': user['email'],
                        'first_name': user['first_name']
                    }
            except Exception as e:
                print(f"Error procesando usuario {user['id']}: {e}")
                continue
        
        if best_match:
            return jsonify({
                'success': True,
                'message': f'Bienvenido {best_match["first_name"]}',
                'user': best_match,
                'confidence': round(best_confidence, 2)
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Rostro no reconocido. Intenta nuevamente.'
            }), 401
            
    except Exception as e:
        print(f"Error en login facial: {e}")
        return jsonify({'success': False, 'message': f'Error del servidor: {str(e)}'}), 500
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/login/password', methods=['POST'])
def login_password():
    """Autentica un usuario por email y contraseña"""
    connection = None
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email y contraseña requeridos'}), 400
        
        # Hashear contraseña
        hashed_password = hash_password(password)
        
        # Conectar a la base de datos
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        query = '''
            SELECT id, email, first_name 
            FROM users 
            WHERE email = %s AND password = %s
        '''
        cursor.execute(query, (email, hashed_password))
        user = cursor.fetchone()
        
        if user:
            return jsonify({
                'success': True,
                'message': f'Bienvenido {user["first_name"]}',
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'first_name': user['first_name']
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Email o contraseña incorrectos'
            }), 401
            
    except Exception as e:
        print(f"Error en login con contraseña: {e}")
        return jsonify({'success': False, 'message': f'Error del servidor: {str(e)}'}), 500
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/users', methods=['GET'])
def get_users():
    """Obtiene la lista de usuarios registrados"""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT id, email, first_name, created_at FROM users ORDER BY created_at DESC')
        users = cursor.fetchall()
        
        users_list = []
        for user in users:
            users_list.append({
                'id': user['id'],
                'email': user['email'],
                'first_name': user['first_name'],
                'createdAt': user['created_at'].isoformat() if user['created_at'] else None
            })
        
        return jsonify({'success': True, 'users': users_list}), 200
        
    except Exception as e:
        print(f"Error obteniendo usuarios: {e}")
        return jsonify({'success': False, 'message': f'Error del servidor: {str(e)}'}), 500
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Elimina un usuario"""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
        
        cursor = connection.cursor()
        cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
        connection.commit()
        
        if cursor.rowcount > 0:
            return jsonify({'success': True, 'message': 'Usuario eliminado'}), 200
        else:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
            
    except Exception as e:
        print(f"Error eliminando usuario: {e}")
        return jsonify({'success': False, 'message': f'Error del servidor: {str(e)}'}), 500
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Verifica que el servidor esté funcionando"""
    connection = get_db_connection()
    db_status = "connected" if connection else "disconnected"
    
    if connection and connection.is_connected():
        connection.close()
    
    return jsonify({
        'success': True, 
        'message': 'Server is running',
        'database': DB_CONFIG['database'],
        'db_status': db_status
    }), 200

if __name__ == '__main__':
    print("="*60)
    print("🚀 Face ID Backend Server - MySQL")
    print("="*60)
    print(f"📊 Base de datos: {DB_CONFIG['database']}")
    print(f"🖥️  Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"👤 Usuario: {DB_CONFIG['user']}")
    print(f"🌐 Servidor: http://localhost:5000")
    print(f"📡 API: http://localhost:5000/api")
    print("="*60)
    
    # Verificar conexión
    conn = get_db_connection()
    if conn:
        print("✅ Conexión a MySQL exitosa")
        conn.close()
    else:
        print("❌ Error al conectar con MySQL")
        print("⚠️  Verifica tu configuración en el archivo .env")
    
    print("="*60)
    
    app.run(debug=True, port=5000, host='0.0.0.0')