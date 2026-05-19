from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException

SECRET_KEY = "thisiskazevereshopsecretkeyforjwt"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

def create_access_token(data: dict):
    payload = {
        "sub": str(data.get('id')),
        "roles": data.get('roles'),
        "exp":datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_token(token:str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        roles = payload.get("roles")
        if user_id is None:
            raise HTTPException(status_code=401, detail="token无效")
        return {
            "id": user_id,
            "roles": roles
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="token解析无效")