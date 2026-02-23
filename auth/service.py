# auth/service.py

import time
import sqlite3
import hashlib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

USER_DB = BASE_DIR / "user.db"

def get_user_conn():
    return sqlite3.connect(USER_DB)

def init_user_db():
    conn = get_user_conn()
    cur = conn.cursor()

    cur.execute("PRAGMA journal_mode=WAL;")
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            uid INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            name TEXT,
            phone TEXT,
            is_active INTEGER DEFAULT 0,
            created_at INTEGER NOT NULL
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS email_otps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid INTEGER NOT NULL,
            otp TEXT NOT NULL,
            expires_at INTEGER NOT NULL,
            is_used INTEGER DEFAULT 0
        );
    """)

    conn.commit()
    conn.close()

def simple_hash(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_hash(password: str, stored_hash: str) -> bool:
    return simple_hash(password) == stored_hash

def get_user(email: str = None, uid: int = None) -> dict | None:
    conn = get_user_conn()
    cur = conn.cursor()

    if email is not None:
        cur.execute("""
            SELECT uid, email, password, name, phone, role, is_active, created_at
            FROM users
            WHERE email = ?
        """, (email,))
    elif uid is not None:
        cur.execute("""
            SELECT uid, email, password, name, phone, role, is_active, created_at
            FROM users
            WHERE uid = ?
        """, (uid,))
    else:
        conn.close()
        return None

    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "uid": row[0],
        "email": row[1],
        "stored_password": row[2],
        "name": row[3],
        "phone": row[4],
        "role": row[5],
        "is_active": row[6],
        "created_at": row[7],
    }

def register_user(
    email: str,
    password: str,
    name: str,
    phone: str | None = None,
):
    conn = get_user_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (
                password,
                name,
                email,
                phone,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            simple_hash(password), name, email, phone, int(time.time()) ))
        conn.commit()
    finally:
        conn.close()

def authenticate_user(email: str, password: str) -> dict | None:
    user = get_user(email)

    if not user:
        return None

    if not verify_hash(password, user["stored_password"]):
        return None

    return user

def update_user(uid: int, data: dict):
    
    if not data:
        return {"message": "Nothing to update"}

    conn = get_user_conn()
    cur = conn.cursor()

    fields = ", ".join([f"{k} = ?" for k in data.keys()])
    values = list(data.values())
    values.append(uid)

    cur.execute(f"""
        UPDATE users
        SET {fields}
        WHERE uid = ?
    """, values)

    conn.commit()
    conn.close()

    return {"message": "User updated successfully"}

def activate_user(uid : int , status : int ) :
    conn = get_user_conn()
    cur = conn.cursor()
    cur.execute('''Update users set is_active =? where uid =? ''' , (status , uid))
    conn.commit()
    conn.close()
    return