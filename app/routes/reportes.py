from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.biochar import Recoleccion, LoteProduccion
from app.models.ruta import RutaGenerada
from app.schemas import ReporteOperativo

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/operativo", response_model=ReporteOperativo)
def reporte_operativo(db: Session = Depends(get_db)):
    """
    Resumen ejecutivo: totales de recolección, biochar estimado,
    distancia acumulada y costo total.
    """
    # Recolecciones
    total_recolecciones = db.query(func.count(Recoleccion.id_recoleccion)).scalar() or 0
    total_peso          = db.query(func.sum(Recoleccion.peso_captado_kg)).scalar() or 0.0
    biochar_estimado    = float(total_peso) * 0.30

    # Rutas
    total_distancia = db.query(func.sum(RutaGenerada.distancia_total_km)).scalar() or 0.0
    costo_total     = db.query(func.sum(RutaGenerada.costo_estimado)).scalar() or 0.0

    # Eficiencia real de lotes
    eficiencia_prom = db.query(func.avg(LoteProduccion.eficiencia_real)).scalar()

    return ReporteOperativo(
        total_recolecciones=total_recolecciones,
        total_peso_kg=round(float(total_peso), 2),
        total_biochar_estimado_kg=round(biochar_estimado, 2),
        total_distancia_km=round(float(total_distancia), 2),
        costo_total=round(float(costo_total), 2),
        eficiencia_promedio_pct=round(float(eficiencia_prom), 2) if eficiencia_prom else None,
    )


@router.get("/proyeccion-biochar")
def proyeccion_biochar(db: Session = Depends(get_db)):
    """
    Equivalente a la vista SQL vista_proyeccion_biochar, 
    pero calculada en Python para mayor flexibilidad.
    """
    from app.models.ruta import RutaGenerada
    from app.models.unidad import Unidad

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
            "id_recoleccion": r.id_recoleccion,
            "id_ruta": r.id_ruta,
            "fecha_recoleccion": r.fecha_recoleccion,
            "peso_captado_kg": float(r.peso_captado_kg),
            "biochar_estimado_kg": round(float(r.peso_captado_kg) * 0.30, 2),
            "unidad": r.placas,
        }
        for r in rows
    ]