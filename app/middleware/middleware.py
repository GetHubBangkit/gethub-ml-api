from datetime import datetime

from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWTError

import configs.config

bearer = HTTPBearer()

def verify_token(token: str) -> bool:
    try:
        payload = jwt.decode(token, configs.config.SECRET_KEY, algorithms=["HS256"])

        if datetime.fromtimestamp(payload["exp"]) < datetime.now():
            return False
        return True
    except PyJWTError:
        return False

async def check_jwt_token(request: Request):
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized: Missing Authorization header")

    token = authorization.replace("Bearer ", "")  # Mengambil token dari Authorization header

    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or expired token")