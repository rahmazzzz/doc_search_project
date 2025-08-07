from pydantic import BaseModel, EmailStr
from typing import Literal

class User(BaseModel):
    username: str
    name: str
    email: EmailStr
    password: str
    role: Literal["admin", "user"]
