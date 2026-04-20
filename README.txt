========================================
   TASKHIRE - SETUP INSTRUCTIONS
========================================

STEP 1 - START THE SERVER
--------------------------
Double-click START.bat
OR open Anaconda Prompt and run:
  cd C:\Users\Ghulam Muhammad\Desktop\TaskHire
  python -m uvicorn main:app --reload

STEP 2 - OPEN API DOCS
-----------------------
Open Chrome and go to:
  http://127.0.0.1:8000/docs

STEP 3 - REGISTER YOUR ACCOUNT
--------------------------------
Go to /api/auth/register and create account with:
  phone: 03001234567
  password: test1234

STEP 4 - MAKE YOURSELF ADMIN
------------------------------
Open Chrome and go to:
  http://127.0.0.1:8000/api/admin/setup?phone=03001234567
Change the method to POST and click Execute.

STEP 5 - OPEN ADMIN DASHBOARD
-------------------------------
Open TaskHire_Admin.html in Chrome
Login with your phone and password.

========================================
   API ENDPOINTS SUMMARY
========================================

Auth:       /api/auth/register  /api/auth/login
OTP Login:  /api/otp/send       /api/otp/verify
Users:      /api/users/me
Workers:    /api/workers/
Bookings:   /api/bookings/
Categories: /api/categories/
Payments:   /api/payments/initiate  /api/payments/confirm
Admin:      /api/admin/stats  /api/admin/workers  /api/admin/bookings

========================================
   PROJECT STRUCTURE
========================================

TaskHire/
├── main.py              <- App entry point
├── START.bat            <- Double-click to start
├── requirements.txt     <- All packages
├── taskhire.db          <- Database (auto created)
├── TaskHire_Admin.html  <- Admin dashboard
├── database/db.py       <- Database connection
├── models/models.py     <- All tables
├── schemas/schemas.py   <- Request/response formats
├── utils/auth.py        <- Login and tokens
└── routers/
    ├── auth.py          <- Register and login
    ├── otp.py           <- OTP phone login
    ├── users.py         <- User profile
    ├── workers.py       <- Worker management
    ├── bookings.py      <- Booking system
    ├── categories.py    <- Service categories
    ├── payments.py      <- JazzCash EasyPaisa
    └── admin.py         <- Admin dashboard API
