from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from models.models import User
from schemas.schemas import UserOut, UserUpdateRequest
from utils.auth import get_current_user

router = APIRouter()


@router.get("/me", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
def update_profile(data: UserUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if data.name:    current_user.name    = data.name
    if data.email:   current_user.email   = data.email
    if data.city:    current_user.city    = data.city
    if data.address: current_user.address = data.address
    db.commit()
    db.refresh(current_user)
    return current_user
