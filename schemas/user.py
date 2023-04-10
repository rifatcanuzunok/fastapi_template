from pydantic import BaseModel


class User(BaseModel):
    username: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(User):
    password: str


class UserCreateDB(User):
    hashed_password: str


class UserResponse(User):
    is_superuser: bool


class UserUpdate(BaseModel):
    username: str = None
    is_superuser: bool = None
    password: str = None
