import random
import time
from datetime import datetime, timedelta

class SMSOTPGenerator:
    def __init__(self, mongo_repository, length: int = 6, expiry_minutes: int = 5):
        self.length = length
        self.expiry_minutes = expiry_minutes
        self.mongo_repo = mongo_repository

    def generate_otp(self, phone_number: str) -> str:
        otp = ''.join([str(random.randint(0, 9)) for _ in range(self.length)])
        expiry_time = datetime.now() + timedelta(minutes=self.expiry_minutes)
        
        # Guardar OTP en MongoDB
        otp_data = {
            'phone_number': phone_number,
            'otp': otp,
            'expires_at': expiry_time,
            'created_at': datetime.now(),
            'used': False
        }
        
        # Guardar en colección de OTPs
        self.mongo_repo.db['otps'].update_one(
            {'phone_number': phone_number},
            {'$set': otp_data},
            upsert=True
        )
        
        print(f"🔐 OTP generado para {phone_number}: {otp} (expira: {expiry_time})")
        return otp

    def verify_otp(self, phone_number: str, otp: str) -> bool:
        print(f"🔍 Verificando OTP {otp} para {phone_number}")
        
        # Buscar OTP en MongoDB
        otp_record = self.mongo_repo.db['otps'].find_one({
            'phone_number': phone_number,
            'used': False
        })
        
        if not otp_record:
            print(f"❌ No hay OTP pendiente para {phone_number}")
            return False
        
        stored_otp = otp_record['otp']
        expiry_time = otp_record['expires_at']
        
        if datetime.now() > expiry_time:
            print(f"❌ OTP expirado para {phone_number}")
            # Marcar como expirado
            self.mongo_repo.db['otps'].update_one(
                {'phone_number': phone_number},
                {'$set': {'used': True}}
            )
            return False
        
        if stored_otp == otp:
            print(f"✅ OTP válido para {phone_number}")
            # Marcar como usado
            self.mongo_repo.db['otps'].update_one(
                {'phone_number': phone_number},
                {'$set': {'used': True}}
            )
            return True
        else:
            print(f"❌ OTP incorrecto para {phone_number}")
            return False