from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database.db import get_db
from models.models import Category
from schemas.schemas import CategoryOut

router = APIRouter()

DEFAULTS = [
    {"name": "Mechanic",       "emoji": "🔧", "description": "Auto and bike mechanics"},
    {"name": "Driver",         "emoji": "🚗", "description": "Car, van and truck drivers"},
    {"name": "Plumber",        "emoji": "🔩", "description": "Pipe and water work"},
    {"name": "Electrician",    "emoji": "⚡", "description": "Wiring, solar and appliances"},
    {"name": "Cleaner",        "emoji": "🧹", "description": "Home and office cleaning"},
    {"name": "Painter",        "emoji": "🎨", "description": "Interior and exterior painting"},
    {"name": "Labour",         "emoji": "👷", "description": "General daily labour"},
    {"name": "Gardener",       "emoji": "🌿", "description": "Lawn and garden care"},
    {"name": "Cook",           "emoji": "👨‍🍳", "description": "Home cooking and catering"},
    {"name": "Carpenter",      "emoji": "🪚", "description": "Furniture and woodwork"},
    {"name": "AC Technician",  "emoji": "❄️", "description": "AC service and repair"},
    {"name": "Security Guard", "emoji": "💂", "description": "Day and night security"},
]


@router.get("/", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    cats = db.query(Category).filter(Category.is_active == True).all()
    if not cats:
        for c in DEFAULTS:
            db.add(Category(**c))
        db.commit()
        cats = db.query(Category).all()
    return cats


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat
