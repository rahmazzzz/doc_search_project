from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings

def create_access_token(user_id: str, username: str, role: str, expires_delta: timedelta = None):
    to_encode = {
        "sub": username,       # standard claim for username
        "user_id": user_id,    # custom claim for user ID
        "role": role,          # custom claim for role
        "exp": datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt
