#!/usr/bin/env bash

# Kyocera Unimerco - Backend Server (Linux/Ubuntu)

set -e

echo "========================================"
echo "  Kyocera Unimerco - Backend Server"
echo "========================================"
echo

# Check Python
if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERROR] python3 is not installed or not in PATH!"
  echo "Please install Python 3.8+ (e.g. 'sudo apt install python3 python3-pip')."
  exit 1
fi

echo "[1/4] Checking Python installation..."
python3 --version
echo

echo "[2/4] Installing/Updating dependencies..."
cd backend
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
echo

echo "[3/4] Setting up environment variables..."
# Set OpenMP environment variable to avoid conflicts
export KMP_DUPLICATE_LIB_OK=TRUE
echo "Environment configured successfully."
echo

echo "[4/4] Starting backend server..."
echo
echo "========================================="
echo "  Backend is starting on port 8000"
echo "  API URL:  http://localhost:8000"
echo "  Docs:     http://localhost:8000/docs"
echo "========================================="
echo
echo "Press Ctrl+C to stop the server"
echo

python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload



