# main.py
from auth.jwt_handler import create_access_token
from fastapi import FastAPI, HTTPException , Depends 
from fastapi.responses import FileResponse 
from fastapi.staticfiles import StaticFiles
import auth.service as service
import auth.otp as otp_service
import control.email as email_control
import control.admin as admin
import control.user as user
from auth.dependencies import *
from pydantic import BaseModel , Field , EmailStr
from typing import Optional
import sqlite3

#================================BASE MODELS================================

class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=4, max_length=60)
    name: str = Field(min_length=2, max_length=60)
    phone: Optional[str] = Field(default=None, min_length=10, max_length=10)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=4)

class CompleteProfileRequest(BaseModel):
    otp: str = Field(min_length=6, max_length=6)
    phone: Optional[str] = Field(default=None, min_length=10)
    name: Optional[str] = Field(default=None, min_length=2)

class UpdateProfileRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=10)
    phone: Optional[str] = Field(default=None, min_length=10, max_length=10)
    

class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=4)
    new_password: str = Field(..., min_length=4)

class AdminUpdateRequest(BaseModel):
    role: Optional[str] = "user"
    is_active: Optional[int] = 0
    name: Optional[str] = Field(default=None, min_length=2, max_length=10)
    phone: Optional[str] = Field(default=None, min_length=10, max_length=10)

class AdminCreateUser(BaseModel):
    email: EmailStr
    password: str
    role: Optional[str] = "user"
    name: Optional[str] = Field(default=None, min_length=2, max_length=10)
    phone: Optional[str] = Field(default=None, min_length=10, max_length=10)
    is_active: Optional[int] = 0


app = FastAPI()
service.init_user_db() 
app.mount("/static", StaticFiles(directory="static"), name="static")

#===============================HOME ROUTES===============================

@app.get("/")
def login_page():
    return FileResponse("templates/index.html")


@app.post("/signup")
def signup(data: SignupRequest):
    try:
        service.register_user(
            email=data.email,
            password=data.password,
            name=data.name,
            phone=data.phone
        )
        return {"message": "User registered successfully"}
    
    except sqlite3.IntegrityError:
        # Triggered if email is UNIQUE and already exists
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )
    
    except Exception as e:
        print("Signup error:", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/login")
def login(data: LoginRequest):
    user = service.authenticate_user(data.email, data.password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "uid": user["uid"],
        "role": user["role"]
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }
#==========================FORGOT PASSWORD ROUTES==========================

@app.get("/forgot-password")
def forgot_page():
    return FileResponse("templates/forgot-password.html")

@app.post("/auth/forgot-password")
def forgot_password(data: ForgotPasswordRequest):

    user = service.get_user(email=data.email)

    # Always return success message
    if not user:
        return {"message": "If account exists, OTP has been sent"}

    # Rate limit
    if not otp_service.can_send_otp(user["uid"]):
        raise HTTPException(
            status_code=429,
            detail="Please wait before requesting another OTP"
        )

    otp = otp_service.create_otp()

    email_sent = email_control.send_email_otp(user["email"], otp)

    if email_sent:
        otp_service.store_otp(user["uid"], otp)

    return {"message": "If account exists, OTP has been sent"}

@app.post("/auth/reset-password")
def reset_password(data: ResetPasswordRequest):
    user = service.get_user(email=data.email)

    if not user:
        raise HTTPException(status_code=400, detail="Invalid request")

    valid = otp_service.verify_otp(user["uid"], data.otp)

    if not valid:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    admin.reset_password(user["uid"], data.new_password)
    return {"message": "Password reset successful"}

#==============================PROFILE ROUTES==============================

@app.get("/me")
def read_current_user(current_user: dict = Depends(get_current_user)):
    return {
        "uid": current_user["uid"],
        "email": current_user["email"],
        "role": current_user["role"],
        "name": current_user["name"],
        "phone": current_user["phone"],
        "is_active": current_user["is_active"]
    }


@app.get("/complete-profile")
def complete_profile_page():
    return FileResponse("templates/complete_profile.html")


@app.post("/me/send-otp")
def send_otp(current_user: dict = Depends(get_current_user)):

    # Already active user should not request OTP
    if current_user["is_active"]:
        raise HTTPException(
            status_code=400,
            detail="Account already active"
        )

    # Rate limiting
    if not otp_service.can_send_otp(current_user["uid"]):
        raise HTTPException(
            status_code=429,
            detail="Please wait before requesting another OTP"
        )

    # Generate OTP
    otp = otp_service.create_otp()

    # Send email
    email_sent = email_control.send_email_otp(current_user["email"], otp)

    if not email_sent:
        raise HTTPException(
            status_code=500,
            detail="Failed to send OTP"
        )

    # Store OTP only after successful send
    otp_service.store_otp(current_user["uid"], otp)

    return {"message": "OTP sent successfully"}


@app.put("/me/activate")
def activate_user(
    data: CompleteProfileRequest,
    current_user: dict = Depends(get_current_user)
):
    if current_user["is_active"]:
        raise HTTPException(status_code=400, detail="Account already active")

    if not otp_service.verify_otp(current_user["uid"], data.otp):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    admin.update_user(current_user["uid"], {
        "phone": data.phone,
        "is_active": 1
    })

    return {"message": "Profile completed"}

#===============================USER ROUTES===============================

@app.get("/dashboard")
def dashboard():
    return FileResponse("templates/dashboard.html")

@app.put("/me")
def update_profile(
    data: UpdateProfileRequest,
    current_user: dict = Depends(get_active_user)
):
    return user.update_user(
        current_user["uid"],
        data.dict(exclude_unset=True)
    )

@app.put("/me/password")
def change_my_password(
    data: ChangePasswordRequest,
    current_user: dict = Depends(get_active_user)
):
    return user.change_password(
        current_user["uid"],
        data.old_password,
        data.new_password
    )

#===============================ADMIN ROUTES==============================

@app.get("/admin")
def admin_panel():
    return FileResponse("templates/admin.html")

@app.post("/admin/users")
def create_user_route(
    data: AdminCreateUser,
    current_user: dict = Depends(require_role("admin"))
):
    return admin.create_user(data.dict())

@app.get("/admin/users")
def list_users_route(current_user: dict = Depends(require_role("admin"))):
    return admin.get_all_users()

@app.get("/admin/users/{uid}")
def get_user_route(uid: int, current_user: dict = Depends(require_role("admin"))):
    return admin.get_user(uid)

@app.put("/admin/users/{uid}")
def update_user_route(
    uid: int,
    data: AdminUpdateRequest,
    current_user: dict = Depends(require_role("admin"))
):
    return admin.update_user(uid, data.dict(exclude_unset=True))

@app.delete("/admin/users/{uid}")
def delete_user_route(
    uid: int,
    current_user: dict = Depends(require_role("admin"))
):
    return admin.delete_user(uid)
