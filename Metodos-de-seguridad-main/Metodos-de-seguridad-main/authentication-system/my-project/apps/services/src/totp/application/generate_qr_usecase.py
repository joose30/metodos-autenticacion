from domain.otp_generator import OTPGenerator

class GenerateQRUseCase:
    def __init__(self, qr_service):
        self.qr_service = qr_service

    def execute(self, secret, email, issuer):
        otp = OTPGenerator(secret=secret)
        uri = otp.generate_uri(usr_email=email,issuer_name=issuer)
        return self.qr_service.generate_qr_image(uri)