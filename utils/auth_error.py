from fastapi import HTTPException


class AuthenticationError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=401, detail=message)