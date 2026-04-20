from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RegisterRequest(BaseModel):
    name:     str
    phone:    str
    password: str
    city:     Optional[str] = "Lahore"

class LoginRequest(BaseModel):
    phone:    str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user_id:      int
    name:         str
    class Config:
        orm_mode = True

class UserOut(BaseModel):
    id:         int
    name:       str
    phone:      str
    email:      Optional[str]
    city:       str
    is_active:  bool
    is_admin:   bool
    created_at: datetime
    class Config:
        orm_mode = True

class UserUpdateRequest(BaseModel):
    name:    Optional[str]
    email:   Optional[str]
    city:    Optional[str]
    address: Optional[str]

class SendOTPRequest(BaseModel):
    phone: str

class VerifyOTPRequest(BaseModel):
    phone: str
    otp:   str
    name:  Optional[str] = "User"
    city:  Optional[str] = "Lahore"

class CategoryOut(BaseModel):
    id:          int
    name:        str
    emoji:       str
    description: Optional[str]
    class Config:
        orm_mode = True

class WorkerRegisterRequest(BaseModel):
    category_id:      int
    bio:              Optional[str]
    experience_years: int
    daily_rate:       float
    half_day_rate:    Optional[float]
    city:             Optional[str] = "Lahore"
    skills:           Optional[str]
    id_card_number:   Optional[str]

class WorkerOut(BaseModel):
    id:               int
    user_id:          int
    category_id:      int
    bio:              Optional[str]
    experience_years: int
    daily_rate:       float
    half_day_rate:    Optional[float]
    city:             str
    is_available:     bool
    is_verified:      bool
    rating:           float
    total_reviews:    int
    total_jobs:       int
    skills:           Optional[str]
    worker_name:      Optional[str]
    category_name:    Optional[str]
    category_emoji:   Optional[str]
    class Config:
        orm_mode = True

class WorkerUpdateAvailability(BaseModel):
    is_available: bool
    latitude:     Optional[float]
    longitude:    Optional[float]

class BookingCreateRequest(BaseModel):
    worker_id:     int
    category_id:   int
    booking_date:  str
    start_time:    str
    duration_type: str
    duration_days: int
    total_amount:  float
    address:       Optional[str]
    note:          Optional[str]

class BookingOut(BaseModel):
    id:             int
    booking_ref:    str
    worker_id:      int
    category_id:    int
    booking_date:   str
    start_time:     str
    duration_type:  str
    duration_days:  int
    total_amount:   float
    status:         str
    is_paid:        bool
    address:        Optional[str]
    created_at:     datetime
    worker_name:    Optional[str]
    category_name:  Optional[str]
    category_emoji: Optional[str]
    class Config:
        orm_mode = True

class BookingStatusUpdate(BaseModel):
    status: str

class ReviewCreateRequest(BaseModel):
    booking_id: int
    worker_id:  int
    rating:     int
    comment:    Optional[str]

class ReviewOut(BaseModel):
    id:         int
    worker_id:  int
    rating:     int
    comment:    Optional[str]
    created_at: datetime
    class Config:
        orm_mode = True

class InitPaymentRequest(BaseModel):
    booking_id:     int
    payment_method: str
    phone:          str

class ConfirmPaymentRequest(BaseModel):
    booking_ref:    str
    transaction_id: str
    payment_method: str
