"""
Main FastAPI application entry point
"""
import os
# Fix OpenMP library conflict (safe workaround for multiple OpenMP runtimes)
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import chat, health

app = FastAPI(
    title="Product Search Chatbot API",
    description="Embeddings-based product search using LangChain, ChromaDB, and OpenAI",
    version="1.0.0"
)

# CORS middleware for frontend (allow all origins so ngrok + remote browsers can call the API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For demo/exam: allow all origins (including ngrok URLs)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.get("/")
async def root():
    return {
        "message": "Product Search Chatbot API",
        "docs": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

