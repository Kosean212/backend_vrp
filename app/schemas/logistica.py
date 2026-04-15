from pydantic import BaseModel
from typing import List
from datetime import date

class RutaBase(BaseModel):
    id_unidad: int
    distancia_total_km: float
    puntos_orden: List[int] # Lista de IDs de puntos en orden

class RespuestaVRP(BaseModel):
    fecha: date
    rutas: List[RutaBase]