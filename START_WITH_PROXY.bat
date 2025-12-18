@echo off
TITLE Kyocera Unimerco - Starting All Services with Proxy
color 0A

echo ========================================
echo  Kyocera Unimerco - Starting All Services
echo ========================================
echo.
echo This will start:
echo   1. Backend (Port 8000)
echo   2. Frontend (Port 3001)
echo   3. Proxy Server (Port 8080)
echo.
echo After all services start, you can run:
echo   ngrok http 8080
echo.
echo Press any key to continue...
pause >nul

REM Start backend in new window
start "Backend - Port 8000" cmd /k backend.bat

REM Wait 5 seconds for backend to start
echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Start frontend in new window
start "Frontend - Port 3001" cmd /k frontend.bat

REM Wait 10 seconds for frontend to start
echo Waiting for frontend to start...
timeout /t 10 /nobreak >nul

REM Start proxy in new window
start "Proxy - Port 8080" cmd /k proxy.bat

echo.
echo ========================================
echo   All services started!
echo   Backend: http://localhost:8000
echo   Frontend: http://localhost:3001
echo   Proxy: http://localhost:8080
echo ========================================
echo.
echo To tunnel with ngrok, open a new terminal and run:
echo   ngrok http 8080
echo.
echo Or if you have the ngrok.yml config:
echo   ngrok start proxy
echo.
pause









