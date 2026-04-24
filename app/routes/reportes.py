from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.biochar import Recoleccion, LoteProduccion, FACTOR_BIOCHAR
from app.models.ruta import RutaGenerada
from app.models.unidad import Unidad
from app.schemas import ReporteOperativo

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/operativo", response_model=ReporteOperativo)
def reporte_operativo(db: Session = Depends(get_db)):
    """
    Resumen ejecutivo: totales de recolección, biochar estimado,
    distancia acumulada y costo total.
    """
    total_recolecciones = db.query(func.count(Recoleccion.id_recoleccion)).scalar() or 0
    total_peso          = float(db.query(func.sum(Recoleccion.peso_captado_kg)).scalar() or 0)
    biochar_estimado    = total_peso * FACTOR_BIOCHAR

    total_distancia = float(db.query(func.sum(RutaGenerada.distancia_total_km)).scalar() or 0)
    costo_total     = float(db.query(func.sum(RutaGenerada.costo_estimado)).scalar() or 0)

    eficiencia_prom_raw = db.query(func.avg(LoteProduccion.eficiencia_real)).scalar()
    eficiencia_prom = round(float(eficiencia_prom_raw), 2) if eficiencia_prom_raw else None

    return ReporteOperativo(
        total_recolecciones=total_recolecciones,
        total_peso_kg=round(total_peso, 2),
        total_biochar_estimado_kg=round(biochar_estimado, 2),
        total_distancia_km=round(total_distancia, 2),
        costo_total=round(costo_total, 2),
        eficiencia_promedio_pct=eficiencia_prom,
    )


@router.get("/proyeccion-biochar")
def proyeccion_biochar(db: Session = Depends(get_db)):
    """
    Equivalente a la vista SQL vista_proyeccion_biochar,
    calculada en Python para mayor flexibilidad.
    """
    rows = (
        db.query(
            Recoleccion.id_recoleccion,
            RutaGenerada.id_ruta,
            Recoleccion.fecha_recoleccion,
            Recoleccion.peso_captado_kg,
            Unidad.placas,
        )
        .join(RutaGenerada, Recoleccion.id_ruta == RutaGenerada.id_ruta)
        .join(Unidad, RutaGenerada.id_unidad == Unidad.id_unidad)
        .order_by(Recoleccion.fecha_recoleccion.desc())
        .all()
    )

    return [
        {
            "id_recoleccion":     row.id_recoleccion,
            "id_ruta":            row.id_ruta,
            "fecha_recoleccion":  row.fecha_recoleccion,
            "peso_captado_kg":    float(row.peso_captado_kg),
            "biochar_estimado_kg": round(float(row.peso_captado_kg) * FACTOR_BIOCHAR, 2),
            "unidad":             row.placas,
        }
        for row in rows
    ]