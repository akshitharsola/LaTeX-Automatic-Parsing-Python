"""
FastAPI DOCX Analyzer - Main Application
Advanced document processing with native Python DOCX support
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn

from app.routers import document, latex

# Create FastAPI application
app = FastAPI(
    title="DOCX Analyzer API",
    description="Advanced document processing system with native DOCX support",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(document.router, prefix="/api/document", tags=["document"])
app.include_router(latex.router, prefix="/api/latex", tags=["latex"])

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "docx-analyzer", "version": "2.0.0"}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "DOCX Analyzer API",
        "version": "2.0.0",
        "features": [
            "Native DOCX processing with docx2python",
            "Advanced list detection using Word styles",
            "Smart section analysis with context awareness",
            "LaTeX generation for IEEE/ACM/Springer templates",
            "High-performance async I/O operations"
        ],
        "endpoints": {
            "docs": "/api/docs",
            "health": "/api/health",
            "upload": "/api/document/upload",
            "analyze": "/api/document/analyze",
            "latex": "/api/latex/generate"
        }
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )