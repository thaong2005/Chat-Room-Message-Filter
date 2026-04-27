import jwt
import os
import uuid
from dotenv import load_dotenv
from datetime import datetime, timedelta
from fastapi import HTTPException, Header
from typing import Optional



# load variables from .env
load_dotenv()

SECRET_KEY=os.getenv("SECRET_KEY")

def generate_token(user_id: str, username: str, role: str) -> str:
    "Generare JWT token after login"
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=24), # token expires after 24 hours
        "iat": datetime.utcnow(), # issued at
        "jti": str(uuid.uuid4())  # unique token id
    }

    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def validate_token(authorization: Optional[str] = Header(None)) -> dict:
    # Validate JWT token from authorization header
    # add `token: dict = Depends(validate_token)` to any end point

    if not authorization:
        raise HTTPException(status_code=401, detail="No token provided")
    
    # Bearer <token>
    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid token format. Use: Bearer <token>")

    token = parts[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms="HS256")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired. Please log in again")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token. Please log in again")


def validate_admin(authorization: Optional[str] = Header(None)) -> dict:\
    # checks for admin role in token
    payload = validate_token(authorization)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access Denied. Admin privilege required.")
    return payload