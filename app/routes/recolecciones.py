from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.biochar import Recoleccion, FACTOR_BIOCHAR
from app.models.ruta import RutaGenerada
from app.schemas import RecoleccionCreate, RecoleccionOut

router = APIRouter(prefix="/recolecciones", tags=["Recolecciones"])


def _enriquecer(r: Recoleccion) -> RecoleccionOut:
    """Añade el estimado de biochar al schema de salida."""
    item = RecoleccionOut.model_validate(r)
    item.biochar_estimado_kg = round(float(r.peso_captado_kg) * FACTOR_BIOCHAR, 2)
    return item


@router.post("", response_model=RecoleccionOut, status_code=status.HTTP_201_CREATED)
def registrar_recoleccion(datos: RecoleccionCreate, db: Session = Depends(get_db)):
    """Registra el resultado real de una recolección sobre una ruta confirmada."""
    ruta = db.query(RutaGenerada).filter(RutaGenerada.id_ruta == datos.id_ruta).first()
    if not ruta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ruta {datos.id_ruta} no encontrada",
        )

    recoleccion = Recoleccion(**datos.model_dump())
    db.add(recoleccion)
    db.commit()
    db.refresh(recoleccion)
    return _enriquecer(recoleccion)


@router.get("", response_model=List[RecoleccionOut])
def listar_recolecciones(db: Session = Depends(get_db)):
    recolecciones = (
        db.query(Recoleccion)
        .order_by(Recoleccion.fecha_recoleccion.desc())
        .all()
    )
    return [_enriquecer(r) for r in recolecciones]


@router.get("/{id_recoleccion}", response_model=RecoleccionOut)
def obtener_recoleccion(id_recoleccion: int, db: Session = Depends(get_db)):
    r = db.query(Recoleccion).filter(Recoleccion.id_recoleccion == id_recoleccion).first()
    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recolección no encontrada",
        )
    return _enriquecer(r)