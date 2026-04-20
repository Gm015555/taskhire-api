@echo off
echo ========================================
echo    TaskHire API Server - Starting...
echo ========================================
echo.

echo Installing required packages...
pip install fastapi==0.95.2 uvicorn==0.22.0 sqlalchemy==1.4.41 pydantic==1.10.21 python-jose[cryptography]==3.3.0 passlib==1.7.4 bcrypt==3.2.2 python-multipart==0.0.6

echo.
echo Starting TaskHire server...
echo.
echo API Docs will open at: http://127.0.0.1:8000/docs
echo Admin Dashboard:       Open TaskHire_Admin.html in Chrome
echo.
echo Press CTRL+C to stop the server
echo.

python -m uvicorn main:app --reload

pause
