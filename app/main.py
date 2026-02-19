from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import excel
from datetime import datetime
import time

app = FastAPI(
    title="Bento Excel Service",
    description="Microservicio para procesamiento de archivos Excel",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

startup_time = time.time()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(excel.router, prefix="/api/excel", tags=["excel"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Bento Excel Service",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/health")
async def health_check():
    """Health check detallado con información de uptime"""
    uptime_seconds = time.time() - startup_time
    return {
        "status": "healthy",
        "service": "bento-excel-service",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": round(uptime_seconds, 2),
        "supabase_configured": bool(settings.supabase_url),
        "environment": settings.app_env if hasattr(settings, 'app_env') else "unknown",
    }
