@echo off
chcp 65001 >nul 2>&1
title CAE Backend Server
cd /d "%~dp0"

echo ==========================================
echo   CAE Backend Server
echo ==========================================
echo.

if not exist backend (
    echo ERROR: backend folder not found
    pause
    exit /b 1
)

cd backend

if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        echo Please make sure Python is installed
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing Python packages...
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo.
echo Setting up database...
if not exist apps\materials\migrations mkdir apps\materials\migrations
echo.> apps\materials\migrations\__init__.py
python manage.py makemigrations materials
python manage.py migrate

echo.
echo ==========================================
echo   Backend Server Starting...
echo   URL: http://127.0.0.1:8000/
echo ==========================================
echo.

python manage.py runserver 127.0.0.1:8000
