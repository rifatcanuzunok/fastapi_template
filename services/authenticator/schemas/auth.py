from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class TokenDTO(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class TokenTypeDTO(str, Enum):
    access = "access"
    refresh = "refresh"


class TokenDataDTO(BaseModel):
    sub: str
    exp: datetime | None = None
    type: TokenTypeDTO | None = None
