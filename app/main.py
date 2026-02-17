from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import excel

app = FastAPI(
    title="Bento Excel Service",
    description="Microservicio para procesamiento de archivos Excel",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

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
    }


@app.get("/health")
async def health_check():
    """Health check detallado"""
    return {
        "status": "healthy",
        "service": "bento-excel-service",
        "version": "1.0.0",
        "supabase_configured": bool(settings.supabase_url),
    }
