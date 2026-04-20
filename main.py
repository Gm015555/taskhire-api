from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.db import engine, Base
from routers import auth, otp, users, workers, bookings, categories, payments, admin

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TaskHire API",
    description="Pakistan's #1 Daily Labour Hire Platform",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,       prefix="/api/auth",       tags=["1 - Auth"])
app.include_router(otp.router,        prefix="/api/otp",        tags=["2 - OTP Login"])
app.include_router(users.router,      prefix="/api/users",      tags=["3 - Users"])
app.include_router(workers.router,    prefix="/api/workers",    tags=["4 - Workers"])
app.include_router(bookings.router,   prefix="/api/bookings",   tags=["5 - Bookings"])
app.include_router(categories.router, prefix="/api/categories", tags=["6 - Categories"])
app.include_router(payments.router,   prefix="/api/payments",   tags=["7 - Payments"])
app.include_router(admin.router,      prefix="/api/admin",      tags=["8 - Admin"])


@app.get("/")
def root():
    return {
        "app":     "TaskHire",
        "version": "3.0.0",
        "status":  "running",
        "docs":    "http://127.0.0.1:8000/docs",
        "setup_admin": "POST http://127.0.0.1:8000/api/admin/setup?phone=YOUR_PHONE"
    }
