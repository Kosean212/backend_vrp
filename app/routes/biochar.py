from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.biochar import LoteProduccion, Recoleccion
from app.schemas import LoteCreate, LoteOut

router = APIRouter(prefix="/biochar", tags=["Producción Biochar"])


@router.post("/lotes", response_model=LoteOut, status_code=201)
def registrar_lote(datos: LoteCreate, db: Session = Depends(get_db)):
    """Registra un lote de producción de biochar vinculado a una recolección."""
    recoleccion = db.query(Recoleccion).filter(
        Recoleccion.id_recoleccion == datos.id_recoleccion
    ).first()
    if not recoleccion:
        raise HTTPException(status_code=404, detail="Recolección no encontrada")

    # Calcular eficiencia real si no se proporciona
    if datos.eficiencia_real is None and recoleccion.peso_captado_kg:
        eficiencia = (float(datos.biochar_obtenido_kg) / float(recoleccion.peso_captado_kg)) * 100
        datos_dict = datos.model_dump()
        datos_dict["eficiencia_real"] = round(eficiencia, 2)
    else:
        datos_dict = datos.model_dump()

    lote = LoteProduccion(**datos_dict)
    db.add(lote)
    db.commit()
    db.refresh(lote)
    return lote


@router.get("/lotes", response_model=List[LoteOut])
def listar_lotes(db: Session = Depends(get_db)):
    return db.query(LoteProduccion).order_by(LoteProduccion.fecha_proceso.desc()).all()


@router.get("/lotes/{id_lote}", response_model=LoteOut)
def obtener_lote(id_lote: int, db: Session = Depends(get_db)):
    lote = db.query(LoteProduccion).filter(LoteProduccion.id_lote == id_lote).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    return lote