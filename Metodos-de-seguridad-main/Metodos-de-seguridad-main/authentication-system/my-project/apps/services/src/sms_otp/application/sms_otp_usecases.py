try:
    from domain.sms_otp_generator import SMSOTPGenerator
    from ports.sms_service_port import SMSServicePort
except ImportError:
    from ..domain.sms_otp_generator import SMSOTPGenerator
    from ..ports.sms_service_port import SMSServicePort

class SendOTPUseCase:
    def __init__(self, sms_service: SMSServicePort, mongo_repository):
        self.sms_service = sms_service
        self.otp_generator = SMSOTPGenerator(mongo_repository)

    def execute(self, phone_number: str) -> bool:
        try:
            otp = self.otp_generator.generate_otp(phone_number)
            result = self.sms_service.send_otp(phone_number, otp)
            print(f"📨 Resultado envío SMS: {result}")
            return result
        except Exception as e:
            print(f"❌ Error en SendOTPUseCase: {e}")
            return False

class VerifyOTPUseCase:
    def __init__(self, mongo_repository):
        self.otp_generator = SMSOTPGenerator(mongo_repository)

    def execute(self, phone_number: str, otp: str) -> bool:
        return self.otp_generator.verify_otp(phone_number, otp)