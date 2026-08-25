@echo off
chcp 65001 >nul 2>&1
title CAE Frontend Server
cd /d "%~dp0"

echo ==========================================
echo   CAE Frontend Server
echo ==========================================
echo.

if not exist frontend (
    echo ERROR: frontend folder not found
    pause
    exit /b 1
)

cd frontend

echo Checking dependencies...
if not exist node_modules\vite (
    echo Vite not found, installing dependencies...
    echo This may take a few minutes...
    echo.
    npm install
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install packages
        echo Try running fix_frontend.bat first
        pause
        exit /b 1
    )
) else (
    echo Dependencies OK
)

echo.
echo ==========================================
echo   Frontend Server Starting...
echo   URL: http://127.0.0.1:5173/
echo ==========================================
echo.

npm run dev

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start server
    echo Try running fix_frontend.bat to reinstall dependencies
    pause
)
