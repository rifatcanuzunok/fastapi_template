from sqlalchemy.orm import Session

from models import User
from utils import Result

from .abstract_dao import AbstractDAO


class UserDAO(AbstractDAO):
    def __init__(self, session: Session):
        super().__init__(session, User)

    def create(self, user: User) -> Result[User]:
        return super().create(user)

    def update(self, user: User, update_dict: dict) -> Result[User]:
        return super().update(user, update_dict)

    def delete(self, user: User) -> Result[User]:
        return super().delete(user)

    def get_all(self) -> Result[User]:
        return super().get_all()

    def get_by_id(self, id: int) -> Result[User]:
        return super().get_by(User.id, id)

    def get_by_email(self, email: str) -> Result[User]:
        return super().get_by(User.email, email)

    def get_by_username(self, username: str) -> Result[User]:
        return super().get_by(User.username, username)
