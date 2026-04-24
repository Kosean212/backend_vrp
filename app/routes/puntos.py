from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
import random

from app.database import get_db
from app.models.punto import PuntoRecoleccion
from app.models.ruta import RutaPunto   # FIX: needed for FK cleanup
from app.schemas import PuntoCreate, PuntoOut

router = APIRouter(prefix="/puntos", tags=["Puntos de Recolección"])

BASE_LAT = 19.817
BASE_LON = -97.359


@router.post("", response_model=PuntoOut, status_code=status.HTTP_201_CREATED)
def crear_punto(datos: PuntoCreate, db: Session = Depends(get_db)):
    punto = PuntoRecoleccion(**datos.model_dump())
    db.add(punto)
    db.commit()
    db.refresh(punto)
    return punto


@router.get("", response_model=List[PuntoOut])
def listar_puntos(
    tipo: str | None = Query(None, description="Filtrar por tipo_residuo"),
    db: Session = Depends(get_db),
):
    q = db.query(PuntoRecoleccion)
    if tipo:
        q = q.filter(PuntoRecoleccion.tipo_residuo == tipo)
    return q.order_by(PuntoRecoleccion.id_punto).all()


@router.get("/{id_punto}", response_model=PuntoOut)
def obtener_punto(id_punto: int, db: Session = Depends(get_db)):
    punto = db.query(PuntoRecoleccion).filter(PuntoRecoleccion.id_punto == id_punto).first()
    if not punto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Punto no encontrado")
    return punto


@router.put("/{id_punto}", response_model=PuntoOut)
def actualizar_punto(id_punto: int, datos: PuntoCreate, db: Session = Depends(get_db)):
    punto = db.query(PuntoRecoleccion).filter(PuntoRecoleccion.id_punto == id_punto).first()
    if not punto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Punto no encontrado")
    for campo, valor in datos.model_dump().items():
        setattr(punto, campo, valor)
    db.commit()
    db.refresh(punto)
    return punto


@router.delete("/{id_punto}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_punto(id_punto: int, db: Session = Depends(get_db)):
    punto = db.query(PuntoRecoleccion).filter(PuntoRecoleccion.id_punto == id_punto).first()
    if not punto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Punto no encontrado")

    # FIX: borrar referencias en ruta_punto antes de eliminar el punto (FK RESTRICT)
    db.query(RutaPunto).filter(RutaPunto.id_punto == id_punto).delete(synchronize_session=False)
    db.delete(punto)
    db.commit()


@router.post("/seed/generar", status_code=status.HTTP_201_CREATED)
def generar_puntos_simulados(
    cantidad: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Genera puntos aleatorios alrededor de Teziutlán para pruebas."""
    for i in range(cantidad):
        punto = PuntoRecoleccion(
            nombre_sector=f"Zona simulada #{i + 1}",
            latitud=BASE_LAT  + random.uniform(-0.03, 0.03),
            longitud=BASE_LON + random.uniform(-0.03, 0.03),
            volumen_estimado_kg=round(random.uniform(20, 150), 2),
            tipo_residuo="organico",
        )
        db.add(punto)
    db.commit()
    return {"mensaje": f"{cantidad} puntos generados correctamente", "total": cantidad}


@router.delete("/seed/limpiar", status_code=status.HTTP_200_OK)
def limpiar_puntos(db: Session = Depends(get_db)):
    """Elimina todos los puntos y sus referencias en ruta_punto."""
    # FIX: borrar FK dependientes primero, luego los puntos
    db.query(RutaPunto).delete(synchronize_session=False)
    eliminados = db.query(PuntoRecoleccion).delete(synchronize_session=False)
    db.commit()
    return {"mensaje": f"{eliminados} puntos eliminados"}