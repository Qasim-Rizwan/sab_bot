# Architecture Overview - Proxy-Based Tunneling

## System Architecture

### Complete Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                         Internet Users                        │
│           (Clients, Colleagues, Examiners, etc.)             │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             │ HTTPS
                             │ (Secure Connection)
                             │
              ┌──────────────▼──────────────┐
              │      ngrok Cloud Service     │
              │   https://abc123.ngrok.io   │
              │  (Public URL - Changes on   │
              │   each restart - Free tier) │
              └──────────────┬──────────────┘
                             │
                             │ HTTP
                             │ (Tunneled to localhost)
                             │
┌────────────────────────────┼────────────────────────────────┐
│ Your Local Machine         │                                │
│ (Windows/Linux/Mac)        │                                │
│                            │                                │
│              ┌─────────────▼─────────────┐                  │
│              │    Proxy Server (8080)    │                  │
│              │       (proxy.js)          │                  │
│              │                           │                  │
│              │  • Routes requests        │                  │
│              │  • Handles WebSockets     │                  │
│              │  • Error handling         │                  │
│              └─────────────┬─────────────┘                  │
│                            │                                │
│              ┌─────────────┴─────────────┐                  │
│              │                           │                  │
│      /api/* routes              All other routes            │
│              │                           │                  │
│              │                           │                  │
│    ┌─────────▼─────────┐       ┌────────▼────────┐         │
│    │  Backend (8000)   │       │ Frontend (3001) │         │
│    │                   │       │                 │         │
│    │  • FastAPI        │       │  • Next.js      │         │
│    │  • Python         │       │  • React        │         │
│    │  • LangChain      │       │  • TypeScript   │         │
│    │  • ChromaDB       │       │  • Tailwind CSS │         │
│    │  • OpenAI API     │       │  • Hot Reload   │         │
│    │                   │       │                 │         │
│    └─────────┬─────────┘       └────────┬────────┘         │
│              │                          │                   │
│              │                          │                   │
│    ┌─────────▼──────────────────────────▼────────┐         │
│    │         Local Resources & Data               │         │
│    │                                              │         │
│    │  • SQL Server Database (Windows Auth)       │         │
│    │  • Vector Embeddings (chroma_db/)           │         │
│    │  • Product Catalog (113K+ products)         │         │
│    │  • Configuration Files                       │         │
│    └──────────────────────────────────────────────┘         │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Request Flow Examples

### Example 1: Loading the Chat UI

```
User Browser
  ↓
  GET https://abc123.ngrok.io/
  ↓
ngrok Cloud
  ↓
  GET http://localhost:8080/
  ↓
Proxy (checks: does "/" start with "/api"? → NO)
  ↓
  GET http://localhost:3001/
  ↓
Frontend (Next.js serves HTML/CSS/JS)
  ↓
Response flows back through proxy → ngrok → user
```

### Example 2: Searching for Products

```
User enters: "sawblades 160mm"
  ↓
Frontend JavaScript sends:
  POST https://abc123.ngrok.io/api/chat
  Body: { message: "sawblades 160mm" }
  ↓
ngrok Cloud
  ↓
  POST http://localhost:8080/api/chat
  ↓
Proxy (checks: does "/api/chat" start with "/api"? → YES)
  ↓
  POST http://localhost:8000/api/chat
  ↓
Backend processes:
  1. LangChain receives message
  2. Searches ChromaDB vectors
  3. Calls OpenAI API
  4. Formats response
  ↓
Response: { results: [...], message: "..." }
  ↓
Flows back: Backend → Proxy → ngrok → Frontend → User
```

### Example 3: WebSocket Connection (Next.js HMR)

```
Frontend Dev Tools
  ↓
  WS https://abc123.ngrok.io/_next/webpack-hmr
  ↓
ngrok Cloud
  ↓
  WS http://localhost:8080/_next/webpack-hmr
  ↓
Proxy (upgrade event, not /api/* → frontend)
  ↓
  WS http://localhost:3001/_next/webpack-hmr
  ↓
Frontend HMR Server
  ↓
Live updates flow back for hot reloading
```

## Component Details

### Proxy Server (Port 8080)
**Technology**: Node.js + http-proxy
**Responsibilities**:
- Route HTTP requests based on path
- Handle WebSocket upgrades
- Provide unified entry point
- Error handling and logging

**Routing Logic**:
```javascript
if (request.url.startsWith('/api')) {
  forward to http://localhost:8000
} else {
  forward to http://localhost:3001
}
```

### Backend (Port 8000)
**Technology**: Python + FastAPI
**Endpoints**:
- `GET /` - Health check
- `POST /api/chat` - Chat with AI
- `GET /api/products` - Get product list
- `GET /docs` - API documentation

**Key Features**:
- LangChain integration
- Vector similarity search
- OpenAI GPT-4o-mini
- CORS enabled
- Real-time streaming responses

### Frontend (Port 3001)
**Technology**: Next.js + React + TypeScript
**Pages**:
- `/` - Chat interface
- `/_next/*` - Next.js internals
- `/api/*` - Proxied to backend

**Key Features**:
- Modern chat UI
- Real-time updates
- Responsive design
- Hot module replacement
- TypeScript safety

### ngrok (Public Tunnel)
**Type**: Secure tunnel service
**Features**:
- HTTPS by default
- Random subdomain (free tier)
- Traffic inspection
- Cross-platform

**Limitations (Free Tier)**:
- URL changes on restart
- 1 agent at a time (but multiple tunnels via config)
- Rate limiting
- Session timeout

## Port Allocation Strategy

| Port | Service  | Reason                                    |
|------|----------|-------------------------------------------|
| 8000 | Backend  | Standard for Python web services          |
| 3001 | Frontend | Avoids conflict with common port 3000     |
| 8080 | Proxy    | Standard for proxy services               |
| 5432 | Database | (If using PostgreSQL - not used here)    |

## Data Flow - Search Query Example

```
1. User Input
   "sawblades 160mm"
   
2. Frontend (React)
   → Validates input
   → Shows loading state
   → POST /api/chat
   
3. Proxy
   → Sees "/api/chat"
   → Routes to backend
   
4. Backend (FastAPI)
   → Receives request
   → Parses query
   
5. LangChain
   → Generates embedding
   → Queries ChromaDB
   
6. ChromaDB
   → Vector similarity search
   → Returns top matches
   
7. OpenAI API
   → Generates natural response
   → Formats results
   
8. Response Chain
   Backend → Proxy → ngrok → Frontend → User
   
9. Frontend Display
   → Renders results
   → Shows product cards
   → Enables user actions
```

## Deployment Scenarios

### Scenario 1: Local Development (Current Setup)
```
Developer Machine:
  Backend (8000) + Frontend (3001) + Proxy (8080)
  ↓
  ngrok http 8080
  ↓
  Share URL with team
```

### Scenario 2: Demo/Testing (Paid ngrok)
```
Server:
  Backend (8000) + Frontend (3001)
  ↓
  ngrok with custom domain
  ↓
  demo.yourcompany.com
```

### Scenario 3: Production (Not ngrok)
```
Server:
  Backend (8000) + Frontend (3001)
  ↓
  nginx reverse proxy
  ↓
  HTTPS + Custom Domain
  ↓
  www.yourcompany.com
```

## Security Considerations

### Current Setup (Development)
- ✅ ngrok provides HTTPS
- ✅ OpenAI API key on server-side only
- ⚠️  No authentication required
- ⚠️  Public URL accessible to anyone
- ⚠️  Database uses Windows Auth (no password)

### Production Recommendations
- 🔒 Add user authentication
- 🔒 API rate limiting
- 🔒 Input validation
- 🔒 SQL injection prevention
- 🔒 CORS restrictions
- 🔒 Environment variables for secrets
- 🔒 HTTPS with valid certificate
- 🔒 Firewall rules

## Performance Considerations

### Latency Breakdown (Typical)
```
User → ngrok:           50-150ms   (varies by location)
ngrok → Proxy:          <1ms       (local)
Proxy → Backend:        <1ms       (local)
Backend → Database:     10-50ms    (query complexity)
Backend → OpenAI:       500-2000ms (API call)
Response chain back:    50-150ms   (same as request)
──────────────────────────────────
Total:                  ~610-2351ms (mostly OpenAI)
```

### Optimization Strategies
1. **Caching**: Cache common queries
2. **Connection Pooling**: Reuse DB connections
3. **Async Processing**: Non-blocking I/O
4. **CDN**: Serve static assets
5. **Compression**: Gzip responses
6. **Vector Search**: Pre-computed embeddings

## Troubleshooting Flow

```
Problem: User can't access the app
  ↓
  Check 1: Is ngrok running?
    NO → Start ngrok http 8080
    YES ↓
  Check 2: Is proxy running?
    NO → Start proxy.bat / npm run proxy
    YES ↓
  Check 3: Is frontend running?
    NO → Start frontend.bat / ./frontend.sh
    YES ↓
  Check 4: Is backend running?
    NO → Start backend.bat / ./backend.sh
    YES ↓
  Check 5: Check logs for errors
    → Review terminal outputs
    → Check browser console
    → Inspect ngrok dashboard
```

## Monitoring & Logging

### What to Monitor
1. **Proxy Logs**: Request routing, errors
2. **Backend Logs**: API calls, database queries
3. **Frontend Logs**: Browser console, network tab
4. **ngrok Dashboard**: Traffic, response times
5. **System Resources**: CPU, memory, disk

### Key Metrics
- **Request Rate**: Requests per minute
- **Error Rate**: 4xx/5xx responses
- **Response Time**: P50, P95, P99
- **Token Usage**: OpenAI API costs
- **Database Queries**: Query time, count

---

## Summary

This architecture provides:
✅ **Simple deployment** - 3 services + 1 tunnel
✅ **Free tier friendly** - Only 1 ngrok tunnel needed
✅ **Development ready** - Hot reload, debugging tools
✅ **Scalable** - Can migrate to production setup
✅ **Maintainable** - Clear separation of concerns

The proxy approach is ideal for:
- 📊 Demos and presentations
- 👥 Team collaboration
- 🎓 Educational purposes
- 🧪 Testing with real users
- 🚀 MVP development

---

**Last Updated**: Dec 16, 2025









