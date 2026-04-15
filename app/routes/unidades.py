from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.unidad import Unidad
from app.schemas import UnidadCreate, UnidadOut

router = APIRouter(prefix="/unidades", tags=["Unidades"])


@router.post("", response_model=UnidadOut, status_code=201)
def crear_unidad(datos: UnidadCreate, db: Session = Depends(get_db)):
    nueva = Unidad(**datos.model_dump(), estado="disponible")
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


@router.get("", response_model=List[UnidadOut])
def listar_unidades(db: Session = Depends(get_db)):
    return db.query(Unidad).all()


@router.get("/{id_unidad}", response_model=UnidadOut)
def obtener_unidad(id_unidad: int, db: Session = Depends(get_db)):
    unidad = db.query(Unidad).filter(Unidad.id_unidad == id_unidad).first()
    if not unidad:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")
    return unidad


@router.patch("/{id_unidad}/estado")
def cambiar_estado(id_unidad: int, estado: str, db: Session = Depends(get_db)):
    estados_validos = {"disponible", "en_ruta", "mantenimiento"}
    if estado not in estados_validos:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Usa: {estados_validos}")
    unidad = db.query(Unidad).filter(Unidad.id_unidad == id_unidad).first()
    if not unidad:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")
    unidad.estado = estado
    db.commit()
    return {"mensaje": f"Estado actualizado a '{estado}'"}


@router.delete("/{id_unidad}", status_code=204)
def eliminar_unidad(id_unidad: int, db: Session = Depends(get_db)):
    unidad = db.query(Unidad).filter(Unidad.id_unidad == id_unidad).first()
    if not unidad:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")
    db.delete(unidad)
    db.commit()