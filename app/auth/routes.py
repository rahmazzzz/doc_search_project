from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.jwt import create_access_token
from app.auth.hashing import hash_password, verify_password
from app.models.user import User
from app.clients.mongo_client import MongoClient

router = APIRouter()
mongo_client = MongoClient()  


@router.post("/register", summary="Register a new user")
async def register(user: User):
    users_collection = mongo_client.get_user_collection()

    existing = await users_collection.find_one({"username": user.username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    user.password = hash_password(user.password)
    await users_collection.insert_one(user.dict())

    return {"message": "Registration successful"}


@router.post("/login", summary="Login and get a JWT token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    users_collection = mongo_client.get_user_collection()

    user = await users_collection.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user['password']):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user['username'], "role": user.get('role', 'user')})
    return {"access_token": token, "token_type": "bearer"}
