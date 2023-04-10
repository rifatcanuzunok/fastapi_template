from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from config import settings
from dao import RedisDAO, UserDAO
from database import SessionLocal
from models import User
from services import Authenticator, UserAuthenticator


class DependencyFactory:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def get_user_dao(db: Session = Depends(get_db)):
        dao = UserDAO(db)
        try:
            yield dao
        finally:
            dao.session.close()

    def get_redis_dao():
        dao = RedisDAO(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_EXPIRE)
        try:
            yield dao
        finally:
            dao.client.close()

    def get_user_authenticator(dao: UserDAO = Depends(get_user_dao), redis_dao: RedisDAO = Depends(get_redis_dao)):
        try:
            yield UserAuthenticator(
                secret_key=settings.SECRET_KEY,
                algorithm=settings.ALGORITHM,
                access_token_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
                refresh_token_expire_minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
                dao=dao,
                redis_dao=redis_dao,
            )
        finally:
            dao.session.close()

    def get_authenticator():
        return Authenticator(
            secret_key=settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
            access_token_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            refresh_token_expire_minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
        )

    async def get_current_user(
        token=Depends(oauth2_scheme), authenticator: Authenticator = Depends(get_user_authenticator)
    ) -> User:
        return authenticator.get_current_user(token)

    async def is_admin(
        token=Depends(oauth2_scheme), authenticator: Authenticator = Depends(get_user_authenticator)
    ) -> User:
        return authenticator.get_current_user_if_admin(token)
