import os
from flask import Flask, Response, request, jsonify, session, make_response
from application.generate_qr_usecase import GenerateQRUseCase
from application.validate_otp_usecase import ValidateOTPUseCase
from application.register_user_usecase import RegisterUserUseCase
from adapters.http.qr_generator_adapter import QRGeneratorAdapter
from infraestructure.mongo_user_repository import MongoUserRepository
from flask_cors import CORS

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "clave-local-segura")

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False

CORS(app, supports_credentials=True,
     resources={r"/*": {"origins": "http://127.0.0.1:5500"}})

user_repo = MongoUserRepository()
qr_adapter = QRGeneratorAdapter()
generate_qr_usecase = GenerateQRUseCase(qr_adapter)
register_usecase = RegisterUserUseCase(user_repo)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    auth_method = data.get('auth_method', 'totp')
    phone_number = data.get('phone_number')

    if not email or not password:
        return jsonify({'error': 'Email y contraseña requeridos'}), 400

    if auth_method == 'sms' and not phone_number:
        return jsonify({'error': 'Número de teléfono requerido para verificación SMS'}), 400

    try:
        if auth_method == 'totp':
            uri = register_usecase.execute(email, password, first_name)
            session['email'] = email
            session['first_name'] = first_name
            session['auth_method'] = 'totp'
            return jsonify({'otp_uri': uri, 'requires_otp': True}), 200
        else:
            # Para método SMS
            user_repo.collection.insert_one({
                "email": email,
                "password": password,
                "first_name": first_name,
                "auth_method": "sms",
                "phone_number": phone_number,
                "secret": None
            })
            session['email'] = email
            session['first_name'] = first_name
            session['auth_method'] = 'sms'
            session['phone_number'] = phone_number
            return jsonify({'message': 'Registro exitoso', 'requires_otp': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = user_repo.collection.find_one({"email": email})
    if user and user.get("password") == password:
        session['email'] = email
        session['first_name'] = user.get("first_name", "")
        auth_method = user.get("auth_method", "totp")
        session['auth_method'] = auth_method
        
        if auth_method == "sms":
            session['phone_number'] = user.get("phone_number")
            return jsonify({
                "success": True, 
                "requires_otp": True,
                "auth_method": "sms"
            }), 200
        else:
            requires_otp = bool(user.get("secret"))
            return jsonify({
                "success": True, 
                "requires_otp": requires_otp,
                "auth_method": "totp"
            }), 200
    else:
        return jsonify({"success": False, "error": "Credenciales inválidas"}), 401

@app.route('/user-info', methods=['GET'])
def user_info():
    email = session.get('email')
    if not email:
        return jsonify({'error': 'No hay sesión activa'}), 401

    user = user_repo.collection.find_one({"email": email}, {"_id": 0, "first_name": 1})
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    return jsonify({
        'email': email,
        'first_name': user.get('first_name', '')
    }), 200


@app.route('/qr')
def qr():
    email = session.get('email')
    if not email:
        return jsonify({'error': 'No hay sesión activa'}), 401

    secret = user_repo.get_secret_by_email(email)
    if not secret:
        return jsonify({'error': 'Usuario no registrado'}), 404
    img_bytes = generate_qr_usecase.execute(secret, email, 'MyApp')
    return Response(img_bytes, mimetype='image/png')

@app.route('/validate', methods=['POST'])
def validate():
    data = request.get_json()
    code = data.get('code')
    email = session.get('email')

    if not email:
        return jsonify({'valid': False, 'error': 'Sesión no activa'}), 401

    if not code or len(code) != 6:
        return jsonify({'valid': False, 'error': 'Código inválido'}), 400

    secret = user_repo.get_secret_by_email(email)
    if not secret:
        return jsonify({'valid': False, 'error': 'Usuario no registrado'}), 404

    validate_usecase = ValidateOTPUseCase(secret)
    is_valid = validate_usecase.execute(code)
    return jsonify({'valid': is_valid})

@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    resp = make_response(jsonify({"success": True}))
    cookie_name = app.config.get("SESSION_COOKIE_NAME", "session")
    resp.delete_cookie(cookie_name, httponly=True, samesite='Lax')
    return resp

@app.route('/session-check', methods=['GET'])
def session_check():
    return jsonify({"logged_in": bool(session.get('email'))})

@app.route('/ping-db')
def ping_db():
    try:
        user_repo.collection.insert_one({"test": "ok"})
        return jsonify({"status": "MongoDB conectado correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
