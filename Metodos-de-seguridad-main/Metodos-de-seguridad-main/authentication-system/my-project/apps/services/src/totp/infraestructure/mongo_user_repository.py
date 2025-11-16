from pymongo import MongoClient
from ports.user_repository_port import UserRepositoryPort

class MongoUserRepository(UserRepositoryPort):
    def __init__(self, uri="mongodb://localhost:27017", db_name="otp_db"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db["users"]

    def save_user(self, email, secret, password, first_name, auth_method="totp"):
        self.collection.insert_one({
            "email": email,
            "password": password,
            "first_name": first_name,
            "secret": secret,
            "auth_method": auth_method,
            "phone_number": None  # Para método SMS
        })
        
    def get_secret_by_email(self, email):
        user = self.collection.find_one({"email": email})
        return user["secret"] if user else None