from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from database.db import get_db
from models.models import Booking, Worker, Review, BookingStatus, User
from schemas.schemas import BookingCreateRequest, BookingOut, BookingStatusUpdate, ReviewCreateRequest, ReviewOut
from utils.auth import get_current_user
import random, string

router = APIRouter()


def gen_ref():
    today = datetime.now().strftime("%Y%m%d")
    rand  = ''.join(random.choices(string.digits, k=4))
    return f"TH-{today}-{rand}"


def build(b: Booking) -> dict:
    d = {c.name: getattr(b, c.name) for c in b.__table__.columns}
    d["status"]         = b.status.value
    d["worker_name"]    = b.worker.user.name      if b.worker and b.worker.user     else None
    d["category_name"]  = b.worker.category.name  if b.worker and b.worker.category else None
    d["category_emoji"] = b.worker.category.emoji if b.worker and b.worker.category else None
    return d


@router.post("/", response_model=BookingOut, status_code=201)
def create_booking(data: BookingCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    worker = db.query(Worker).filter(Worker.id == data.worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    if not worker.is_available:
        raise HTTPException(status_code=400, detail="Worker not available")
    b = Booking(booking_ref=gen_ref(), user_id=current_user.id, **data.dict())
    db.add(b)
    db.commit()
    db.refresh(b)
    return build(b)


@router.get("/my", response_model=List[BookingOut])
def my_bookings(status: Optional[str] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(Booking).filter(Booking.user_id == current_user.id)
    if status:
        q = q.filter(Booking.status == status)
    return [build(b) for b in q.order_by(Booking.created_at.desc()).all()]


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(booking_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    b = db.query(Booking).filter(Booking.id == booking_id, Booking.user_id == current_user.id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")
    return build(b)


@router.patch("/{booking_id}/status", response_model=BookingOut)
def update_status(booking_id: int, data: BookingStatusUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    b = db.query(Booking).filter(Booking.id == booking_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")
    is_owner  = b.user_id == current_user.id
    is_worker = b.worker and b.worker.user_id == current_user.id
    if not (is_owner or is_worker):
        raise HTTPException(status_code=403, detail="Not authorized")
    try:
        b.status = BookingStatus(data.status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status")
    if data.status == "completed" and b.worker:
        b.worker.total_jobs += 1
    db.commit()
    db.refresh(b)
    return build(b)


@router.post("/{booking_id}/review", response_model=ReviewOut, status_code=201)
def leave_review(booking_id: int, data: ReviewCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    b = db.query(Booking).filter(Booking.id == booking_id, Booking.user_id == current_user.id, Booking.status == BookingStatus.completed).first()
    if not b:
        raise HTTPException(status_code=404, detail="Completed booking not found")
    if b.review:
        raise HTTPException(status_code=400, detail="Review already submitted")
    if not (1 <= data.rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be 1 to 5")
    review = Review(booking_id=booking_id, worker_id=data.worker_id, user_id=current_user.id, rating=data.rating, comment=data.comment)
    db.add(review)
    worker = db.query(Worker).filter(Worker.id == data.worker_id).first()
    if worker:
        all_r = db.query(Review).filter(Review.worker_id == worker.id).all()
        worker.rating        = round((sum(r.rating for r in all_r) + data.rating) / (len(all_r) + 1), 1)
        worker.total_reviews = len(all_r) + 1
    db.commit()
    db.refresh(review)
    return review
