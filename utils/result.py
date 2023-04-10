from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Result(Generic[T], BaseModel):
    success: bool = False
    message: str | None = None
    data: T = None
