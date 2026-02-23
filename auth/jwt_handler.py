# auth/jwt_handler.py

from jose import jwt, JWTError
import time

SECRET_KEY = "super-secret-key-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 3600  # 1 hour


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = int(time.time()) + ACCESS_TOKEN_EXPIRE_SECONDS
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None