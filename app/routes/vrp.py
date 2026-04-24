"""
Rutas VRP — endpoints de optimización y confirmación de rutas.

Cambios críticos respecto al original:
- Se agrega un depósito virtual (almacén de Teziutlán) como índice 0 de la
  lista de puntos enviada al solver. Esto es requerido por OR-Tools.
- Se propaga correctamente la lista de puntos no asignados al response.
- resolver_vrp ahora devuelve (rutas, no_asignados) → se desempaca.
- Se elimina la importación circular de logistica.py (schema duplicado).
"""

from fastapi import APIRouter, Depends, HTTPException, status
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

# Depósito: almacén central de Teziutlán, Puebla
DEPOSITO = {"id": 0, "lat": 19.817, "lon": -97.359, "demanda": 0, "nombre": "Depósito Central"}


@router.get("/optimizar", response_model=RespuestaVRP)
def optimizar_rutas(db: Session = Depends(get_db)):
    """
    Ejecuta el algoritmo CVRP y devuelve rutas optimizadas con métricas.
    El depósito (almacén) se inserta automáticamente como punto 0.
    """
    puntos_db  = db.query(PuntoRecoleccion).all()
    unidades_db = db.query(Unidad).filter(Unidad.estado == "disponible").all()

    if not puntos_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay puntos de recolección registrados",
        )
    if not unidades_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay unidades disponibles",
        )

    # 1. Construir lista: depósito en índice 0, luego puntos reales
    puntos_solver = [DEPOSITO] + [
        {
            "id":      p.id_punto,
            "lat":     float(p.latitud),
            "lon":     float(p.longitud),
            "demanda": int(p.volumen_estimado_kg or 0),
            "nombre":  p.nombre_sector,
        }
        for p in puntos_db
    ]
    capacidades = [int(u.capacidad_max_kg) for u in unidades_db]

    # 2. Validación de capacidad total (advertencia, no bloqueo)
    demanda_total   = sum(p["demanda"] for p in puntos_solver[1:])
    capacidad_total = sum(capacidades)

    if demanda_total > capacidad_total:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Demanda total ({demanda_total} kg) supera la capacidad "
                f"combinada de los vehículos ({capacidad_total} kg). "
                "Agrega más unidades o reduce los puntos."
            ),
        )

    # 3. Ejecutar solver
    try:
        rutas_indices, no_asignados_idx = resolver_vrp(
            puntos_solver, len(capacidades), capacidades, deposito=0
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en motor de optimización: {exc}",
        )

    if not rutas_indices:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El solver no encontró rutas factibles con las restricciones actuales",
        )

    # 4. Construir respuesta
    rutas_respuesta: List[RutaVRP] = []
    for i, ruta_idx in enumerate(rutas_indices):
        unidad  = unidades_db[i]
        metricas = calcular_metricas_ruta(ruta_idx, puntos_solver, float(unidad.rendimiento_km_l))

        puntos_ruta = [
            PuntoEnRuta(
                id=puntos_solver[idx]["id"],
                lat=puntos_solver[idx]["lat"],
                lon=puntos_solver[idx]["lon"],
                nombre=puntos_solver[idx].get("nombre"),
                demanda_kg=puntos_solver[idx].get("demanda"),
            )
            for idx in ruta_idx
        ]

        rutas_respuesta.append(
            RutaVRP(
                id_unidad=unidad.id_unidad,
                placas=unidad.placas,
                puntos=puntos_ruta,
                distancia_total_km=metricas["distancia_total_km"],
                tiempo_total_min=metricas["tiempo_total_min"],
                costo_estimado=metricas["costo_estimado"],
                carga_total_kg=metricas["carga_total_kg"],
            )
        )

    # IDs reales de puntos no asignados (convertir índices solver → ids BD)
    ids_no_asignados = [
        puntos_solver[idx]["id"]
        for idx in no_asignados_idx
        if idx < len(puntos_solver)
    ]

    return RespuestaVRP(
        rutas=rutas_respuesta,
        total_puntos=len(puntos_db),
        puntos_sin_ruta=ids_no_asignados,
    )


@router.post("/confirmar", status_code=status.HTTP_201_CREATED)
def confirmar_rutas(datos: ConfirmarRutas, db: Session = Depends(get_db)):
    """Persiste en BD las rutas optimizadas aprobadas por el usuario."""
    try:
        ids_creados = []
        for r in datos.rutas:
            # Verificar que la unidad existe
            unidad = db.query(Unidad).filter(Unidad.id_unidad == r.id_unidad).first()
            if not unidad:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Unidad {r.id_unidad} no encontrada",
                )

            nueva_ruta = RutaGenerada(
                id_unidad=r.id_unidad,
                fecha=datos.fecha,
                distancia_total_km=r.distancia_total_km,
                tiempo_total_min=r.tiempo_total_min,
                costo_estimado=r.costo_estimado,
            )
            db.add(nueva_ruta)
            db.flush()

            for orden, id_punto in enumerate(r.puntos_orden):
                db.add(RutaPunto(
                    id_ruta=nueva_ruta.id_ruta,
                    id_punto=id_punto,
                    orden_visita=orden,
                ))

            # Marcar unidad como en_ruta
            unidad.estado = "en_ruta"
            ids_creados.append(nueva_ruta.id_ruta)

        db.commit()
        return {"mensaje": "Rutas guardadas exitosamente", "ids_ruta": ids_creados}

    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.get("/historial")
def historial_rutas(db: Session = Depends(get_db)):
    """Devuelve el historial de rutas confirmadas, con sus puntos en orden."""
    rutas = db.query(RutaGenerada).order_by(RutaGenerada.fecha.desc()).all()
    resultado = []
    for ruta in rutas:
        # FIX: query explícita en lugar de relación ORM (compatible con modelo original)
        puntos_orden = (
            db.query(RutaPunto)
            .filter(RutaPunto.id_ruta == ruta.id_ruta)
            .order_by(RutaPunto.orden_visita)
            .all()
        )
        resultado.append({
            "id_ruta":            ruta.id_ruta,
            "id_unidad":          ruta.id_unidad,
            "fecha":              ruta.fecha,
            "distancia_total_km": float(ruta.distancia_total_km or 0),
            "tiempo_total_min":   ruta.tiempo_total_min,
            "costo_estimado":     float(ruta.costo_estimado or 0),
            "puntos": [
                {"id_punto": p.id_punto, "orden": p.orden_visita}
                for p in puntos_orden
            ],
        })
    return resultado


@router.delete("/{id_ruta}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_ruta(id_ruta: int, db: Session = Depends(get_db)):
    """Elimina una ruta y sus puntos asociados (CASCADE)."""
    ruta = db.query(RutaGenerada).filter(RutaGenerada.id_ruta == id_ruta).first()
    if not ruta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ruta no encontrada")
    db.delete(ruta)
    db.commit()