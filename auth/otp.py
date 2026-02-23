# auth/otp.py
import time
import secrets
import auth.service as service


OTP_EXPIRY_SECONDS = 300  # 5 minutes

def create_otp() -> str:
    return f"{secrets.randbelow(1000000):06d}"

def store_otp(uid: int, otp: str):

    hashed_otp = service.simple_hash(otp)
    expires_at = int(time.time()) + OTP_EXPIRY_SECONDS

    conn = service.get_user_conn()
    cur = conn.cursor()

    # Invalidate previous unused OTPs
    cur.execute("""
        UPDATE email_otps
        SET is_used = 1
        WHERE uid = ? AND is_used = 0
    """, (uid,))

    # Insert new OTP
    cur.execute("""
        INSERT INTO email_otps (uid, otp, expires_at, is_used)
        VALUES (?, ?, ?, 0)
    """, (uid, hashed_otp, expires_at))

    conn.commit()
    conn.close()


def verify_otp(uid: int, otp: str) -> bool:

    hashed_input = service.simple_hash(otp)
    current_time = int(time.time())

    conn = service.get_user_conn()
    cur = conn.cursor()

    # Get latest unused OTP for this user
    cur.execute("""
        SELECT id, otp, expires_at
        FROM email_otps
        WHERE uid = ? AND is_used = 0
        ORDER BY id DESC
        LIMIT 1
    """, (uid,))

    row = cur.fetchone()

    if not row:
        conn.close()
        return False

    otp_id, stored_hash, expires_at = row

    # Check expiry
    if current_time > expires_at:
        cur.execute("UPDATE email_otps SET is_used = 1 WHERE id = ?", (otp_id,))
        conn.commit()
        conn.close()
        return False

    # Check hash match
    if hashed_input != stored_hash:
        conn.close()
        return False

    # Mark OTP as used
    cur.execute("""
        UPDATE email_otps
        SET is_used = 1
        WHERE id = ?
    """, (otp_id,))

    conn.commit()
    conn.close()

    return True
