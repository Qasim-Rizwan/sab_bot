@echo off
TITLE Kyocera Unimerco - Backend Server
color 0A

echo ========================================
echo   Kyocera Unimerco - Backend Server
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.8 or higher from https://www.python.org/
    echo.
    pause
    exit /b 1
)

echo [1/4] Checking Python installation...
python --version
echo.

echo [2/4] Installing/Updating dependencies...
cd backend

python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install dependencies!
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)
echo.

echo [3/4] Setting up environment variables...
REM Set OpenMP environment variable to avoid conflicts
set KMP_DUPLICATE_LIB_OK=TRUE
echo Environment configured successfully.
echo.

echo [4/4] Starting backend server...
echo.
echo ========================================
echo   Backend is starting on port 8000
echo   API URL: http://localhost:8000
echo   Docs: http://localhost:8000/docs
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

REM If server stops
echo.
echo Backend server stopped.
pause

