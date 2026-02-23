#control/user.py

import auth.service as service
from fastapi import HTTPException

ALLOWED_UPDATE_FIELDS = ["name", "email", "phone"]

def update_user(uid: int, data: dict):
    filtered = {
        k: v for k, v in data.items()
        if k in ALLOWED_UPDATE_FIELDS
    }

    if not filtered:
        raise HTTPException(400, "No valid fields to update")

    return service.update_user(uid, filtered)


def change_password(uid: int, old_password: str, new_password: str):
    user = service.get_user(uid=uid)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify old password
    if not service.verify_hash(old_password, user["stored_password"]):
        raise HTTPException(status_code=400, detail="Old password incorrect")

    # Hash new password
    new_hashed = service.simple_hash(new_password)

    return service.update_user(uid, {"password": new_hashed})