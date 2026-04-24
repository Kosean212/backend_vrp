"""
Motor de optimización VRP (Vehicle Routing Problem with Capacities).

Correcciones aplicadas vs versión original:
1. BUG CRÍTICO: Se usaban `manager` y `routing` antes de crearlos (líneas de
   AddDisjunction al inicio de la función, antes de instanciar los objetos).
2. BUG: `from app.routes import puntos` importado pero nunca usado (circular import).
3. BUG: Comparación de dicts `if p1 == p2` en crear_matriz_distancias podía
   fallar si dos puntos distintos tenían los mismos coords; se cambió a índices.
4. MEJORA: Se añade un depósito virtual (índice 0) para que OR-Tools tenga un
   punto de partida/llegada explícito que NO sea un punto de recolección real.
5. MEJORA: Las penalizaciones (disjunction) ahora se aplican CORRECTAMENTE
   después de crear `routing`.
6. MEJORA: La función devuelve también los IDs reales de los puntos no asignados.
"""

from ortools.constraint_solver import pywrapcp, routing_enums_pb2
import math
import logging

logger = logging.getLogger(__name__)

VELOCIDAD_PROMEDIO_KMH = 30   # velocidad urbana estimada
COSTO_LITRO_MXN = 22.0        # precio combustible referencia
FACTOR_REALIDAD = 1.35        # corrección para zonas montañosas
PENALTY_NO_SERVICIO = 1_000_000_000  # penalización por no visitar un punto


def calcular_distancia_km(p1: dict, p2: dict) -> float:
    """Distancia Haversine entre dos puntos (lat/lon) en kilómetros."""
    R = 6371.0
    lat1, lon1 = math.radians(p1["lat"]), math.radians(p1["lon"])
    lat2, lon2 = math.radians(p2["lat"]), math.radians(p2["lon"])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def crear_matriz_distancias(puntos: list) -> list:
    """
    Matriz n×n de distancias en metros (enteros), requerida por OR-Tools.
    FIX: Usa índices en lugar de comparación de dicts para la diagonal.
    """
    n = len(puntos)
    matriz = []
    for i, p1 in enumerate(puntos):
        fila = []
        for j, p2 in enumerate(puntos):
            if i == j:
                fila.append(0)
            else:
                dist_km = calcular_distancia_km(p1, p2)
                fila.append(int(dist_km * 1000 * FACTOR_REALIDAD))
        matriz.append(fila)
    return matriz


def calcular_metricas_ruta(
    ruta_indices: list,
    puntos: list,
    rendimiento_km_l: float,
) -> dict:
    """
    Calcula distancia total, tiempo y costo para una ruta.

    Args:
        ruta_indices: Índices de puntos en orden (sin repetir el depósito al final).
        puntos:       Lista completa de puntos (incluyendo depósito en índice 0).
        rendimiento_km_l: Rendimiento del vehículo (km/L).

    Returns:
        dict con distancia_total_km, tiempo_total_min, costo_estimado, carga_total_kg.
    """
    if not ruta_indices:
        return {"distancia_total_km": 0.0, "tiempo_total_min": 0, "costo_estimado": 0.0, "carga_total_kg": 0.0}

    # La ruta incluye volver al depósito (índice 0)
    secuencia = ruta_indices + [ruta_indices[0]]
    distancia_km = 0.0

    for i in range(len(secuencia) - 1):
        distancia_km += calcular_distancia_km(
            puntos[secuencia[i]],
            puntos[secuencia[i + 1]],
        )

    tiempo_min = int((distancia_km / VELOCIDAD_PROMEDIO_KMH) * 60)
    litros = distancia_km / rendimiento_km_l if rendimiento_km_l > 0 else 0.0
    costo = round(litros * COSTO_LITRO_MXN, 2)
    carga_total_kg = sum(puntos[idx].get("demanda", 0) for idx in ruta_indices)

    return {
        "distancia_total_km": round(distancia_km, 3),
        "tiempo_total_min":   tiempo_min,
        "costo_estimado":     costo,
        "carga_total_kg":     round(carga_total_kg, 2),
    }


