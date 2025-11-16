from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

class TwilioSMSAdapter:
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID', 'XXXXXXXXXXXXXXXXXXXXXXXX')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN', 'XXXXXXXXXXXXXXXXXXXXX')
        self.phone_number = os.getenv('TWILIO_FROM_NUMBER', 'XXXXXXXXXXXXXXXXXXXXX')
        
        print(f"🔧 Twilio Config:")
        print(f"   Account SID: {self.account_sid}")
        print(f"   Auth Token: {self.auth_token[:10]}...")
        print(f"   Phone: {self.phone_number}")
        
        if not all([self.account_sid, self.auth_token, self.phone_number]):
            print("❌ FALTAN CREDENCIALES DE TWILIO")
            self.client = None
            return
        
        try:
            self.client = Client(self.account_sid, self.auth_token)
            print("✅ Cliente Twilio inicializado correctamente")
        except Exception as e:
            print(f"❌ Error inicializando Twilio: {e}")
            self.client = None

    def send_otp(self, phone_number: str, otp: str) -> bool:
        try:
            if not self.client:
                print("❌ Cliente Twilio no disponible")
                return False
                
            print("=" * 50)
            print("📤 ENVIANDO SMS CON TWILIO:")
            print(f"   FROM: {self.phone_number}")
            print(f"   TO: {phone_number}")
            print(f"   OTP: {otp}")
            print("=" * 50)
            
            if not self._is_valid_phone_number(phone_number):
                return False
            
            # ENVIAR SMS - VERSIÓN SIMPLIFICADA Y SEGURA
            message = self.client.messages.create(
                body=f'Tu código de verificación es: {otp}',
                from_=self.phone_number,
                to=phone_number
            )
            
            print(f"✅ SMS ENVIADO EXITOSAMENTE!")
            print(f"   SID: {message.sid}")
            print(f"   Status: {message.status}")
            print("=" * 50)
            
            # RETORNAR TRUE SI SE ENVIÓ CORRECTAMENTE
            return True
            
        except Exception as e:
            print(f"❌ ERROR ENVIANDO SMS: {e}")
            print("=" * 50)
            return False
    
    def _is_valid_phone_number(self, phone_number):
        """Valida el formato del número"""
        if not phone_number:
            return False
        if not phone_number.startswith('+'):
            return False
        digits = phone_number[1:]
        if not digits.isdigit():
            return False
        if len(digits) < 10 or len(digits) > 15:
            return False
        return True