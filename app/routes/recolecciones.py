from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.biochar import Recoleccion
from app.models.ruta import RutaGenerada
from app.schemas import RecoleccionCreate, RecoleccionOut

router = APIRouter(prefix="/recolecciones", tags=["Recolecciones"])


@router.post("", response_model=RecoleccionOut, status_code=201)
def registrar_recoleccion(datos: RecoleccionCreate, db: Session = Depends(get_db)):
    """Registra el resultado real de una recolección sobre una ruta confirmada."""
    ruta = db.query(RutaGenerada).filter(RutaGenerada.id_ruta == datos.id_ruta).first()
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")

    recoleccion = Recoleccion(**datos.model_dump())
    db.add(recoleccion)
    db.commit()
    db.refresh(recoleccion)

    # Añadir proyección de biochar al response
    result = RecoleccionOut.model_validate(recoleccion)
    result.biochar_estimado_kg = round(float(recoleccion.peso_captado_kg) * 0.30, 2)
    return result


@router.get("", response_model=List[RecoleccionOut])
def listar_recolecciones(db: Session = Depends(get_db)):
    recolecciones = db.query(Recoleccion).order_by(Recoleccion.fecha_recoleccion.desc()).all()
    resultado = []
    for r in recolecciones:
        item = RecoleccionOut.model_validate(r)
        item.biochar_estimado_kg = round(float(r.peso_captado_kg) * 0.30, 2)
        resultado.append(item)
    return resultado


@router.get("/{id_recoleccion}", response_model=RecoleccionOut)
def obtener_recoleccion(id_recoleccion: int, db: Session = Depends(get_db)):
    r = db.query(Recoleccion).filter(Recoleccion.id_recoleccion == id_recoleccion).first()
    if not r:
        raise HTTPException(status_code=404, detail="Recolección no encontrada")
    item = RecoleccionOut.model_validate(r)
    item.biochar_estimado_kg = round(float(r.peso_captado_kg) * 0.30, 2)
    return item