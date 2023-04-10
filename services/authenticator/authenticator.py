from datetime import datetime, timedelta
from typing import TypeVar

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from .schemas.auth import TokenDataDTO, TokenTypeDTO

T = TypeVar("T")


class Authenticator:
    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        access_token_expire_minutes: int,
        refresh_token_expire_minutes: int,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_minutes = refresh_token_expire_minutes
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password) -> str:
        return self.pwd_context.hash(password)

    def is_token_expired(self, token: str) -> bool:
        try:
            decoded_token = jwt.decode(token, self.secret_key, algorithms=self.algorithm)
            expires = decoded_token["exp"]
            return datetime.utcfromtimestamp(expires) < datetime.utcnow()
        except (jwt.exceptions.InvalidTokenError, KeyError):
            return True

    def decode_token(self, token: str) -> TokenDataDTO:
        try:
            decoded_token = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            token_data = TokenDataDTO(**decoded_token)
            return token_data
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    def create_token(self, token_data: TokenDataDTO, token_type: TokenTypeDTO) -> str:
        expires = (
            datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            if token_type == TokenTypeDTO.access
            else datetime.utcnow() + timedelta(minutes=self.refresh_token_expire_minutes)
        )
        token_data.exp = expires
        token_data.type = token_type
        return jwt.encode(token_data.dict(), self.secret_key, algorithm=self.algorithm)

    def create_access_token(self, token_data: TokenDataDTO) -> str:
        return self.create_token(token_data, TokenTypeDTO.access)

    def create_refresh_token(self, token_data: TokenDataDTO) -> str:
        return self.create_token(token_data, TokenTypeDTO.refresh)
