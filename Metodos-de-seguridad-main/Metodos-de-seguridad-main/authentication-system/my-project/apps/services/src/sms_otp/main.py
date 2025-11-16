import sys
import os
import secrets
from flask import Flask, request, jsonify, session
from flask_cors import CORS

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from application.sms_otp_usecases import SendOTPUseCase, VerifyOTPUseCase
    from infrastructure.twilio_sms_adapter import TwilioSMSAdapter
    from infrastructure.mongo_repository import MongoDBUserRepository
    print("✅ Módulos importados correctamente")
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    exit(1)

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Configuración CORS completa
CORS(app, resources={
    r"/*": {
        "origins": ["http://127.0.0.1:5500", "http://localhost:5500"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# INICIALIZAR MONGODB
print("🔄 Conectando a MongoDB...")
try:
    mongo_repo = MongoDBUserRepository()
    sms_service = TwilioSMSAdapter()
    send_otp_use_case = SendOTPUseCase(sms_service, mongo_repo)
    verify_otp_use_case = VerifyOTPUseCase(mongo_repo)
    print("✅ MongoDB y servicios inicializados correctamente")
except Exception as e:
    print(f"❌ Error crítico: {e}")
    exit(1)

# Importar y registrar las rutas del controlador
from adapters.http.flask_controller import init_routes
init_routes(app, mongo_repo)

# INICIALIZAR MONGODB
print("🔄 Conectando a MongoDB...")
try:
    mongo_repo = MongoDBUserRepository()
    sms_service = TwilioSMSAdapter()
    send_otp_use_case = SendOTPUseCase(sms_service, mongo_repo)
    verify_otp_use_case = VerifyOTPUseCase(mongo_repo)
    print("✅ MongoDB y servicios inicializados correctamente")
except Exception as e:
    print(f"❌ Error crítico: {e}")
    exit(1)

# Solo pending_verifications en memoria (sesiones activas)
pending_verifications = {}

@app.route('/health', methods=['GET'])
def health_check():
    users_count = mongo_repo.collection.count_documents({})
    return jsonify({
        'status': 'OK', 
        'service': 'SMS OTP Service',
        'mongo_connected': True,
        'total_users': users_count,
        'pending_sessions': len(pending_verifications)
    }), 200

@app.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        data = request.get_json()
        print("=" * 50)
        print("📝 REGISTRO - Datos recibidos:")
        print(f"   Email: {data.get('email')}")
        print(f"   Teléfono: {data.get('phone_number')}")
        print("=" * 50)
        
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name', '')
        auth_method = data.get('auth_method', 'sms')
        phone_number = data.get('phone_number')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        if mongo_repo.user_exists(email):
            return jsonify({'error': 'User already exists'}), 400
        
        if auth_method == 'sms' and not phone_number:
            return jsonify({'error': 'Phone number is required for SMS authentication'}), 400
        
        # Guardar usuario en MONGODB
        user_data = {
            'email': email,
            'password': password,
            'first_name': first_name,
            'auth_method': auth_method,
            'phone_number': phone_number,
            'verified': False,
            'secret': None
        }
        
        success = mongo_repo.save_user(email, user_data)
        
        if not success:
            return jsonify({'error': 'Failed to save user'}), 500
        
        print(f"✅ Usuario guardado en MongoDB: {email}")
        
        # Si es SMS, enviar OTP INMEDIATAMENTE
        if auth_method == 'sms':
            print(f"📤 ENVIANDO OTP a: {phone_number}")
            otp_sent = send_otp_use_case.execute(phone_number)
            
            if otp_sent:
                # Guardar en sesión y pending_verifications
                pending_verifications[email] = phone_number
                session['email'] = email
                session['phone_number'] = phone_number
                session['pending_2fa'] = True
                
                print(f"✅ OTP enviado exitosamente a {phone_number}")
                
                return jsonify({
                    'success': True,
                    'message': 'User registered. OTP sent to phone.',
                    'requires_otp': True,  # ✅ IMPORTANTE
                    'auth_method': 'sms',
                    'email': email
                }), 200
            else:
                print("❌ Falló el envío de OTP")
                return jsonify({'error': 'Failed to send OTP'}), 500
        
        # Para TOTP
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'requires_qr': True
        }), 200
        
    except Exception as e:
        print(f"❌ Error in register: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        data = request.get_json()
        print("=" * 50)
        print("🔐 LOGIN - Datos recibidos:")
        print(f"   Email: {data.get('email')}")
        print("=" * 50)
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # BUSCAR EN MONGODB
        user = mongo_repo.get_user(email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user['password'] != password:
            return jsonify({'error': 'Invalid password'}), 401
        
        session['email'] = email
        session['phone_number'] = user['phone_number']
        session['pending_2fa'] = True
        
        print(f"✅ Login exitoso para: {email}")
        
        if user['auth_method'] == 'sms':
            phone_number = user['phone_number']
            print(f"📤 ENVIANDO OTP a: {phone_number}")
            
            success = send_otp_use_case.execute(phone_number)
            
            if success:
                pending_verifications[email] = phone_number
                print(f"✅ OTP enviado exitosamente")
                
                return jsonify({
                    'success': True,
                    'requires_otp': True,  # ✅ IMPORTANTE
                    'auth_method': 'sms',
                    'message': 'OTP sent to your phone',
                    'email': email
                }), 200
            else:
                print("❌ Falló el envío de OTP")
                return jsonify({'error': 'Failed to send OTP'}), 500
        
        return jsonify({
            'success': True,
            'requires_otp': True,
            'auth_method': 'totp'
        }), 200
        
    except Exception as e:
        print(f"❌ Error in login: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/resend-otp', methods=['POST', 'OPTIONS'])
def resend_otp():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        data = request.get_json()
        print("=" * 50)
        print("🔄 RESEND OTP - Datos recibidos:")
        print(f"   Email en body: {data.get('email')}")
        print(f"   Email en sesión: {session.get('email')}")
        print("=" * 50)
        
        # BUSCAR EMAIL EN BODY O SESIÓN
        email = data.get('email') or session.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        print(f"🔍 Buscando teléfono para: {email}")
        
        # BUSCAR PHONE_NUMBER
        phone_number = None
        
        # 1. Buscar en pending_verifications (sesión activa)
        if email in pending_verifications:
            phone_number = pending_verifications[email]
            print(f"📱 Teléfono encontrado en pending: {phone_number}")
        # 2. Buscar en MONGODB (usuario registrado)
        else:
            user = mongo_repo.get_user(email)
            if user and user.get('phone_number'):
                phone_number = user['phone_number']
                pending_verifications[email] = phone_number  # Agregar a sesión activa
                print(f"📱 Teléfono encontrado en MongoDB: {phone_number}")
            else:
                print(f"❌ Usuario no encontrado en MongoDB: {email}")
                return jsonify({'error': 'No pending verification found for this email'}), 400
        
        print(f"📤 REENVIANDO OTP a: {phone_number}")
        success = send_otp_use_case.execute(phone_number)
        
        if success:
            print(f"✅ OTP reenviado exitosamente")
            return jsonify({'message': 'OTP resent successfully'}), 200
        else:
            print(f"❌ Falló el reenvío de OTP")
            return jsonify({'error': 'Failed to resend OTP'}), 500
            
    except Exception as e:
        print(f"❌ Error in resend_otp: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/verify-otp', methods=['POST', 'OPTIONS'])
def verify_otp():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        data = request.get_json()
        print("=" * 50)
        print("🔍 VERIFICACIÓN OTP:")
        print(f"   OTP recibido: {data.get('otp')}")
        print(f"   Email recibido en body: {data.get('email')}")
        print(f"   Email en sesión: {session.get('email')}")
        print(f"   Datos completos recibidos: {data}")
        print("=" * 50)
        
        otp = data.get('otp')
        email_from_body = data.get('email')  # ✅ CORREGIDO: Leer email del body
        email_from_session = session.get('email')
        
        if not otp:
            return jsonify({'error': 'OTP is required'}), 400
        
        # ✅ PRIORIDAD: Usar email del body (más confiable) o de la sesión
        email = email_from_body or email_from_session
        
        if not email:
            print("❌ No se pudo obtener email ni del body ni de la sesión")
            return jsonify({'error': 'No active session. Please login again.'}), 400
        
        # Obtener phone_number de la sesión o MongoDB
        phone_number = session.get('phone_number')
        if not phone_number:
            # Buscar en MongoDB si no está en sesión
            user = mongo_repo.get_user(email)
            if user and user.get('phone_number'):
                phone_number = user['phone_number']
                session['phone_number'] = phone_number
                print(f"📱 Teléfono recuperado de MongoDB: {phone_number}")
            else:
                print(f"❌ No se encontró teléfono para el usuario: {email}")
                return jsonify({'error': 'No phone number found'}), 400
        
        print(f"🔐 Verificando OTP: {otp} para teléfono: {phone_number}, email: {email}")
        is_valid = verify_otp_use_case.execute(phone_number, otp)
        
        if is_valid:
            # Actualizar usuario en MongoDB
            mongo_repo.update_user(email, {'verified': True})
            
            session['pending_2fa'] = False
            session['authenticated'] = True
            
            # Limpiar sesión activa
            if email in pending_verifications:
                del pending_verifications[email]
            
            print("✅ OTP verificado exitosamente")
            return jsonify({
                'valid': True,
                'message': 'OTP verified successfully',
                'email': email
            }), 200
        else:
            print("❌ OTP inválido o expirado")
            return jsonify({
                'valid': False,
                'error': 'Invalid or expired OTP'
            }), 400
            
    except Exception as e:
        print(f"❌ Error in verify_otp: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/debug', methods=['GET'])
def debug():
    users_from_mongo = list(mongo_repo.collection.find({}, {'password': 0}))
    return jsonify({
        'mongo_users': [user['email'] for user in users_from_mongo],
        'pending_verifications': pending_verifications,
        'session': dict(session),
        'total_users': len(users_from_mongo)
    }), 200

@app.route('/send-otp', methods=['POST', 'OPTIONS'])
def send_otp():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        data = request.get_json()
        print("=" * 50)
        print("📤 SEND OTP - Datos recibidos:")
        print(f"   Teléfono: {data.get('phone_number')}")
        print("=" * 50)
        
        phone_number = data.get('phone_number')
        
        if not phone_number:
            return jsonify({'error': 'Phone number is required'}), 400
        
        print(f"📤 ENVIANDO OTP a: {phone_number}")
        success = send_otp_use_case.execute(phone_number)
        
        if success:
            print(f"✅ OTP enviado exitosamente a {phone_number}")
            return jsonify({
                'success': True,
                'message': 'OTP sent successfully',
                'phone_number': phone_number
            }), 200
        else:
            print("❌ Falló el envío de OTP")
            return jsonify({'error': 'Failed to send OTP'}), 500
            
    except Exception as e:
        print(f"❌ Error in send_otp: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/sms-login', methods=['POST', 'OPTIONS'])
def sms_login():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        data = request.get_json()
        print("=" * 50)
        print("📱 SMS LOGIN - Datos recibidos:")
        print(f"   Teléfono: {data.get('phone_number')}")
        print("=" * 50)
        
        phone_number = data.get('phone_number')
        
        if not phone_number:
            return jsonify({'error': 'Phone number is required'}), 400
        
        # BUSCAR USUARIO POR TELÉFONO
        user = mongo_repo.collection.find_one({'phone_number': phone_number})
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'No user found with this phone number'
            }), 404
        
        email = user['email']
        print(f"✅ Usuario encontrado: {email}")
        
        # CONFIGURAR SESIÓN ESPECÍFICA PARA SMS LOGIN
        session.clear()  # Limpiar sesión anterior
        session['email'] = email
        session['phone_number'] = phone_number
        session['pending_2fa'] = True
        session['auth_method'] = 'sms'
        session['sms_login'] = True  # ✅ Bandera específica para SMS login
        
        # Agregar a pending_verifications
        pending_verifications[email] = phone_number
        
        print(f"💾 Sesión SMS-LOGIN configurada para: {email}")
        print(f"📱 Datos de sesión: {dict(session)}")
        
        # ENVIAR OTP
        print(f"📤 ENVIANDO OTP a: {phone_number}")
        success = send_otp_use_case.execute(phone_number)
        
        if success:
            print(f"✅ OTP enviado exitosamente")
            return jsonify({
                'success': True,
                'message': 'OTP sent successfully',
                'phone_number': phone_number,
                'email': email,
                'requires_otp': True,
                'auth_method': 'sms'
            }), 200
        else:
            print("❌ Falló el envío de OTP")
            return jsonify({'error': 'Failed to send OTP'}), 500
            
    except Exception as e:
        print(f"❌ Error in sms_login: {e}")
        return jsonify({'error': str(e)}), 500
    
    # ✅ NUEVOS ENDPOINTS PARA LOGIN NORMAL + SMS
@app.route('/get-user-by-email', methods=['POST', 'OPTIONS'])
def get_user_by_email():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        data = request.get_json()
        print("=" * 50)
        print("🔍 GET USER BY EMAIL:")
        print(f"   Email: {data.get('email')}")
        print("=" * 50)
        
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Buscar usuario en MongoDB
        user = mongo_repo.get_user(email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        print(f"✅ Usuario encontrado: {user['email']}")
        return jsonify({
            'email': user['email'],
            'phone_number': user.get('phone_number'),
            'auth_method': user.get('auth_method', 'sms')
        }), 200
            
    except Exception as e:
        print(f"❌ Error in get_user_by_email: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/create-sms-session', methods=['POST', 'OPTIONS'])
def create_sms_session():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        data = request.get_json()
        print("=" * 50)
        print("📱 CREATE SMS SESSION:")
        print(f"   Email: {data.get('email')}")
        print(f"   Teléfono: {data.get('phone_number')}")
        print("=" * 50)
        
        email = data.get('email')
        phone_number = data.get('phone_number')
        
        if not email or not phone_number:
            return jsonify({'error': 'Email and phone number are required'}), 400
        
        # CONFIGURAR SESIÓN SMS
        session.clear()  # Limpiar sesión anterior
        session['email'] = email
        session['phone_number'] = phone_number
        session['pending_2fa'] = True
        session['auth_method'] = 'sms'
        session['sms_login'] = True
        
        # Agregar a pending_verifications
        pending_verifications[email] = phone_number
        
        print(f"💾 Sesión SMS creada para: {email}")
        print(f"📱 Datos de sesión: {dict(session)}")
        
        # ✅ IMPORTANTE: GENERAR Y ENVIAR OTP
        print(f"📤 GENERANDO OTP para: {phone_number}")
        success = send_otp_use_case.execute(phone_number)
        
        if success:
            print(f"✅ OTP generado y enviado exitosamente")
            return jsonify({
                'success': True,
                'message': 'SMS session created and OTP sent',
                'email': email
            }), 200
        else:
            print(f"❌ Error generando OTP")
            return jsonify({
                'success': False,
                'error': 'Failed to generate OTP'
            }), 500
            
    except Exception as e:
        print(f"❌ Error in create_sms_session: {e}")
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Starting SMS OTP Service CON MONGODB")
    print("📡 Server: http://localhost:8000")
    print("💾 MongoDB: otp_db.users")
    print("🔐 Endpoints available:")
    print("   - POST /register")
    print("   - POST /login")
    print("   - POST /verify-otp")
    print("   - POST /resend-otp")
    print("   - GET  /health")
    print("   - GET  /debug")
    print("   - POST /send-otp")
    print("   - POST /sms-login")
    print("   - POST /get-user-by-email")
    print("   - POST /create-sms-session")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=8000)