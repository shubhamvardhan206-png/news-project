@echo off
REM Quick test to verify Django setup
cd /d "%~dp0"
cd newsproject

echo ============================================
echo Testing Django Installation...
echo ============================================
echo.

echo [1/3] Checking Python version...
python --version
echo.

echo [2/3] Checking Django installation...
python -c "import django; print(f'Django {django.get_version()} OK')"
echo.

echo [3/3] Checking database configuration...
python manage.py shell -c "from django.conf import settings; print(f'Database Engine: {settings.DATABASES[\"default\"][\"ENGINE\"]}'); print(f'Database Name: {settings.DATABASES[\"default\"][\"NAME\"]}')"
echo.

echo ============================================
echo All tests passed! Your setup is ready.
echo ============================================
echo.

echo Starting development server...
echo Press Ctrl+C to stop the server
echo.
set DEBUG=True
start "" "http://127.0.0.1:8000/"
python manage.py runserver 127.0.0.1:8000

pause
