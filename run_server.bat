@echo off
cd /d "%~dp0"
cd newsproject
echo.
echo ============================================
echo NewsPortal Development Server
echo ============================================
echo.
echo Starting server...
echo Visit: http://127.0.0.1:8000/
echo (Use HTTP, not HTTPS)
echo.
echo Press Ctrl+C to stop
echo ============================================
echo.
set DEBUG=True
start "" "http://127.0.0.1:8000/"
python manage.py runserver 127.0.0.1:8000
pause

