from sqlalchemy import Column, Integer, Numeric, DateTime, Date, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

# Factor de conversión de residuo orgánico a biochar
FACTOR_BIOCHAR = 0.30


class Recoleccion(Base):
    __tablename__ = "recolecciones"

    id_recoleccion                 = Column(Integer, primary_key=True, index=True)
    id_ruta                        = Column(Integer, ForeignKey("rutas_generadas.id_ruta", ondelete="RESTRICT"), nullable=False, index=True)
    fecha_recoleccion              = Column(DateTime(timezone=True), server_default=func.now())
    peso_captado_kg                = Column(Numeric(10, 2), nullable=False)
    tiempo_empleado_min            = Column(Integer)
    consumo_combustible_l          = Column(Numeric(10, 2))
    costo_operativo                = Column(Numeric(10, 2))
    porcentaje_capacidad_utilizada = Column(Numeric(5, 2))


class LoteProduccion(Base):
    __tablename__ = "lotes_produccion"

    id_lote              = Column(Integer, primary_key=True, index=True)
    id_recoleccion       = Column(Integer, ForeignKey("recolecciones.id_recoleccion", ondelete="RESTRICT"), nullable=False, index=True)
    fecha_proceso        = Column(DateTime(timezone=True), server_default=func.now())
    temperatura_proceso  = Column(Numeric(6, 2))
    tiempo_proceso_min   = Column(Integer)
    biochar_obtenido_kg  = Column(Numeric(10, 2))
    eficiencia_real      = Column(Numeric(5, 2))