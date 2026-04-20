from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database.db import get_db
from models.models import Worker, Category
from schemas.schemas import WorkerOut, WorkerRegisterRequest, WorkerUpdateAvailability
from utils.auth import get_current_user
from models.models import User

router = APIRouter()


def build(w: Worker) -> dict:
    d = {c.name: getattr(w, c.name) for c in w.__table__.columns}
    d["worker_name"]    = w.user.name     if w.user     else None
    d["category_name"]  = w.category.name  if w.category else None
    d["category_emoji"] = w.category.emoji if w.category else None
    return d


@router.get("/", response_model=List[WorkerOut])
def list_workers(
    category_id:  Optional[int]  = None,
    city:         Optional[str]  = None,
    is_available: Optional[bool] = None,
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db)
):
    q = db.query(Worker)
    if category_id:              q = q.filter(Worker.category_id == category_id)
    if city:                     q = q.filter(Worker.city.ilike(f"%{city}%"))
    if is_available is not None: q = q.filter(Worker.is_available == is_available)
    return [build(w) for w in q.offset(skip).limit(limit).all()]


@router.get("/{worker_id}", response_model=WorkerOut)
def get_worker(worker_id: int, db: Session = Depends(get_db)):
    w = db.query(Worker).filter(Worker.id == worker_id).first()
    if not w:
        raise HTTPException(status_code=404, detail="Worker not found")
    return build(w)


@router.post("/register", response_model=WorkerOut, status_code=201)
def register_worker(data: WorkerRegisterRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if db.query(Worker).filter(Worker.user_id == current_user.id).first():
        raise HTTPException(status_code=400, detail="Already registered as worker")
    if not db.query(Category).filter(Category.id == data.category_id).first():
        raise HTTPException(status_code=404, detail="Category not found")
    w = Worker(user_id=current_user.id, **data.dict())
    db.add(w)
    db.commit()
    db.refresh(w)
    return build(w)


@router.patch("/{worker_id}/availability", response_model=WorkerOut)
def update_availability(worker_id: int, data: WorkerUpdateAvailability, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    w = db.query(Worker).filter(Worker.id == worker_id, Worker.user_id == current_user.id).first()
    if not w:
        raise HTTPException(status_code=404, detail="Worker not found")
    w.is_available = data.is_available
    if data.latitude:  w.latitude  = data.latitude
    if data.longitude: w.longitude = data.longitude
    db.commit()
    db.refresh(w)
    return build(w)
