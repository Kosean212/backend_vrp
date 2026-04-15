from sqlalchemy import Column, Integer, Numeric, Date, ForeignKey
from app.database import Base

class RutaGenerada(Base):
    __tablename__ = "rutas_generadas"

    id_ruta            = Column(Integer, primary_key=True, index=True)
    id_unidad          = Column(Integer, ForeignKey("unidades.id_unidad"), index=True)
    fecha              = Column(Date)
    distancia_total_km = Column(Numeric(10, 2))
    tiempo_total_min   = Column(Integer)
    costo_estimado     = Column(Numeric(10, 2))


class RutaPunto(Base):
    __tablename__ = "ruta_punto"

    id           = Column(Integer, primary_key=True, index=True)
    id_ruta      = Column(Integer, ForeignKey("rutas_generadas.id_ruta", ondelete="CASCADE"), index=True)
    id_punto     = Column(Integer, ForeignKey("puntos_recoleccion.id_punto"))
    orden_visita = Column(Integer, nullable=False)