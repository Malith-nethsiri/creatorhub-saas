from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.security import get_password_hash, verify_password, create_access_token, get_current_active_user
from app.core.database import get_db
from app.schemas import auth as auth_schemas, user as user_schemas
from app.models import user as user_models

router = APIRouter()

@router.post("/signup", response_model=user_schemas.UserResponse)
def signup(user_data: user_schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(user_models.User).filter(user_models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = get_password_hash(user_data.password)
    new_user = user_models.User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=auth_schemas.Token)
def login(form_data: auth_schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(user_models.User).filter(user_models.User.email == form_data.email).first()

    if not user or not verify_password(form_data.password, getattr(user, "hashed_password")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=300)
    access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=user_schemas.UserResponse)
def get_current_user(current_user: user_models.User = Depends(get_current_active_user)):
    return current_user
