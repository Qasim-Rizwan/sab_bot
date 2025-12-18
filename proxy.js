// proxy.js
// Combine frontend (Next.js) and backend (FastAPI) behind a single port.
// Usage:
//   npm install http-proxy
//   node proxy.js
//   ngrok http 8080   <-- tunnel the single public URL

const http = require('http');
const httpProxy = require('http-proxy');

const BACKEND_TARGET = process.env.BACKEND_URL || 'http://localhost:8000';
const FRONTEND_TARGET = process.env.FRONTEND_URL || 'http://localhost:3001';
const PROXY_PORT = parseInt(process.env.PROXY_PORT || '8080', 10);

const proxy = httpProxy.createProxyServer({
  changeOrigin: true,
  ws: true,
});

const routeRequest = (req, res) => {
  const isApi = req.url.startsWith('/api');
  const target = isApi ? BACKEND_TARGET : FRONTEND_TARGET;
  proxy.web(req, res, { target }, err => {
    console.error(`[proxy] HTTP error targeting ${target}:`, err?.message);
    if (!res.headersSent) {
      res.writeHead(502, { 'Content-Type': 'text/plain' });
    }
    res.end('Proxy error');
  });
};

const server = http.createServer(routeRequest);

// Handle websocket upgrades (required for Next.js HMR and dev tools)
server.on('upgrade', (req, socket, head) => {
  const isApi = req.url.startsWith('/api');
  const target = isApi ? BACKEND_TARGET : FRONTEND_TARGET;
  proxy.ws(req, socket, head, { target }, err => {
    console.error(`[proxy] WS error targeting ${target}:`, err?.message);
    socket.destroy();
  });
});

server.listen(PROXY_PORT, () => {
  console.log(`Proxy server running on port ${PROXY_PORT}`);
  console.log(`→ Forwarding /api/* → ${BACKEND_TARGET}`);
  console.log(`→ Forwarding everything else → ${FRONTEND_TARGET}`);
  console.log(`Run: ngrok http ${PROXY_PORT}`);
});


