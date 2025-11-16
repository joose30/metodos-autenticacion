from flask import jsonify, session
import sys
import os

# Añadir el directorio raíz del proyecto al path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from infrastructure.mongo_repository import MongoDBUserRepository

def init_routes(app, mongo_repo=None):
    if mongo_repo is None:
        mongo_repo = MongoDBUserRepository()

    @app.route('/user-info-sms', methods=['GET'])
    def get_user_info():
        email = session.get('email')
        if not email:
            return jsonify({'error': 'Not authenticated'}), 401
            
        user = mongo_repo.get_user(email)
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify({
            'email': user['email'],
            'first_name': user.get('first_name', ''),
            'auth_method': user.get('auth_method', 'sms')
        })
