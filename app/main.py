from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.database import engine, Base

# Registrar todos los modelos antes de create_all
import app.models.unidad   # noqa: F401
import app.models.punto    # noqa: F401
import app.models.ruta     # noqa: F401
import app.models.biochar  # noqa: F401

from app.routes import unidades, puntos, vrp, recolecciones, biochar, reportes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Crea tablas al iniciar; libera recursos al cerrar."""
    logger.info("Iniciando API Biochar — creando tablas si no existen...")
    Base.metadata.create_all(bind=engine)
    yield
    logger.info("API Biochar apagándose.")


app = FastAPI(
    title="API Biochar — Optimización de Rutas",
    description=(
        "Sistema de gestión de recolección de residuos orgánicos "
        "y producción de biochar para Teziutlán, Puebla."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
# En producción: reemplaza "*" con el dominio real del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── ROUTERS ──────────────────────────────────────────────────────────────────
app.include_router(unidades.router)
app.include_router(puntos.router)
app.include_router(vrp.router)
app.include_router(recolecciones.router)
app.include_router(biochar.router)
app.include_router(reportes.router)


@app.get("/", tags=["Root"])
def root():
    return {
        "mensaje": "API Biochar funcionando 🚀",
        "version": "2.0.0",
        "docs":    "/docs",
        "redoc":   "/redoc",
    }


@app.get("/health", tags=["Root"])
def health():
    """Health-check para load balancers / Docker."""
    return {"status": "ok"}