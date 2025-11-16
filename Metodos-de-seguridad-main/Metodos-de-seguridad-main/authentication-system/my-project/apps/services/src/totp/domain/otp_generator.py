import pyotp

class OTPGenerator:
    def __init__(self, secret=None):
        self.secret = secret or pyotp.random_base32()

    def generate_secret(self):
        return pyotp.random_base32()

    def generate_uri(self, usr_email, issuer_name):
        totp = pyotp.TOTP(self.secret)
        return totp.provisioning_uri(usr_email, issuer_name)

    def verify_code(self, code: str) -> bool:
        totp = pyotp.TOTP(self.secret)
        return totp.verify(code)