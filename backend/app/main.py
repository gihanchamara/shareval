from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.core.config import APP_NAME, API_V1_PREFIX, FRONTEND_DIR
from backend.app.api.v1.router import api_v1_router

app = FastAPI(
    title=APP_NAME,
    version="1.0.0",
    description="Fair valuation service for equities and options with pluggable market data and spec-driven knowledge base.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for decoupled frontends (React / Angular / Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 API endpoints
app.include_router(api_v1_router, prefix=API_V1_PREFIX)

# Health endpoint
@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": APP_NAME,
        "version": "1.0.0"
    }

# Serve Thin UI statically if frontend directory exists
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        index_path = FRONTEND_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"message": "Frontend index.html not found. Check /docs for API."}
