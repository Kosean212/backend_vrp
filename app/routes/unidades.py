from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.unidad import Unidad
from app.schemas import UnidadCreate, UnidadOut, UnidadEstadoUpdate

router = APIRouter(prefix="/unidades", tags=["Unidades"])


@router.post("", response_model=UnidadOut, status_code=status.HTTP_201_CREATED)
def crear_unidad(datos: UnidadCreate, db: Session = Depends(get_db)):
    """Registra una nueva unidad vehicular."""
    existente = db.query(Unidad).filter(Unidad.placas == datos.placas).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe una unidad con placas '{datos.placas}'",
        )
    nueva = Unidad(**datos.model_dump(), estado="disponible")
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


@router.get("", response_model=List[UnidadOut])
def listar_unidades(db: Session = Depends(get_db)):
    """Devuelve todas las unidades registradas."""
    return db.query(Unidad).order_by(Unidad.id_unidad).all()


@router.get("/{id_unidad}", response_model=UnidadOut)
def obtener_unidad(id_unidad: int, db: Session = Depends(get_db)):
    unidad = db.query(Unidad).filter(Unidad.id_unidad == id_unidad).first()
    if not unidad:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidad no encontrada")
    return unidad


@router.patch("/{id_unidad}/estado", response_model=UnidadOut)
def cambiar_estado(
    id_unidad: int,
    datos: UnidadEstadoUpdate,
    db: Session = Depends(get_db),
):
    """Actualiza el estado operativo de una unidad."""
    unidad = db.query(Unidad).filter(Unidad.id_unidad == id_unidad).first()
    if not unidad:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidad no encontrada")
    unidad.estado = datos.estado.value
    db.commit()
    db.refresh(unidad)
    return unidad


@router.delete("/{id_unidad}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_unidad(id_unidad: int, db: Session = Depends(get_db)):
    unidad = db.query(Unidad).filter(Unidad.id_unidad == id_unidad).first()
    if not unidad:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidad no encontrada")
    db.delete(unidad)
    db.commit()