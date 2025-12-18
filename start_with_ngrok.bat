@echo off
TITLE Kyocera Unimerco - Start with Ngrok Tunneling
color 0E

echo ========================================
echo   KYOCERA UNIMERCO - NGROK SETUP
echo ========================================
echo.
echo This will start Backend, Frontend, and Ngrok tunnels
echo for sharing with others.
echo.
echo Requirements:
echo  - Backend must be running on port 8000
echo  - Frontend must be running on port 3000
echo  - Ngrok must be installed and configured
echo.
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed!
    pause
    exit /b 1
)

REM Check if ngrok exists (common locations)
set NGROK_PATH=
if exist "C:\Users\%USERNAME%\Downloads\ngrok-v3-stable-windows-386\ngrok.exe" (
    set NGROK_PATH=C:\Users\%USERNAME%\Downloads\ngrok-v3-stable-windows-386\ngrok.exe
) else if exist "C:\Program Files\ngrok\ngrok.exe" (
    set NGROK_PATH=C:\Program Files\ngrok\ngrok.exe
) else (
    echo [ERROR] Ngrok not found!
    echo Please install ngrok or update the path in this script.
    echo Expected locations:
    echo   C:\Users\%USERNAME%\Downloads\ngrok-v3-stable-windows-386\ngrok.exe
    echo   C:\Program Files\ngrok\ngrok.exe
    pause
    exit /b 1
)

echo [OK] Python installed:
python --version
echo.
echo [OK] Node.js installed:
node --version
echo.
echo [OK] Ngrok found: %NGROK_PATH%
echo.

echo ========================================
echo   IMPORTANT: 4 Terminal Setup
echo ========================================
echo.
echo You need to run these commands in 4 separate terminals:
echo.
echo TERMINAL 1 - Backend:
echo   cd %~dp0
echo   backend.bat
echo.
echo TERMINAL 2 - Backend Ngrok (for API):
echo   %NGROK_PATH% http 8000
echo   ^(Copy the https://...ngrok.io URL shown^)
echo.
echo TERMINAL 3 - Frontend ^(with backend ngrok URL^):
echo   cd %~dp0\frontend
echo   set NEXT_PUBLIC_API_URL=https://YOUR_BACKEND_NGROK_URL_HERE
echo   npm run dev
echo   ^(Replace YOUR_BACKEND_NGROK_URL_HERE with the URL from Terminal 2^)
echo.
echo TERMINAL 4 - Frontend Ngrok ^(for UI^):
echo   %NGROK_PATH% http 3000
echo   ^(Share this https://...ngrok.io URL with others^)
echo.
echo ========================================
echo.
echo Press any key to open Terminal 1 (Backend)...
pause >nul

REM Start Terminal 1 - Backend
start "Kyocera Backend" cmd /k "cd /d %~dp0 && backend.bat"

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   Terminal 1 opened! Backend starting...
echo ========================================
echo.
echo Now manually open 3 more terminals:
echo.
echo TERMINAL 2: Run this command:
echo   %NGROK_PATH% http 8000
echo.
echo TERMINAL 3: Run these commands:
echo   cd %~dp0\frontend
echo   set NEXT_PUBLIC_API_URL=https://YOUR_BACKEND_NGROK_URL
echo   npm run dev
echo.
echo TERMINAL 4: Run this command:
echo   %NGROK_PATH% http 3000
echo.
echo ========================================
echo.
pause

