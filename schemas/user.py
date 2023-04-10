from pydantic import BaseModel, EmailStr


class User(BaseModel):
    username: str
    email: EmailStr


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
    email: EmailStr = None
    is_superuser: bool = None
    password: str = None
