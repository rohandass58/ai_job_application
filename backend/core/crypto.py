# backend/core/crypto.py

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

from core.exceptions import AppException


def _fernet() -> Fernet:
    key = settings.FIELD_ENCRYPTION_KEY
    if not key:
        raise AppException("FIELD_ENCRYPTION_KEY is not configured", status_code=500)
    return Fernet(key.encode())


def encrypt(plain: str) -> str:
    return _fernet().encrypt(plain.encode()).decode()


def decrypt(token: str) -> str:
    try:
        return _fernet().decrypt(token.encode()).decode()
    except InvalidToken:
        raise AppException("Stored email credentials could not be decrypted", status_code=500)