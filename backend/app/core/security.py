from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from sqlalchemy.orm import Session
import logging
from functools import wraps
from time import time
from collections import defaultdict

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.models.api_key import APIKey  # ✅ Correctly import your APIKey SQLAlchemy model

logger = logging.getLogger(__name__)

# ---------------------------
# PASSWORD HASHING
# ---------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def safe_verify_password(plain_password: str, user_hashed_password) -> bool:
    """Safely verify password handling SQLAlchemy columns."""
    return pwd_context.verify(plain_password, str(user_hashed_password))

# ---------------------------
# JWT SECURITY
# ---------------------------
security = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")  # ✅ Correct endpoint

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != token_type:
            return None
        if payload.get("exp") is None or datetime.utcfromtimestamp(payload["exp"]) < datetime.utcnow():
            return None
        return payload
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        return None

# ---------------------------
# USER AUTH HELPERS
# ---------------------------
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user: Optional[User] = db.query(User).filter(User.id == user_id).first()
    if not user or not bool(user.is_active):  # ✅ Explicit bool cast for Pylance
        raise HTTPException(status_code=400, detail="Inactive or invalid user")

    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not bool(current_user.is_active):  # ✅ Explicit cast
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, str(user.hashed_password)):
        return None
    return user

# ---------------------------
# SUBSCRIPTION CHECK
# ---------------------------
def check_subscription_access(
    required_plan: str,
    current_user: User = Depends(get_current_user)
) -> User:
    plan_hierarchy = {
        "free": 0,
        "creator": 1,
        "pro": 2,
        "enterprise": 3
    }

    user_plan_level = plan_hierarchy.get(current_user.subscription_plan.value, 0)
    required_plan_level = plan_hierarchy.get(required_plan, 99)

    if user_plan_level < required_plan_level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": f"{required_plan.title()} plan required",
                "current_plan": current_user.subscription_plan.value,
                "required_plan": required_plan,
                "upgrade_required": True
            }
        )
    return current_user

# ---------------------------
# SIMPLE RATE LIMITING (Dev Only)
# ---------------------------
rate_limit_store = defaultdict(list)

def rate_limit(requests_per_minute: int = 60):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = next((arg for arg in args if isinstance(arg, User)), None)
            if current_user:
                user_id = str(current_user.id)
                current_time = time()
                rate_limit_store[user_id] = [
                    req_time for req_time in rate_limit_store[user_id]
                    if current_time - req_time < 60
                ]
                if len(rate_limit_store[user_id]) >= requests_per_minute:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded"
                    )
                rate_limit_store[user_id].append(current_time)
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# ---------------------------
# API KEY VALIDATION
# ---------------------------
def validate_api_key(api_key: str, db: Session) -> Optional[User]:
    """Validate API key and return associated user."""
    api_key_record = db.query(APIKey).filter(
        APIKey.id == api_key,
        APIKey.is_active.is_(True)  # ✅ SQLAlchemy-safe check
    ).first()

    if not api_key_record:
        return None

    setattr(api_key_record, "last_used", datetime.utcnow())
    db.commit()

    return api_key_record.user
