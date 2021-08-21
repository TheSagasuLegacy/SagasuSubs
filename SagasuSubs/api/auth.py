from pathlib import Path


class AuthTokenManager:
    _token = None
    default_path = Path(".") / "auth.txt"

    @classmethod
    def load_file(cls, file: Path = None):
        file = file or cls.default_path
        cls._token = file.read_text(encoding="utf-8")

    @classmethod
    def get_token(cls) -> str:
        assert cls._token is not None, "token must be loaded first"
        return cls._token

    @classmethod
    def set_token(cls, token: str, *, persist: bool = False):
        if persist:
            cls.default_path.write_text(token, encoding="utf-8")
        cls._token = token


if AuthTokenManager.default_path.is_file():
    AuthTokenManager.load_file()
