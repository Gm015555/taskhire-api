from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.db import Base
import enum


class BookingStatus(str, enum.Enum):
    pending   = "pending"
    confirmed = "confirmed"
    ongoing   = "ongoing"
    completed = "completed"
    cancelled = "cancelled"


class User(Base):
    __tablename__ = "users"
    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String(100), nullable=False)
    phone         = Column(String(20), unique=True, nullable=False, index=True)
    email         = Column(String(100), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    city          = Column(String(100), default="Lahore")
    address       = Column(Text, nullable=True)
    is_active     = Column(Boolean, default=True)
    is_admin      = Column(Boolean, default=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    bookings      = relationship("Booking", back_populates="user", foreign_keys="Booking.user_id")
    worker_profile = relationship("Worker", back_populates="user", uselist=False)


class Category(Base):
    __tablename__ = "categories"
    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), unique=True, nullable=False)
    emoji       = Column(String(10), default="🔧")
    description = Column(Text, nullable=True)
    is_active   = Column(Boolean, default=True)
    workers     = relationship("Worker", back_populates="category")


class Worker(Base):
    __tablename__ = "workers"
    id               = Column(Integer, primary_key=True, index=True)
    user_id          = Column(Integer, ForeignKey("users.id"), unique=True)
    category_id      = Column(Integer, ForeignKey("categories.id"))
    bio              = Column(Text, nullable=True)
    experience_years = Column(Integer, default=1)
    daily_rate       = Column(Float, nullable=False)
    half_day_rate    = Column(Float, nullable=True)
    city             = Column(String(100), default="Lahore")
    latitude         = Column(Float, nullable=True)
    longitude        = Column(Float, nullable=True)
    is_available     = Column(Boolean, default=True)
    is_verified      = Column(Boolean, default=False)
    rating           = Column(Float, default=0.0)
    total_reviews    = Column(Integer, default=0)
    total_jobs       = Column(Integer, default=0)
    skills           = Column(Text, nullable=True)
    id_card_number   = Column(String(20), nullable=True)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    user             = relationship("User", back_populates="worker_profile")
    category         = relationship("Category", back_populates="workers")
    bookings         = relationship("Booking", back_populates="worker")
    reviews          = relationship("Review", back_populates="worker")


class Booking(Base):
    __tablename__ = "bookings"
    id            = Column(Integer, primary_key=True, index=True)
    booking_ref   = Column(String(30), unique=True, nullable=False)
    user_id       = Column(Integer, ForeignKey("users.id"))
    worker_id     = Column(Integer, ForeignKey("workers.id"))
    category_id   = Column(Integer, ForeignKey("categories.id"))
    booking_date  = Column(String(20), nullable=False)
    start_time    = Column(String(10), nullable=False)
    duration_type = Column(String(20), default="full_day")
    duration_days = Column(Integer, default=1)
    total_amount  = Column(Float, nullable=False)
    status        = Column(Enum(BookingStatus), default=BookingStatus.pending)
    address       = Column(Text, nullable=True)
    note          = Column(Text, nullable=True)
    is_paid       = Column(Boolean, default=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    user          = relationship("User", back_populates="bookings", foreign_keys=[user_id])
    worker        = relationship("Worker", back_populates="bookings")
    review        = relationship("Review", back_populates="booking", uselist=False)


class Review(Base):
    __tablename__ = "reviews"
    id         = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), unique=True)
    worker_id  = Column(Integer, ForeignKey("workers.id"))
    user_id    = Column(Integer, ForeignKey("users.id"))
    rating     = Column(Integer, nullable=False)
    comment    = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    worker     = relationship("Worker", back_populates="reviews")
    booking    = relationship("Booking", back_populates="review")


class Payment(Base):
    __tablename__ = "payments"
    id             = Column(Integer, primary_key=True, index=True)
    booking_id     = Column(Integer, ForeignKey("bookings.id"))
    user_id        = Column(Integer, ForeignKey("users.id"))
    amount         = Column(Float, nullable=False)
    method         = Column(String(20), nullable=False)
    transaction_id = Column(String(100), nullable=True)
    status         = Column(String(20), default="pending")
    created_at     = Column(DateTime(timezone=True), server_default=func.now())
