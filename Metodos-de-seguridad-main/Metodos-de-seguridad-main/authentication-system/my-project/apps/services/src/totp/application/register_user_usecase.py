from domain.otp_generator import OTPGenerator

class RegisterUserUseCase:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def execute(self, email, password,first_name, issuer_name="Mi App"):
        otp = OTPGenerator(secret=None)
        secret = otp.generate_secret()
        uri = otp.generate_uri(email, issuer_name)
        self.user_repository.save_user(email, secret, password, first_name)
        return uri