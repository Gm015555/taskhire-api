from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from models.models import User
from schemas.schemas import RegisterRequest, LoginRequest, TokenResponse
from utils.auth import hash_password, verify_password, create_token

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.phone == data.phone).first():
        raise HTTPException(status_code=400, detail="Phone already registered")
    user = User(
        name=data.name,
        phone=data.phone,
        city=data.city or "Lahore",
        password_hash=hash_password(data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(access_token=create_token(user.id), user_id=user.id, name=user.name)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == data.phone).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Wrong phone or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is blocked")
    return TokenResponse(access_token=create_token(user.id), user_id=user.id, name=user.name)
