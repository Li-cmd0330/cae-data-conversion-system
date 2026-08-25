@echo off
chcp 65001 >nul 2>&1
title CAE System Launcher
cd /d "%~dp0"

echo ==========================================
echo   CAE Data Conversion System
echo ==========================================
echo.
echo Starting backend and frontend servers...
echo.
echo Backend:  http://127.0.0.1:8000/
echo Frontend: http://127.0.0.1:5173/
echo.
echo Two windows will open - DO NOT CLOSE THEM
echo.

start "CAE Backend" cmd /c "%~dp0backend_start.bat"
timeout /t 5 /nobreak >nul
start "CAE Frontend" cmd /c "%~dp0frontend_start.bat"

echo.
echo Servers are starting...
echo Wait for both windows to finish loading
echo Then open: http://127.0.0.1:5173/
echo.
echo Press any key to exit this launcher
echo (The servers will keep running)
echo.
pause >nul
