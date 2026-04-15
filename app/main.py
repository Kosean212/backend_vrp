from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base

# Importar todos los modelos para que SQLAlchemy los registre
import app.models.unidad
import app.models.punto
import app.models.ruta
import app.models.biochar

# Importar routers
from app.routes import unidades, puntos, vrp, recolecciones, biochar, reportes

app = FastAPI(
    title="API Biochar - Optimización de Rutas",
    description="Sistema de gestión de recolección de residuos orgánicos y producción de biochar",
    version="1.0.0",
)

# ─── CORS ────────────────────────────────────────────────────────────────────
# IMPORTANTE: el middleware debe registrarse ANTES de incluir los routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # En producción reemplaza con tu dominio frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── ROUTERS ─────────────────────────────────────────────────────────────────
app.include_router(unidades.router)
app.include_router(puntos.router)
app.include_router(vrp.router)
app.include_router(recolecciones.router)
app.include_router(biochar.router)
app.include_router(reportes.router)

# ─── CREAR TABLAS ────────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)


@app.get("/", tags=["Root"])
def root():
    return {"mensaje": "API Biochar funcionando 🚀", "docs": "/docs"}