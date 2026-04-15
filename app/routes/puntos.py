from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import random

from app.database import get_db
from app.models.punto import PuntoRecoleccion
from app.schemas import PuntoCreate, PuntoOut

router = APIRouter(prefix="/puntos", tags=["Puntos de Recolección"])


@router.post("", response_model=PuntoOut, status_code=201)
def crear_punto(datos: PuntoCreate, db: Session = Depends(get_db)):
    punto = PuntoRecoleccion(**datos.model_dump())
    db.add(punto)
    db.commit()
    db.refresh(punto)
    return punto


@router.get("", response_model=List[PuntoOut])
def listar_puntos(db: Session = Depends(get_db)):
    return db.query(PuntoRecoleccion).all()


@router.get("/{id_punto}", response_model=PuntoOut)
def obtener_punto(id_punto: int, db: Session = Depends(get_db)):
    punto = db.query(PuntoRecoleccion).filter(PuntoRecoleccion.id_punto == id_punto).first()
    if not punto:
        raise HTTPException(status_code=404, detail="Punto no encontrado")
    return punto


@router.delete("/{id_punto}", status_code=204)
def eliminar_punto(id_punto: int, db: Session = Depends(get_db)):
    punto = db.query(PuntoRecoleccion).filter(PuntoRecoleccion.id_punto == id_punto).first()
    if not punto:
        raise HTTPException(status_code=404, detail="Punto no encontrado")
    db.delete(punto)
    db.commit()


@router.post("/generar", status_code=201)
def generar_puntos_simulados(cantidad: int = 20, db: Session = Depends(get_db)):
    """Genera puntos aleatorios alrededor de Teziutlán para pruebas."""
    BASE_LAT = 19.817
    BASE_LON = -97.359

    for _ in range(cantidad):
        punto = PuntoRecoleccion(
            nombre_sector="Zona simulada",
            latitud=BASE_LAT + random.uniform(-0.02, 0.02),
            longitud=BASE_LON + random.uniform(-0.02, 0.02),
            volumen_estimado_kg=random.uniform(20, 100),
            tipo_residuo="organico",
        )
        db.add(punto)

    db.commit()
    return {"mensaje": f"{cantidad} puntos generados correctamente"}


@router.delete("/limpiar/todos", status_code=200)
def limpiar_puntos(db: Session = Depends(get_db)):
    """Elimina todos los puntos simulados (útil para pruebas)."""
    eliminados = db.query(PuntoRecoleccion).delete()
    db.commit()
    return {"mensaje": f"{eliminados} puntos eliminados"}