from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth.jwt_handler import verify_token
from auth.service import get_user

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    payload = verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    uid = payload.get("uid")
    user = get_user(uid=uid)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


#  Activation Enforcement
def get_active_user(current_user: dict = Depends(get_current_user)):
    if not (current_user["is_active"] == 1 ):
        raise HTTPException(
            status_code=403,
            detail="Complete profile first"
        )
    return current_user


def require_role(required_role: str):
    def role_checker(current_user: dict = Depends(get_active_user)):
        if current_user["role"] != required_role:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker