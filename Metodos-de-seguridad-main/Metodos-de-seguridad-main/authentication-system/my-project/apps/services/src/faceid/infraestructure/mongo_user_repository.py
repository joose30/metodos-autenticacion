from pymongo import MongoClient
from bson.objectid import ObjectId
import pickle
import base64
from datetime import datetime
import os # <-- IMPORTANTE

# Imports corregidos (sin ".." y sin sys.path)
from ports.user_repository_port import UserRepositoryPort

class MongoUserRepository(UserRepositoryPort):
    
    def __init__(self):

        mongo_uri = os.getenv('MONGODB_URI', 'mongodb+srv://autentication:gashj421b@cluster0.xoe7f.mongodb.net/autentication?retryWrites=true&w=majority&appName=Cluster0')
        db_name = os.getenv('MONGODB_DB_NAME', 'autentication')
        
        
        self.client = MongoClient(mongo_uri) # <-- Usar la variable
        self.db = self.client[db_name]       # <-- Usar la variable
        self.collection = self.db["users"]
        self.db_name = db_name

    def check_db_connection(self):
        try:
            self.client.admin.command('ping')
            return True, self.db_name
        except Exception:
            return False, self.db_name

    def save_user(self, email, hashed_password, first_name, face_encoding, auth_method="faceid"):
        secret = base64.b64encode(pickle.dumps(face_encoding)).decode('utf-8')
        
        existing_user = self.collection.find_one({"email": email})
        if existing_user:
            raise ValueError("El email ya está registrado")

        user_document = {
            "email": email,
            "password": hashed_password,
            "first_name": first_name,
            "secret": secret,
            "auth_method": auth_method,
            "phone_number": None,
            "created_at": datetime.now()
        }
        
        result = self.collection.insert_one(user_document)
        return str(result.inserted_id)

    def get_all_users_with_secret(self):
        query = {"auth_method": "faceid", "secret": {"$ne": None}}
        users = self.collection.find(query)
        
        deserialized_users = []
        for user in users:
            try:
                user['secret_encoding'] = pickle.loads(base64.b64decode(user['secret']))
                deserialized_users.append(user)
            except Exception as e:
                print(f"Error deserializando secret para usuario {user['_id']}: {e}")
                continue
        return deserialized_users

    def find_user_by_credentials(self, email, hashed_password):
        user = self.collection.find_one({
            "email": email,
            "password": hashed_password
        })
        return user

    def get_all_users(self):
        projection = {"password": 0, "secret": 0}
        users = self.collection.find({}, projection).sort("created_at", -1)
        
        users_list = []
        for user in users:
            created_at_val = user.get('created_at')
            created_at_iso = None
            if isinstance(created_at_val, datetime):
                created_at_iso = created_at_val.isoformat()
                
            users_list.append({
                'id': str(user['_id']), 
                'email': user['email'],
                'first_name': user.get('first_name', ''),
                'createdAt': created_at_iso
            })
        return users_list

    def delete_user_by_id(self, user_id: str):
        try:
            obj_id = ObjectId(user_id)
            result = self.collection.delete_one({"_id": obj_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error al eliminar usuario por ObjectId: {e}")
            return False