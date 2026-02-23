import time 
import auth.service as service
from fastapi import HTTPException

ALLOWED_UPDATE_FIELDS = ["name", "email", "phone", "role", "is_active"]

def get_all_users():
    conn = service.get_user_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT uid,name, email, phone, role, is_active, created_at
        FROM users
    """)

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "uid": row[0],
            "name": row[1],
            "email": row[2],
            "phone": row[3],
            "role": row[4],
            "is_active": row[5],
            "created_at": row[6]
        }
        for row in rows
    ]

def get_user(uid: int):
    user = service.get_user(uid=uid)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.pop("stored_password", None)
    return user

def create_user(data: dict):
    required_fields = {"email", "password"}

    if not required_fields.issubset(data.keys()):
        raise HTTPException(status_code=400, detail="Missing required fields")

    conn = service.get_user_conn()
    cur = conn.cursor()

    # Check if email already exists
    cur.execute("SELECT uid FROM users WHERE email = ?", (data["email"],))
    if cur.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email already exists")

    cur.execute("""
        INSERT INTO users (email, password, role, name, phone, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data["email"],
        service.simple_hash(data["password"]),
        data.get("role", "user"),
        data.get("name"),
        data.get("phone"),
        data.get("is_active", 1),
        int(time.time())
    ))

    conn.commit()
    conn.close()

    return {"message": "User created successfully"}

def update_user(uid: int, data: dict):
    filtered = {
        k: v for k, v in data.items()
        if k in ALLOWED_UPDATE_FIELDS
    }

    return service.update_user(uid, filtered)

def delete_user(uid: int):
    conn = service.get_user_conn()
    cur = conn.cursor()

    # Check if user exists
    cur.execute("SELECT uid FROM users WHERE uid = ?", (uid,))
    user = cur.fetchone()

    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    # Perform deletion
    cur.execute("DELETE FROM users WHERE uid = ?", (uid,))
    conn.commit()
    conn.close()

    return {"message": "User deleted successfully"}

def upgarde_user(uid : int , role : str ) :
    conn = service.get_user_conn()
    cur = conn.cursor()
    cur.execute('''Update users set role =? where uid =? ''' , (role,uid))
    conn.commit()
    conn.close()
    return

def activate_user(uid : int , status : int ) :
    conn = service.get_user_conn()
    cur = conn.cursor()
    cur.execute('''Update users set is_active =? where uid =? ''' , (status , uid))
    conn.commit()
    conn.close()
    return