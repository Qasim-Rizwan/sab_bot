# Kyocera Unimerco — Product Finder

AI-powered product search assistant for industrial tools.

---

## 🚀 Quick Start Guide

### **Option 1: Start Everything (Recommended)**

Double-click **`START_APPLICATION.bat`**

This will:
- Install all dependencies automatically
- Start the backend server (Port 8000)
- Start the frontend application (Port 3000)
- Open in separate windows

Wait 10-15 seconds, then open your browser to: **http://localhost:3000**

---

### **Option 2: Start Individually**

If you want to run them separately:

1. **Backend Only**: Double-click `backend.bat`
2. **Frontend Only**: Double-click `frontend.bat`

---

## 📋 Requirements

### **Software**
- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Node.js 16+** - [Download](https://nodejs.org/)

### **Hardware**
- Minimum 8GB RAM (16GB recommended)
- 2GB free disk space
- Internet connection (for first-time setup)

---

## 🛠️ Installation

### **First Time Setup**

1. **Install Python**:
   - Download from https://www.python.org/
   - During installation, check ☑ "Add Python to PATH"

2. **Install Node.js**:
   - Download from https://nodejs.org/
   - Use the LTS version
   - Install with default settings

3. **Run the Application**:
   - Double-click `START_APPLICATION.bat`
   - Wait for dependencies to install (only needed once)
   - Servers will start automatically

---

## 📂 Project Structure

```
db_fahad/
├── backend/                 # Python FastAPI backend
│   ├── api/                # API endpoints
│   ├── services/           # LangChain, embeddings, LLM
│   ├── scripts/            # Data export, embedding generation
│   ├── main.py             # Backend entry point
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # Next.js React frontend
│   ├── components/         # React components
│   ├── pages/              # Next.js pages
│   ├── styles/             # CSS styles
│   └── package.json        # Node dependencies
│
├── START_APPLICATION.bat   # 🚀 Start everything
├── backend.bat             # Start backend only
└── frontend.bat            # Start frontend only
```

---

## 🎯 Features

- **Natural Language Search**: Ask in plain English (e.g., "sawblades 160mm")
- **Smart Recommendations**: Get suggestions for similar products
- **Rich Product Details**: View specifications, descriptions, and links
- **113K+ Products**: Comprehensive catalog
- **Multilingual Support**: English, Danish, Swedish, Norwegian, etc.
- **Real-time Responses**: Powered by OpenAI GPT-4o-mini

---

## 🔧 Configuration

### **Backend Configuration**

File: `backend/services/langchain_setup.py`

```python
# OpenAI API Key
openai_api_key = "your-api-key-here"

# Model settings
openai_model = "gpt-4o-mini"
openai_temperature = 0.2

# Site configuration
site_host = "https://www.kyocera-unimerco.com"
default_locale = "en-dk"
```

### **Frontend Configuration**

File: `frontend/pages/_app.tsx` or `.env.local`

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🌍 Sharing the Frontend with Others (ngrok, Ubuntu/Linux)

If you deploy this project on an **Ubuntu server** and want other people (client, colleagues, examiner) to see the chatbot, you need **3 terminals** with **1 ngrok agent** running **2 tunnels**:

1. **Backend tunnel** (port 8000) - so the frontend JavaScript can call the backend API from remote browsers
2. **Frontend tunnel** (port 3000) - so people can access the chatbot UI

**Note**: ngrok free tier allows only 1 agent session, so we use a config file to run both tunnels from a single agent.

### 1. Install ngrok (once, on Ubuntu)

```bash
# Example using snap (you can also use the .deb or direct binary)
sudo snap install ngrok

# Connect your ngrok account (token from ngrok dashboard)
ngrok config add-authtoken YOUR_NGROK_AUTHTOKEN_HERE
```

### 2. Start backend (Terminal 1, on Ubuntu)

From the project root:

```bash
./backend.sh
```

- Backend runs at `http://localhost:8000` (only accessible on the server).

### 3. Start both ngrok tunnels (Terminal 2, on Ubuntu)

From the project root (where `ngrok.yml` is located):

```bash
ngrok start --all
```

ngrok will show both tunnels:

```text
Forwarding  https://abc123.ngrok.io -> http://localhost:8000  (backend)
Forwarding  https://xyz789.ngrok.io -> http://localhost:3000  (frontend)
```

- **Copy the backend URL** (`https://abc123.ngrok.io`) - you'll need it for Terminal 3.
- **Share the frontend URL** (`https://xyz789.ngrok.io`) with anyone who should access the chatbot.

### 4. Start frontend with backend ngrok URL (Terminal 3, on Ubuntu)

In a third terminal, from the project root:

```bash
cd frontend
NEXT_PUBLIC_API_URL=https://abc123.ngrok.io npm run dev
```

**Important**: Replace `https://abc123.ngrok.io` with the actual backend URL from Terminal 2!

- Frontend runs at `http://localhost:3000` and will call the backend via the ngrok URL.

### 5. Stopping the demo

- Press **Ctrl+C** in all 3 terminals:
  - Terminal 1: Backend (`backend.sh`)
  - Terminal 2: Ngrok tunnels (`ngrok start --all`)
  - Terminal 3: Frontend (`npm run dev`)

Code, database, and embeddings remain on the server; only the running processes stop.

### Quick Reference (Windows)

On Windows, from the project root:

- **Terminal 1**: `backend.bat`
- **Terminal 2**: `C:\Users\qasim\Downloads\ngrok-v3-stable-windows-386\ngrok.exe start --all --config=ngrok.yml` (copy both URLs)
- **Terminal 3**: `cd frontend` then `set NEXT_PUBLIC_API_URL=https://YOUR_BACKEND_NGROK_URL && npm run dev`

---

## 🐛 Troubleshooting

### **Backend Issues**

**Problem**: `Python is not recognized`
- **Solution**: Reinstall Python and check "Add to PATH"

**Problem**: `Failed to install dependencies`
- **Solution**: Check internet connection, run `pip install -r backend/requirements.txt` manually

**Problem**: `Port 8000 already in use`
- **Solution**: Close other applications using port 8000, or change port in `backend.bat`

### **Frontend Issues**

**Problem**: `Node is not recognized`
- **Solution**: Reinstall Node.js with default settings

**Problem**: `npm install fails`
- **Solution**: Delete `frontend/node_modules` and `frontend/package-lock.json`, then run `frontend.bat` again

**Problem**: `Port 3000 already in use`
- **Solution**: Close other applications using port 3000

### **General Issues**

**Problem**: Servers start but page doesn't load
- **Solution**: Wait 15-20 seconds for initialization, then refresh browser

**Problem**: Chatbot gives errors
- **Solution**: Ensure backend is running (check backend window for errors)

---

## 📊 Performance Tips

1. **First Run**: Slower due to dependency installation (5-10 minutes)
2. **Subsequent Runs**: Much faster (10-15 seconds)
3. **Embedding Generation**: Already pre-generated in `backend/scripts/chroma_db`
4. **Token Usage**: Optimized for low token consumption with efficient embeddings

---

## 🔐 Security Notes

- OpenAI API key is hardcoded in `backend/services/langchain_setup.py`
- For production deployment, use environment variables
- Database credentials use Windows Authentication (no password needed)

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all requirements are installed
3. Check both terminal windows for error messages
4. Ensure ports 3000 and 8000 are available

---

## 🚦 Server Status

**Backend (Port 8000)**:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000

**Frontend (Port 3000)**:
- Application: http://localhost:3000

---

## 📝 Notes

- Keep both terminal windows open while using the application
- Close windows or press Ctrl+C to stop servers
- Data is stored locally in `backend/scripts/chroma_db`
- No internet required after initial setup (except for OpenAI API calls)

---

**Made with ❤️ for Kyocera Unimerco**

