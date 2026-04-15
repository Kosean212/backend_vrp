export interface PuntoRecoleccion {
  id_punto: number;
  nombre_sector: string;
  latitud: number;
  longitud: number;
  volumen_estimado_kg: number;
  tipo_residuo: string;
}

export interface RutaOptimizada {
  id_unidad: number;
  placas: string;
  distancia_total_km: number;
  tiempo_total_min: number;
  costo_estimado: number;
  puntos: { id: number; lat: number; lon: number; nombre: string }[];
}

export interface RespuestaVRP {
  rutas: RutaOptimizada[];
}

export interface Recoleccion {
  id_recoleccion: number;
  id_ruta: number;
  fecha_recoleccion: string;
  peso_captado_kg: number;
  tiempo_empleado_min: number;
  consumo_combustible_l: number;
  costo_operativo: number;
  porcentaje_capacidad_utilizada: number;
  biochar_estimado_kg: number;
}

export interface LoteProduccion {
  id_lote: number;
  id_recoleccion: number;
  fecha_proceso: string;
  temperatura_proceso: number;
  tiempo_proceso_min: number;
  biochar_obtenido_kg: number;
  eficiencia_real: number;
}

export interface ReporteOperativo {
  total_recolecciones: number;
  total_peso_kg: number;
  total_biochar_estimado_kg: number;
  total_distancia_km: number;
  costo_total: number;
  eficiencia_promedio_pct?: number;
}
