from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models.user import User
from app.security.hashing import hash_password, verify_password
from app.utils.jwt_handler import create_access_token
from app.container.core_container import container

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/register")
async def register(user: User):
    existing = await container.mongo_repository.get_user_by_username(user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed = hash_password(user.password)
    user_dict = user.dict()
    user_dict["password"] = hashed

    await container.mongo_repository.create_user(user_dict)
    return {"message": "User registered successfully"}


@router.post("/login")
async def login(data: LoginRequest):
    user = await container.mongo_repository.get_user_by_username(data.username)

    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(
        user_id=str(user["_id"]),   
        username=user["username"],   
        role=user.get("role", "user")  
    )

    return {"access_token": token, "token_type": "bearer"}