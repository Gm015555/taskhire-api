from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from models.models import User
from schemas.schemas import SendOTPRequest, VerifyOTPRequest
from utils.auth import hash_password, create_token
from datetime import datetime, timedelta
import random, string

router = APIRouter()
otp_store = {}


@router.post("/send")
def send_otp(data: SendOTPRequest):
    otp = ''.join(random.choices(string.digits, k=6))
    otp_store[data.phone] = {
        "otp": otp,
        "expires": datetime.utcnow() + timedelta(minutes=5)
    }
    print(f"\n>>> OTP for {data.phone} is: {otp} <<<\n")
    return {"message": "OTP sent to " + data.phone, "otp_preview": otp}


@router.post("/verify")
def verify_otp(data: VerifyOTPRequest, db: Session = Depends(get_db)):
    stored = otp_store.get(data.phone)
    if not stored:
        raise HTTPException(status_code=400, detail="OTP not sent. Call /api/otp/send first.")
    if datetime.utcnow() > stored["expires"]:
        del otp_store[data.phone]
        raise HTTPException(status_code=400, detail="OTP expired.")
    if stored["otp"] != data.otp:
        raise HTTPException(status_code=400, detail="Wrong OTP.")
    del otp_store[data.phone]
    user = db.query(User).filter(User.phone == data.phone).first()
    is_new = False
    if not user:
        user = User(name=data.name or "User", phone=data.phone,
                    city=data.city or "Lahore", password_hash=hash_password(data.phone))
        db.add(user)
        db.commit()
        db.refresh(user)
        is_new = True
    return {"access_token": create_token(user.id), "token_type": "bearer",
            "user_id": user.id, "name": user.name, "is_new_user": is_new}