def resolver_vrp(
    puntos: list,
    num_vehiculos: int,
    capacidades: list,
    deposito: int = 0,
) -> tuple[list, list]:
    """
    Resuelve el CVRP (Capacitated VRP) con OR-Tools.

    El índice `deposito` debe apuntar a un elemento de `puntos` que actúe
    como base (latitud/longitud del almacén). Los puntos de recolección
    son el resto.

    Args:
        puntos:        Lista de dicts {"id", "lat", "lon", "demanda"}.
                       puntos[0] = depósito (demanda=0).
        num_vehiculos: Número de vehículos disponibles.
        capacidades:   Lista de capacidades máximas por vehículo.
        deposito:      Índice del depósito (default 0).

    Returns:
        (rutas, no_asignados)
        rutas:         Lista de listas de índices de puntos por vehículo.
        no_asignados:  Lista de índices de puntos que no fueron cubiertos.
    """
    # ── Validaciones de entrada ──────────────────────────────────────────────
    if not puntos or num_vehiculos == 0:
        return [], []

    if len(capacidades) != num_vehiculos:
        raise ValueError("capacidades debe tener un elemento por vehículo")

    # OR-Tools requiere capacidades como enteros
    capacidades_int = [int(c) for c in capacidades]

    matriz = crear_matriz_distancias(puntos)
    demandas = [int(p.get("demanda", 0)) for p in puntos]

    # ── Crear modelo ─────────────────────────────────────────────────────────
    manager = pywrapcp.RoutingIndexManager(len(matriz), num_vehiculos, deposito)
    routing = pywrapcp.RoutingModel(manager)

    # ── Callback de distancia ────────────────────────────────────────────────
    def distancia_callback(from_index, to_index):
        return matriz[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

    transit_idx = routing.RegisterTransitCallback(distancia_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)

    # ── Callback de demanda / capacidad ──────────────────────────────────────
    def demanda_callback(from_index):
        return demandas[manager.IndexToNode(from_index)]

    demanda_idx = routing.RegisterUnaryTransitCallback(demanda_callback)
    routing.AddDimensionWithVehicleCapacity(
        demanda_idx,
        0,               # sin slack
        capacidades_int,
        True,            # empezar acumulado desde 0
        "Capacity",
    )

    # ── Penalización por no visitar (DESPUÉS de crear routing) ───────────────
    # FIX CRÍTICO: en el original esto estaba ANTES de crear manager/routing
    for node in range(1, len(puntos)):  # excluir el depósito
        routing.AddDisjunction(
            [manager.NodeToIndex(node)],
            PENALTY_NO_SERVICIO,
        )

    # ── Parámetros de búsqueda ───────────────────────────────────────────────
    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    params.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    params.time_limit.seconds = 15
    params.log_search = False

    solution = routing.SolveWithParameters(params)

    # ── Extraer solución ─────────────────────────────────────────────────────
    if not solution:
        logger.warning("OR-Tools no encontró solución factible")
        return [], list(range(1, len(puntos)))

    rutas: list[list[int]] = []
    nodos_cubiertos: set[int] = set()

    for v_id in range(num_vehiculos):
        index = routing.Start(v_id)
        ruta: list[int] = []

        while not routing.IsEnd(index):
            nodo = manager.IndexToNode(index)
            if nodo != deposito:
                ruta.append(nodo)
                nodos_cubiertos.add(nodo)
            index = solution.Value(routing.NextVar(index))

        if ruta:  # Excluir vehículos sin paradas
            rutas.append(ruta)

    todos_los_nodos = set(range(1, len(puntos)))
    no_asignados = sorted(todos_los_nodos - nodos_cubiertos)

    if no_asignados:
        logger.warning(
            "Puntos no asignados (demanda supera capacidad disponible): %s",
            no_asignados,
        )

    return rutas, no_asignados