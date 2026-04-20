from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from models.models import Booking, BookingStatus, Payment, User
from schemas.schemas import InitPaymentRequest, ConfirmPaymentRequest
from utils.auth import get_current_user
from datetime import datetime
import random, string

router = APIRouter()


def gen_txn():
    return 'TXN-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


@router.post("/initiate")
def initiate_payment(data: InitPaymentRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == data.booking_id, Booking.user_id == current_user.id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.is_paid:
        raise HTTPException(status_code=400, detail="Already paid")
    txn_id = gen_txn()
    payment = Payment(booking_id=booking.id, user_id=current_user.id, amount=booking.total_amount, method=data.payment_method, transaction_id=txn_id, status="pending")
    db.add(payment)
    db.commit()
    instructions = {
        "jazzcash":  f"Send Rs.{int(booking.total_amount)} to JazzCash: 03XX-XXXXXXX",
        "easypaisa": f"Send Rs.{int(booking.total_amount)} to EasyPaisa: 03XX-XXXXXXX",
        "card":      f"Pay Rs.{int(booking.total_amount)} via card",
    }
    return {"status": "pending", "txn_id": txn_id, "booking_ref": booking.booking_ref, "amount": booking.total_amount, "method": data.payment_method, "instruction": instructions.get(data.payment_method, "Pay manually")}


@router.post("/confirm")
def confirm_payment(data: ConfirmPaymentRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.booking_ref == data.booking_ref, Booking.user_id == current_user.id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    payment = db.query(Payment).filter(Payment.booking_id == booking.id).first()
    if payment:
        payment.status         = "completed"
        payment.transaction_id = data.transaction_id
    booking.is_paid = True
    booking.status  = BookingStatus.confirmed
    db.commit()
    return {"status": "success", "message": "Payment confirmed! Booking is now active.", "booking_ref": booking.booking_ref, "amount_paid": booking.total_amount}


@router.get("/history")
def payment_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payments = db.query(Payment).filter(Payment.user_id == current_user.id).all()
    return [{"id": p.id, "booking_id": p.booking_id, "amount": p.amount, "method": p.method, "transaction_id": p.transaction_id, "status": p.status, "created_at": str(p.created_at)} for p in payments]
