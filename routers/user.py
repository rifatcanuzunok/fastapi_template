import uuid

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from dao import RedisDAO, UserDAO
from dependencies import DependencyFactory
from models import User
from schemas import UserCreate, UserResponse, UserUpdate
from services import Authenticator, RedisClient, TokenDTO, UserAuthenticator, registration_confirmation
from utils import Result, filter_none_values

router = APIRouter(prefix="/user", tags=["user"])
redis_client = RedisClient()


@router.get("/")
def list_users(dao: UserDAO = Depends(DependencyFactory.get_user_dao)):
    users = dao.get_all()
    users.data = [UserResponse(username=i.username, is_superuser=i.is_superuser) for i in users.data]
    return users


@router.post("/register/admin")
async def create_admin_user(
    data: UserCreate,
    user_dao: UserDAO = Depends(DependencyFactory.get_user_dao),
    authenticator: Authenticator = Depends(DependencyFactory.get_authenticator),
    admin_user: User = Depends(DependencyFactory.is_admin),
):
    hashed_password = authenticator.get_password_hash(data.password)
    user = User(
        username=data.username,
        hashed_password=hashed_password,
        is_superuser=True,
        email=data.email,
        mail_confirmed=True,
    )
    db_result = user_dao.create(user)
    if db_result.success:
        return JSONResponse("Registration successfull.", status.HTTP_201_CREATED)
    return JSONResponse(db_result.message, status.HTTP_400_BAD_REQUEST)


@router.delete("/delete")
async def delete_user(
    username: str,
    user_dao: UserDAO = Depends(DependencyFactory.get_user_dao),
    admin_user: User = Depends(DependencyFactory.is_admin),
):
    user_result = user_dao.get_by_username(username=username)
    if user_result.success:
        user: User = user_result.data
        delete_result: Result[User] = user_dao.delete(user=user)
        if delete_result.success:
            return JSONResponse(
                jsonable_encoder(
                    UserResponse(username=delete_result.data.username, is_superuser=delete_result.data.is_superuser)
                ),
                status_code=status.HTTP_200_OK,
            )
        return JSONResponse(delete_result.message, status_code=status.HTTP_400_BAD_REQUEST)
    return JSONResponse(user_result.message, status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/changepassword/me")
async def change_password(
    password: str,
    current_user: User = Depends(DependencyFactory.get_current_user),
    authenticator: Authenticator = Depends(DependencyFactory.get_authenticator),
    user_dao: UserDAO = Depends(DependencyFactory.get_user_dao),
):
    hashed_password = authenticator.get_password_hash(password)
    update_result = user_dao.update(current_user, update_dict={"hashed_password": hashed_password})
    if update_result.success:
        return JSONResponse(
            jsonable_encoder(
                UserResponse(username=update_result.data.username, is_superuser=update_result.data.is_superuser)
            ),
            status_code=status.HTTP_200_OK,
        )
    return JSONResponse(update_result.message, status.HTTP_400_BAD_REQUEST)


@router.post("/changeusername/me")
async def change_username(
    username: str,
    current_user: User = Depends(DependencyFactory.get_current_user),
    user_dao: UserDAO = Depends(DependencyFactory.get_user_dao),
):
    update_result = user_dao.update(current_user, update_dict={"username": username})
    if update_result.success:
        return JSONResponse(
            jsonable_encoder(
                UserResponse(username=update_result.data.username, is_superuser=update_result.data.is_superuser)
            ),
            status_code=status.HTTP_200_OK,
        )
    return JSONResponse(update_result.message, status.HTTP_400_BAD_REQUEST)


@router.post("/update/admin")
async def update_user(
    update_dict: UserUpdate,
    username: str,
    admin_user: User = Depends(DependencyFactory.is_admin),
    user_dao: UserDAO = Depends(DependencyFactory.get_user_dao),
):
    user_result = user_dao.get_by_username(username=username)
    if user_result.success:
        update_result = user_dao.update(user_result.data, update_dict=filter_none_values(update_dict.dict()))
        if update_result.success:
            return JSONResponse(
                jsonable_encoder(
                    UserResponse(username=update_result.data.username, is_superuser=update_result.data.is_superuser)
                ),
                status_code=status.HTTP_200_OK,
            )
        return JSONResponse(update_result.message, status.HTTP_400_BAD_REQUEST)
    return JSONResponse(user_result.message, status.HTTP_400_BAD_REQUEST)


@router.post("/register")
async def register(
    data: UserCreate,
    user_dao: UserDAO = Depends(DependencyFactory.get_user_dao),
    redis_dao: RedisDAO = Depends(DependencyFactory.get_redis_dao),
    authenticator: Authenticator = Depends(DependencyFactory.get_authenticator),
):
    hashed_password = authenticator.get_password_hash(data.password)
    user = User(username=data.username, hashed_password=hashed_password, email=data.email)
    db_result = user_dao.create(user)
    if db_result.success:
        mail_uuid = str(uuid.uuid4())
        redis_dao.set(mail_uuid, data.username)
        registration_confirmation.delay(
            "Verify your e-mail",
            data.username,
            f"http://localhost:3654/user/verify/{mail_uuid}",
            data.email,
        )
        return JSONResponse("Registration successfull. Please confirm your email", status.HTTP_201_CREATED)
    return JSONResponse(db_result.message, status.HTTP_400_BAD_REQUEST)


@router.post("/login", response_model=TokenDTO, status_code=status.HTTP_200_OK)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    authenticator: UserAuthenticator = Depends(DependencyFactory.get_user_authenticator),
):
    auth_result: Result[TokenDTO] = authenticator.authenticate_user(form_data.username, form_data.password)
    return auth_result.data


@router.get("/verify/{mail_uuid}")
async def verify(
    mail_uuid,
    user_dao: UserDAO = Depends(DependencyFactory.get_user_dao),
    redis_dao: RedisDAO = Depends(DependencyFactory.get_redis_dao),
):
    username = redis_dao.get(mail_uuid)
    db_result = user_dao.get_by_username(username)
    if db_result.success:
        user = db_result.data
        if not user:
            return JSONResponse("Invalid validation code", status_code=status.HTTP_404_NOT_FOUND)
        if redis_dao.delete(mail_uuid):
            return user_dao.update(user, {"mail_confirmed": True})
    return JSONResponse(db_result.message, status.HTTP_400_BAD_REQUEST)
