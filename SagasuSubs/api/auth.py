from pathlib import Path
from typing import Optional

import jwt
from pydantic import BaseModel, EmailStr


class JWTPayload(BaseModel):
    id: int
    name: str
    email: EmailStr
    token: str

    @classmethod
    def from_token(cls, token: str):
        return cls(
            **jwt.decode(token, options={"verify_signature": False}), token=token
        )


class AuthTokenManager:
    _token_data: Optional[JWTPayload] = None
    default_path = Path(".") / "auth.txt"

    @classmethod
    def load_file(cls, file: Path = None):
        file = file or cls.default_path
        token = file.read_text(encoding="utf-8")
        cls._token_data = JWTPayload.from_token(token)

    @classmethod
    def get_token(cls) -> JWTPayload:
        assert cls._token_data is not None, "token must be loaded first"
        return cls._token_data

    @classmethod
    def set_token(cls, token: str, *, persist: bool = False):
        if persist:
            cls.default_path.write_text(token, encoding="utf-8")
        cls._token_data = JWTPayload.from_token(token)


if AuthTokenManager.default_path.is_file():
    AuthTokenManager.load_file()
