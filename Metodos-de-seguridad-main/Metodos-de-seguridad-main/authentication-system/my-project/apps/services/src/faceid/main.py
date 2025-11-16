import os
import sys

# --- INICIO DE LA CORRECCIÓN ---
# Añadir el directorio actual al path para que encuentre los módulos
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


# Imports corregidos (sin el ".")
from adapters.http.flask_controller import app
from infraestructure.mongo_user_repository import MongoUserRepository

if __name__ == '__main__':
    # ¡¡¡IMPORTANTE!!!
    # CAMBIAMOS EL PUERTO A 5001
    # 5000 es de TOTP, 8000 es de SMS
    
    print("="*60)
    print("🚀 Face ID Backend Server - MongoDB (Refactored)")
    print("="*60)
    
    # Verificar conexión a MongoDB
    try:
        repo = MongoUserRepository()
        connected, db_name = repo.check_db_connection()
        if connected:
            print(f"✅ Conexión a MongoDB ({db_name}) exitosa")
        else:
            print(f"❌ Error al conectar con MongoDB ({db_name})")
    except Exception as e:
        print(f"❌ Error crítico de MongoDB: {e}")
        
    print(f"🌐 Servidor: http://localhost:5001")
    print(f"📡 API: http://localhost:5001/api")
    print("="*60)
    
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, port=port, host='0.0.0.0')