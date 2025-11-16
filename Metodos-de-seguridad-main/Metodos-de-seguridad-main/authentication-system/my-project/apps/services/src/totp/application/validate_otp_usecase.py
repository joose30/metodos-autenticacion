from domain.otp_generator import OTPGenerator

class ValidateOTPUseCase:
    def __init__(self, secret):
        self.secret = secret

    def execute(self, code: str) -> bool:
        otp = OTPGenerator(secret=self.secret)
        return otp.verify_code(code)