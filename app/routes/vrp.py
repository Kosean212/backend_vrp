from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import List

from app.database import get_db
from app.models.punto import PuntoRecoleccion
from app.models.unidad import Unidad
from app.models.ruta import RutaGenerada, RutaPunto
from app.schemas import RespuestaVRP, RutaVRP, PuntoEnRuta, ConfirmarRutas
from app.optimization.vrp_solver import resolver_vrp, calcular_metricas_ruta

router = APIRouter(prefix="/rutas", tags=["Rutas VRP"])


@router.get("/optimizar", response_model=RespuestaVRP)
def optimizar_rutas(db: Session = Depends(get_db)):
    """
    Ejecuta el algoritmo VRP y devuelve las rutas optimizadas con métricas.
    No guarda nada en BD — usar /confirmar para persistir.
    """
    puntos_db  = db.query(PuntoRecoleccion).all()
    unidades_db = db.query(Unidad).filter(Unidad.estado == "disponible").all()

    if not puntos_db:
        raise HTTPException(status_code=400, detail="No hay puntos de recolección registrados")
    if not unidades_db:
        raise HTTPException(status_code=400, detail="No hay unidades disponibles")

    # Preparar datos para el solver
    puntos = [
        {
            "id": p.id_punto,
            "lat": float(p.latitud),
            "lon": float(p.longitud),
            "demanda": float(p.volumen_estimado_kg or 0),
        }
        for p in puntos_db
    ]
    capacidades = [int(u.capacidad_max_kg) for u in unidades_db]

    rutas_indices = resolver_vrp(puntos, len(capacidades), capacidades)

    if not rutas_indices:
        raise HTTPException(status_code=500, detail="El solver no encontró solución válida")

    rutas_respuesta: List[RutaVRP] = []
    for i, ruta in enumerate(rutas_indices):
        unidad = unidades_db[i]
        metricas = calcular_metricas_ruta(ruta, puntos, float(unidad.rendimiento_km_l))

        puntos_ruta = [
            PuntoEnRuta(
                id=puntos_db[idx].id_punto,
                lat=float(puntos_db[idx].latitud),
                lon=float(puntos_db[idx].longitud),
                nombre=puntos_db[idx].nombre_sector,
            )
            for idx in ruta
        ]

        rutas_respuesta.append(
            RutaVRP(
                id_unidad=unidad.id_unidad,
                placas=unidad.placas,
                puntos=puntos_ruta,
                **metricas,
            )
        )

    return RespuestaVRP(rutas=rutas_respuesta)


@router.post("/confirmar")
def confirmar_rutas(datos: ConfirmarRutas, db: Session = Depends(get_db)):
    """
    Persiste en BD las rutas optimizadas una vez revisadas por el operador.
    """
    try:
        for r in datos.rutas:
            nueva_ruta = RutaGenerada(
                id_unidad=r.id_unidad,
                fecha=datos.fecha,
                distancia_total_km=r.distancia_total_km,
                tiempo_total_min=r.tiempo_total_min,
                costo_estimado=r.costo_estimado,
            )
            db.add(nueva_ruta)
            db.flush()  # obtener id_ruta generado

            for orden, id_punto in enumerate(r.puntos_orden):
                db.add(RutaPunto(
                    id_ruta=nueva_ruta.id_ruta,
                    id_punto=id_punto,
                    orden_visita=orden,
                ))

        db.commit()
        return {"mensaje": "Rutas guardadas exitosamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/historial")
def historial_rutas(db: Session = Depends(get_db)):
    """Devuelve todas las rutas guardadas con sus puntos en orden."""
    rutas = db.query(RutaGenerada).order_by(RutaGenerada.fecha.desc()).all()
    resultado = []
    for ruta in rutas:
        puntos_orden = (
            db.query(RutaPunto)
            .filter(RutaPunto.id_ruta == ruta.id_ruta)
            .order_by(RutaPunto.orden_visita)
            .all()
        )
        resultado.append({
            "id_ruta": ruta.id_ruta,
            "id_unidad": ruta.id_unidad,
            "fecha": ruta.fecha,
            "distancia_total_km": float(ruta.distancia_total_km or 0),
            "tiempo_total_min": ruta.tiempo_total_min,
            "costo_estimado": float(ruta.costo_estimado or 0),
            "puntos": [p.id_punto for p in puntos_orden],
        })
    return resultado