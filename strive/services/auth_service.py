import hashlib
import secrets
from typing import Optional
from sqlalchemy.orm import Session
from models import User


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()
    return f"{salt}${pwd_hash}"


def verify_password(plain_password: str, stored_hash: str) -> bool:
    salt, pwd_hash = stored_hash.split("$", 1)
    return hashlib.pbkdf2_hmac("sha256", plain_password.encode(), salt.encode(), 100_000).hex() == pwd_hash


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_user(
    db: Session, username: str, email: str, password: str
) -> tuple[bool, str, Optional[User]]:
    existing = db.query(User).filter(
        (User.email == email) | (User.username == username)
    ).first()
    if existing:
        return False, "Email or username already taken", None

    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
    )
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return True, "Account created!", user
    except Exception as e:
        db.rollback()
        return False, f"Failed to create account: {str(e)}", None
