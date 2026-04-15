import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Configuración de la URL de la base de datos
# Intentará leer desde las variables de entorno (.env), si no, usa la local
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:150698@localhost:5432/biochar_db")

# 2. Creación del motor (engine)
engine = create_engine(DATABASE_URL)

# 3. Configuración de la sesión
# autocommit=False y autoflush=False son las configuraciones recomendadas para FastAPI
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Clase base para los modelos
Base = declarative_base()

# 5. Dependencia para obtener la sesión de BD en las rutas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()