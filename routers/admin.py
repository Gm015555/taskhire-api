from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from database.db import get_db
from models.models import User, Worker, Booking, Category, BookingStatus, Payment
from utils.auth import get_current_user, get_admin_user

router = APIRouter()


@router.post("/setup")
def setup_admin(phone: str, db: Session = Depends(get_db)):
    """Run this once to make yourself admin. No auth needed."""
    user = db.query(User).filter(User.phone == phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Register first at /api/auth/register")
    user.is_admin = True
    db.commit()
    return {"message": f"Success! {user.name} is now admin.", "user_id": user.id}


@router.get("/stats")
def dashboard_stats(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    return {
        "total_users":        db.query(func.count(User.id)).scalar(),
        "total_workers":      db.query(func.count(Worker.id)).scalar(),
        "total_bookings":     db.query(func.count(Booking.id)).scalar(),
        "total_revenue":      db.query(func.sum(Payment.amount)).filter(Payment.status == "completed").scalar() or 0,
        "pending_bookings":   db.query(func.count(Booking.id)).filter(Booking.status == BookingStatus.pending).scalar(),
        "confirmed_bookings": db.query(func.count(Booking.id)).filter(Booking.status == BookingStatus.confirmed).scalar(),
        "completed_bookings": db.query(func.count(Booking.id)).filter(Booking.status == BookingStatus.completed).scalar(),
        "available_workers":  db.query(func.count(Worker.id)).filter(Worker.is_available == True).scalar(),
        "verified_workers":   db.query(func.count(Worker.id)).filter(Worker.is_verified == True).scalar(),
        "total_categories":   db.query(func.count(Category.id)).scalar(),
    }


@router.get("/users")
def all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    users = db.query(User).offset(skip).limit(limit).all()
    return [{"id": u.id, "name": u.name, "phone": u.phone, "city": u.city, "is_active": u.is_active, "is_admin": u.is_admin, "bookings": len(u.bookings), "created_at": str(u.created_at)} for u in users]


@router.patch("/users/{user_id}/block")
def block_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = not user.is_active
    db.commit()
    return {"message": f"User {'unblocked' if user.is_active else 'blocked'} successfully"}


@router.get("/workers")
def all_workers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    workers = db.query(Worker).offset(skip).limit(limit).all()
    return [{"id": w.id, "name": w.user.name if w.user else None, "phone": w.user.phone if w.user else None, "category": w.category.name if w.category else None, "daily_rate": w.daily_rate, "city": w.city, "is_available": w.is_available, "is_verified": w.is_verified, "rating": w.rating, "total_jobs": w.total_jobs, "created_at": str(w.created_at)} for w in workers]


@router.patch("/workers/{worker_id}/verify")
def verify_worker(worker_id: int, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    w = db.query(Worker).filter(Worker.id == worker_id).first()
    if not w:
        raise HTTPException(status_code=404, detail="Worker not found")
    w.is_verified = not w.is_verified
    db.commit()
    return {"message": f"Worker {'verified' if w.is_verified else 'unverified'} successfully"}


@router.delete("/workers/{worker_id}")
def delete_worker(worker_id: int, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    w = db.query(Worker).filter(Worker.id == worker_id).first()
    if not w:
        raise HTTPException(status_code=404, detail="Worker not found")
    db.delete(w)
    db.commit()
    return {"message": "Worker deleted"}


@router.get("/bookings")
def all_bookings(status: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    q = db.query(Booking)
    if status:
        q = q.filter(Booking.status == status)
    bookings = q.order_by(Booking.created_at.desc()).offset(skip).limit(limit).all()
    return [{"id": b.id, "booking_ref": b.booking_ref, "user_name": b.user.name if b.user else None, "worker_name": b.worker.user.name if b.worker and b.worker.user else None, "category": b.worker.category.name if b.worker and b.worker.category else None, "booking_date": b.booking_date, "total_amount": b.total_amount, "status": b.status.value, "is_paid": b.is_paid, "created_at": str(b.created_at)} for b in bookings]


@router.patch("/bookings/{booking_id}/status")
def update_booking(booking_id: int, status: str, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    b = db.query(Booking).filter(Booking.id == booking_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")
    try:
        b.status = BookingStatus(status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status. Use: pending, confirmed, ongoing, completed, cancelled")
    db.commit()
    return {"message": f"Booking updated to {status}"}
