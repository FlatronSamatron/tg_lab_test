from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
import jwt
from app.config import settings
from pwdlib import PasswordHash

class AuthService:
    password_hash = PasswordHash.recommended()

    def get_password_hash(self, password):
        return self.password_hash.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.password_hash.verify(plain_password, hashed_password)


    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def decode_token(self, token: str):
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        except jwt.exceptions.DecodeError:
            raise HTTPException(401, 'Wrong token')
