import os
import sys 
from flask import Flask, request, jsonify, session
from flask_cors import CORS

# Imports corregidos (sin "..." y sin sys.path)
from application.register_usecase import RegisterUseCase
from application.login_face_usecase import LoginFaceUseCase
from application.login_password_usecase import LoginPasswordUseCase
from application.user_management_usecase import UserManagementUseCase
from infraestructure.mongo_user_repository import MongoUserRepository # (Respeta tu nombre "infraestructure")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "faceid-clave-local-segura")
CORS(app, supports_credentials=True,
     resources={r"/*": {"origins": ["http://127.0.0.1:5500", "http://localhost:5500"]}})

# Helper para instanciar el repo
def get_repo():
    return MongoUserRepository()

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        repo = get_repo()
        use_case = RegisterUseCase(repo)
        
        user_id = use_case.execute(
            data.get('first_name'),
            data.get('email'),
            data.get('password'),
            data.get('image')
        )
        return jsonify({
            'success': True,
            'message': f'Usuario registrado exitosamente',
            'userId': user_id
        }), 201
        
    except (ValueError, Exception) as e:
        # --- INICIO DE LA CORRECCIÓN ---
        print(f"❌ Error en /api/register: {e}", file=sys.stderr)
        sys.stderr.flush() # Forzar la impresión en la terminal
        sys.stdout.flush() # Forzar la impresión en la terminal
        # --- FIN DE LA CORRECCIÓN ---
        
        status_code = 409 if "El email ya está registrado" in str(e) else 400
        return jsonify({'success': False, 'message': str(e)}), status_code

@app.route('/api/login/face', methods=['POST'])
def login_face():
    try:
        data = request.json
        repo = get_repo()
        use_case = LoginFaceUseCase(repo)
        
        user, confidence = use_case.execute(data.get('image'))
        
        session['email'] = user['email']
        session['first_name'] = user['first_name']
        session['auth_method'] = 'faceid'
        
        return jsonify({
            'success': True,
            'message': f'Bienvenido {user["first_name"]}',
            'user': user,
            'confidence': confidence
        }), 200
        
    except (ValueError, Exception) as e:
        # --- INICIO DE LA CORRECCIÓN ---
        print(f"❌ Error en /api/login/face: {e}", file=sys.stderr)
        sys.stderr.flush()
        sys.stdout.flush()
        # --- FIN DE LA CORRECCIÓN ---
        return jsonify({'success': False, 'message': str(e)}), 401

@app.route('/api/login/password', methods=['POST'])
def login_password():
    try:
        data = request.json
        repo = get_repo()
        use_case = LoginPasswordUseCase(repo)
        
        user = use_case.execute(data.get('email'), data.get('password'))
        
        session['email'] = user['email']
        session['first_name'] = user['first_name']
        session['auth_method'] = 'faceid' # O 'password'
        
        return jsonify({
            'success': True,
            'message': f'Bienvenido {user["first_name"]}',
            'user': user
        }), 200

    except (ValueError, Exception) as e:
        # --- INICIO DE LA CORRECCIÓN ---
        print(f"❌ Error en /api/login/password: {e}", file=sys.stderr)
        sys.stderr.flush()
        sys.stdout.flush()
        # --- FIN DE LA CORRECCIÓN ---
        return jsonify({'success': False, 'message': str(e)}), 401

@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        repo = get_repo()
        use_case = UserManagementUseCase(repo)
        users = use_case.get_all_users()
        return jsonify({'success': True, 'users': users}), 200
    except Exception as e:
        # --- INICIO DE LA CORRECCIÓN ---
        print(f"❌ Error en /api/users: {e}", file=sys.stderr)
        sys.stderr.flush()
        sys.stdout.flush()
        # --- FIN DE LA CORRECCIÓN ---
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        repo = get_repo()
        use_case = UserManagementUseCase(repo)
        success = use_case.delete_user(user_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Usuario eliminado'}), 200
        else:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    except Exception as e:
        # --- INICIO DE LA CORRECCIÓN ---
        print(f"❌ Error en /api/users/<id>: {e}", file=sys.stderr)
        sys.stderr.flush()
        sys.stdout.flush()
        # --- FIN DE LA CORRECCIÓN ---
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    repo = get_repo()
    connected, db_name = repo.check_db_connection()
    status = "conectado" if connected else "desconectado"
    
    return jsonify({
        'success': True, 
        'message': 'Server is running',
        'database': db_name,
        'db_status': status
    }), 200