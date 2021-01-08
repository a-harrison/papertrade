from passlib.context import CryptContext
from fastapi import Depends

class CryptoLogic:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(client_hash, password_hash):
        return CryptoLogic.pwd_context.verify(client_hash, password_hash)

    def get_password_hash(client_hash):
        return CryptoLogic.pwd_context.hash(client_hash)
