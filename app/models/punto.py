from sqlalchemy import Column, Integer, String, Numeric
from app.database import Base

class PuntoRecoleccion(Base):
    __tablename__ = "puntos_recoleccion"

    id_punto             = Column(Integer, primary_key=True, index=True)
    nombre_sector        = Column(String(100))
    latitud              = Column(Numeric(10, 8), nullable=False)
    longitud             = Column(Numeric(11, 8), nullable=False)
    volumen_estimado_kg  = Column(Numeric(10, 2))
    tipo_residuo         = Column(String(50), default="organico")