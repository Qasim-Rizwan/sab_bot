@echo off
TITLE Kyocera Unimerco - Product Finder
color 0E

echo ========================================
echo   KYOCERA UNIMERCO - PRODUCT FINDER
echo ========================================
echo.
echo This will start both Backend and Frontend servers
echo in separate windows.
echo.
echo Requirements:
echo  - Python 3.8 or higher
echo  - Node.js 16 or higher
echo.
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Please install Python from https://www.python.org/
    echo.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed!
    echo Please install Node.js from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo [OK] Python installed: 
python --version
echo.
echo [OK] Node.js installed: 
node --version
echo.

echo ========================================
echo   Starting Servers...
echo ========================================
echo.

echo [1/2] Starting Backend Server...
start "Kyocera Backend" cmd /k backend.bat
timeout /t 2 /nobreak >nul

echo [2/2] Starting Frontend Application...
start "Kyocera Frontend" cmd /k frontend.bat

echo.
echo ========================================
echo   SERVERS STARTED!
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:3000
echo.
echo Two windows have been opened:
echo  1. Backend Server (Port 8000)
echo  2. Frontend Application (Port 3000)
echo.
echo Wait 10-15 seconds for both servers to start,
echo then open your browser to:
echo.
echo   http://localhost:3000
echo.
echo To stop: Close both terminal windows or press Ctrl+C
echo.
pause

