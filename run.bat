@echo off
REM Windows batch script to run Hyperlynx Backend API

echo.
echo ========================================
echo   Hyperlynx Backend API Server
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found!
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements if needed
echo Checking dependencies...
pip install -q -r requirements.txt

REM Run migrations
echo Running migrations...
python manage.py migrate --noinput

REM Start server
echo.
echo ========================================
echo   Starting server at http://localhost:8000
echo ========================================
echo.
echo Press CTRL+C to stop the server
echo.
python manage.py runserver

pause
