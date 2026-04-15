from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime

# ─── UNIDADES ───────────────────────────────────────────────
class UnidadCreate(BaseModel):
    placas: str
    modelo: Optional[str] = None
    capacidad_max_kg: float
    rendimiento_km_l: float


class UnidadOut(BaseModel):
    id_unidad: int
    placas: str
    modelo: Optional[str]
    capacidad_max_kg: float
    rendimiento_km_l: float
    estado: str

    class Config:
        from_attributes = True


# ─── PUNTOS DE RECOLECCIÓN ──────────────────────────────────
class PuntoCreate(BaseModel):
    nombre_sector: str
    latitud: float
    longitud: float
    volumen_estimado_kg: float
    tipo_residuo: Optional[str] = "organico"

class PuntoOut(BaseModel):
    id_punto: int
    nombre_sector: Optional[str]
    latitud: float
    longitud: float
    volumen_estimado_kg: Optional[float]
    tipo_residuo: Optional[str]

    class Config:
        from_attributes = True


# ─── VRP / RUTAS ────────────────────────────────────────────
class PuntoEnRuta(BaseModel):
    id: int
    lat: float
    lon: float
    nombre: Optional[str]

class RutaVRP(BaseModel):
    id_unidad: int
    placas: str
    puntos: List[PuntoEnRuta]
    distancia_total_km: float
    tiempo_total_min: int
    costo_estimado: float

class RespuestaVRP(BaseModel):
    rutas: List[RutaVRP]

# Schema para confirmar y guardar rutas
class RutaConfirmar(BaseModel):
    id_unidad: int
    distancia_total_km: float
    tiempo_total_min: int
    costo_estimado: float
    puntos_orden: List[int]   # Lista de id_punto en orden

class ConfirmarRutas(BaseModel):
    fecha: date
    rutas: List[RutaConfirmar]


# ─── RECOLECCIONES ──────────────────────────────────────────
class RecoleccionCreate(BaseModel):
    id_ruta: int
    peso_captado_kg: float
    tiempo_empleado_min: Optional[int] = None
    consumo_combustible_l: Optional[float] = None
    costo_operativo: Optional[float] = None
    porcentaje_capacidad_utilizada: Optional[float] = None

class RecoleccionOut(BaseModel):
    id_recoleccion: int
    id_ruta: int
    fecha_recoleccion: Optional[datetime]
    peso_captado_kg: float
    tiempo_empleado_min: Optional[int]
    consumo_combustible_l: Optional[float]
    costo_operativo: Optional[float]
    porcentaje_capacidad_utilizada: Optional[float]
    biochar_estimado_kg: Optional[float] = None  # 30% del peso

    class Config:
        from_attributes = True


# ─── LOTES BIOCHAR ──────────────────────────────────────────
class LoteCreate(BaseModel):
    id_recoleccion: int
    temperatura_proceso: float
    tiempo_proceso_min: int
    biochar_obtenido_kg: float
    eficiencia_real: Optional[float] = None

class LoteOut(BaseModel):
    id_lote: int
    id_recoleccion: int
    fecha_proceso: Optional[datetime]
    temperatura_proceso: Optional[float]
    tiempo_proceso_min: Optional[int]
    biochar_obtenido_kg: Optional[float]
    eficiencia_real: Optional[float]

    class Config:
        from_attributes = True


# ─── REPORTES ───────────────────────────────────────────────
class ReporteOperativo(BaseModel):
    total_recolecciones: int
    total_peso_kg: float
    total_biochar_estimado_kg: float
    total_distancia_km: float
    costo_total: float
    eficiencia_promedio_pct: Optional[float]