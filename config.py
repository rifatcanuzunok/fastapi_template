import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str
    SECRET_KEY: str
    MAIL_HOST: str
    MAIL_PORT: int
    SENDER_MAIL: str
    SENDER_PASSWORD: str
    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_EXPIRE: int
    # jwt
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int

    class Config:
        if os.getenv("DOCKER"):
            env_file = "docker.env"
        else:
            env_file = ".env"


settings = Settings()