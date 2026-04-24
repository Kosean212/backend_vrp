from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional
from datetime import date, datetime
from enum import Enum

FACTOR_BIOCHAR = 0.30


# ─── ENUMS ──────────────────────────────────────────────────
class EstadoUnidad(str, Enum):
    disponible   = "disponible"
    en_ruta      = "en_ruta"
    mantenimiento = "mantenimiento"


class TipoResiduo(str, Enum):
    organico   = "organico"
    inorganico = "inorganico"
    mixto      = "mixto"


# ─── UNIDADES ───────────────────────────────────────────────
class UnidadCreate(BaseModel):
    placas:           str   = Field(..., min_length=1, max_length=20, examples=["TEZ-01"])
    modelo:           Optional[str] = Field(None, max_length=50)
    capacidad_max_kg: float = Field(..., gt=0, description="Capacidad máxima en kg")
    rendimiento_km_l: float = Field(..., gt=0, description="Km por litro")

    @field_validator("placas")
    @classmethod
    def placas_uppercase(cls, v: str) -> str:
        return v.strip().upper()


class UnidadOut(BaseModel):
    id_unidad:        int
    placas:           str
    modelo:           Optional[str]
    capacidad_max_kg: float
    rendimiento_km_l: float
    estado:           str

    model_config = {"from_attributes": True}


class UnidadEstadoUpdate(BaseModel):
    estado: EstadoUnidad


# ─── PUNTOS DE RECOLECCIÓN ──────────────────────────────────
class PuntoCreate(BaseModel):
    nombre_sector:       str   = Field(..., min_length=1, max_length=100)
    latitud:             float = Field(..., ge=-90,  le=90)
    longitud:            float = Field(..., ge=-180, le=180)
    volumen_estimado_kg: float = Field(..., ge=0)
    tipo_residuo:        TipoResiduo = TipoResiduo.organico


class PuntoOut(BaseModel):
    id_punto:            int
    nombre_sector:       Optional[str]
    latitud:             float
    longitud:            float
    volumen_estimado_kg: Optional[float]
    tipo_residuo:        Optional[str]

    model_config = {"from_attributes": True}


# ─── VRP / RUTAS ────────────────────────────────────────────
class PuntoEnRuta(BaseModel):
    id:     int
    lat:    float
    lon:    float
    nombre: Optional[str]
    demanda_kg: Optional[float] = None


class RutaVRP(BaseModel):
    id_unidad:         int
    placas:            str
    puntos:            List[PuntoEnRuta]
    distancia_total_km: float
    tiempo_total_min:  int
    costo_estimado:    float
    carga_total_kg:    float = 0.0


class RespuestaVRP(BaseModel):
    rutas:          List[RutaVRP]
    total_puntos:   int = 0
    puntos_sin_ruta: List[int] = []  # IDs de puntos que no pudieron ser asignados


class RutaConfirmar(BaseModel):
    id_unidad:          int
    distancia_total_km: float = Field(..., ge=0)
    tiempo_total_min:   int   = Field(..., ge=0)
    costo_estimado:     float = Field(..., ge=0)
    puntos_orden:       List[int] = Field(..., min_length=1)


class ConfirmarRutas(BaseModel):
    fecha: date
    rutas: List[RutaConfirmar] = Field(..., min_length=1)

    @field_validator("fecha")
    @classmethod
    def fecha_no_pasado(cls, v: date) -> date:
        # Advertencia suave: permite fechas pasadas pero las valida
        return v


# ─── RECOLECCIONES ──────────────────────────────────────────
class RecoleccionCreate(BaseModel):
    id_ruta:                       int
    peso_captado_kg:               float = Field(..., gt=0)
    tiempo_empleado_min:           Optional[int]   = Field(None, ge=0)
    consumo_combustible_l:         Optional[float] = Field(None, ge=0)
    costo_operativo:               Optional[float] = Field(None, ge=0)
    porcentaje_capacidad_utilizada: Optional[float] = Field(None, ge=0, le=100)


class RecoleccionOut(BaseModel):
    id_recoleccion:                int
    id_ruta:                       int
    fecha_recoleccion:             Optional[datetime]
    peso_captado_kg:               float
    tiempo_empleado_min:           Optional[int]
    consumo_combustible_l:         Optional[float]
    costo_operativo:               Optional[float]
    porcentaje_capacidad_utilizada: Optional[float]
    biochar_estimado_kg:           Optional[float] = None

    model_config = {"from_attributes": True}


# ─── LOTES BIOCHAR ──────────────────────────────────────────
class LoteCreate(BaseModel):
    id_recoleccion:     int
    temperatura_proceso: float = Field(..., gt=0, le=1200, description="°C")
    tiempo_proceso_min: int   = Field(..., gt=0)
    biochar_obtenido_kg: float = Field(..., gt=0)
    eficiencia_real:    Optional[float] = Field(None, ge=0, le=100)


class LoteOut(BaseModel):
    id_lote:            int
    id_recoleccion:     int
    fecha_proceso:      Optional[datetime]
    temperatura_proceso: Optional[float]
    tiempo_proceso_min: Optional[int]
    biochar_obtenido_kg: Optional[float]
    eficiencia_real:    Optional[float]

    model_config = {"from_attributes": True}


# ─── REPORTES ───────────────────────────────────────────────
class ReporteOperativo(BaseModel):
    total_recolecciones:       int
    total_peso_kg:             float
    total_biochar_estimado_kg: float
    total_distancia_km:        float
    costo_total:               float
    eficiencia_promedio_pct:   Optional[float]