from dao import RedisDAO, UserDAO
from models.user import User
from services import Authenticator
from utils import AuthenticationError, Result

from .schemas.auth import TokenDataDTO, TokenDTO


class UserAuthenticator(Authenticator):
    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        access_token_expire_minutes: int,
        refresh_token_expire_minutes: int,
        dao: UserDAO,
        redis_dao: RedisDAO,
    ):
        super().__init__(secret_key, algorithm, access_token_expire_minutes, refresh_token_expire_minutes)
        self.dao = dao
        self.redis_dao = redis_dao

    def authenticate_user(self, username: str, password: str) -> Result[TokenDTO]:
        user_result: Result[User] = self.dao.get_by_username(username)
        if not user_result.success:
            return Result(message=user_result.message)
        if not user_result.data:
            raise AuthenticationError(message="Incorrect username or password")
        user = user_result.data
        if not self.verify_password(password, user.hashed_password):
            raise AuthenticationError(message="Incorrect username or password")
        refresh_token = self.redis_dao.get(str(user.id))
        if refresh_token:
            if not self.is_token_expired(refresh_token):
                access_token = self.create_access_token(TokenDataDTO(sub=user.username))
                token = TokenDTO(access_token=access_token, refresh_token=refresh_token)
                return Result(success=True, data=token)
            else:
                raise AuthenticationError(message="Please login.")
        access_token = self.create_access_token(TokenDataDTO(sub=user.username))
        refresh_token = self.create_refresh_token(TokenDataDTO(sub=user.username))
        self.redis_dao.set(str(user.id), refresh_token)
        token = TokenDTO(access_token=access_token, refresh_token=refresh_token)
        return Result(success=True, data=token)

    def get_current_user(self, token: str) -> User:
        token_content: TokenDataDTO = self.decode_token(token)
        username: str = token_content.sub
        user_result: Result[User] = self.dao.get_by_username(username)
        return user_result.data

    def get_current_user_if_admin(self, token: str) -> User:
        user = self.get_current_user(token)
        if user.is_superuser:
            return user
        else:
            raise AuthenticationError("User is not admin.")
