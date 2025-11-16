from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

class MongoDBUserRepository:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['otp_db']
        self.collection = self.db['users']
        print("✅ Conectado a MongoDB: otp_db.users")

    def save_user(self, email, user_data):
        """Guarda o actualiza un usuario"""
        result = self.collection.update_one(
            {'email': email},
            {'$set': user_data},
            upsert=True
        )
        return result.upserted_id or result.modified_count > 0

    def get_user(self, email):
        """Obtiene un usuario por email"""
        return self.collection.find_one({'email': email})

    def update_user(self, email, updates):
        """Actualiza un usuario"""
        result = self.collection.update_one(
            {'email': email},
            {'$set': updates}
        )
        return result.modified_count > 0

    def user_exists(self, email):
        """Verifica si un usuario existe"""
        return self.collection.count_documents({'email': email}) > 0