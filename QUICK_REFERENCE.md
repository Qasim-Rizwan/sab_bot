# Quick Reference Guide - Proxy Tunneling Setup

## 🚀 Fastest Way to Start

### Windows
```bash
# Double-click this file:
START_WITH_PROXY.bat

# Then open new terminal and run:
ngrok http 8080
```

### Linux/Ubuntu
```bash
# Terminal 1: Backend
./backend.sh

# Terminal 2: Frontend  
./frontend.sh

# Terminal 3: Proxy
npm install && npm run proxy

# Terminal 4: Tunnel
ngrok http 8080
```

---

## 📋 Port Reference

| Service    | Port | URL                      | Access        |
|------------|------|--------------------------|---------------|
| Backend    | 8000 | http://localhost:8000    | Local only    |
| Frontend   | 3001 | http://localhost:3001    | Local only    |
| **Proxy**  | 8080 | http://localhost:8080    | **Use this!** |
| ngrok      | -    | https://abc123.ngrok.io  | Public        |

---

## 🔄 Request Flow

```
User Browser
    ↓
ngrok (https://abc123.ngrok.io)
    ↓
Proxy (localhost:8080)
    ↓
    ├── /api/* → Backend (localhost:8000)
    └── /* → Frontend (localhost:3001)
```

---

## ✅ Startup Checklist

- [ ] 1. Start Backend (port 8000)
- [ ] 2. Start Frontend (port 3001)
- [ ] 3. Start Proxy (port 8080)
- [ ] 4. Start ngrok tunnel (port 8080)
- [ ] 5. Test locally: http://localhost:8080
- [ ] 6. Share ngrok URL with others

---

## 🎯 Key Files

| File                    | Purpose                           |
|-------------------------|-----------------------------------|
| `proxy.js`              | Proxy server implementation       |
| `START_WITH_PROXY.bat`  | Start all services (Windows)      |
| `proxy.bat`             | Start proxy only (Windows)        |
| `package.json`          | Proxy dependencies                |
| `ngrok.yml`             | ngrok tunnel configuration        |
| `PROXY_SETUP.md`        | Full setup guide                  |

---

## 🐛 Quick Troubleshooting

| Problem                  | Solution                              |
|--------------------------|---------------------------------------|
| 502 Proxy Error          | Start backend and frontend first      |
| Port 8080 in use         | Close other apps or change port       |
| ngrok tunnel but no API  | Use relative URLs (`/api/...`)        |
| Frontend not loading     | Wait 10-15s, then refresh             |

---

## 💡 Pro Tips

1. **Always start in order**: Backend → Frontend → Proxy → ngrok
2. **Test locally first**: Visit http://localhost:8080 before using ngrok
3. **Check terminal logs**: Each service shows helpful error messages
4. **ngrok URLs expire**: Restart ngrok = new URL
5. **Free tier limits**: 1 ngrok agent = multiple tunnels via config file

---

## 🔧 Environment Variables

```bash
# Windows
set BACKEND_URL=http://localhost:8000
set FRONTEND_URL=http://localhost:3001
set PROXY_PORT=8080

# Linux/Mac
export BACKEND_URL=http://localhost:8000
export FRONTEND_URL=http://localhost:3001
export PROXY_PORT=8080
```

---

## 📱 Sharing with Others

1. Start all services (backend, frontend, proxy)
2. Run: `ngrok http 8080`
3. Copy the HTTPS URL: `https://abc123.ngrok.io`
4. Share with anyone!
5. They access both frontend and backend through one URL

---

## 🛑 Stopping Services

### Windows
Press `Ctrl+C` in each terminal window

### Linux
Press `Ctrl+C` in each terminal, or:
```bash
pkill -f "python.*main.py"  # Backend
pkill -f "next dev"         # Frontend
pkill -f "node proxy.js"    # Proxy
pkill -f "ngrok"            # ngrok
```

---

## 📚 More Help

- **Full Setup Guide**: See `PROXY_SETUP.md`
- **Client Guide**: See `README_CLIENT.md`
- **Changes Log**: See `CHANGES_SUMMARY.md`

---

**Need more help?** Check the main documentation files or contact support.









