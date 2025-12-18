#!/bin/bash

# Kyocera Unimerco - Start with Ngrok Tunneling (Linux/Ubuntu)
# This script provides instructions for setting up ngrok tunneling

echo "========================================"
echo "   KYOCERA UNIMERCO - NGROK SETUP"
echo "========================================"
echo ""
echo "This will help you set up Backend, Frontend, and Ngrok tunnels"
echo "for sharing with others."
echo ""
echo "Requirements:"
echo "  - Backend must be running on port 8000"
echo "  - Frontend must be running on port 3000"
echo "  - Ngrok must be installed and configured"
echo ""
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed!"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js is not installed!"
    exit 1
fi

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "[ERROR] Ngrok is not installed!"
    echo "Install with: sudo snap install ngrok"
    echo "Or download from: https://ngrok.com/download"
    exit 1
fi

echo "[OK] Python installed:"
python3 --version
echo ""
echo "[OK] Node.js installed:"
node --version
echo ""
echo "[OK] Ngrok installed:"
ngrok version
echo ""

echo "========================================"
echo "   IMPORTANT: 4 Terminal Setup"
echo "========================================"
echo ""
echo "You need to run these commands in 4 separate terminals:"
echo ""
echo "TERMINAL 1 - Backend:"
echo "  cd $(pwd)"
echo "  ./backend.sh"
echo ""
echo "TERMINAL 2 - Backend Ngrok (for API):"
echo "  ngrok http 8000"
echo "  (Copy the https://...ngrok.io URL shown)"
echo ""
echo "TERMINAL 3 - Frontend (with backend ngrok URL):"
echo "  cd $(pwd)/frontend"
echo "  NEXT_PUBLIC_API_URL=https://YOUR_BACKEND_NGROK_URL_HERE npm run dev"
echo "  (Replace YOUR_BACKEND_NGROK_URL_HERE with the URL from Terminal 2)"
echo ""
echo "TERMINAL 4 - Frontend Ngrok (for UI):"
echo "  ngrok http 3000"
echo "  (Share this https://...ngrok.io URL with others)"
echo ""
echo "========================================"
echo ""
echo "Press Enter to continue..."
read

echo ""
echo "Opening Terminal 1 (Backend) in background..."
echo ""

# Start backend in background (optional - user can also do manually)
# gnome-terminal -- bash -c "cd $(pwd) && ./backend.sh; exec bash" 2>/dev/null || \
# xterm -e "cd $(pwd) && ./backend.sh" 2>/dev/null || \
# echo "Please manually open Terminal 1 and run: ./backend.sh"

echo ""
echo "========================================"
echo "   Setup Instructions"
echo "========================================"
echo ""
echo "Now manually open 3 more terminals:"
echo ""
echo "TERMINAL 2: Run this command:"
echo "  ngrok http 8000"
echo ""
echo "TERMINAL 3: Run these commands:"
echo "  cd $(pwd)/frontend"
echo "  NEXT_PUBLIC_API_URL=https://YOUR_BACKEND_NGROK_URL npm run dev"
echo ""
echo "TERMINAL 4: Run this command:"
echo "  ngrok http 3000"
echo ""
echo "========================================"
echo ""

