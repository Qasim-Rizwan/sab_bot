@echo off
TITLE Kyocera Unimerco - Proxy Server
color 0E

echo ========================================
echo  Kyocera Unimerco - Proxy Server
echo ========================================
echo.
echo This proxy combines frontend and backend
echo behind a single port for ngrok tunneling.
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH!
    echo Please install Node.js from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo [1/3] Checking Node.js installation...
node --version
echo.

echo [2/3] Installing proxy dependencies...
call npm install
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install dependencies!
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)
echo.

echo [3/3] Starting proxy server...
echo.
echo ========================================
echo   Proxy server starting on port 8080
echo   Routes:
echo   - /api/* ^-^> http://localhost:8000
echo   - /* ^-^> http://localhost:3001
echo ========================================
echo.
echo IMPORTANT: Make sure backend (8000) and 
echo frontend (3001) are running first!
echo.
echo After proxy starts, run in another terminal:
echo   ngrok http 8080
echo.
echo Press Ctrl+C to stop the proxy server
echo.

REM Start the proxy server
call npm run proxy

REM If server stops
echo.
echo Proxy server stopped.
pause









