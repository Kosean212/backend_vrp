from ortools.constraint_solver import pywrapcp, routing_enums_pb2
import math

VELOCIDAD_PROMEDIO_KMH = 30   # velocidad urbana estimada
COSTO_LITRO_MXN = 22.0        # precio combustible referencia


def calcular_distancia_km(p1: dict, p2: dict) -> float:
    """Distancia Haversine entre dos puntos en kilómetros."""
    R = 6371.0
    lat1, lon1 = math.radians(p1["lat"]), math.radians(p1["lon"])
    lat2, lon2 = math.radians(p2["lat"]), math.radians(p2["lon"])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def crear_matriz_distancias(puntos: list) -> list:
    """Matriz de distancias en metros (enteros) requerida por OR-Tools."""
    return [
        [int(calcular_distancia_km(p1, p2) * 1000) for p2 in puntos]
        for p1 in puntos
    ]


def calcular_metricas_ruta(ruta_indices: list, puntos: list, rendimiento_km_l: float) -> dict:
    """
    Calcula distancia total, tiempo estimado y costo de combustible de una ruta.
    
    Args:
        ruta_indices: Lista de índices de puntos en orden de visita.
        puntos: Lista de dicts con lat/lon de cada punto.
        rendimiento_km_l: Rendimiento del vehículo en km/l.
    
    Returns:
        dict con distancia_km, tiempo_min y costo_estimado.
    """
    distancia_km = 0.0
    secuencia = ruta_indices + [ruta_indices[0]] if len(ruta_indices) > 1 else ruta_indices

    for i in range(len(secuencia) - 1):
        distancia_km += calcular_distancia_km(puntos[secuencia[i]], puntos[secuencia[i + 1]])

    tiempo_min = int((distancia_km / VELOCIDAD_PROMEDIO_KMH) * 60)
    litros = distancia_km / rendimiento_km_l if rendimiento_km_l > 0 else 0
    costo = round(litros * COSTO_LITRO_MXN, 2)

    return {
        "distancia_total_km": round(distancia_km, 3),
        "tiempo_total_min": tiempo_min,
        "costo_estimado": costo,
    }


def resolver_vrp(puntos: list, num_vehiculos: int, capacidades: list, deposito: int = 0) -> list:
    """
    Resuelve el VRP con capacidades usando OR-Tools.

    Args:
        puntos: Lista de dicts {"id", "lat", "lon", "demanda"}.
        num_vehiculos: Número de vehículos disponibles.
        capacidades: Lista de capacidades máximas por vehículo (mismo orden que unidades).
        deposito: Índice del punto depósito (por defecto 0).

    Returns:
        Lista de rutas; cada ruta es una lista de índices de puntos.
    """
    if not puntos or num_vehiculos == 0:
        return []

    matriz = crear_matriz_distancias(puntos)
    demandas = [int(p["demanda"]) for p in puntos]

    manager = pywrapcp.RoutingIndexManager(len(matriz), num_vehiculos, deposito)
    routing = pywrapcp.RoutingModel(manager)

    # Callback de distancia
    def distancia_callback(from_index, to_index):
        return matriz[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

    transit_idx = routing.RegisterTransitCallback(distancia_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)

    # Callback de demanda
    def demanda_callback(from_index):
        return demandas[manager.IndexToNode(from_index)]

    demanda_idx = routing.RegisterUnaryTransitCallback(demanda_callback)
    routing.AddDimensionWithVehicleCapacity(demanda_idx, 0, capacidades, True, "Capacity")

    # Parámetros de búsqueda
    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    params.time_limit.seconds = 15

    solution = routing.SolveWithParameters(params)

    rutas = []
    if solution:
        for v_id in range(num_vehiculos):
            index = routing.Start(v_id)
            ruta = []
            while not routing.IsEnd(index):
                nodo = manager.IndexToNode(index)
                ruta.append(nodo)
                index = solution.Value(routing.NextVar(index))
            # Excluir rutas vacías (solo el depósito)
            if len(ruta) > 1:
                rutas.append(ruta)

    return rutas