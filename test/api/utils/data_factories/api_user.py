# utils/data_factories/api_user.py
from dataclasses import dataclass
import random
import string
from typing import Optional


@dataclass
class APIUser:
    username: str
    password: str
    token: Optional[str] = None

    @property
    def is_authenticated(self) -> bool:
        return self.token is not None


class APIUserFactory:
    @staticmethod
    def generate_username() -> str:
        return f"testuser_{random.randint(100000, 999999)}"

    @staticmethod
    def generate_password(length: int = 12) -> str:
        return "".join(random.choices(
            string.ascii_letters + string.digits + "!@#$%^&*",
            k=length
        ))

    @classmethod
    def create(cls, username: Optional[str] = None, password: Optional[str] = None) -> APIUser:
        """Create a new APIUser with either provided or random credentials"""
        return APIUser(
            username=username or cls.generate_username(),
            password=password or cls.generate_password()
        )
