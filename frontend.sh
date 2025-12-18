#!/usr/bin/env bash

# Kyocera Unimerco - Frontend Application (Linux/Ubuntu)

set -e

echo "========================================="
echo "  Kyocera Unimerco - Frontend Application"
echo "========================================="
echo

# Check Node.js
if ! command -v node >/dev/null 2>&1; then
  echo "[ERROR] Node.js is not installed or not in PATH!"
  echo "Please install Node.js 16+ (e.g. from https://nodejs.org or 'nvm')."
  exit 1
fi

echo "[1/4] Checking Node.js installation..."
node --version
npm --version
echo

echo "[2/4] Installing/Updating dependencies..."
cd frontend
npm install
echo

echo "[3/4] Building Next.js application (dev env)..."
echo "This may take a moment on first run..."
echo

echo "[4/4] Starting frontend development server..."
echo
echo "========================================="
echo "  Frontend is starting on port 3000"
echo "  URL: http://localhost:3000"
echo "========================================="
echo
echo "Press Ctrl+C to stop the server"
echo

npm run dev



