#!/usr/bin/env bash

# Kyocera Unimerco - Product Finder (Linux/Ubuntu)

set -e

echo "========================================="
echo "  KYOCERA UNIMERCO - PRODUCT FINDER"
echo "========================================="
echo
echo "This will start both Backend and Frontend servers"
echo "in separate terminal processes."
echo
echo "Requirements:"
echo "  - Python 3.8 or higher"
echo "  - Node.js 16 or higher"
echo "========================================="
echo

# Check Python
if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERROR] python3 is not installed!"
  echo "Please install Python 3.8+ (e.g. 'sudo apt install python3 python3-pip')."
  exit 1
fi

# Check Node.js
if ! command -v node >/dev/null 2>&1; then
  echo "[ERROR] Node.js is not installed!"
  echo "Please install Node.js 16+ (e.g. from https://nodejs.org or using nvm)."
  exit 1
fi

echo "[OK] Python installed:"
python3 --version
echo
echo "[OK] Node.js installed:"
node --version
echo

echo "========================================="
echo "  Starting Servers..."
echo "========================================="
echo

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[1/2] Starting Backend Server..."
(
  cd "$SCRIPT_DIR"
  bash backend.sh
) &

sleep 2

echo "[2/2] Starting Frontend Application..."
(
  cd "$SCRIPT_DIR"
  bash frontend.sh
) &

echo
echo "========================================="
echo "  SERVERS STARTED (launching in background)"
echo "========================================="
echo
echo "Backend API:   http://localhost:8000"
echo "Frontend UI:   http://localhost:3000"
echo
echo "Give it 10–20 seconds on first run, then open:"
echo "  http://localhost:3000"
echo
echo "To stop everything, press Ctrl+C in this terminal"
echo "or kill the backend/frontend processes."
echo

wait



