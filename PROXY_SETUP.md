# Proxy Server Setup for ngrok Tunneling

This guide explains how to use the proxy server to share your application with others using a single ngrok tunnel.

## Why Use a Proxy?

ngrok's free tier only allows 1 tunnel at a time. By using a proxy server, we can:
- Combine frontend (port 3001) and backend (port 8000) behind a single port (8080)
- Tunnel only port 8080 with ngrok
- Share a single public URL that provides access to both frontend and backend

## Quick Start (Windows)

### Option A: Start Everything at Once
1. Double-click **`START_WITH_PROXY.bat`**
2. Wait for all 3 services to start (30-45 seconds)
3. Open a new terminal and run:
   ```
   ngrok http 8080
   ```
4. Share the ngrok URL with others!

### Option B: Start Services Individually
Open 3 separate terminals:

**Terminal 1 - Backend:**
```
backend.bat
```

**Terminal 2 - Frontend:**
```
frontend.bat
```

**Terminal 3 - Proxy:**
```
proxy.bat
```

**Terminal 4 - ngrok:**
```
ngrok http 8080
```

## Quick Start (Linux/Ubuntu)

Open 4 separate terminals:

**Terminal 1 - Backend:**
```bash
./backend.sh
```

**Terminal 2 - Frontend:**
```bash
./frontend.sh
```

**Terminal 3 - Proxy:**
```bash
# Install dependencies (first time only)
npm install

# Start proxy
npm run proxy
```

**Terminal 4 - ngrok:**
```bash
ngrok http 8080
```

## How It Works

The proxy server (`proxy.js`) routes incoming requests:

```
Client Request → Proxy (8080) → Backend (8000)  [if /api/*]
                              → Frontend (3001) [everything else]
```

### Request Routing
- **`/api/*`** → Backend at `http://localhost:8000`
- **Everything else** → Frontend at `http://localhost:3001`

### WebSocket Support
The proxy also handles WebSocket connections for:
- Next.js Hot Module Replacement (HMR)
- Real-time features

## Configuration

You can customize the proxy by setting environment variables:

```bash
# Windows
set BACKEND_URL=http://localhost:8000
set FRONTEND_URL=http://localhost:3001
set PROXY_PORT=8080
npm run proxy

# Linux/Mac
BACKEND_URL=http://localhost:8000 FRONTEND_URL=http://localhost:3001 PROXY_PORT=8080 npm run proxy
```

## Using ngrok

### Method 1: Direct Tunnel (Simple)
```bash
ngrok http 8080
```

You'll see:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8080
```

Share `https://abc123.ngrok.io` with others!

### Method 2: Using ngrok.yml (Multiple Tunnels)
```bash
# Start specific tunnel
ngrok start proxy

# Or start all tunnels (backend, frontend, proxy)
ngrok start --all
```

## Troubleshooting

### "502 Proxy error" in browser
- **Cause**: Backend or frontend not running
- **Solution**: Make sure both backend and frontend are started before starting the proxy

### "ECONNREFUSED" error in proxy logs
- **Cause**: Backend (8000) or frontend (3001) not accessible
- **Solution**: Check that both services are running and accessible

### Port 8080 already in use
- **Cause**: Another application is using port 8080
- **Solution**: 
  - Close the other application, or
  - Change proxy port: `set PROXY_PORT=8081 && npm run proxy`

### ngrok tunnel works but API calls fail
- **Cause**: Frontend trying to call backend at localhost instead of through proxy
- **Solution**: Make sure frontend API calls use relative URLs (`/api/...`) not absolute URLs

## Testing the Setup

1. **Test locally first:**
   - Open `http://localhost:8080` in your browser
   - Verify the chatbot loads and works correctly

2. **Test with ngrok:**
   - Start ngrok: `ngrok http 8080`
   - Open the ngrok URL in your browser
   - Test the chatbot functionality
   - Check the proxy and backend logs for any errors

## Architecture Diagram

```
┌─────────────────────────────────────────────┐
│           Users / Clients                   │
│     (anywhere on the internet)              │
└───────────────────┬─────────────────────────┘
                    │
                    │ HTTPS
                    │
         ┌──────────▼──────────┐
         │   ngrok Tunnel      │
         │   (abc123.ngrok.io) │
         └──────────┬──────────┘
                    │
                    │ HTTP
                    │
         ┌──────────▼──────────┐
         │   Proxy Server      │
         │   (Port 8080)       │
         └──────────┬──────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        │ /api/*                │ /*
        │                       │
┌───────▼────────┐    ┌────────▼────────┐
│   Backend      │    │   Frontend      │
│  (Port 8000)   │    │  (Port 3001)    │
│   FastAPI      │    │   Next.js       │
└────────────────┘    └─────────────────┘
```

## Security Notes

- ngrok URLs are public by default - anyone with the URL can access your app
- Don't share ngrok URLs with untrusted parties
- ngrok free tier URLs expire when you restart ngrok
- For production deployment, use a proper reverse proxy (nginx, Apache) and domain

## Advanced: Multiple Proxies

If you need to run multiple instances:

```bash
# Instance 1
BACKEND_URL=http://localhost:8000 FRONTEND_URL=http://localhost:3001 PROXY_PORT=8080 npm run proxy

# Instance 2
BACKEND_URL=http://localhost:9000 FRONTEND_URL=http://localhost:4001 PROXY_PORT=9080 npm run proxy
```

## Files Reference

- **`proxy.js`** - Proxy server implementation
- **`proxy.bat`** - Windows batch file to start proxy
- **`START_WITH_PROXY.bat`** - Start all services (Windows)
- **`package.json`** - Proxy dependencies and scripts
- **`ngrok.yml`** - ngrok tunnel configuration

---

**Need help?** Check the main README_CLIENT.md for more troubleshooting tips.









