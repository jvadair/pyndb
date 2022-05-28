import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def derive_key(password: bytes, salt: bytes, iterations: int):
    kdf = PBKDF2HMAC(  # PBKDF2 instances can only be used once
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key


def encrypt(data: bytes, password: bytes, salt: bytes, iterations: int):
    f = Fernet(derive_key(password, salt, iterations))
    output = f.encrypt(data)
    return output


def decrypt(data: bytes, password: bytes, salt: bytes, iterations: int):
    f = Fernet(derive_key(password, salt, iterations))
    output = f.decrypt(data)
    return output