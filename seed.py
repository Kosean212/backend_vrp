from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.unidad import Unidad
from app.models.punto import PuntoRecoleccion

# Asegurarse de que las tablas existan
Base.metadata.create_all(bind=engine)

def seed():
    db = SessionLocal()
    try:
        # 1. Insertar Unidades (Camiones)
        if db.query(Unidad).count() == 0:
            unidades = [
                Unidad(placas="TEZ-01", modelo="International 4300", capacidad_max_kg=5000.0, rendimiento_km_l=3.5, estado="disponible"),
                Unidad(placas="TEZ-02", modelo="Foton Aumark", capacidad_max_kg=3000.0, rendimiento_km_l=5.0, estado="disponible"),
            ]
            db.add_all(unidades)
            print("✅ Unidades insertadas.")

        # 2. Insertar Puntos Reales (Teziutlán)
        if db.query(PuntoRecoleccion).count() == 0:
            puntos = [
                # El punto 0 suele ser el Depósito (Palacio Municipal o Limpia Pública)
                PuntoRecoleccion(nombre_sector="Depósito Municipal (Centro)", latitud=19.8172, longitud=-97.3592, volumen_estimado_kg=0),
                PuntoRecoleccion(nombre_sector="Mercado Victoria", latitud=19.8185, longitud=-97.3585, volumen_estimado_kg=150.5),
                PuntoRecoleccion(nombre_sector="Barrio de San Diego", latitud=19.8250, longitud=-97.3500, volumen_estimado_kg=85.0),
                PuntoRecoleccion(nombre_sector="Xoloco", latitud=19.8100, longitud=-97.3700, volumen_estimado_kg=120.0),
                PuntoRecoleccion(nombre_sector="Chignaulingo", latitud=19.8200, longitud=-97.3400, volumen_estimado_kg=95.0),
                PuntoRecoleccion(nombre_sector="La Legua", latitud=19.8300, longitud=-97.3650, volumen_estimado_kg=200.0),
            ]
            db.add_all(puntos)
            print("✅ Puntos de recolección insertados.")
        
        db.commit()
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()