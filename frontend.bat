@echo off
TITLE Kyocera Unimerco - Frontend Application
color 0B

echo ========================================
echo  Kyocera Unimerco - Frontend Application
echo ========================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH!
    echo Please install Node.js 16 or higher from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo [1/4] Checking Node.js installation...
node --version
npm --version
echo.

echo [2/4] Installing/Updating dependencies...
cd frontend
call npm install
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install dependencies!
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)
echo.

echo [3/4] Building Next.js application...
echo This may take a moment on first run...
echo.

echo [4/4] Starting frontend development server...
echo.
echo ========================================
echo   Frontend is starting on port 3000
echo   URL: http://localhost:3000
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the development server
call npm run dev

REM If server stops
echo.
echo Frontend server stopped.
pause

