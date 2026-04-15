from sqlalchemy import Column, Integer, String, Numeric
from app.database import Base

class Unidad(Base):
    __tablename__ = "unidades"

    id_unidad     = Column(Integer, primary_key=True, index=True)
    placas        = Column(String(20), nullable=False)
    modelo        = Column(String(50))
    capacidad_max_kg  = Column(Numeric(10, 2), nullable=False)
    rendimiento_km_l  = Column(Numeric(5, 2), nullable=False)
    estado        = Column(String(20), default="disponible")