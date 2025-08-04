from fastapi import APIRouter, HTTPException, Depends
from pydantic import EmailStr
from app.auth.jwt import create_access_token
from app.auth.hashing import hash_password, verify_password
from app.models.user import User
from app.core.config import settings
from app.services.mongo_client import get_user_collection
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/register")
async def register(user: User):  #  Make it async
    users_collection = get_user_collection()  # Correct use, not awaited

    existing = await users_collection.find_one({"username": user.username})  #  await here
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    user.password = hash_password(user.password)
    await users_collection.insert_one(user.dict())  #  await here
    return {"message": "Registration successful"}


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    users_collection = get_user_collection()
    user = await users_collection.find_one({"username": form_data.username})

    if not user or not verify_password(form_data.password, user['password']):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user['username'], "role": user.get('role', 'user')})
    return {"access_token": token, "token_type": "bearer"}
