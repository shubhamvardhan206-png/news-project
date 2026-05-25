@echo off
cd /d C:\Users\SHUBHAM KUMAR\Desktop\news-project\newsproject
echo Running coverage tests...
python -m coverage run --source=. manage.py test
echo.
echo Generating coverage report...
python -m coverage report
echo.
echo Generating HTML coverage report...
python -m coverage html
echo.
echo Coverage report complete!
echo HTML report location: htmlcov\index.html
pause
